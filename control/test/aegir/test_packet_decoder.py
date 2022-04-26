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

from test_controller import test_packet, DummySerialPortFixture, serial_fixture

class TestPacketDecoder():
    
    def test_decoder_unpack(self, test_packet, serial_fixture):
        serial_fixture.dummy_serial_writeread(test_packet)
        output = serial_fixture.data
        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
            if len(output) >= serial_fixture.decoder.size:
                    print([hex(val) for val in output])
                    serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])
        
        assert serial_fixture.decoder.t1 == 1
        serial_fixture.reset_data()

    def test_decoder_unpack_bad_eop(self, serial_fixture):
        test_packet_bad = struct.pack('<HH?BH', 1, 2, 0, 3, 0)
        serial_fixture.dummy_serial_writeread(test_packet_bad)
        output = serial_fixture.data

        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
           if len(output) >= serial_fixture.decoder.size:
                print([hex(val) for val in output])
                serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])
        else:
            pass
        
        assert serial_fixture.decoder.t1 != 1
        serial_fixture.reset_data()

    def test_decoder_checksum(self, test_packet, serial_fixture):
        serial_fixture.dummy_serial_writeread(test_packet)
        output = serial_fixture.data
        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
            if len(output) >= serial_fixture.decoder.size:
                    print([hex(val) for val in output])
                    serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])
                    serial_fixture.decoder.checkSumCheck(output[-(serial_fixture.decoder.size):])
        
        assert serial_fixture.decoder.csumValid == True
        serial_fixture.reset_data()

    def test_decoder_checksum_bad(self, serial_fixture):
        test_packet_bad = struct.pack('<HH?BH', 1, 2, 0, 0, 42405)
        serial_fixture.dummy_serial_writeread(test_packet_bad)
        output = serial_fixture.data
        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
            if len(output) >= serial_fixture.decoder.size:
                    print([hex(val) for val in output])
                    serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])
                    serial_fixture.decoder.checkSumCheck(output[-(serial_fixture.decoder.size):])
        
        assert serial_fixture.decoder.csumValid == False
        serial_fixture.reset_data()

    def test_decoder_string_format(self, test_packet, serial_fixture):
        serial_fixture.dummy_serial_writeread(test_packet)
        output = serial_fixture.data
        if len(output) > 2 and output[-1] == 0xA5 and output[-2] == 0xA5:
            if len(output) >= serial_fixture.decoder.size:
                    print([hex(val) for val in output])
                    serial_fixture.decoder.unpack(output[-(serial_fixture.decoder.size):])
        
        log = str(serial_fixture.decoder)

        assert log == "t1=1 t2=2 fault=False checksum=3 eop=0xa5a5"
        serial_fixture.reset_data()