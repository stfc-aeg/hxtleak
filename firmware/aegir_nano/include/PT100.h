/*
 * PT100.h - simple container class for PT100 temperature conversions
 *
 * This header implrements a simple container class providing temperature conversion utilities for
 * the PT100 devices included in the AEGIR leak detection board.
 *
 * Tim Nicholls, STFC Detector Systems Software Group
 */
#ifndef _INCLUDE_PT100_H_
#define _INCLUDE_PT100_H_

#include <Arduino.h>

class PT100
{
public:

    //! Constructor (empty)
    PT100(void) { };

    //! Convert raw ADC value into PT1100 temperatur
    //!
    //! This utility method converts a raw ADC value into a PT100 temperature, derived from
    //! a measured calibration.
    //!
    //! CAUTION - this conversion is calibration dependent and may not be stable across all boards
    //! and devices
    //!
    //! \param[in] raw_adc_val - raw ADC value
    //! \return - floating point temperature in Celsius
    float temperature(uint16_t raw_adc_val)
    {
        //return (float)raw_adc_val * 0.1972 - 491.3;
        return (float)raw_adc_val * 0.096 - 262.12;
    }
};

#endif // _INCLUDE_PT100_H_