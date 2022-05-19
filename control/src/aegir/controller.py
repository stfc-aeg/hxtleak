"""Controller portion of the Aegir Adapter.

The controller handles the main background task, and the parameter tree.
"""
import logging
import tornado
import time
import serial
from datetime import datetime
from concurrent import futures

from tornado.concurrent import run_on_executor

from odin.adapters.parameter_tree import ParameterTree
from odin._version import get_versions

from aegir.packet_decoder import AegirPacketDecoder


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

        # Store initialisation time
        self.init_time = time.time()

        # Get package version information
        version_info = get_versions()

        # Initialise the values of the parameter tree and packet information
        self.arduino_status = "unknown"
        self.time_received = "unknown"

        self.t1 = "unknown"
        self.t2 = "unknown"
        self.fault = "unknown"
        self.checksum = "unknown"
        self.eop = "unknown"

        self.packet_dict = "unknown"
        self.good_packet_counter = 0
        self.bad_packet_counter = 0

        # Initialise the packet decoder class
        self.decoder = AegirPacketDecoder()

        # Initialise the serial port
        try:
            self.serial_input = serial.Serial(port=self.port_name, baudrate=57600, timeout=.1)
        except serial.serialutil.SerialException:
            logging.error('Failed to open serial port')
            self.arduino_status = "No serial port"
            self.background_task_enable = False

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'odin_version': version_info['version'],
            'tornado_version': tornado.version,
            'server_uptime': (self.get_server_uptime, None),
            'arduino_status' : (lambda: self.arduino_status, None),
            'packet_info' : (lambda: self.packet_dict, None),
            'time_received' : (lambda: self.time_received, None),
            'good_packets' : (lambda: self.good_packet_counter, None),
            'bad_packets' : (lambda: self.bad_packet_counter, None),
        })

        # Launch the background task
        if self.background_task_enable:
            logging.debug(
                "Launching background task"
            )
            self.background_arduino_task()

    def get_server_uptime(self):
        """Get the uptime for the ODIN server.

        This method returns the current uptime for the ODIN server.
        """
        return time.time() - self.init_time

    def get(self, path):
        """Get the parameter tree.

        This method returns the parameter tree for use by clients via the controller adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def cleanup(self):
        """Clean up the controller instance.

        This method stops the background tasks, allowing the adapter state to be cleaned up
        correctly.
        """
        self.background_task_enable = False

    def controller_bg_task(self):
        """Run the main controller task.

        This method reads data from the serial input and uses the packet decoder class to
        parse the data. The values in the parameter tree are updated with the appropriate
        information.
        """
        maxsize = self.decoder.size * 2
        data = bytearray()

        data.extend(self.serial_input.read(maxsize))

        if self.decoder.packet_complete(data):

            now = datetime.now()
            self.time_received = str(now)

            if len(data) >= self.decoder.size:
                self.decoder.unpack(data[-(self.decoder.size):])

                self.decoder.checkSumCheck(data[-(self.decoder.size):])
                if self.decoder.csumValid is True:
                    logging.debug("Checksum VALID!")
                    self.arduino_status = "Packet received"
                    self.packet_dict = self.decoder.make_dict()
                    self.good_packet_counter += 1
                    logging.debug("{} : got packet len {} : {}".format(
                        now, len(data), self.packet_dict))
                else:
                    logging.debug("Checksum NOT VALID!")
                    self.arduino_status = "Checksum invalid"
                    self.bad_packet_counter += 1

            else:
                self.arduino_status = "Incorrect packet size"
                logging.debug("{} : got incorrect size packet len {} : {}".format(
                    now, len(data), ' '.join([hex(val) for val in data])
                ))
                self.bad_packet_counter += 1

            data = bytearray()

    @run_on_executor
    def background_arduino_task(self):
        """Run the background task on a thread executor continuously in a while loop."""
        while self.background_task_enable:
            self.controller_bg_task()
