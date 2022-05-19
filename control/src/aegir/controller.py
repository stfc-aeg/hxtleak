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
            self.status = "No serial port"
            self.background_task_enable = False

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'status' : (lambda: self.status, None),
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
            self.background_task()

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

    @run_on_executor
    def background_task(self):
        """Run the background task on a thread executor continuously in a while loop."""
        while self.background_task_enable:
            self.process_packets()

    def process_packets(self):
        """Run the main controller task.

        This method reads data from the serial input and uses the packet decoder class to
        parse the data. The values in the parameter tree are updated with the appropriate
        information.
        """
        # Initialise the decoder maximum size and serial input buffer
        maxsize = self.decoder.size * 2
        data = bytearray()

        data.extend(self.serial_input.read(maxsize))

        if self.decoder.packet_complete(data):

            now = datetime.now()
            self.time_received = str(now)

            # Unpack the received packet and handle incorrect packet size
            if len(data) >= self.decoder.size:
                self.decoder.unpack(data[-(self.decoder.size):])

                # Handles the validation of the checksum value
                self.decoder.checkSumCheck(data[-(self.decoder.size):])
                if self.decoder.csumValid is True:
                    logging.debug("Checksum VALID!")
                    self.status = "Packet received"
                    self.packet_dict = self.decoder.make_dict()
                    self.good_packet_counter += 1
                    logging.debug("{} : got packet len {} : {}".format(
                        now, len(data), self.packet_dict))
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
