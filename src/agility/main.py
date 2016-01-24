from agility.maestro import Maestro, Servo
from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.usc import Usc
from finesse.main import Finesse
import time
import logging

logger = logging.getLogger('universe')


class Leg:
    def __init__(self, servo1, servo2, servo3, lengths, index):
        """
        Create a leg object.
        :param servo1: The first hip servo object.
        :param servo2: The second hip servo object.
        :param servo3: The knee servo object.
        :param lengths: The leg segment lengths l1 and l2.
        :param index: THe leg index (1 - 4).
        """

        self.servos = [servo1, servo2, servo3]
        self.lengths = lengths
        self.index = index

    def __getitem__(self, key):
        return self.servos[key]

    def __add__(self, other):
        return self.servos + other.servos

    def __radd__(self, other):
        return other + self.servos


class Robot:
    def __init__(self, leg1, leg2, leg3, leg4):
        self.legs = [leg1, leg2, leg3, leg4]
        self.servos = leg1 + leg2 + leg3 + leg4
        self.gait = None

    def __getitem__(self, key):
        return self.legs[key]

    def set_gait(self, gait):
        self.legs = sorted(self.legs, key=lambda leg: int(leg.index))

        if gait == '1243-creeping':
            self.legs = [self.legs[0], self.legs[1], self.legs[3], self.legs[2]]
        elif gait == '1342-creeping':
            self.legs = [self.legs[0], self.legs[2], self.legs[3], self.legs[1]]
        elif gait == '1234-creeping' or gait == 'bound':
            self.legs = [self.legs[0], self.legs[1], self.legs[2], self.legs[3]]
        elif gait == '1324-creeping' or gait == 'pace':
            self.legs = [self.legs[0], self.legs[2], self.legs[1], self.legs[3]]
        elif gait == '1423-creeping' or gait == 'trot':
            self.legs = [self.legs[0], self.legs[3], self.legs[1], self.legs[2]]
        elif gait == 'crawl':
            self.legs = [self.legs[0], self.legs[3], self.legs[1], self.legs[2]]
        else:
            logger.error('Unknown gait. Assuming 1234-creeping.')
            gait = '1234-creeping'

        self.gait = gait


class Agility:
    def __init__(self, robot):
        # Set up robot.
        self.robot = robot

        # Set up Usc.
        self.usc = Usc()
        self.settings = self.usc.getUscSettings()
        self.configure()

        # Set up virtual COM and TTL ports.
        self.maestro = Maestro()

    def animate_synchronized(self, sequence):
        """
        Animate one iteration of a synchronized gait sequence.

        :param sequence: The gait sequence.

        sequence = {
            'frame_time': 0,
            'length': 0,
            'leg1': [],
            'leg2': [],
            'leg3': [],
            'leg4': []
        }
        """

        # Debugging checks, can remove later.
        assert(sequence['frame_time'] > 20)
        assert(len(sequence['leg1']) == len(sequence['leg2']) ==
               len(sequence['leg3']) == len(sequence['leg4']) ==
               sequence['length'] > 0)

        # Begin animation.
        for i in range(sequence['length']):
            for leg in self.robot:
                self.target_euclidean(leg, sequence['leg%s' % leg.index][i])

            self.maestro.get_multiple_positions(self.robot.servos)
            self.maestro.end_together(self.robot.servos, time=sequence['frame_time'])

            while not self.is_at_target():
                # Sleep for a short time to drastically save CPU cycles.
                time.sleep(0.001)

    @staticmethod
    def target_euclidean(leg, position, a2=False, a3=False):
        angles = Finesse.inverse(leg.lengths, position, a2=a2, a3=a3)

        if angles is not None:
            leg[0].set_target(angles[0])
            leg[1].set_target(angles[1])
            leg[2].set_target(angles[2])
        else:
            logger.warn('Unable to reach position (%s, %s, %s).' % position)

    def configure(self):
        self.settings.serialMode = uscSerialMode.SERIAL_MODE_USB_DUAL_PORT

        for leg in self.robot:
            for servo in leg:
                servo.set_target(0)
                channel = self.settings.channelSettings[servo.channel]
                channel.mode = ChannelMode.Servo
                channel.homeMode = HomeMode.Goto
                channel.home = servo.target
                channel.minimum = servo.min_pwm // 4
                channel.maximum = servo.max_pwm // 4

        self.usc.setUscSettings(self.settings, False)

    def go_home(self):
        """
        Let the Maestro return all servos to home.
        """

        self.maestro.go_home()

    def zero(self):
        """
        Manual return home by resetting all servo targets.
        """

        for leg in self.robot:
            for servo in leg:
                servo.set_target(0)
                self.maestro.set_speed(servo, 0)
                self.maestro.set_target(servo)

        self.maestro.flush()

    def is_at_target(self, servos=None):
        """
        Check if servos are at their target.
        :param servos: An array of servos. If None, checks if all servos have reached their targets (more efficient).
        :return: True if all servos are at their targets, False otherwise.
        """

        if servos is None:
            return self.maestro.get_moving_state()
        else:
            for servo in servos:
                self.maestro.get_position(servo)

            if all(servo.at_target() for servo in servos):
                return True

            return False