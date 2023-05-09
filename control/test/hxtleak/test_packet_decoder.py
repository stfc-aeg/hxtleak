"""Test packet decoder class.

James Foster
"""
import pytest
from hxtleak.packet_decoder import HxtleakPacketDecoder
import struct


class DecoderTestFixture(object):
    """Container class used in the creation of a packet decoder fixture."""

    def __init__(self):
        """Initialise the packet decoder and test packets."""
        self.good_packet = struct.pack('<HH?BH', 1, 2, 0, 3, 42405)
        self.bad_checksum = struct.pack('<HH?BH', 1, 2, 0, 0, 42405)
        self.bad_eop = struct.pack('<HH?BH', 1, 2, 0, 3, 0)
        self.bad_large_packet = struct.pack('<HH?BHH', 1, 2, 0, 3, 4, 42405)

        self.decoder = HxtleakPacketDecoder()


@pytest.fixture(scope="class")
def decoder_fixture():
    """Test fixture used in the testing of packet decoder behaviour."""
    decoder_fixture = DecoderTestFixture()
    yield decoder_fixture


class TestPacketDecoder():
    """Class to test the packet decoder behaviour."""

    def test_unpack(self, decoder_fixture):
        """Test that a packet is unpacked correctly."""
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        assert decoder_fixture.decoder.t1 == 1
        assert decoder_fixture.decoder.t2 == 2

    def test_packet_complete(self, decoder_fixture):
        """Test that an appropriate packet meets the requirements of a completed packet."""
        if decoder_fixture.decoder.packet_complete(decoder_fixture.good_packet):
            packet_completed = True
        assert packet_completed

    def test_packet_complete_bad_eop(self, decoder_fixture):
        """Test that an inappropriate packet does not meet the requirements of a complete packet."""
        if not decoder_fixture.decoder.packet_complete(decoder_fixture.bad_eop):
            packet_completed = False
        assert not packet_completed

    def test_checksum(self, decoder_fixture):
        """Test that the checksum validation method validates an appropriate packet."""
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        decoder_fixture.decoder.checkSumCheck(decoder_fixture.good_packet)
        assert decoder_fixture.decoder.csumValid

    def test_checksum_bad(self, decoder_fixture):
        """Test that the checksum validation method does not validate an inappropriate packet."""
        decoder_fixture.decoder.unpack(decoder_fixture.bad_checksum)
        decoder_fixture.decoder.checkSumCheck(decoder_fixture.bad_checksum)
        assert not decoder_fixture.decoder.csumValid

    def test_make_dict(self, decoder_fixture):
        """Test that an unpacked packet is returned as a dictionary using the method."""
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        decoder_dict = decoder_fixture.decoder.make_dict()

        assert decoder_dict["t1"] == 1
        assert decoder_dict["t2"] == 2

    def test_string_format(self, decoder_fixture):
        """Test that an unpacked packet is returned as a string."""
        decoder_fixture.decoder.unpack(decoder_fixture.good_packet)
        decoder_string = str(decoder_fixture.decoder)

        assert decoder_string == "t1=1 t2=2 fault=False checksum=3 eop=0xa5a5"

    def test_large_packet_size(self, decoder_fixture):
        """Test that a packet which is too large raises an error."""
        with pytest.raises(struct.error):
            decoder_fixture.decoder.unpack(decoder_fixture.bad_large_packet)
