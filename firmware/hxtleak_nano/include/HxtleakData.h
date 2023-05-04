/*
 * HxtleakData.h - data structure representing HEXITEC leak detector data
 *
 * This header implements a simple data struct that is used for
 * storing and transmittig leak detection data from the HEXITEC leak detector system
 *
 * James Foster, Tim Nicholls, STFC Detector Systems Software Group
 */

#ifndef _INCLUDE_HXTLEAK_DATA_H_
#define _INCLUDE_HXTLEAK_DATA_H_

#include <Arduino.h>

#define HXTLEAK_SENSOR_THRESHOLDS 4 // Number of sensor thresholds
#define HXTLEAK_TEMP_PROBES  2  // Number of external temperature probes

#define STATUS_BOARD_SENSOR_INIT_ERROR 0
#define STATUS_PROBE_SENSOR_INIT_ERROR 1
#define STATUS_BOARD_SENSOR_READ_ERROR 2
#define STATUS_PROBE_SENSOR_READ_ERROR 3
#define STATUS_BOARD_TEMPERATURE_WARNING 4
#define STATUS_BOARD_HUMIDITY_WARNING 5
#define STATUS_PROBE_1_TEMPERATURE_FAULT 6
#define STATUS_PROBE_2_TEMPERATURE_FAULT 7

struct HxtleakData
{
    float threshold[HXTLEAK_SENSOR_THRESHOLDS];   // Sensor thresholds

    float board_temperature;                      // Board temperature (Celsius)
    float board_humidity;                         // Board relative humidity (%)
    float probe_temperature[HXTLEAK_TEMP_PROBES]; // PT100 probe temperatures (Celsuis)

    bool leak_detected;                           // Leak detection flag
    bool leak_continuity;                         // Leak continuity flag
    bool fault_condition;                         // Fault condition flag
    bool warning_condition;                       // Warning condition flag
    uint8_t sensor_status;                        // Sensor status bits
    uint8_t checksum;                             // XOR checksum
    const uint16_t eop = 0xA5A5;                  // End of packet marker

    // Update the checksum in the data structure
    void update_checksum()
    {
        checksum = 0;
        uint8_t *ptr = (uint8_t*)this;

        // Calculate size of data structure exclduing checksum and EOP marker
        int data_len = sizeof(HxtleakData) - sizeof(checksum) - sizeof(eop);

        // Loop through data bytes and update XOR checksum
        for (int idx= 0; idx < data_len; idx++)
        {
            checksum ^= ptr[idx];
        }
    }

    void set_sensor_status(uint8_t bit, bool value)
    // Set a bit in the sensor status field to a specific value
    {
        if (value)
        {
            set_sensor_status(bit);
        }
        else
        {
            clear_sensor_status(bit);
        }
    }

    // Set a bit in the sensor status field
    void set_sensor_status(uint8_t bit)
    {
        sensor_status |= 1 << bit;
    }

    // Set a bit in the sensor status field
    void clear_sensor_status(uint8_t bit)
    {
        sensor_status &= ~(1 << bit);
    }

};// HxtleakData;

#endif