"""Outlet relay control.

This module implements GPIO-based control of the AEGIR power outlet relays. The state of the relay
can be controlled, and the outlet control enabled/disabled as appropriate during fault conditions.

Tim Nicholls, STFC Detector Systems Software Group
"""
import logging

from .gpio import Gpio
from .util import AegirError


class OutletRelay():
    """
    Outlet relay control class.

    The class implmenents control of the AEGIR power outlet relays via GPIO pins.
    """

    logger = logging.getLogger()  # Logger for OutletRelay instances - defaults to root logger

    @classmethod
    def set_logger(cls, logger):
        """Set the logger for OutletRelay instances.

        This class method sets the logger for OutletRelay instance message logging. If not called,
        logging will default to the root logger.

        :param logger: logger instance to use
        """
        cls.logger = logger

    def __init__(self, name, gpio_pin, enabled=True, state=False):
        """
        Initialise the outlet relay.

        Intialises the outlet relay on the specified GPIO pin. The initial enable and state of the
        relay can be set.

        :param name: name of the outlet, used for log messages
        :param gpio_pin: GPIO pin descriptor
        :param enabled: initial enable state (default True = enabled)
        :param state: initial outlet state (default False = off)
        """
        self.name = name
        self.gpio = Gpio(gpio_pin, Gpio.OUT)

        self.enabled = enabled
        self.state = state

        self.logger.debug("%s outlet initialised", self.name)

    def set_enabled(self, enable):
        """
        Set the enable of the outlet relay.

        This method allows the enable of the outlet to be controlled. State changes when the outlet
        is disabled raise an exception.

        :param enable: enable state (True or False)
        """
        self.enabled = enable

    def set_state(self, state):
        """
        Set the state of the outlet relay.

        This method sets the state of the outlet relay. If the outlet is not enabled, attempting to
        set the state will raise an AegirError exception.

        :param state: outlet state (True or False)
        """
        if not self.enabled:
            raise AegirError("Cannot change the state of a disabled outlet relay")

        self.state = bool(state)
        self.gpio.write(self.state)

        self.logger.info("%s outlet state set to %s", self.name, "on" if state else "off")

    def tree(self):
        """
        Return a dict-like tree of outlet relay parameters.

        Thie method returns a dict-like tree out outlet relay parameters, i.e. the state and enable
        values and their accessors. It is intended to be incorporated into a ParameterTree instance
        by an enclosing adapter.

        :return dict-like tree of state and enable parameter accessors
        """
        return {
            'state': (lambda: self.state, self.set_state),
            'enabled': (lambda: self.enabled, None)
        }
