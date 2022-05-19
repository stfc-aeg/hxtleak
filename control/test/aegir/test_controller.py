from ast import Import
import pytest
from aegir.controller import AegirController, AegirControllerError
from aegir.packet_decoder import AegirPacketDecoder
from datetime import datetime
import struct
import os, serial
import threading
import time

from odin.adapters.dummy import DummyAdapter
from odin.adapters.parameter_tree import ParameterAccessor, ParameterTree, ParameterTreeError
from odin.adapters.adapter import ApiAdapter, ApiAdapterRequest, ApiAdapterResponse, request_types, response_types
from odin._version import get_versions
from copy import deepcopy

try:
    import pty
except ImportError:
    pty = None


class DummySerialPortFixture(object):
    def __init__(self):
        self.master, self.slave = pty.openpty()

        self.port_name = os.ttyname(self.slave)

        self.packet = struct.pack('<HH?BH', 1, 2, 0, 3, 42405)
        self.packet_small = struct.pack('<HH?H', 5, 2, 0, 42405)
        self.bad_checksum = struct.pack('<HH?BH', 1, 2, 0, 0, 42405)

        self.controller = AegirController(self.port_name)

    def ser_write(self, input):
        os.write(self.master, input)
    
    # def reset_data(self):
    #     self.data = bytearray()
    #     self.decoder = AegirPacketDecoder()

@pytest.fixture()
def serial_fixture():
    serial_fixture = DummySerialPortFixture()
    yield serial_fixture
    serial_fixture.controller.cleanup()

class TestAegirController():

    def test_serial_read(self, serial_fixture):
        serial_fixture.ser_write(serial_fixture.packet)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        output = serial_fixture.controller.decoder
        assert serial_fixture.packet[0] == output.t1
        assert serial_fixture.packet[2] == output.t2
        assert serial_fixture.packet[4] == output.fault

    def test_serial_packet_small(self, serial_fixture):
        serial_fixture.ser_write(serial_fixture.packet_small)
        time.sleep(.1)
        serial_fixture.controller.background_task_enable = False
        output = serial_fixture.controller.decoder
        assert serial_fixture.packet_small[0] != output.t1

    def test_no_serial_port(self):
        controller = AegirController('/dev/doesntexist')
        assert controller.status == "No serial port"
        
    def test_param_tree_get(self, serial_fixture):
        dt_vals = serial_fixture.controller.get('')
        assert dt_vals, serial_fixture.controller.param_tree

    def test_param_tree_get_single_value(self, serial_fixture):
        expected_output = "unknown"
        dt_odin_ver = serial_fixture.controller.get('status')
        assert dt_odin_ver['status'] == expected_output

    def test_param_tree_missing_value(self, serial_fixture):
        with pytest.raises(ParameterTreeError) as excinfo:
            serial_fixture.controller.get('missing')
        
        assert 'Invalid path: missing' in str(excinfo.value)
        
    def test_checksum_bad(self, serial_fixture):
        serial_fixture.ser_write(serial_fixture.bad_checksum)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        output = serial_fixture.controller.status
        assert output == "Checksum invalid"

    def test_good_packet_counter(self, serial_fixture):
        serial_fixture.ser_write(serial_fixture.packet)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        assert serial_fixture.controller.good_packet_counter == 1

    def test_bad_packet_counter(self, serial_fixture):
        serial_fixture.ser_write(serial_fixture.bad_checksum)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        assert serial_fixture.controller.bad_packet_counter == 1

    def test_cleanup(self, serial_fixture):
        serial_fixture.controller.cleanup()
        assert serial_fixture.controller.background_task_enable == False