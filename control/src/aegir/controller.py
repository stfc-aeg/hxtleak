"""Controller portion of the Aegir Adapter.

The controller handles the main background task which receives raw data packets
through a serial port and handles them, and the parameter tree which displays
information from the data packet after it has been decoded.

James Foster
"""
import logging
import serial
from concurrent import futures
from datetime import datetime
from enum import Enum

from tornado.concurrent import run_on_executor

from odin.adapters.parameter_tree import ParameterTree

from aegir.packet_decoder import AegirPacketDecoder
from aegir.gpio import Gpio
from aegir.outlet_relay import OutletRelay


class PacketReceiveState(Enum):
    """Enumeration of controller packet receive state."""
    UNKNOWN = "unknown"
    OK = "OK"
    TIMEOUT = "timed out"
    SERIAL_ERROR = "serial port error"
    INVALID_CHECKSUM = "checksum error"
    INVALID_SIZE = "invalid packet size"

    def __str__(self):
        """Return string representation of state enumeration."""
        return str(self.value)


class AegirController():
    """Main class for the controller object."""

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self, port_name, packet_recv_timeout=5.0):
        """Initialise the controller object.

        This constructor initlialises the controller object, building a parameter tree and
        launching a background task if enabled
        """
        self.port_name = port_name
        self.packet_recv_timeout = packet_recv_timeout
        self.background_task_enable = True

        # Initialise the values of the parameter tree and packet information
        self.status = PacketReceiveState.UNKNOWN
        self.time_received = datetime.now()

        self.temp = "unknown"
        self.humidity = "unknown"
        self.fault = "unknown"
        self.checksum = "unknown"
        self.eop = "unknown"

        self.packet_dict = "unknown"
        self.good_packet_counter = 0
        self.bad_packet_counter = 0

        # Initialise the packet decoder class
        self.decoder = AegirPacketDecoder()

        # Define the fault detect GPIO pin, add an event callback and initialise the fault state
        # value
        self.fault_detect = Gpio("P8_12", Gpio.IN)
        self.fault_detect.add_event_detect(Gpio.BOTH, self.fault_event_detected)
        self.fault_state = bool(self.fault_detect.read())

        # Define the RS485 driver RO and DI GPIO pins and set both low to enable RX, disable TX
        self.rs485_ro = Gpio("P9_23", Gpio.OUT)
        self.rs485_di = Gpio("P9_27", Gpio.OUT)
        self.rs485_ro.write(Gpio.LOW)
        self.rs485_di.write(Gpio.LOW)

        # Define the chiller and DAQ outlet relay controllers
        self.chiller_outlet = OutletRelay("P8_14", enabled=not self.fault_state)
        self.daq_outlet = OutletRelay("P8_16", enabled=not self.fault_state)
        self.outlets = (self.chiller_outlet, self.daq_outlet)

        # Initialise the serial port
        try:
            self.serial_input = serial.Serial(port=self.port_name, baudrate=57600, timeout=.5)
        except serial.serialutil.SerialException:
            logging.error('Failed to open serial port')
            self.status = "No serial port"
            self.background_task_enable = False

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'status' : (lambda: str(self.status), None),
            'packet_info' : (lambda: self.packet_dict, None),
            'time_received' : (self._get_time_received, None),
            'good_packets' : (lambda: self.good_packet_counter, None),
            'bad_packets' : (lambda: self.bad_packet_counter, None),
            'outlets' : {
                'chiller': self.chiller_outlet.tree(),
                'daq': self.daq_outlet.tree(),
            },
            'fault' : (lambda: bool(self.fault_state), None),
        })

        # Launch the background task
        if self.background_task_enable:
            logging.debug("Launching background tasks")
            self.receive_packets()

    def get(self, path):
        """Get the parameter tree.

        This method returns the parameter tree for use by clients via the controller adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def set(self, path, data):
        """Set parameter values.

        This method sets values in the parameter tree.

        :param path: path to set in the tree
        :param data: data value(s) to set
        """
        self.param_tree.set(path, data)
        return self.param_tree.get(path)

    def _get_time_received(self):
        """Get the last packet receive time as a string."""
        if self.time_received:
            return self.time_received.strftime("%d/%m/%y %X")
        else:
            return "unknown"

    def cleanup(self):
        """Clean up the controller instance.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        self.background_task_enable = False

    def fault_event_detected(self, _):
        """Event callback for the fault detect GPIO pin.

        This method is called when transitions occur on the fault detect GPIO pin. The state of
        the pin is read into the appropriate parameter, and the outlet relay states and enables
        are set accordingly.
        """
        # Read the current state of the fault detect pin.
        self.fault_state = bool(self.fault_detect.read())
        logging.debug("Fault transition detected, state is now: %s", self.fault_state)

        # If the fault state is set, disable user operation of the outlet relays and turn off.
        # Otherwise, re-enable the relays but leave them off.
        if self.fault_state:
            logging.info("Fault state detected, disabling and turning off outlets")
            for outlet in self.outlets:
                outlet.set_state(False)
                outlet.set_enabled(False)
        else:
            logging.info("Fault state cleared, enabling outlets")
            for outlet in self.outlets:
                outlet.set_enabled(True)

    @run_on_executor
    def receive_packets(self):
        """Run the main controller task.

        This method reads data from the serial input and uses the packet decoder class to
        parse the data. The values in the parameter tree are updated with the appropriate
        information.
        """
        # Initialise the decoder maximum size and serial input buffer
        maxsize = self.decoder.size * 2
        data = bytearray()

        while self.background_task_enable:

            data.extend(self.serial_input.read(maxsize))

            if self.decoder.packet_complete(data):

                self.time_received = datetime.now()

                # Unpack the received packet and handle incorrect packet size
                if len(data) >= self.decoder.size:
                    self.decoder.unpack(data[-(self.decoder.size):])

                    # Varify that the transmitted packet checksum is correct
                    if self.decoder.verify_checksum(data[-(self.decoder.size):]):
                        self.status = PacketReceiveState.OK
                        self.packet_dict = self.decoder.as_dict()
                        self.good_packet_counter += 1
                        #logging.debug("{} : got packet len {} : {}".format(
                        #    now, len(data), str(self.decoder)))
                    else:
                        logging.warning("Received packet with bad checksum {%02X}".format(
                            self.decoder.checksum
                        ))
                        self.status = PacketReceiveState.INVALID_CHECKSUM
                        self.bad_packet_counter += 1

                else:
                    self.status = PacketReceiveState.INVALID_SIZE
                    logging.warning("Received incorrectly size packet with length {} : {}".format(
                        len(data), ' '.join([hex(val) for val in data])
                    ))
                    self.bad_packet_counter += 1

                # Reset the data bytearray
                data = bytearray()

            else:

                recv_delta = (datetime.now() - self.time_received).total_seconds()
                if recv_delta > self.packet_recv_timeout:
                    if set.status != PacketReceiveState.TIMEOUT:
                        logging.warning("Packet receive timed out")
                    self.status = PacketReceiveState.TIMEOUT


