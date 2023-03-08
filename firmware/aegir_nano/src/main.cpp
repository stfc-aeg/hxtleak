/*
 * main.cpp - AEGIR leak detectormicrocontroller implementation
 *
 * This file implements the main functionality of the AEGDIR leak detector microcontroller. This
 * this based on the Arduino framework and targets an Arduino Nano Every device.
 *
 * James Foster, Tim Nicholls, STFC Detector Systems Software Group
 */
#include <Arduino.h>
#include <Adafruit_BME280.h>
#include <Adafruit_MAX31865.h>

#include "AnalogueThreshold.h"

#include "AegirData.h"

// Pin definitions
#define LEAK_CONTINUITY_PIN 2
#define LEAK_DETECT_PIN 3
#define WARNING_CONDITION_PIN 4
#define ERROR_CONDITION_PIN 6
#define GPIO_OUTPUT_PIN 5
#define PT100_T1_CS_PIN 8
#define PT100_T2_CS_PIN 7
#define RS485_DE_PIN 9
#define RS485_RE_PIN 10

// Resistance values for the PT100 RTD MAX31865 amplifiers
#define RREF 400.0
#define RNOMINAL 100.0

// Set to 1 to enable debug print
#define DEBUG_PRINT 0

// Update period in ms
int update_period = 500;
unsigned long time_now = 0;

// Devices and data structure instances
Adafruit_BME280 bme280;
Adafruit_MAX31865 pt100[] = {
    Adafruit_MAX31865(PT100_T1_CS_PIN),
    Adafruit_MAX31865(PT100_T2_CS_PIN)
};

const unsigned int num_pt100 = sizeof(pt100) / sizeof(pt100[0]);

enum Threshold
{
    board_temp = 0,
    board_humidity = 1,
    probe_temp_1 = 2,
    probe_temp_2 = 3,
};

AnalogueThreshold threshold[] = {
    AnalogueThreshold("board_temp", PIN_A3, 0.0, 100.0, 1.0),
    AnalogueThreshold("board_humidity", PIN_A2, 0.0, 100.0, 1.0),
    AnalogueThreshold("probe_temp_1", PIN_A1, 0.0, 100.0, 1.0),
    AnalogueThreshold("probe_temp_2", PIN_A0, 0.0, 100.0, 1.0),
};
const unsigned int num_threshold = sizeof(threshold) / sizeof(threshold[0]);

AegirData tx_data;

// Forward declarations
void update_state(void);
void dump_data(void);

// Setup function - configure the various resources used by the system
void setup()
{

    //Initialise the serial comms port
    Serial.begin(57600);
    while (!Serial) { ;}
    Serial.println("AEGIR startup");

    // Set up the second serial port for RS485 data transmission
    Serial1.begin(57600);
    while (!Serial1) { ;}

    // Set GPIO pins to appropriate modes
    pinMode(LEAK_CONTINUITY_PIN, INPUT);
    pinMode(LEAK_DETECT_PIN, INPUT);
    pinMode(WARNING_CONDITION_PIN, OUTPUT);
    pinMode(ERROR_CONDITION_PIN, OUTPUT);
    pinMode(GPIO_OUTPUT_PIN, OUTPUT);

    digitalWrite(WARNING_CONDITION_PIN, LOW);
    digitalWrite(ERROR_CONDITION_PIN, LOW);
    digitalWrite(GPIO_OUTPUT_PIN, LOW);

    // Set RS485 transceiver RE and DE pins to output and set high to enable transmission
    pinMode(RS485_DE_PIN, OUTPUT);
    pinMode(RS485_RE_PIN, OUTPUT);
    digitalWrite(RS485_DE_PIN, HIGH);
    digitalWrite(RS485_RE_PIN, HIGH);

    // Initialise the BME280 sensor
    bool status = bme280.begin();
    if (!status) {
        Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
        Serial.print("SensorID was: 0x"); Serial.println(bme280.sensorID(),16);
        Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
        Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
        Serial.print("        ID of 0x60 represents a BME 280.\n");
        Serial.print("        ID of 0x61 represents a BME 680.\n");

        // TODO set error bit in status word
    }

    // Initialise the PT100 sensors (MAX31865 devices)
    Serial.print("Number of PT100 channels: "); Serial.println(num_pt100);

    for (int idx = 0; idx < num_pt100; idx++)
    {
        pt100[idx].begin(MAX31865_4WIRE);
        pt100[idx].enable50Hz(true);
    }

}

