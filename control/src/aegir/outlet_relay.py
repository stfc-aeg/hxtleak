from .gpio import Gpio

class OutletRelay():

    def __init__(self, gpio_pin):

        self.gpio = Gpio(gpio_pin, Gpio.OUT)

        self.enabled = True
        self.set_state(False)

    def set_state(self, state):

        self.state = bool(state)
        self.gpio.write(self.state)

    def tree(self):

        return {
            'state': (lambda: self.state, self.set_state),
            'enabled': (lambda: self.enabled, None)
        }
