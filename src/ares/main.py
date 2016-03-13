import serial
from serial.tools import list_ports
import time


class RFID:
    def __init__(self, port=None):
        """
        RFID reader class for SparkFun's USB RFID Reader.
        :param port: The virtual port number.
        """

        if port is not None:
            self.port = port
        else:
            ports = list(list_ports.grep(r'(?i)0403'))

            if len(ports) == 1:
                self.port = ports[0][0]
            else:
                raise Exception('Unable to determine RFID reader port automatically. Please specify.')

        # Start a connection using pyserial.
        try:
            self.usb = serial.Serial(self.port, timeout=0)
        except:
            raise Exception('Unable to connect to RFID reader at %s.' % self.port)

    def read(self, timeout=10):
        """
        Read one tag from the buffer.
        :param timeout: Maximum time to wait.
        :return: None if timeout, otherwise a 12 character RFID.
        """

        end = time.time() + 10

        while time.time() <= end:
            if self.usb.inWaiting() >= 16:
                data = self.usb.read(size=16)
                data = data.decode()

                # Assert for debugging verification.
                assert(data[0] == '\x02')
                assert(data[13:] == '\r\n\x03')

                rfid = data[1:13]

                return rfid
            else:
                time.sleep(0.01)

        return None