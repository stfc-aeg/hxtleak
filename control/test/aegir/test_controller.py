from ast import Import
import pytest
from aegir.controller import AegirController, AegirControllerError
from aegir.packet_decoder import AegirPacketDecoder
from datetime import datetime
import struct
import os, serial

from odin.adapters.dummy import DummyAdapter
from odin.adapters.parameter_tree import ParameterAccessor, ParameterTree, ParameterTreeError
from odin.adapters.adapter import ApiAdapter, ApiAdapterRequest, ApiAdapterResponse, request_types, response_types
from odin._version import get_versions
from copy import deepcopy

try:
    import pty
except ImportError:
    pty = None

@pytest.fixture
def test_packet():
    test_packet = struct.pack('<HH?BH', 1, 2, 0, 3, 42405)
    yield test_packet

class DummySerialPortFixture(object):
    def __init__(self):
        self.master, self.slave = pty.openpty()
        self.data = bytearray()
        self.decoder = AegirPacketDecoder()
        self.maxsize = self.decoder.size * 2

    def dummy_serial_writeread(self, input_packet):
        port_name = os.ttyname(self.slave)
        ser = serial.Serial(port_name, baudrate=57600, timeout=.1)

        ser.write(input_packet)
        out = os.read(self.master, self.maxsize)
        self.data.extend(out)
    
    def reset_data(self):
        self.data = bytearray()
        self.decoder = AegirPacketDecoder()

@pytest.fixture(scope="class")
def serial_fixture():
    serial_fixture = DummySerialPortFixture()
    yield serial_fixture

@pytest.fixture(scope="class")
def dummy_aegir_controller():
    dummy_aegir_controller = AegirController()
    yield dummy_aegir_controller

class TestAegirController():

    def test_serial_writeread(self, test_packet, serial_fixture):
        serial_fixture.dummy_serial_writeread(test_packet)
        output = serial_fixture.data
        assert test_packet == output
        serial_fixture.reset_data()
        

    def test_bad_packet_size(self, serial_fixture):
        test_packet_bad = struct.pack('<HH?H', 1, 2, 0, 42405)
        serial_fixture.dummy_serial_writeread(test_packet_bad)
        output = serial_fixture.data
        log = None

        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
            now = datetime.now()
            if len(output) >= serial_fixture.decoder.size:
                print([hex(val) for val in output])
                serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])
            else:
                log = ("{} : got incorrect size packet len {} : {}".format(
                    now, len(output), ' '.join([hex(val) for val in output])
                ))
        
        assert log == ("{} : got incorrect size packet len {} : {}".format(
                    now, len(output), ' '.join([hex(val) for val in output])
                ))
        serial_fixture.reset_data()
        
    def test_param_tree_get(self, dummy_aegir_controller):
       dt_vals = dummy_aegir_controller.param_tree.get('')
       assert dt_vals, dummy_aegir_controller.param_tree

    def test_param_tree_get_single_values(self, dummy_aegir_controller):
        dt_odin_ver = dummy_aegir_controller.param_tree.get('odin_version')
        assert dt_odin_ver['odin_version'] == '1.1.0'

        dt_ard_stats = dummy_aegir_controller.param_tree.get('arduino_status')
        assert dt_ard_stats['arduino_status'] == 'unknown'

    def test_param_tree_missing_value(self, dummy_aegir_controller):
        with pytest.raises(ParameterTreeError) as excinfo:
            dummy_aegir_controller.param_tree.get('missing')
        
        assert 'Invalid path: missing' in str(excinfo.value)

    def test_arduino_status_update(self, dummy_aegir_controller, serial_fixture, test_packet):
        serial_fixture.dummy_serial_writeread(test_packet)
        output = serial_fixture.data
        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
            if len(output) >= serial_fixture.decoder.size:
                    print([hex(val) for val in output])
                    serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])

        ard_stat = str(serial_fixture.decoder.fault)
        dummy_aegir_controller.arduino_status = ard_stat
        dt_ard_stats = dummy_aegir_controller.param_tree.get('arduino_status')
        assert dt_ard_stats['arduino_status'] == 'False'
        serial_fixture.reset_data()

    def test_cleanup(self, dummy_aegir_controller):
        dummy_aegir_controller.cleanup()
        assert dummy_aegir_controller.background_task_enable == False