from agility.maestro import Maestro
from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.usc import Usc
from finesse.main import Finesse
import time
import logging

logger = logging.getLogger('universe')


class Servo:
    def __init__(self, channel, min_deg, max_deg, min_pwm, max_pwm, max_vel,
                 bias=0, direction=1):
        self.channel = channel # 0 to 17
        self.min_deg = min_deg # -360 to 360 as (degrees)
        self.max_deg = max_deg # -360 to 360 as (degrees)
        self.min_pwm = min_pwm * 4 # 0 to 4000 as (us)
        self.max_pwm = max_pwm * 4 # 0 to 4000 as (us)
        self.max_vel = max_vel # 0 to 1000, as (ms / 60deg)

        # Bias should be adjusted such that the servo is at kinematic "0" degree when it's target is 0 degrees.
        # This is used to compensate for ridge spacing and inaccuracies during installation.
        # Think of this like the "home" value of the servo.
        self.bias = bias

        # If the front of the servo is pointing in a negative axis, set this to negative 1.
        # This reverses the directionality of all angle inputs.
        self.direction = direction

        # Dynamic current data.
        self.pwm = 0
        self.vel = 0
        self.accel = 0

        # User defined target. Also used to store last target.
        # In units of 0.25 us.
        self.target = 0

        # Compute constants.
        self.k_deg2mae = (self.max_pwm - self.min_pwm) / (self.max_deg - self.min_deg)
        self.k_mae2deg = (self.max_deg - self.min_deg) / (self.max_pwm - self.min_pwm)
        self.k_vel2mae = (60 * self.k_deg2mae) / self.max_vel * 10
        self.k_mae2vel = self.max_vel / ((60 * self.k_deg2mae) * 10)

    def set_target(self, deg):
        """
        Set the target for the servo.
        :param deg: The input degrees.
        """

        # Account for direction and bias.
        deg = deg * self.direction + self.bias

        # Normalize.
        if deg > self.max_deg:
            deg -= 360
        elif deg < self.min_deg:
            deg += 360

        if deg > self.max_deg or deg < self.min_deg:
            raise Exception('Target out of range!')

        self.target = self.deg_to_maestro(deg)

    def at_target(self):
        """
        Checks if the servo is at its target.
        :return: True if servo is at its target, else False.
        """

        return self.target == self.pwm

    def deg_to_maestro(self, deg):
        """
        Converts degrees to 0.25 us.
        :param deg: The input degrees.
        :return: The PWM in units of 0.25 us.
        """

        return round(self.min_pwm + self.k_deg2mae * (deg - self.min_deg))

    # Convert 0.25 us to degrees.
    def maestro_to_deg(self, pwm):
        """
        Converts 0.25 us to degrees.
        :param pwm: The input PWM in units of 0.25 us.
        :return: Degrees.
        """

        return self.min_deg + self.k_mae2deg * (pwm - self.min_pwm)


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

    def animate_single(self, frame):
        """
        Animate a single frame of one leg.
        :param sequence: The sequence single.

        frame = (index, frame_time, [])
        """

        index, frame_time, points = frame

        if index is None:
            time.sleep(frame_time / 1000)
            return

        t = frame_time / len(points)
        for point in points:
            self.target_euclidean(self.robot[index], point)
            self.maestro.get_multiple_positions(self.robot[index])
            self.maestro.end_together(self.robot[index], time=t)
            while self.is_at_target():
                # Sleep for a short time to drastically save CPU cycles.
                time.sleep(0.0005)

    def animate_synchronized(self, sequence):
        """
        Animate one iteration of a synchronized gait sequence.

        :param sequence: The gait sequence.

        sequence = {
            'frame_time': 0,
            'length': 0,
            'leg0': [],
            'leg1': [],
            'leg2': [],
            'leg3': []
        }
        """

        # Debugging checks, can remove later.
        assert(sequence['frame_time'] > 20)
        assert(len(sequence['leg0']) == len(sequence['leg1']) ==
               len(sequence['leg2']) == len(sequence['leg3']) ==
               sequence['length'] > 0)

        # Begin animation.
        for i in range(sequence['length']):
            for leg in self.robot:
                self.target_euclidean(leg, sequence['leg%s' % leg.index][i], a3=True)

            self.maestro.get_multiple_positions(self.robot.servos)
            self.maestro.end_together(self.robot.servos, time=sequence['frame_time'])

            while self.is_at_target():
                # Sleep for a short time to drastically save CPU cycles.
                time.sleep(0.0005)

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
                channel.minimum = servo.min_pwm
                channel.maximum = servo.max_pwm

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
