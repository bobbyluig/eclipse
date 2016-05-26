import serial
from serial.tools import list_ports
import time


class Ares:
    def __init__(self, robot, camera, info):
        self.robot = robot
        self.camera = camera

        self.max_speed = info['max_speed']
        self.max_rotation = info['max_rotation']

        self.k = 1

    def compute_vector(self, target, area, x, hr):
        """
        From given Theia data, compute desired movement vector.
        :param target: The target area of the object.
        :param area: The current area of the object..
        :param x: The x-center of the target.
        :param hr: Head rotation.
        :return: (forward, rotation).
        """

        # Compute absolute r.
        dr = (x - 0.5 * self.camera.width) * -1
        r = dr / self.camera.width * (self.camera.fx / 2)
        r += hr

        # Get range bounds.
        servo = self.robot.head[0]
        low = servo.left_bound - self.camera.fx / 2
        high = servo.right_bound + self.camera.fx / 2
        mid = (low + high) / 2
        delta = abs(high - mid)

        # Compute magnitude of r.
        if abs(r - mid) <= 5:
            # Close enough to target.
            rotation = 0
        elif r > mid:
            # Left turn.
            rotation = abs(self.max_rotation * r / delta)
        else:
            # Right turn.
            rotation = abs(self.max_rotation * r / delta)
            rotation *= -1

        if rotation > 0.5:
            # Too much rotation, perform in place turn.
            forward = 0
        else:
            v = self.max_speed - self.max_speed * area / target

            if abs(v) < 0.5:
                # Too slow. No need to move.
                forward = 0
            else:
                forward = v

        # Round because rounded things are better.
        rotation = round(rotation, 2)
        forward = round(forward, 2)

        return forward, rotation

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