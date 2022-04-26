import logging
from pickletools import uint8
import tornado
import time
import serial
from datetime import datetime
from concurrent import futures

from tornado.ioloop import PeriodicCallback
from tornado.concurrent import run_on_executor
from tornado.escape import json_decode

from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from odin.adapters.parameter_tree import ParameterTree, ParameterTreeError
from odin._version import get_versions

from aegir.packet_decoder import AegirPacketDecoder

class AegirControllerError(Exception):
    """Simple exception class to wrap lower-level exceptions."""

    pass

class AegirController():

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self):
        """Initialise the controller object.

        This constructor initlialises the controller object, building a parameter tree and
        launching a background task if enabled
        """

        # Store initialisation time
        self.init_time = time.time()

        # Get package version information
        version_info = get_versions()

        self.arduino_status = "unknown"
        self.time_received = "unknown"

        # Store all information in a parameter tree
        self.param_tree = ParameterTree({
            'odin_version': version_info['version'],
            'tornado_version': tornado.version,
            'server_uptime': (self.get_server_uptime, None),
            'arduino_status' : (lambda: self.arduino_status, None),
            'time_received' : (lambda: self.time_received, None),
        })

        # Launch the background task if enabled in options
        self.start_background_tasks()

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
        self.stop_background_tasks()

    def start_background_tasks(self):
        """Start the background tasks."""
        logging.debug(
            "Launching background tasks"
        )

        self.background_task_enable = True

        self.background_arduino_task()

    def stop_background_tasks(self):
        """Stop the background tasks."""
        self.background_task_enable = False

    @run_on_executor
    def background_arduino_task(self):
        decoder = AegirPacketDecoder()
        maxsize = decoder.size * 2
        data = bytearray()

        arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=.1)

        while self.background_task_enable:
            
            data.extend(arduino.read(maxsize))

            if len(data) > 2 and data[-1] == 0xA5 and data[-2] == 0xA5:

                now = datetime.now()
                self.time_received = str(now)

                if len(data) >= decoder.size:
                    print([hex(val) for val in data])
                    decoder.unpack(data[-(decoder.size):])

                    decoder.checkSumCheck(data[-(decoder.size):])
                    if decoder.csumValid == True:
                        logging.debug("Checksum VALID!")
                    else:
                        logging.debug("Checksum NOT VALID!")

                    self.arduino_status = str(decoder)
                    logging.debug("{} : got packet len {} : {}".format(now, len(data), decoder))
                else:
                    logging.debug("{} : got incorrect size packet len {} : {}".format(
                        now, len(data), ' '.join([hex(val) for val in data])
                    ))

                data = bytearray()