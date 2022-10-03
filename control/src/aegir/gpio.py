from Adafruit_BBIO import GPIO

class Gpio():

    IN = GPIO.IN
    OUT = GPIO.OUT
    HIGH = GPIO.HIGH
    LOW = GPIO.LOW
    FALLING = GPIO.FALLING
    RISING = GPIO.RISING
    BOTH = GPIO.BOTH

    def __init__(self, pin, mode=None):

        self.pin = pin
        if mode is not None:
            self.setup(mode)

    def setup(self, mode):

        GPIO.setup(self.pin, mode)

    def read(self):

        return GPIO.input(self.pin)

    def write(self, value):

        return GPIO.output(self.pin, value)

    def add_event_detect(self, edge, callback=None, bouncetime=0):

        GPIO.add_event_detect(self.pin, edge, callback, bouncetime)
