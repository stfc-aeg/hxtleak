"""Packet Decoder portion of the Aegir Adapter.

This handles the unpacking and validation of received packets,
as well as the formatting of the decoded output.

James Foster, STFC Detector Systems Software Group
"""
import struct


class AegirPacketDecoder(struct.Struct):
    """Decoder class for received data packets."""

    EOP_VAL = 0xa5
    EOP_BYTES = bytearray([EOP_VAL]*2)

    def __init__(self):
        """Initialise the Packet Decoder.

        The constructor uses a super init to create the structure
        for a decoded packet, as well as setting the expected values to a default.
        """
        super().__init__('<ffffffff????BBH')

        self.board_temp_threshold = None
        self.board_humidity_threshold = None
        self.probe_temp_1_threshold = None
        self.probe_temp_2_threshold = None
        self.board_temp = None
        self.board_humidity = None
        self.probe_temp_1 = None
        self.probe_temp_2 = None
        self.leak_detected = None
        self.cont = None
        self.fault = None
        self.warning = None
        self.sensor_status = None
        self.checksum = None
        self.eop = None

        self.checksum_valid = None

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
        # (self.adc_val1, self.adc_val2, self.adc_val3, self.adc_val4,
        (self.board_temp_threshold, self.board_humidity_threshold,
         self.probe_temp_1_threshold, self.probe_temp_2_threshold,
         self.board_temp, self.board_humidity, self.probe_temp_1, self.probe_temp_2,
         self.leak_detected, self.cont, self.fault, self.warning, self.sensor_status,
         self.checksum, self.eop) = super().unpack(buffer)

        self.checksum_valid = None

    def verify_checksum(self, buffer):
        """Verify the checksum value of the packet using an XOR checksum.

        :param buffer: buffer for received raw data packet input
        """
        calc_checksum = 0
        csum_and_eop_size = 3
        packet_size = (len(buffer) - csum_and_eop_size)
        i = 0

        for i in range(packet_size):
            calc_checksum ^= buffer[i]

        if calc_checksum == self.checksum:
            self.checksum_valid = True
        else:
            self.checksum_valid = False

        return self.checksum_valid

    def as_dict(self):
        """Return the values as a dictionary."""
        dictionary = {
            "board_temp_threshold"     : (self.board_temp_threshold),
            "board_humidity_threshold" : (self.board_humidity_threshold),
            "probe_temp_1_threshold"   : (self.probe_temp_1_threshold),
            "probe_temp_2_threshold"   : (self.probe_temp_2_threshold),

            "board_temp": (self.board_temp),
            "board_humidity": (self.board_humidity),
            "probe_temp_1": (self.probe_temp_1),
            "probe_temp_2": (self.probe_temp_2),

            "leak_detected": self.leak_detected,
            "cont": self.cont,
            "fault": self.fault,
            "warning": self.warning,
            "sensor_status": self.sensor_status,
            "checksum": self.checksum,
            "eop": hex(self.eop)
        }
        return dictionary

    def __str__(self):
        """Return the values as a formatted string."""
        return """
        board_temp_threshold={:.2f} board_humidity_threshold={:.2f}
        probe_temp_1_threshold={:.2f} probe_temp_2_threshold={:.2f}
        board_temp={:.2f} board_humidity={:.2f} probe_temp_1={:.2f} probe_temp_2={:.2f}
        leak_detected={} cont={} fault={} warning={} sensor_status={}
        checksum={} eop={:#x}""".format(
            self.board_temp_threshold, self.board_humidity_threshold,
            self.probe_temp_1_threshold, self.probe_temp_2_threshold,
            self.board_temp, self.board_humidity, self.probe_temp_1, self.probe_temp_2,
            self.leak_detected, self.cont, self.fault, self.warning, self.sensor_status,
            self.checksum, self.eop
        )
