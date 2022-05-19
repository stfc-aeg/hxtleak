"""Packet Decoder portion of the Aegir Adapter.

This handles the unpacking and validation of received packets.
"""
import struct
import logging


class AegirPacketDecoder(struct.Struct):
    """Decoder class for incoming struct packets from the Arduino."""

    EOP_VAL = 0xa5
    EOP_BYTES = bytearray([EOP_VAL]*2)

    def __init__(self):
        """Initialise the Packet Decoder.

        The constructor uses a super init to create the structure
        for a decoded packet, as well as setting the expected values to a default.
        """
        super().__init__('<HH?BH')

        self.t1 = None
        self.t2 = None
        self.fault = None
        self.checksum = None
        self.eop = None

        self.csumValid = None

    def packet_complete(self, buffer):
        """Verify the packet is complete.

        Check if the packet is the appropriate size and has the correct
        End of Packet identification bytes.
        """
        return len(buffer) > 2 and buffer[-2:] == self.EOP_BYTES

    def unpack(self, buffer):
        """Unpack the data from the buffer into the initialised values."""
        (self.t1, self.t2, self.fault, self.checksum, self.eop) = super().unpack(buffer)

    def checkSumCheck(self, buffer):
        """Verify the checksum value of the packet using an XOR checksum."""
        checkSumCheck = 0
        csum_and_eop_size = 3
        packet_size = (len(buffer) - csum_and_eop_size)
        i = 0

        for i in range(packet_size):
            checkSumCheck ^= buffer[i]

        logging.debug('Python-side Checksum = ' + str(checkSumCheck))
        if checkSumCheck - self.checksum == 0:
            self.csumValid = True
        else:
            self.csumValid = False

    def make_dict(self):
        """Return the values as a dictionary."""
        dictionary = {
            "t1": self.t1,
            "t2": self.t2,
            "fault": self.fault,
            "checksum": self.checksum,
            "eop": hex(self.eop)
        }
        return dictionary

    def __str__(self):
        """Return the values as a formatted string."""
        return "t1={} t2={} fault={} checksum={} eop={:#x}".format(
            self.t1, self.t2, self.fault, self.checksum, self.eop)
