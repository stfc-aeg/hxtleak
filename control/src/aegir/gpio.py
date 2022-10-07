"""Simple GPIO pin class.

This class is a simple wrapper around the Adafruit BBIO GPIO library, providing a class-based
interface to use GPIO pins.

Tim Nicholls, STFC Detector Systems Software Group
"""
from Adafruit_BBIO import GPIO


class Gpio():
    """
    GPIO pin class.

    The class implements a simple wrapper around the Adafruit BBIO GPIO library, allowing GPIO
    objects to be instantiated and used.
    """
    # Expose the GPIO library constants for use
    IN = GPIO.IN
    OUT = GPIO.OUT
    HIGH = GPIO.HIGH
    LOW = GPIO.LOW
    FALLING = GPIO.FALLING
    RISING = GPIO.RISING
    BOTH = GPIO.BOTH

    def __init__(self, pin, mode=None):
        """
        Initialise the GPIO pin instance.

        This method initisialises the GPIO pin instance, optonally setting the input/output mode as
        desired.

        :param pin: GPIO pin descriptor
        :param mode: GPIO I/O mode (one of IN or OUT), not set if None
        """
        self.pin = pin
        if mode is not None:
            self.setup(mode)

    def setup(self, mode):
        """
        Set the mode of the GPIO pin.

        :param mode: GPIO I/O mode (one of IN or OUT)
        """
        GPIO.setup(self.pin, mode)

    def read(self):
        """
        Read the state of the GPIO pin.

        This method returns the current state of a pin when set to input mode. If in output mode,
        the value may not be defined.

        :return the current state of the GPIO pin (1/HIGH, 0/LOW)
        """

        return GPIO.input(self.pin)

    def write(self, value):
        """
        Write the state of the GPIO pin.

        This method set the current state of a pin when set to output mode

        :param value: desired output state state of the GPIO pin (1/HIGH, 0/LOW)
        """

        return GPIO.output(self.pin, value)

    def add_event_detect(self, edge, callback=None, bouncetime=0):
        """
        Add an event detect callback to the pin.

        This method adds an event detect callback to the pin. The callback is executed when the
        requested edge transition is detected.

        :param edge: which edge to trigger the callback (RISING, FALLING or BOTH)
        :param callback: function to be called when edge transition is detected. The callback is
                         passed an argument which is the pin descriptor
        :param bouncetime: debounce detect holdoff time in milliseconds
        """

        GPIO.add_event_detect(self.pin, edge, callback, bouncetime)
