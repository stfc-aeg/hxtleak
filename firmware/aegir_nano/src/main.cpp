/*
 * main.cpp - AEGIR leak detectormicrocontroller implementation
 *
 * This file implements the main functionality of the AEGDIR leak detector microcontroller. This
 * this based on the Arduino framework and targets an Arduino Nano Every device.
 *
 * James Foster, Tim Nicholls, STFC Detector Systems Software Group
 */
#include <Arduino.h>
#include <Wire.h>

#include "AD7994.h"
#include "SHT31.h"
#include "PT100.h"
#include "AegirData.h"

// Pin definitions
#define LEAK_CONTINUITY_PIN 2
#define LEAK_DETECT_PIN 3
#define GPIO_OUTPUT_PIN 4
#define FAULT_CONDITION_PIN 6
#define RS485_DE_PIN 9
#define RS485_RE_PIN 10

// Set to 1 to enable debug print
#define DEBUG_PRINT 1

// Devices and data structure instances
AD7994 ad7994;
SHT31 sht31;
PT100 pt100;
AegirData tx_data;

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
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(GPIO_OUTPUT_PIN, OUTPUT);
    pinMode(LEAK_CONTINUITY_PIN, INPUT);
    pinMode(LEAK_DETECT_PIN, INPUT);
    pinMode(FAULT_CONDITION_PIN, INPUT);

    digitalWrite(GPIO_OUTPUT_PIN, LOW);

    // Set RS485 transceiver RE and DE pins to output and set high to enable transmission
    pinMode(RS485_DE_PIN, OUTPUT);
    pinMode(RS485_RE_PIN, OUTPUT);
    digitalWrite(RS485_DE_PIN, HIGH);
    digitalWrite(RS485_RE_PIN, HIGH);

    // Initialise the I2C bus
    Wire.begin();

    // Initialise the ADC
    ad7994.begin();

}

// Loop function - reads all the appropriate data from the board and transmit over the
// RS485 serial port
void loop()
{

    // Static led state flag - used to bcycle LED to indicate activity
    static uint8_t led_state = HIGH;

    // Toggle state of LED
    led_state = (led_state == HIGH ? LOW : HIGH);
    digitalWrite(LED_BUILTIN, led_state);

    // Set GPIO output pin high - this is done temporarily to time the loop functionality
    digitalWrite(GPIO_OUTPUT_PIN, HIGH);

    // Read the GPIO pins for leak continuity, detection and overall fault condition
    tx_data.leak_continuity = digitalRead(LEAK_CONTINUITY_PIN);
    tx_data.leak_detected = 1 - digitalRead(LEAK_DETECT_PIN);
    tx_data.fault_condition = 1 - digitalRead(FAULT_CONDITION_PIN);

    // Read the raw ADC values
    for (uint8_t idx = 0; idx < AEGIR_ADC_CHANNELS; idx++)
    {
        tx_data.adc_val[idx] = ad7994.read_adc_chan(idx);
    }

    // Convert the raw ADC values into the appropriate measurements
    tx_data.board_humidity = sht31.relative_humidity((float)tx_data.adc_val[0] / 4095.0);
    tx_data.board_temperature = sht31.temperature((float)tx_data.adc_val[1] / 4095.0);
    tx_data.probe_temperature[0] = pt100.temperature(tx_data.adc_val[2]);
    tx_data.probe_temperature[1] = pt100.temperature(tx_data.adc_val[3]);

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
    digitalWrite(GPIO_OUTPUT_PIN, LOW);

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
        Serial.print(ad7994.adc_to_volts(tx_data.adc_val[idx]), 2);
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

