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

// #include <Wire.h>

// #include "AD7994.h"
// #include "SHT31.h"
// #include "PT100.h"
#include "AegirData.h"

// Pin definitions
#define LEAK_CONTINUITY_PIN 2
#define LEAK_DETECT_PIN 3
#define WARNING_CONDITION_PIN 4
#define ERROR_CONDITION_PIN 6
#define PT100_T1_CS_PIN 7
#define PT100_T2_CS_PIN 8
#define RS485_DE_PIN 9
#define RS485_RE_PIN 10

// Resistance values for the PT100 RTD MAX31865 amplifiers
#define RREF 400.0
#define RNOMINAL 100.0

// Set to 1 to enable debug print
#define DEBUG_PRINT 1

// Devices and data structure instances
// AD7994 ad7994;
// SHT31 sht31;
// PT100 pt100;
Adafruit_BME280 bme280;
Adafruit_MAX31865 pt100[] = {
    Adafruit_MAX31865(PT100_T1_CS_PIN),
    Adafruit_MAX31865(PT100_T2_CS_PIN)
};
AegirData tx_data;

AnalogueThreshold threshold1(PIN_A0, 0.0, 100.0);

const unsigned int num_pt100 = sizeof(pt100) / sizeof(pt100[0]);

// Forward declarations
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
    // pinMode(LED_BUILTIN, OUTPUT);
    // pinMode(GPIO_OUTPUT_PIN, OUTPUT);
    pinMode(LEAK_CONTINUITY_PIN, INPUT);
    pinMode(LEAK_DETECT_PIN, INPUT);
    pinMode(WARNING_CONDITION_PIN, OUTPUT);
    pinMode(ERROR_CONDITION_PIN, OUTPUT);

    digitalWrite(WARNING_CONDITION_PIN, LOW);
    digitalWrite(ERROR_CONDITION_PIN, LOW);

    // Set RS485 transceiver RE and DE pins to output and set high to enable transmission
    pinMode(RS485_DE_PIN, OUTPUT);
    pinMode(RS485_RE_PIN, OUTPUT);
    digitalWrite(RS485_DE_PIN, HIGH);
    digitalWrite(RS485_RE_PIN, HIGH);

    // // Initialise the I2C bus
    // Wire.begin();

    // // Initialise the ADC
    // ad7994.begin();

    // Initialise the BME280 sensor
    bool status = bme280.begin();
    if (!status) {
        Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
        Serial.print("SensorID was: 0x"); Serial.println(bme280.sensorID(),16);
        Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
        Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
        Serial.print("        ID of 0x60 represents a BME 280.\n");
        Serial.print("        ID of 0x61 represents a BME 680.\n");
        while (1) delay(10);
    }

    // Initialise the PT100 sensors (MAX31865 devices)
    Serial.print("Number of PT100 channels: "); Serial.println(num_pt100);

    for (int idx = 0; idx < num_pt100; idx++)
    {
        pt100[idx].begin(MAX31865_4WIRE);
    }

    for (int idx = 0; idx < 5; idx++)
    {
        threshold1.update();
        float value = threshold1.value();
        Serial.println("Calculated value is: " + String(value));
    }

}

// Loop function - reads all the appropriate data from the board and transmit over the
// RS485 serial port
void loop()
{

    // Static led state flag - used to bcycle LED to indicate activity
    static uint8_t led_state = HIGH;

    // Toggle state of LED
    led_state = (led_state == HIGH ? LOW : HIGH);
    // digitalWrite(LED_BUILTIN, led_state);

    // Set GPIO output pin high - this is done temporarily to time the loop functionality
    // digitalWrite(GPIO_OUTPUT_PIN, HIGH);

    // Read the GPIO pins for leak continuity, detection and overall fault condition
    tx_data.leak_continuity = digitalRead(LEAK_CONTINUITY_PIN);
    // tx_data.leak_detected = 1 - digitalRead(LEAK_DETECT_PIN);
    tx_data.leak_detected = digitalRead(LEAK_DETECT_PIN);
    // tx_data.fault_condition = 1 - digitalRead(FAULT_CONDITION_PIN);
    tx_data.fault_condition = 0;

    // digitalWrite(ERROR_CONDITION_PIN, led_state);

    // Read the raw ADC values
    for (uint8_t idx = 0; idx < AEGIR_ADC_CHANNELS; idx++)
    {
        // tx_data.adc_val[idx] = ad7994.read_adc_chan(idx);
        tx_data.adc_val[idx] = analogRead(A0 + idx);
    }

    // Convert the raw ADC values into the appropriate measurements
    // tx_data.board_humidity = sht31.relative_humidity((float)tx_data.adc_val[0] / 4095.0);
    // tx_data.board_temperature = sht31.temperature((float)tx_data.adc_val[1] / 4095.0);
    // tx_data.probe_temperature[0] = pt100.temperature(tx_data.adc_val[2]);
    // tx_data.probe_temperature[1] = pt100.temperature(tx_data.adc_val[3]);
    tx_data.board_humidity = bme280.readHumidity();
    tx_data.board_temperature = bme280.readTemperature();
    for (int idx = 0; idx < num_pt100; idx++)
    {
        tx_data.probe_temperature[idx] = pt100[idx].temperature(RNOMINAL, RREF);
    }

    // Update the data structure checksum
    tx_data.update_checksum();

    // Print debug output if enabled
    if (DEBUG_PRINT)
    {
        dump_data();
    }

    // Transmit the data structure over the RS485 serial port
    uint8_t* ptr = (uint8_t *)&tx_data;
    for (int idx = 0; idx < sizeof(tx_data); idx++)
    {
        Serial1.write(ptr[idx]);
    }

    // Toggle the GPIO pin low to signal end the loop activity
   //  digitalWrite(GPIO_OUTPUT_PIN, LOW);

    // Delay for 1 second
    delay(1000);

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
    Serial.println(tx_data.fault_condition);

    Serial.print("Raw ADC: ");
    for (int idx = 0; idx < 4; idx++)
    {
        Serial.print(idx);
        Serial.print(": 0x");
        Serial.print(tx_data.adc_val[idx], HEX);
        Serial.print(" (");
        Serial.print(tx_data.adc_val[idx]);
        Serial.print(", ");
        // Serial.print(ad7994.adc_to_volts(tx_data.adc_val[idx]), 2);
        Serial.print(((float)tx_data.adc_val[idx] / 1023) * 5.0, 2);
        Serial.print("V) ");
    }
    Serial.println("");

    Serial.print("SHT31: rel humidity: ");
    Serial.print(tx_data.board_humidity, 1);
    Serial.print(" % ");
    Serial.print("temp: ");
    Serial.print(tx_data.board_temperature, 1);
    Serial.println(" C");

    Serial.print("PT100 temps: 1: ");
    Serial.print(tx_data.probe_temperature[0], 1);
    Serial.print(" (+/-)0.5 C ");

    Serial.print("2: ");
    Serial.print(tx_data.probe_temperature[1], 1);
    Serial.println(" (+/-)0.5 C");

    Serial.print("Checksum: 0x");
    Serial.print((int)tx_data.checksum, HEX);
    Serial.print(" (");
    Serial.print((int)tx_data.checksum);
    Serial.println(")");

    Serial.println("");
}

