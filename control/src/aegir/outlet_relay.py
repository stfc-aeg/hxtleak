from .gpio import Gpio
from .util import AegirError

class OutletRelay():

    def __init__(self, gpio_pin, enabled=True, state=False):

        self.gpio = Gpio(gpio_pin, Gpio.OUT)

        self.enabled = enabled
        self.state = state

    def set_enabled(self, enable):

        self.enabled = enable

    def set_state(self, state):

        if not self.enabled:
            raise AegirError("Cannot change the state of a disabled outlet relay")

        self.state = bool(state)
        self.gpio.write(self.state)

    def tree(self):

        return {
            'state': (lambda: self.state, self.set_state),
            'enabled': (lambda: self.enabled, None)
        }
