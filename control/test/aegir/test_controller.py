"""Test Controller class.

James Foster
"""
import pytest
from aegir.controller import AegirController
import struct
import os
import time

from odin.adapters.parameter_tree import ParameterTreeError

try:
    import pty
except ImportError:
    pty = None


class DummySerialPortFixture(object):
    """Container class used in the creation of a dummy serial port fixture."""

    def __init__(self):
        """Initialise the dummy serial port and test packets."""
        self.master, self.slave = pty.openpty()

        self.port_name = os.ttyname(self.slave)

        self.packet = struct.pack('<HH?BH', 1, 2, 0, 3, 42405)
        self.packet_small = struct.pack('<HH?H', 5, 2, 0, 42405)
        self.bad_checksum = struct.pack('<HH?BH', 1, 2, 0, 0, 42405)

        self.controller = AegirController(self.port_name)

    def ser_write(self, input):
        """Write a packet to the dummy serial port.

        :param input: input packet written to the port
        """
        os.write(self.master, input)


@pytest.fixture()
def serial_fixture():
    """Test fixture used in testing controller serial port behaviour."""
    serial_fixture = DummySerialPortFixture()
    yield serial_fixture
    serial_fixture.controller.cleanup()


class TestAegirController():
    """Class to test the controller behaviour."""

    def test_serial_read(self, serial_fixture):
        """Test that a packet written to serial can be read."""
        serial_fixture.ser_write(serial_fixture.packet)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        output = serial_fixture.controller.decoder
        assert serial_fixture.packet[0] == output.t1
        assert serial_fixture.packet[2] == output.t2
        assert serial_fixture.packet[4] == output.fault

    def test_serial_packet_small(self, serial_fixture):
        """Test that a packet which is too small is not decoded."""
        serial_fixture.ser_write(serial_fixture.packet_small)
        time.sleep(.1)
        serial_fixture.controller.background_task_enable = False
        output = serial_fixture.controller.decoder
        assert serial_fixture.packet_small[0] != output.t1

    def test_no_serial_port(self):
        """Test that creating a controller with a non-existent port sets the status message."""
        controller = AegirController('/dev/doesntexist')
        assert controller.status == "No serial port"

    def test_param_tree_get(self, serial_fixture):
        """Test that the parameter tree values can be obtained using the get function."""
        dt_vals = serial_fixture.controller.get('')
        assert dt_vals, serial_fixture.controller.param_tree

    def test_param_tree_get_single_value(self, serial_fixture):
        """Test that an individual param tree value can be obtained using get function."""
        expected_output = "unknown"
        dt_odin_ver = serial_fixture.controller.get('status')
        assert dt_odin_ver['status'] == expected_output

    def test_param_tree_missing_value(self, serial_fixture):
        """Test that a missing param tree value raises an error using get function."""
        with pytest.raises(ParameterTreeError) as excinfo:
            serial_fixture.controller.get('missing')

        assert 'Invalid path: missing' in str(excinfo.value)

    def test_checksum_bad(self, serial_fixture):
        """Test that an invalid checksum sets the status message."""
        serial_fixture.ser_write(serial_fixture.bad_checksum)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        output = serial_fixture.controller.status
        assert output == "Checksum invalid"

    def test_good_packet_counter(self, serial_fixture):
        """
        Test that the good packet counter increases by 1
        when a packet with no errors is received.
        """
        serial_fixture.ser_write(serial_fixture.packet)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        assert serial_fixture.controller.good_packet_counter == 1

    def test_bad_packet_counter(self, serial_fixture):
        """
        Test that the bad packet counter increases by 1
        if the packet does not meet the requirements.
        """
        serial_fixture.ser_write(serial_fixture.bad_checksum)
        while serial_fixture.controller.status == 'unknown':
            pass
        serial_fixture.controller.background_task_enable = False
        assert serial_fixture.controller.bad_packet_counter == 1

    def test_cleanup(self, serial_fixture):
        """Test the controller cleanup function."""
        serial_fixture.controller.cleanup()
        assert not serial_fixture.controller.background_task_enable
