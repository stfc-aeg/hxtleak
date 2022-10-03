"""Controller portion of the Aegir Adapter.

The controller handles the main background task which receives raw data packets
through a serial port and handles them, and the parameter tree which displays
information from the data packet after it has been decoded.

James Foster
"""
import logging
import serial
from datetime import datetime
from concurrent import futures

from tornado.concurrent import run_on_executor

from odin.adapters.parameter_tree import ParameterTree

from aegir.packet_decoder import AegirPacketDecoder
from aegir.gpio import Gpio
from aegir.outlet_relay import OutletRelay

class AegirControllerError(Exception):
    """Simple exception class to wrap lower-level exceptions."""

    pass


class AegirController():
    """Main class for the controller object."""

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self, port_name):
        """Initialise the controller object.

        This constructor initlialises the controller object, building a parameter tree and
        launching a background task if enabled
        """
        self.port_name = port_name
        self.background_task_enable = True

        # Initialise the values of the parameter tree and packet information
        self.status = "unknown"
        self.time_received = "unknown"

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
        self.fault_state = self.fault_detect.read()

        # Define the RS485 driver RO and DI GPIO pins and set both low to enable RX, disable TX
        self.rs485_ro = Gpio("P9_23", Gpio.OUT)
        self.rs485_di = Gpio("P9_27", Gpio.OUT)
        self.rs485_ro.write(Gpio.LOW)
        self.rs485_di.write(Gpio.LOW)

        # Define the chiller and DAQ outlet relay controllers
        self.chiller_outlet = OutletRelay("P8_14")
        self.daq_outlet = OutletRelay("P8_16")

        # Initialise the serial port
        try:
            self.serial_input = serial.Serial(port=self.port_name, baudrate=57600, timeout=.1)
        except serial.serialutil.SerialException:
            logging.error('Failed to open serial port')
            self.status = "No serial port"
            self.background_task_enable = False

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'status' : (lambda: self.status, None),
            'packet_info' : (lambda: self.packet_dict, None),
            'time_received' : (lambda: self.time_received, None),
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

        self.param_tree.set(path, data)
        return self.param_tree.get(path)

    def cleanup(self):
        """Clean up the controller instance.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        self.background_task_enable = False

    def fault_event_detected(self, _):

        self.fault_state = self.fault_detect.read()
        logging.debug("Fault transition detected, state is now: {}".format(self.fault_state))

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

                now = datetime.now()
                #self.time_received = str(now.isoformat())
                self.time_received = now.strftime("%d/%m/%y %X")

                # Unpack the received packet and handle incorrect packet size
                if len(data) >= self.decoder.size:
                    self.decoder.unpack(data[-(self.decoder.size):])

                    # Handles the validation of the checksum value
                    self.decoder.checkSumCheck(data[-(self.decoder.size):])
                    if self.decoder.csumValid is True:
                        #logging.debug("Checksum VALID!")
                        self.status = "Packet received"
                        self.packet_dict = self.decoder.as_dict()
                        self.good_packet_counter += 1
                        #logging.debug("{} : got packet len {} : {}".format(
                        #    now, len(data), str(self.decoder)))
                    else:
                        logging.debug("Checksum NOT VALID!")
                        self.status = "Checksum invalid"
                        self.bad_packet_counter += 1

                else:
                    self.status = "Incorrect packet size"
                    logging.debug("{} : got incorrect size packet len {} : {}".format(
                        now, len(data), ' '.join([hex(val) for val in data])
                    ))
                    self.bad_packet_counter += 1

                # Reset the data bytearray
                data = bytearray()
