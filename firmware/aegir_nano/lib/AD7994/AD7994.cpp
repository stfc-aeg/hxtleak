/*
 * AD7994.cpp - Analog Devices AD7994 4-channel I2C ADC device library
 *
 * This library implements simple support for the AD7994 ADC device.
 *
 * Author: Tim Nicholls, STFC Detector Systems Software Group
 */

#include "AD7994.h"

//! Constructor
AD7994::AD7994(void) :
    v_ref_(5.0) // default voltage reference
{
    // This does no initialisation, simply creates the instance
}

//! Start the device, setting I2C address and bus type (Arduino Wire instance)
//!
//! The method sets up the AD7994 for operation. The specified address and bus type
//! are stored and access to the device over the I2C bus is confirmed.
//!
//! \param[in] i2c_address - I2C bus address of the AD7994 (defaults to 0x21)
//! \param[in] i2c_bus - I2C bus object (defaults to Arduino TwoWire instance)
//!
//! \return - true if device is connected at the specified address

bool AD7994::begin(uint8_t i2c_address, TwoWire& i2c_bus)
{
    // Save the device address and bus instance
    i2c_address_ = i2c_address;
    i2c_bus_ = &i2c_bus;

    // Check if connected and return status
    bool connected = is_connected();
    if (!connected)
    {
        Serial.println("ERROR: AD7994 device not connected");
    }
    return connected;
}

//! Check if the AD7994 device is connected on the specified address
//!
//! This method checks if the AD7994 device is connected and responds at the specified address.
//! This is achieved by executing an empty I2C transaction.
//!
//! \return - true if the AD7994 is connected and responding

bool AD7994::is_connected(void)
{
    i2c_bus_->beginTransmission(i2c_address_);
    return (i2c_bus_->endTransmission() == 0);
}

//! Read the value of the specified ADC channel
//!
//! This method triggers a command mode (mode 2) conversion of the specified ADC channel, reads
//! and returns the value.
//!
//! \param[in] chan_idx - ADC channel index
//!
//! \return - uint16_t value read from the specified channel

uint16_t AD7994::read_adc_chan(uint8_t chan_idx)
{
    uint16_t adc_val = 0;

    // Check that the specified channel is within range
    if (chan_idx >= AD7994_NUM_CHANNELS)
    {
        Serial.println("ERROR: illegal channel requested");
        return adc_val;
    }

    // Construct the address pointer for a mode 2 conversion
    uint8_t adc_addr_ptr = 1 << (4 + chan_idx);

    // Write the address pointer to the device
    i2c_bus_->beginTransmission(i2c_address_);
    i2c_bus_->write(adc_addr_ptr);
    i2c_bus_->endTransmission();

    // Read two bytes back from the ADC, packing them into a uint16_t ADC value
    i2c_bus_->requestFrom(i2c_address_, (size_t)2);
    if (2 <= i2c_bus_->available())
    {
        adc_val = i2c_bus_->read();
        adc_val = adc_val << 8;
        adc_val |= i2c_bus_->read();
        adc_val = adc_val & 0xFFF;
    }
    else
    {
        Serial.println("ERROR: no response from ADC");
    }

    // Return the channel value
    return adc_val;
}

//! Convert a raw ADC value into volts
//!
//! This method converts a raw ADC value into a voltage, based on the current voltage
//! reference
//!
//! \param[in] raw_adc - raw ADC value
//! \return floating point ADC voltage value

float AD7994::adc_to_volts(uint16_t raw_adc)
{
    return ((float)raw_adc / 4095.0) * v_ref_;
}