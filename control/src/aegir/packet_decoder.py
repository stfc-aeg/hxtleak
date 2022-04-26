import struct
import logging

class AegirPacketDecoder(struct.Struct):
    """Decoder class for incoming struct packets from the Arduino."""
    def __init__(self):

        super().__init__('<HH?BH')

        self.t1 = None
        self.t2 = None
        self.fault = None
        self.checksum = None
        self.eop = None

        self.csumValid = None

    def unpack(self, buffer):

        (self.t1, self.t2, self.fault, self.checksum, self.eop) = super().unpack(buffer)

    def checkSumCheck(self, buffer):
        checkSumCheck = 0
        csum_and_eop_size = 3
        packet_size = (len(buffer) - csum_and_eop_size)
        i=0

        for i in range(packet_size):
            checkSumCheck ^= buffer[i]
        
        logging.debug('Python-side Checksum = ' + str(checkSumCheck))
        if checkSumCheck - self.checksum == 0:
            self.csumValid = True
        else:
            self.csumValid = False
        
    def __str__(self):
        return "t1={} t2={} fault={} checksum={} eop={:#x}".format(self.t1, self.t2, self.fault, self.checksum, self.eop)