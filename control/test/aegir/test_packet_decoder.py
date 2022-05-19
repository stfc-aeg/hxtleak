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

class DecoderTestFixture(object):
    def __init__(self):
        self.good_packet = struct.pack('<HH?BH', 1, 2, 0, 3, 42405)
        self.bad_checksum = struct.pack('<HH?BH', 1, 2, 0, 0, 42405)
        self.bad_eop = struct.pack('<HH?BH', 1, 2, 0, 3, 0)
        self.bad_large_packet = struct.pack('<HH?BHH', 1, 2, 0, 3, 4, 42405)

        self.decoder = AegirPacketDecoder()

@pytest.fixture(scope="class")
def decoder_fixture():
    decoder_fixture = DecoderTestFixture()
    yield decoder_fixture

class TestPacketDecoder():

    def test_unpack(self, decoder_fixture):
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        assert decoder_fixture.decoder.t1 == 1
        assert decoder_fixture.decoder.t2 == 2

    def test_packet_complete(self, decoder_fixture):
        if decoder_fixture.decoder.packet_complete(decoder_fixture.good_packet):
            packet_completed = True
        assert packet_completed == True

    def test_packet_complete_bad_eop(self, decoder_fixture):
        if not decoder_fixture.decoder.packet_complete(decoder_fixture.bad_eop):
            packet_completed = False
        assert packet_completed == False

    def test_checksum(self, decoder_fixture):
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        decoder_fixture.decoder.checkSumCheck(decoder_fixture.good_packet)
        assert decoder_fixture.decoder.csumValid == True
    
    def test_checksum_bad(self, decoder_fixture):
        decoder_fixture.decoder.unpack(decoder_fixture.bad_checksum)
        decoder_fixture.decoder.checkSumCheck(decoder_fixture.bad_checksum)
        assert decoder_fixture.decoder.csumValid == False

    def test_make_dict(self, decoder_fixture):
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        decoder_dict = decoder_fixture.decoder.make_dict()

        assert decoder_dict["t1"] == 1
        assert decoder_dict["t2"] == 2

    def test_string_format(self, decoder_fixture):
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        decoder_string = str(decoder_fixture.decoder)

        assert decoder_string == "t1=1 t2=2 fault=False checksum=3 eop=0xa5a5"
    
    def test_large_packet_size(self, decoder_fixture):
        with pytest.raises(struct.error):
            decoder_fixture.decoder.unpack(decoder_fixture.bad_large_packet)