// Loop function - call the state update method with the specified update period
void loop()
{
    // Evaluate if time since last update exceeds period and do update if so. This check
    // accommodates the millis() call wrapping periodically
    if ((unsigned long)(millis() - time_now) > update_period)
    {
        time_now = millis();
        update_state();
    }
}

// Update the state of all sensors, evaluate error and warning conditions and transmit
// data to the controller via the RS485 serial port.
void update_state()
{

    // Set GPIO output pin high (used for timing measurements)
    digitalWrite(GPIO_OUTPUT_PIN, HIGH);

    // Read the GPIO pins for leak continuity and detection
    tx_data.leak_continuity = digitalRead(LEAK_CONTINUITY_PIN);
    tx_data.leak_detected = digitalRead(LEAK_DETECT_PIN);
    tx_data.fault_condition = 0;
    tx_data.warning_condition = 0;

    // Update the analogue thresholds
    for (uint8_t idx = 0; idx < num_threshold; idx++)
    {
        threshold[idx].update();
        tx_data.threshold[idx] = threshold[idx].value();
    }

    // Update all sensor measurements
    tx_data.board_temperature = bme280.readTemperature();
    tx_data.board_humidity = bme280.readHumidity();
    for (int idx = 0; idx < num_pt100; idx++)
    {
        tx_data.probe_temperature[idx] = pt100[idx].temperature(RNOMINAL, RREF);
    }

    // Compare the sensor readings with their respective thresholds
    bool board_temp_ok = threshold[Threshold::board_temp].compare(tx_data.board_temperature);
    bool board_humidity_ok = threshold[Threshold::board_humidity].compare(tx_data.board_humidity);
    bool probe_temp_0_ok = threshold[Threshold::probe_temp_1].compare(tx_data.probe_temperature[0]);
    bool probe_temp_1_ok = threshold[Threshold::probe_temp_2].compare(tx_data.probe_temperature[1]);

    // Evaluate the warning condition based on board temperature and humidity and update warning
    // pin state accordingly
    tx_data.warning_condition = !(board_temp_ok && board_humidity_ok);
    digitalWrite(WARNING_CONDITION_PIN, tx_data.warning_condition);

    // Evaluate the error condition based on probe temperatures and leak continuity and update
    // error pin state accordingly
    bool error_condition = !(
        tx_data.leak_continuity && probe_temp_0_ok && probe_temp_1_ok
    );
    digitalWrite(ERROR_CONDITION_PIN, error_condition);

    // The fault condition output to the controller board is OR of error condition and leak
    // detection state, so mirror that in the transmitted data structure
    tx_data.fault_condition = tx_data.leak_detected | error_condition;

    // Update the data structure checksum
    tx_data.update_checksum();

    // Transmit the data structure over the RS485 serial port
    uint8_t* ptr = (uint8_t *)&tx_data;
    for (int idx = 0; idx < sizeof(tx_data); idx++)
    {
        Serial1.write(ptr[idx]);
    }

    // Print debug output if enabled
    if (DEBUG_PRINT)
    {
        dump_data();
    }

    // Toggle the GPIO pin low to signal end the loop activity
    digitalWrite(GPIO_OUTPUT_PIN, LOW);

}

// Print debug output of all measured parameters in the data structure
void dump_data(void)
{

    // Print status of all measurements
    Serial.print("Leak: ");
    Serial.print(tx_data.leak_detected);

    Serial.print(" Cont: ");
    Serial.print(tx_data.leak_continuity);

    Serial.print(" Fault: ");
    Serial.print(tx_data.fault_condition);

    Serial.print(" Warning: ");
    Serial.println(tx_data.warning_condition);

    Serial.print("Thresholds: ");
    for (int idx = 0; idx < num_threshold; idx++)
    {
        Serial.print(String(idx) + ": " + threshold[idx].name() + " ");
        Serial.print(tx_data.threshold[idx], 1);
        Serial.print(" ");
    }
    Serial.println("");

    Serial.print("Board: temp ");
    Serial.print(tx_data.board_temperature, 1);
    Serial.print(" C rel humidity: ");
    Serial.print(tx_data.board_humidity, 1);
    Serial.println(" % ");

    Serial.print("Probe temps: 1: ");
    Serial.print(tx_data.probe_temperature[0], 1);
    Serial.print(" C ");

    Serial.print("2: ");
    Serial.print(tx_data.probe_temperature[1], 1);
    Serial.println(" C");

    Serial.print("Checksum: 0x");
    Serial.print((int)tx_data.checksum, HEX);
    Serial.print(" (");
    Serial.print((int)tx_data.checksum);
    Serial.println(")");

    Serial.println("");
}

