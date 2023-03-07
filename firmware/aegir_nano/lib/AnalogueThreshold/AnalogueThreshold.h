/*
 * AnalogueThreshold.h - rolling average analogue threshold
 *
 * This library implements a rolling average analogue threshold based on sampling an analogue input
 * pin of the Arduino.
 *
 * Author: Tim Nicholls, STFC Detector Systems Software Group
 */

#ifndef _INCULDE_ANALOGUE_THRESHOLD_H_
#define _INCULDE_ANALOGUE_THRESHOLD_H_

#include <Arduino.h>

#define DEFAULT_NUM_SAMPLES 5  // Default number of samples in rolling average
#define DEFAULT_HYSTERESIS 0.0 // Default threshold hysteresis value
#define MAX_ADC_VAL 1023       // Maximum ADC value (12-bit Arduino ADC on analogue inputs)

//! Analogue threshold class
//!
//! This class implements a rolling average analogue threshold based on sampling the value of
//! the specified analogue input pin. A conversion to a physical value, e.g. temperature, humidity
//! is specified with minimum and maximum values. The threshold sampling occurs by calling an update
//! method.
class AnalogueThreshold
{
public:

    //! Constructors
    AnalogueThreshold(
        const char* name, pin_size_t pin_number, float min_val, float max_val,
        float hysteresis=DEFAULT_HYSTERESIS, uint8_t num_samples=DEFAULT_NUM_SAMPLES
    );

    AnalogueThreshold(const char* name, pin_size_t pin_number, uint8_t num_samples=DEFAULT_NUM_SAMPLES);

    //! Destructor
    ~AnalogueThreshold();

    //! Get the name of the analogue threshold
    String name(void) const;

    //! Update the threshold by sampling the specified pin
    void update(void);

    //! Get the calculated rolling average value of the threshold
    float value(void);

    //! Get the rolling average raw ADC sample value
    float sample_mean(void);

    //! Compare a given value with the threshold
    bool compare(float reading);

private:
    String name_;              // Name of the threshold
    pin_size_t pin_number_;    // Analogue pin number to read
    uint8_t num_samples_;      // Number of samples to retain in the rolling average
    int* samples_;             // Pointer to array of samples
    uint8_t write_ptr_;        // Current sample array write pointer
    uint8_t saved_;            // Number of saved samples
    bool state_ok_;            // Saved threshold comparison state

    float min_val_;            // Minimum threshold value (corresponding to 0 input value)
    float max_val_;            // Maximum threshold value (corresponding to full-scale input value)
    float range_;              // Calculated threshold range
    float hysteresis_;         // Threshold comparison hysterisis

};

#endif // _INCULDE_ANALOGUE_THRESHOLD_H_