from agility.maestro import Maestro
from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.usc import Usc
from finesse.eclipse import Finesse
from enum import IntEnum
from bisect import bisect
import numpy as np
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

    def zero(self):
        """
        Set the servo to zero, ignoring bias.
        """

        self.target = self.deg_to_maestro(0)

    def set_target(self, deg):
        """
        Set the target for the servo.
        :param deg: The input degrees.
        """

        deg = self.normalize(deg)
        self.target = self.deg_to_maestro(deg)

    def normalize(self, deg):
        """
        Normalize a degree for the servo, taking into account direction and bias.
        :param deg: Input degrees.
        :return: Output degrees.
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

        return deg

    def at_target(self):
        """
        Checks if the servo is at its target.
        :return: True if servo is at its target, else False.
        """

        return self.target == self.pwm

    def passed_target(self, deg, greater):
        """
        Checks if a servo has passed its target.
        :param deg: The desired degrees to check.
        :param greater: True to check >=, else <=.
        :return: True if test is true, else False.
        """

        deg = self.normalize(deg)

        # Due to clockwise being defined as negative by Finesse, PWM checks should be inverted.
        # This is due to the fact that higher PWM in servos is clockwise.
        if greater:
            return self.deg_to_maestro(deg) <= self.pwm
        else:
            return self.deg_to_maestro(deg) >= self.pwm

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
        :param index: The leg index (1 - 4).
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


class Head:
    def __init__(self, servo1, servo2):
        """
        Create a head object.
        :param servo1: Servo object controlling left and right head turns.
        :param servo2: Servo object controlling up and down head turns.
        """

        self.servos = [servo1, servo2]

    def __getitem__(self, item):
        return self.servos[item]


class Robot:
    def __init__(self, leg1, leg2, leg3, leg4, head=None):
        self.legs = [leg1, leg2, leg3, leg4]
        self.head = head


class IR(IntEnum):
    WAIT_ALL = 1        # (Ins)
    WAIT_GE = 2         # (Ins, Leg, Servo, Deg)
    WAIT_LE = 3         # (Ins, Leg, Servo, Deg)
    WAIT_FIN = 4        # (Ins, Leg)
    MOVE = 5            # (Ins, Leg, (theta1, theta2, theta3), Time)


class Agility:
    def __init__(self, robot):
        # Set up robot.
        self.robot = robot

        # Set up Usc.
        try:
            self.usc = Usc()
            logger.info('Successfully attached to Maestro low-level interface.')
        except ConnectionError:
            self.usc = None
            logger.warn('Failed to attached to Maestro low-level interface. Skipping.')

        # Set up virtual COM and TTL ports.
        self.maestro = Maestro()

    def move_head(self, x, y, w, h):
        k = 0.2

        x1, y1 = w, h
        v = (x - 0.5 * x1) * k

        servo = self.robot.head[0]
        self.maestro.get_position(servo)
        self.maestro.set_speed(servo, int(abs(round(v))))

        if -1 < v < 1:
            servo.target = servo.pwm
        elif v > 0:
            # Target is on left. Servo target is minimum degrees.
            servo.set_target(servo.min_deg)
        else:
            # Target is on right. Servo target is maximum degrees.
            servo.set_target(servo.max_deg)

        self.maestro.set_target(servo)

    def center_head(self):
        servo = self.robot.head[0]
        self.maestro.set_speed(servo, 20)
        servo.set_target(0)
        self.maestro.set_target(servo)

    def generate_crawl(self, tau, beta):
        """
        Generate a crawl gait from a base sequence.
        Output has to be parsed by IR generator before execution.
        :param tau: The time to run through the entire sequence.
        :param beta: The percent of time each leg is on the ground. Usually >= 0.75.
        :return: A tuple of (angles, key_frames). The number of cols match the rows of the sequence.
        """

        # Points in the gait.
        sequence = np.array([
            (3, 0, -13),
            (0, 0, -13),
            (-3, 0, -13),
            (-3, 0, -10),
            (3, 0, -10)
        ])

        # Order of legs.
        order = [0, 3, 1, 2]

        # Compute distances.
        shifted = np.roll(sequence, -1, axis=0)
        distances = np.linalg.norm(sequence - shifted, axis=1)

        # Normalize time for each segment.
        ground = distances[:2]
        ground = ground / np.sum(ground)
        air = distances[2:]
        air = air / np.sum(air)

        # Scale using constants.
        t_ground = tau * beta
        t_air = tau - t_ground
        ground *= t_ground
        air *= t_air

        # Compute combined and cumulative.
        times = np.concatenate((ground, air))
        cumulative = np.cumsum(times)
        cumulative = np.roll(cumulative, 1)
        cumulative[0] = 0

        # Compute angles semi-efficiently. Needs improvement using numpy vectorization.
        if all(leg.lengths == self.robot.legs[0].lengths for leg in self.robot.legs):
            angle = [np.array(Finesse.inverse_pack(self.robot.legs[0].lengths, point)) for point in sequence]
            angles = np.array([angle, angle, angle, angle])
        else:
            angles = np.array([
                [np.array(Finesse.inverse_pack(self.robot.legs[order[0]].lengths, point)) for point in sequence],
                [np.array(Finesse.inverse_pack(self.robot.legs[order[1]].lengths, point)) for point in sequence],
                [np.array(Finesse.inverse_pack(self.robot.legs[order[2]].lengths, point)) for point in sequence],
                [np.array(Finesse.inverse_pack(self.robot.legs[order[3]].lengths, point)) for point in sequence]
            ])

        # Compute animation key frames.
        key_frames = np.array([
            cumulative,
            cumulative - tau / 4,
            cumulative - tau / 4 * 2,
            cumulative - tau / 4 * 3
        ])

        key_frames[key_frames < 0] += tau
        key_frames[key_frames >= tau] -= tau

        # Sort key_frames.
        key_frames = key_frames[order]

        return angles, key_frames

    @staticmethod
    def dual_sort(a, b):
        """
        Sort a and b but first sorting a and then using that order to sort b.
        Sorting is done in place.
        :param a: A numpy array.
        :param b: A numpy array whose first two dimensions must match a.
        :return (a, b)
        """

        # Perform sorting.
        args = np.argsort(a)

        # Pre-generate "axis" for sorting 2D arrays.
        axis = np.arange(a.shape[0])[:, np.newaxis]

        # Sorting 2D array using another 2D array.
        return a[axis, args], b[axis, args]

    def unwind(self, sequence):
        """
        Unwind a sequence to angles and key frames.
        This is essentially a pre-IR function for custom sequences.
        :param sequence: A sequence array of [leg1, leg2, leg3, leg4] where leg1 is [(target, time), ...].
        :return: A tuple of (angles, key_frames).
        """

        angles = []
        key_frames = []

        # Search for max length.
        lengths = [len(s) for s in sequence]
        length = max(lengths)

        for i in range(len(sequence)):
            x, y = zip(*sequence[i])

            x = [Finesse.inverse_pack(self.robot.legs[i].lengths, x[j]) for j in range(len(x))]

            padding = length - len(x)
            angles.append(x + [(None, None, None)] * padding)
            key_frames.append(y + (None,) * padding)

        angles = np.array(angles, dtype=float)
        key_frames = np.array(key_frames, dtype=float)

        return angles, key_frames

    @staticmethod
    def generate_ir(tau, angles, key_frames, ref=0):
        """
        Generate an intermediate representation for a continuous gait sequence.
        It automatically handles non-synchronized gaits very efficiently.
        This function does not actually execute the gait.
        It legs do not have the same number of points, angles and key_frames must be padded with nans at the end.
        :param tau: The time to run through the entire sequence.
        :param angles: A numpy array or target angles for each leg. NxM shape must match that of key_frames'.
        :param key_frames: A numpy array of times for each set of angles. NxM shape must match that of angles'.
        :param ref: Reference leg. This is usually leg 0 for whichever gait.
        :return An instruction array with IR instructions for execution or further compilation.
        """

        # Debugging checks.
        assert(angles.shape[:2] == key_frames.shape[:2])
        assert(0 <= ref < 4)

        # Sort.
        key_frames, angles = Agility.dual_sort(key_frames, angles)

        # Lengths of each (discount padding).
        lengths = (~np.isnan(key_frames)).sum(1)

        # Get unique key frames to iterate over. Discard nans (padding).
        unique_kf = np.unique(key_frames)
        unique_kf = unique_kf[~np.isnan(unique_kf)]

        # Instruction array.
        instructions = []

        # Iterate through sequence and build instructions.
        for k in range(len(unique_kf)):
            # Easier definition.
            frame = unique_kf[k]

            # Identify which legs are active.
            active = np.where((key_frames == frame) & (~np.isnan(key_frames)))

            # Determine when the frame should begin.
            if len(active[0]) == 4:
                # All legs begin together.
                instructions.append((IR.WAIT_ALL,))
            else:
                # Check if leg is in the middle of a sequence or at the end.
                if ref in active[0]:
                    # Leg is at end. Wait until leg reaches previous target.
                    instructions.append((IR.WAIT_FIN, ref))
                else:
                    # Define length.
                    length = lengths[ref]

                    # Interpolate by performing a right bisection on a sorted key_frame.
                    i = np.searchsorted(key_frames[ref], frame, side='right')

                    # Compute a delta.
                    delta = angles[ref][i % length] - angles[ref][i - 1]

                    # Find max angle change.
                    best = np.argmax(np.abs(delta))

                    # Interpolate angle for the best one of three.
                    angle = (angles[ref][i - 1][best] + delta[best] * abs(frame - key_frames[ref][i - 1]) /
                             abs(key_frames[ref][i % length] - key_frames[ref][i - 1]))

                    # Wait until angle is greater? (or less if false)
                    greater = delta[best] > 0

                    # Create instruction.
                    ctrl = IR.WAIT_GE if greater else IR.WAIT_LE
                    ins = (ctrl, ref, best, angle)

                    # Append instruction.
                    instructions.append(ins)

            # Create instructions to move servos.
            for l in range(len(active[0])):
                leg = active[0][l]

                # Define length.
                length = lengths[leg]

                # Get column.
                col = active[1][l]

                # Make indexing easier.
                x = (col + 1) % length

                # Get the target set of angles (the next one).
                ang = angles[leg][x]

                # Get time. Either at end of sequence of not.
                if x == 0:
                    t = tau - key_frames[leg][col]
                else:
                    t = key_frames[leg][x] - key_frames[leg][col]

                # Append instruction.
                instructions.append((IR.MOVE, leg, ang, t))

        # Create intro array.
        intro = []

        # Define some constants.
        zero_time = 500

        # Place all legs in start position.
        for leg in range(4):
            intro.append((IR.MOVE, leg, angles[leg][0], zero_time))

        return intro, instructions

    def execute_ir(self, ir):
        """
        Execute a generated IR sequence.
        :param ir: An array of IR commands.
        """

        for frame in ir:
            ins = frame[0]

            if ins == IR.WAIT_ALL:
                while not self.is_at_target():
                    time.sleep(0.0005)

            elif ins == IR.WAIT_FIN:
                leg = frame[1]

                while not self.is_at_target(servos=self.robot.legs[leg]):
                    time.sleep(0.0005)

            elif ins == IR.MOVE:
                if frame[1] == 2:
                    print(frame)
                leg = frame[1]
                angles = frame[2]
                t = frame[3]

                self.robot.legs[leg][0].set_target(float(angles[0]))
                self.robot.legs[leg][1].set_target(float(angles[1]))
                self.robot.legs[leg][2].set_target(float(angles[2]))
                self.maestro.end_together(self.robot.legs[leg], time=t, update=True)

            elif ins == IR.WAIT_GE:
                leg = frame[1]
                servo = frame[2]
                deg = frame[3]

                self.maestro.get_position(self.robot.legs[leg][servo])

                while not self.robot.legs[leg][servo].passed_target(deg, True):
                    self.maestro.get_position(self.robot.legs[leg][servo])
                    time.sleep(0.0005)

            elif ins == IR.WAIT_LE:
                leg = frame[1]
                servo = frame[2]
                deg = frame[3]

                self.maestro.get_position(self.robot.legs[leg][servo])

                while not self.robot.legs[leg][servo].passed_target(deg, False):
                    self.maestro.get_position(self.robot.legs[leg][servo])
                    time.sleep(0.0005)

    def animate_single(self, frame):
        """
        Animate a single frame of one leg.
        :param frame: The sequence single.

        frame = (index, frame_time, [])
        """

        index, frame_time, points = frame

        if index is None:
            time.sleep(frame_time / 1000)
            return

        t = frame_time / len(points)
        for point in points:
            self.target_euclidean(self.robot.legs[index], point)
            self.maestro.get_multiple_positions(self.robot.legs[index])
            self.maestro.end_together(self.robot.legs[index], time=t)
            while not self.is_at_target():
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
                self.target_euclidean(leg, sequence['leg%s' % leg.index][i])

            self.maestro.get_multiple_positions(self.robot.servos)
            self.maestro.end_together(self.robot.servos, time=sequence['frame_time'])

            while not self.is_at_target():
                # Sleep for a short time to drastically save CPU cycles.
                time.sleep(0.0005)

    @staticmethod
    def target_euclidean(leg, position, a2=False, a3=False):
        """
        Set a leg to a point.
        :param leg: The leg object.
        :param position: The target position.
        :param a2: True to find alternate solution for theta2.
        :param a3: True to find alternate solution for theta3.
        """

        angles = Finesse.inverse_pack(leg.lengths, position, a2=a2, a3=a3)

        if angles is not None:
            leg[0].set_target(angles[0])
            leg[1].set_target(angles[1])
            leg[2].set_target(angles[2])
        else:
            logger.warning('Unable to reach position ({}, {}, {}).'.format(*position))

    def configure(self):
        """
        Configure the Maestro by writing home positions and other configuration data to the device.
        """

        if self.usc is None:
            logger.warning('Low-level interface not attached!')
            return

        settings = self.usc.getUscSettings()
        settings.serialMode = uscSerialMode.SERIAL_MODE_USB_DUAL_PORT

        for leg in self.robot:
            for servo in leg:
                servo.set_target(0)
                channel = settings.channelSettings[servo.channel]
                channel.mode = ChannelMode.Servo
                channel.homeMode = HomeMode.Goto
                channel.home = servo.target
                channel.minimum = servo.min_pwm
                channel.maximum = servo.max_pwm

        self.usc.setUscSettings(settings, False)

    def go_home(self):
        """
        Let the Maestro return all servos to home.
        """

        self.maestro.go_home()

    def zero(self):
        """
        Manual return home by resetting all servo targets.
        """

        for leg in self.robot.legs:
            for servo in leg:
                servo.set_target(0)
                self.maestro.set_speed(servo, 30)
                self.maestro.set_target(servo)

        # Wait until completion.
        while not self.is_at_target():
            # Sleep for a short time to drastically save CPU cycles.
            time.sleep(0.0005)

    def is_at_target(self, servos=None):
        """
        Check if servos are at their target.
        :param servos: An array of servos. If None, checks if all servos have reached their targets (more efficient).
        :return: True if all servos are at their targets, False otherwise.
        """

        if servos is None:
            return not self.maestro.get_moving_state()
        else:
            for servo in servos:
                self.maestro.get_position(servo)

            if all(servo.at_target() for servo in servos):
                return True

            return False
