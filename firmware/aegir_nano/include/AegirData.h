/*
 * AegirData.h - data structure representing AEGIR data
 *
 * This header implements a simple data struct that is used for
 * storing and transmittig leak detection data from the AEGIR system
 *
 * James Foster, Tim Nicholls, STFC Detector Systems Software Group
 */

#ifndef _INCLUDE_AEGIR_DATA_H_
#define _INCLUDE_AEGIR_DATA_H_

#include <Arduino.h>

#define AEGIR_ADC_CHANNELS 4  // Number of ADC channels
#define AEGIR_TEMP_PROBES  2  // Number of external temperature probes

struct AegirData
{
    uint16_t adc_val[AEGIR_ADC_CHANNELS];       // Raw ADC channel values

    float board_temperature;                    // Board temperature (Celsius)
    float board_humidity;                       // Board relative humidity (%)
    float probe_temperature[AEGIR_TEMP_PROBES]; // PT100 probe temperatures (Celsuis)

    bool leak_detected;                         // Leak detection flag
    bool leak_continuity;                       // Leak continuity flag
    bool fault_condition;                       // Fault condition flag
    uint8_t checksum;                           // XOR checksum
    const uint16_t eop = 0xA5A5;                // End of packet marker

    // Update the checksum in the data structure
    void update_checksum()
    {
        checksum = 0;
        uint8_t *ptr = (uint8_t*)this;

        // Calculate size of data structure exclduing checksum and EOP marker
        int data_len = sizeof(AegirData) - sizeof(checksum) - sizeof(eop);

        // Loop through data bytes and update XOR checksum
        for (int idx= 0; idx < data_len; idx++)
        {
            checksum ^= ptr[idx];
        }
    }

};// AegirData;

#endif