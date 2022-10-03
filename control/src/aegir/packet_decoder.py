"""Packet Decoder portion of the Aegir Adapter.

This handles the unpacking and validation of received packets,
as well as the formatting of the decoded output.

James Foster
"""
import struct
import logging


class AegirPacketDecoder(struct.Struct):
    """Decoder class for received data packets."""

    EOP_VAL = 0xa5
    EOP_BYTES = bytearray([EOP_VAL]*2)

    def __init__(self):
        """Initialise the Packet Decoder.

        The constructor uses a super init to create the structure
        for a decoded packet, as well as setting the expected values to a default.
        """
        super().__init__('<HHHHffff???BH')

        self.adc_val1 = None
        self.adc_val2 = None
        self.adc_val3 = None
        self.adc_val4 = None
        self.temp = None
        self.humidity = None
        self.probe1 = None
        self.probe2 = None
        self.leak_detected = None
        self.cont = None
        self.fault = None
        self.checksum = None
        self.eop = None

        self.csumValid = None

    def packet_complete(self, buffer):
        """Verify the packet is complete.

        Check if the packet is the appropriate size and has the correct
        End of Packet identification bytes.

        :param buffer: buffer for received raw data packet input
        """
        return len(buffer) > 2 and buffer[-2:] == self.EOP_BYTES

    def unpack(self, buffer):
        """Unpack the data from the buffer into the initialised values.

        :param buffer: buffer for received raw data packet input
        """
        (self.adc_val1, self.adc_val2, self.adc_val3, self.adc_val4,
         self.temp, self.humidity, self.probe1, self.probe2,
         self.leak_detected, self.cont, self.fault,
         self.checksum, self.eop) = super().unpack(buffer)

    def checkSumCheck(self, buffer):
        """Verify the checksum value of the packet using an XOR checksum.

        :param buffer: buffer for received raw data packet input
        """
        checkSumCheck = 0
        csum_and_eop_size = 3
        packet_size = (len(buffer) - csum_and_eop_size)
        i = 0

        for i in range(packet_size):
            checkSumCheck ^= buffer[i]

        #logging.debug('Python-side Checksum = ' + str(checkSumCheck))
        if checkSumCheck - self.checksum == 0:
            self.csumValid = True
        else:
            self.csumValid = False

    def as_dict(self):
        """Return the values as a dictionary."""
        dictionary = {
            "adc_val1": (self.adc_val1),
            "adc_val2": (self.adc_val2),
            "adc_val3": (self.adc_val3),
            "adc_val4": (self.adc_val4),

            "temp": (self.temp),
            "humidity": (self.humidity),
            "probe1": (self.probe1),
            "probe2": (self.probe2),

            "leak_detected": self.leak_detected,
            "cont": self.cont,
            "fault": self.fault,
            "checksum": self.checksum,
            "eop": hex(self.eop)
        }
        return dictionary

    def __str__(self):
        """Return the values as a formatted string."""
        return """
        adc_val1={} adc_val2={} adc_val3={} adc_val4={} 
        temp={:.2f} humidity={:.2f} probe1={:.2f} probe2={:.2f} 
        leak_detected={} cont={} fault={} checksum={} eop={:#x}""".format(
            self.adc_val1, self.adc_val2, self.adc_val3, self.adc_val4,
            self.temp, self.humidity, self.probe1, self.probe2,
            self.leak_detected, self.cont, self.fault, self.checksum, self.eop)