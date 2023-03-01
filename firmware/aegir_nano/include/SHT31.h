/*
 * SHT31.h - simple container class for SHT31 temperature and humidity conversions
 *
 * This header implrements a simple container class providing temperature and humidity conversions
 * utility functions for the SHT31 device implemented on the AEGIR leak detection board.
 *
 * Tim Nicholls, STFC Detector Systems Software Group
 */

#ifndef _INCLUDE_SHT31_H_
#define _INCLUDE_SHT31_H_
#include <Arduino.h>

class SHT31
{
public:

    //! Constructor (empty)
    SHT31(void) { };

    //! Convert a SHT31 humidity voltage output into relative humidity
    //!
    //! This utility method converts a voltage reading of the humidity output channel of a SHT31
    //! device into a relative humidity in percent. The conversion factors are provided by the SHT31
    //! datasheet.
    //!
    //! \param[in] v_humidity - floating point humidity voltage
    //! \returns floating point relative humidity in percent
    float relative_humidity(float v_humidity)
    {
        return -12.5 + 125.0 * v_humidity;
    }

    //! Convert a SHT31 temperature voltage output into temperature
    //!
    //! This utility method converts a voltage reading of the temperature output channel of a SHT31
    //! device into temperature in Celsius. The conversion factors are provided by the SHT31
    //! datasheet.
    //!
    //! \param[in] v_temperature - floating point temperature voltage
    //! \returns floating point temperature in Celsius
    float temperature(float v_temperature)
    {
        return -66.875 + 218.75 * v_temperature;
    }
};

#endif // _INCLUDE_SHT31_H_