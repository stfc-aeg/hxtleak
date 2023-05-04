"""Controller for the Hxtleak adapter.

The controller handles the main background task which receives raw data packets
through a serial port and handles them, and the parameter tree which displays
information from the data packet after it has been decoded.

James Foster, STFC Detector Systems Software Group
"""
import logging
import serial
from concurrent import futures
from datetime import datetime
from enum import Enum
from threading import Lock

from tornado.concurrent import run_on_executor

from odin.adapters.parameter_tree import ParameterTree

from hxtleak.packet_decoder import HxtleakPacketDecoder
from hxtleak.gpio import Gpio
from hxtleak.outlet_relay import OutletRelay
from hxtleak.event_logger import HxtleakEventLogger


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


class HxtleakController():
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
        self.receive_task_enable = True

        # Create a lock for checking and reporting system state across threads and previous
        # fault/warning conditions
        self.state_lock = Lock()
        self.last_fault_state = False
        self.last_warning_state = False
        self.last_fault_triggers = None
        self.last_warning_triggers = None

        # Create a logger for system events that can be retrieved by client requests
        self.logger = HxtleakEventLogger(logging.getLogger())
        self.logger.info("System starting up")

        # Initialise the values of the parameter tree and packet information
        self.status = PacketReceiveState.UNKNOWN
        self.time_received = datetime.now()

        self.warning_state = False

        self.packet_data = None
        self.good_packet_counter = 0
        self.bad_packet_counter = 0

        # Initialise the packet decoder class
        self.decoder = HxtleakPacketDecoder()

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
        OutletRelay.set_logger(self.logger)
        self.chiller_outlet = OutletRelay("Chiller", "P8_14", enabled=not self.fault_state)
        self.daq_outlet = OutletRelay("DAQ", "P8_16", enabled=not self.fault_state)
        self.outlets = (self.chiller_outlet, self.daq_outlet)

        # Initialise the serial port
        try:
            self.serial_input = serial.Serial(port=self.port_name, baudrate=57600, timeout=.5)
        except serial.serialutil.SerialException:
            self.logger.error('Failed to open serial port %s', self.port_name)
            self.status = "No serial port"
            self.receive_task_enable = False

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'system' : {
                'status' : (lambda: str(self.status), None),
                'packet_info' : (lambda: self.packet_data, None),
                'time_received' : (self._get_time_received, None),
                'good_packets' : (lambda: self.good_packet_counter, None),
                'bad_packets' : (lambda: self.bad_packet_counter, None),
                'outlets' : {
                    'chiller': self.chiller_outlet.tree(),
                    'daq': self.daq_outlet.tree(),
                },
                'fault' : (lambda: bool(self.fault_state), None),
                'warning': (lambda: bool(self.warning_state), None),
            },
            'event_log': {
                'events': (self.logger.events, None),
                'last_timestamp': (self.logger.last_timestamp, None),
                'events_since': (self.logger.events_since, self.logger.set_events_since),
            },
        })

        # Launch the packet receive task in the background
        if self.receive_task_enable:
            self.logger.info("Launching packet receive task")
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

        This method stops the background task, allowing the adapter state to be cleaned up
        correctly.
        """
        self.receive_task_enable = False

    def fault_event_detected(self, _):
        """Event callback for the fault detect GPIO pin.

        This method is called when transitions occur on the fault detect GPIO pin. The state of
        the pin is read into the appropriate parameter, and the outlet relay states and enables
        are set accordingly.
        """
        # Read the current state of the fault detect pin.
        self.fault_state = bool(self.fault_detect.read())
        logging.debug("Fault transition detected, state is now: %s", self.fault_state)

        # Check and log the state of the system
        self.report_system_state()

        # If the fault state is set, disable user operation of the outlet relays and turn off.
        # Otherwise, re-enable the relays but leave them off.
        if self.fault_state:
            for outlet in self.outlets:
                outlet.set_state(False)
                outlet.set_enabled(False)
        else:
            for outlet in self.outlets:
                outlet.set_enabled(True)

    def report_system_state(self):
        """Report system state to event log.

        This method reports the state of the system to the event log. Transitions in the fault
        and warning states are reported, along with changes in the conditions forming those states.
        The last fault and warning states are stored so that changes can be detected.
        """
        # Acquire the state lock, since this method may be called by the background packet
        # receive thread or by the fault detection callback.
        with self.state_lock:

            # If the fault state has changed, report and store the new state
            if self.fault_state != self.last_fault_state:
                if self.fault_state:
                    self.logger.warning("Fault state detected")
                else:
                    self.logger.info("Fault state cleared")
                self.last_fault_state = self.fault_state

            # Evaluate which conditions have triggered the change in the current fault state
            fault_triggers = {
                "Leak detected" : self.decoder.leak_detected,
                "Leak continuity" : not self.decoder.leak_continuity,
                "Probe 1 temp" : self.decoder.status_probe_1_temperature_fault(),
                "Probe 2 temp" : self.decoder.status_probe_2_temperature_fault(),
            }

            # Save the last fault trigger data if not yet populated
            if self.last_fault_triggers is None:
                self.last_fault_triggers = fault_triggers

            # If the fault triggers have changed and the fault state is asserted, report which
            # conditions have triggered the fault
            if fault_triggers != self.last_fault_triggers:
                if self.fault_state:
                    fault_str = [key for (key, val) in fault_triggers.items() if val]
                    self.logger.warning("Fault conditions: %s", ', '.join(fault_str))
                self.last_fault_triggers = fault_triggers

            # If the warning state has changed, report and store the new state
            if self.warning_state != self.last_warning_state:
                if self.warning_state:
                    self.logger.warning("Warning state detected")
                else:
                    self.logger.info("Warning state cleared")
                self.last_warning_state = self.warning_state

            # Evaluate which conditions have triggered the change in the current warning state
            warning_triggers = {
                "Board temp" : self.decoder.status_board_temperature_warning(),
                "Board humidity" : self.decoder.status_board_humidity_warning(),
            }

            # Save the last warning trigger data if not yet populated
            if self.last_warning_triggers is None:
                self.last_warning_triggers = warning_triggers

            # If the warning triggers have changed and the warning state is asserted, report which
            # conditions have triggered the warning
            if warning_triggers != self.last_warning_triggers:
                if self.warning_state:
                    warning_str = [key for (key, val) in warning_triggers.items() if val]
                    self.logger.warning("Warning conditions: %s", ', '.join(warning_str))
                self.last_warning_triggers = warning_triggers

    @run_on_executor
    def receive_packets(self):
        """Run the main packet receiver task.

        This method reads data from the serial input and uses the packet decoder class to
        parse the data. The values in the parameter tree are updated with the appropriate
        information.
        """
        # Initialise the decoder maximum size and serial input buffer
        maxsize = self.decoder.size * 2
        input_buf = bytearray()

        # Loop while this task is enabled
        while self.receive_task_enable:

            # Append any available data to the input buffer
            input_buf.extend(self.serial_input.read(maxsize))

            # If the input buffer terminates in an end of packet marker, process accordingly
            if self.decoder.packet_complete(input_buf):

                # Record time that packet was received
                self.time_received = datetime.now()

                # Unpack a packet from the input buffer if enough data received
                if len(input_buf) >= self.decoder.size:

                    self.decoder.unpack(input_buf[-(self.decoder.size):])

                    # Verify that the transmitted packet checksum is correct
                    if self.decoder.verify_checksum(input_buf[-(self.decoder.size):]):
                        if self.status != PacketReceiveState.OK:
                            self.logger.info("Packet received OK")
                        self.status = PacketReceiveState.OK
                        self.packet_data = self.decoder.as_dict()
                        self.warning_state = self.packet_data["warning"]
                        self.good_packet_counter += 1
                    else:
                        self.logger.warning(
                            "Received packet with bad checksum 0x%X", self.decoder.checksum
                        )
                        self.status = PacketReceiveState.INVALID_CHECKSUM
                        self.bad_packet_counter += 1

                # Otherwise handle an invalid sized packet
                else:
                    self.status = PacketReceiveState.INVALID_SIZE
                    self.logger.warning(
                        "Received incorrectly size packet with length %d : %s",
                        len(input_buf), ' '.join([hex(val) for val in input_buf])
                    )
                    self.bad_packet_counter += 1

                # Reset the data bytearray
                input_buf = bytearray()

            # Check if the packet receive timeout has been received and set status if so
            else:

                recv_delta = (datetime.now() - self.time_received).total_seconds()
                if recv_delta > self.packet_recv_timeout:
                    if self.status != PacketReceiveState.TIMEOUT:
                        self.logger.warning("Packet receive timed out")
                    self.status = PacketReceiveState.TIMEOUT

            # Check and log the state of the system
            self.report_system_state()
