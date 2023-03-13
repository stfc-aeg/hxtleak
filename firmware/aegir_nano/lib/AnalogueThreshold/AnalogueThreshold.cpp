/*
 * AnalogueThreshold.cpp - rolling average analogue threshold
 *
 * This library implements a rolling average analogue threshold based on sampling an analogue input
 * pin of the Arduino.
 *
 * Author: Tim Nicholls, STFC Detector Systems Software Group
 */

#include "AnalogueThreshold.h"

//! AnalogueThreshold constructor
//!
//! This constructor fully initalises an analogue threshold, including giving minimum and maximum
//! values to define a scale agaisnt a physical value, e.g. temperature.
//!
//! \param[in] name - logical name for theshold (can be used for debug printout)
//! \param[in] pin_number - Arduino analogue pin number
//! \param[in] min_val - miniumum scale value for threshold
//! \param[in] max_val - maxiumum scale value for threshold
//! \param[in] num_samples - (optional) number of samples for rolling average
//!
AnalogueThreshold::AnalogueThreshold(
    const char* name, pin_size_t pin_number, float min_val, float max_val,
    float hysteresis, uint8_t num_samples
) :
    AnalogueThreshold(name, pin_number, num_samples)
{
    // Set minimum and maximum scale values and calculate range
    min_val_ = min_val;
    max_val_ = max_val;
    range_ = max_val_ - min_val;

    // Set the hysteresis value
    hysteresis_ = hysteresis;
}

//! AnalogueThreshold constructor
//!
//! This constructor minimally-initalises an analogue threshold.
//!
//! \param[in] name - logical name for theshold (can be used for debug printout)
//! \param[in] pin_number - Arduino analogue pin number
//! \param[in] num_samples - (optional) number of samples for rolling average
//!
AnalogueThreshold::AnalogueThreshold(const char* name, pin_size_t pin_number, uint8_t num_samples) :
    name_(name),
    pin_number_(pin_number),
    num_samples_(num_samples),
    write_ptr_(0),
    saved_(0),
    state_ok_(true),
    min_val_(0.0),
    max_val_(0.0),
    range_(0.0),
    hysteresis_(0.0)
 {
    // Allocate an array for rolling average samples
    samples_ = new int[num_samples_];

    // Set the specified pin mode to input
    pinMode(pin_number, INPUT);

}

//! Destructor
//!
//! This destructor cleans up the analogue threshold, deleting the sample array
//!
AnalogueThreshold::~AnalogueThreshold()
{
    delete[] samples_;
}


//! Get the name of the analogue threshold
//!
//! This getter method returns the name of the analogue threshold for e.g. debug printing
//!
String AnalogueThreshold::name(void) const
{
    return name_;
}

//! Update the threshold by sampling the specified pin
//!
//! This method updates the threshold value by sampling the specified analogue input pi and adding
//! the value to the rolling sample array
//!
void AnalogueThreshold::update(void)
{

    // Read the analogue pin and add to the sample array at the current write pointer.
    // The ADC value is inverted for convenience so the variable pots increase the threshold
    // when turned clockwise
    samples_[write_ptr_] = MAX_ADC_VAL - analogRead(pin_number_);

    // Update the write pointer modulo the number of samples
    write_ptr_ = (write_ptr_ + 1) % num_samples_;

    // Increment the number of samples saved up to the maximum depth of the sample array
    if (saved_ < num_samples_)
    {
        saved_++;
    }
}

//! Get the calculated rolling average value of the threshold
//!
//! This method returns the calculated value of the threshold based on the rolling average. If the
//! threshold has been fully initialised with minimum and maximum values, return the calculated
//! value. Otherwise return the mean of the currently stored samples.
//!
//! \return current calculated threshold value or rolling average sample value.
//!
float AnalogueThreshold::value(void)
{
    // Get the sample mean
    float value = sample_mean();

    // If range is initialised calculate value
    if (range_ != 0.0)
    {
        value = min_val_ + (value / MAX_ADC_VAL) * range_;
        value = float(floor(value * 2) / 2.0);
    }

    // Return the value
    return value;
}

//! Get the rolling average raw ADC sample value
//!
//! This method returns the rolling average mean value of samples for the threshold.
//!
//! \return current rolling average mean value of ADC samples as floating point.
//!
float AnalogueThreshold::sample_mean(void)
{
    // Sum the currently stored samples
    float sum = 0.0;
    for (int idx = 0; idx < saved_; idx++)
    {
        sum += samples_[idx];
    }

    // Calculate and return the mean
    float mean = sum / saved_;

    return mean;
}

//! Compare a given reading with the threshold
//!
//! This method compares a given reading, e.g. sensor temperature, with the current value of the
//! threshold, returning true if the reading is below threshold, false otherwise. The state
//! determined in that comparison is stored in the object to allow the hysteresis to be implemented.
//! If the previous state was false, then the comparison is made with the hysteresis subtracted
//  from the threshold value. This avoids the treshold state toggling rapdily back and forth when
//! the reading is close to the current value.
//!
//! \param[in] reading - current reading to compare with threshold
//!
//! \return boolean indicating state of comparison (true: below threshold, false: above threshold)
//!
bool AnalogueThreshold::compare(float reading)
{

    // If previous comparison state was OK, compare reading with threshold, otherwise subtract
    // the hysteresis value. Store the current comparison state for future use.
    if (state_ok_)
    {
        state_ok_ = (reading < value());
    }
    else
    {
        state_ok_ = (reading < (value() - hysteresis_));
    }

    return state_ok_;
}
