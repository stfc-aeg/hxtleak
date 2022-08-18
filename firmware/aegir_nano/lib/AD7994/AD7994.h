/*
 * AD7994.h - Analog Devices AD7994 4-channel I2C ADC device library
 *
 * This library implements simple support for the AD7994 ADC device.
 *
 * Author: Tim Nicholls, STFC Detector Systems Software Group
 */

#ifndef _INCLUDE_AD7994_H_
#define _INCLUDE_AD7994_H_

#include <Arduino.h>
#include <Wire.h>

#define DEFAULT_AD7994_I2C_ADDR 0x21   // Default I2C address for the AD7994
#define AD7994_NUM_CHANNELS 4          // Number of ADC channels

//! AD7994 device support class
//!
//! This class implemnents support for the AD7994 I2C ADC. At present, only command mode (mode 2)
//! ADC immediate conversions are supported.
class AD7994
{
public:

    //! Constructor
    AD7994(void);

    //! Start the device, setting I2C address and bus type (Arduino Wire instance)
    bool begin(uint8_t i2c_address=DEFAULT_AD7994_I2C_ADDR, TwoWire& i2c_bus = Wire);

    //! Check if the AD7994 device is connected on the specified address
    bool is_connected(void);

    //! Read the value of the specified ADC channel
    uint16_t read_adc_chan(uint8_t chan_idx);

    //! Convert a raw ADC value into volts
    float adc_to_volts(uint16_t raw_adc);

private:

    uint8_t i2c_address_;   // I2C address of the device
    TwoWire* i2c_bus_;      // I2C bus (Arduino TwoWire instance)
    float v_ref_;           // AD7994 external voltage reference

};

#endif // _INCLUDE_AD7994_H_

