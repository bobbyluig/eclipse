from agility.maestro import Maestro
from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.usc import Usc
from finesse.eclipse import Finesse
from enum import IntEnum
from bisect import bisect
import numpy as np
from matplotlib.path import Path
import time
import logging

logger = logging.getLogger('universe')


class ServoError(Exception):
    pass


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

    def get_range(self):
        """
        Get the maximum and minimum with bias.
        :return: (min, max)
        """

        low = self.min_deg - self.bias
        high = self.max_deg - self.bias

        return low, high

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
            raise ServoError('Target out of range!')

        return deg

    def get_position(self):
        """
        Get the servo's current position in degrees.
        :return: Output degrees.
        """

        deg = self.maestro_to_deg(self.pwm)
        deg = (deg - self.bias) * self.direction

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


class Body:
    def __init__(self, length, width, cx, cy):
        """
        Create a body object.
        Note that dimensions are between kinematic roots.
        :param length: Length of body (along x-axis).
        :param width: Width of body (along y-axis).
        :param cx: Bias of center of mass along x.
        :param cy: Bias of center of mass along y.
        """

        self.length = length
        self.width = width
        self.cx = cx
        self.cy = cy

        self.com = np.array([cx, cy, 0])

        x = 0.5 * self.length
        y = 0.5 * self.width
        self.vertices = np.array([
            (x, y, 0),
            (x, -y, 0),
            (-x, y, 0),
            (-x, -y, 0)
        ])

        self.bias = np.zeros(3)

    def adjust_com(self, off, next_frame):
        """
        Adjust the center of mass based on grounded leg positions.
        :param off: An array of True or False indicating if a leg is up.
        :param next_frame: An array representing the next frame (4 x 3).
        """

        # Get indices.
        air = np.where(off == True)[0]
        ground = np.where(off == False)[0]

        # No static com adjustments can be made for trot.
        if len(air) != 1:
            return

        index = int(ground)

        if index == 0:
            self.bias = np.array([
                [0, 0, 0],
                [-0.7, -0.5, 0],
                [-0.7, -0.5, 0],
                [-0.7, -0.5, -1]
            ], dtype=float)
        elif index == 1:
            self.bias = np.array([
                [-0.7, 0.5, 0],
                [0, 0, 0],
                [-0.7, 0.5, -1],
                [-0.7, 0.5, 0]
            ], dtype=float)
        elif index == 2:
            self.bias = np.array([
                [0.7, -0.5, 0],
                [0.7, -0.5, -1],
                [0, 0, 0],
                [0.7, -0.5, 0]
            ], dtype=float)
        elif index == 3:
            self.bias = np.array([
                [0.7, 0.5, -1],
                [0.7, 0.5, 0],
                [0.7, 0.5, 0],
                [0, 0, 0]
            ], dtype=float)

        # next_pose = [next_frame[i] for i in air]

    def translate(self, x, y, z):
        """
        Translate the body and thus the center of mass.
        :param x: Motion along x.
        :param y: Motion along y.
        :param z: Motion along z.
        """

        t = np.array([x, y, z], dtype=float)

        self.com = np.array([self.cx, self.cy, 0], dtype=float) + t
        self.bias = self.com

    def is_supported(self, vertices):
        """
        Checks if a given support triangle contains the center of mass.
        This assumes the robot is not on a slant or hill.
        :param vertices: The transformed vertices as a 3 x 2 numpy matrix.
        :return: True if center of mass is in triangle, else False.
        """

        triangle = Path(vertices)
        return triangle.contains_point(self.com[:2])


class Leg:
    def __init__(self, servo1, servo2, servo3, lengths, index, ik, fk):
        """
        Create a leg object.
        :param servo1: The first hip servo object.
        :param servo2: The second hip servo object.
        :param servo3: The knee servo object.
        :param lengths: The leg segment lengths l1 and l2.
        :param index: The leg index (1 - 4).
        :param ik: Inverse kinematics solver.
        :param fk: Forward kinematics solver.
        """

        self.servos = [servo1, servo2, servo3]
        self.lengths = lengths
        self.index = index

        self.ik_solver = ik
        self.fk_solver = fk

        self.position = None

    def target(self, point):
        """
        Target a point in space.
        :param point: (x, y, z).
        :return: True if target is reachable, else False.
        """

        try:
            angles = self.ik_solver(self.lengths, point)
            self.servos[0].set_target(angles[0])
            self.servos[1].set_target(angles[1])
            self.servos[2].set_target(angles[2])
            self.position = point
        except (ServoError, ValueError, ZeroDivisionError):
            return False

        return True

    def get_position(self):
        """
        Compute current leg position based on servo data.
        """

        a = self.servos[0].get_position()
        b = self.servos[0].get_position()
        c = self.servos[0].get_position()

        self.position = self.fk_solver(self.lengths, (a, b, c))

    def __getitem__(self, key):
        return self.servos[key]

    def __add__(self, other):
        return self.servos + other.servos

    def __radd__(self, other):
        return other + self.servos

    def __len__(self):
        return len(self.servos)


class Head:
    def __init__(self, servo1, servo2, eye):
        """
        Create a head object.
        :param servo1: Servo object controlling left and right head turns.
        :param servo2: Servo object controlling up and down head turns.
        :param eye: An eye object for configuration.
        """

        if servo2 is None:
            self.servos = [servo1]
        else:
            self.servos = [servo1, servo2]

        self.width = eye.width
        self.height = eye.height
        self.fov = eye.fov

    def __getitem__(self, item):
        return self.servos[item]

    def __len__(self):
        return len(self.servos)


class Robot:
    def __init__(self, leg1, leg2, leg3, leg4, body, head=None):
        self.legs = [leg1, leg2, leg3, leg4]
        self.head = head
        self.body = body


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

    def look_at(self, x, y):
        """
        Move the head to look at a given target.
        :param x: x-coordinate of target.
        :param y: y-coordinate of target.
        :return: (dt, vt, dp, vp)
        """

        head = self.robot.head

        # Define velocity constant.
        k = 1.5

        # Compute deltas.
        dx = (x - 0.5 * head.width) * -1
        dy = (y - 0.5 * head.height) * -1

        dt = dx / head.width * (head.fov / 2)
        dp = dy / head.height * (head.fov / 2)

        # Compute suggested velocity. Balance between blur and speed.
        vt = int(round(abs(dt * k)))
        vp = int(round(abs(dt * k)))

        return dt, vt, dp, vp

    def move_head(self, dt, vt, dp, vp):
        head = self.robot.head
        sx = head[0]

        self.maestro.get_position(sx)
        current = sx.get_position()

        if vt == 0:
            sx.target = sx.pwm
            target = current
        else:
            low, high = sx.get_range()
            target = current + dt

            if target < low:
                target = low
            elif target > high:
                target = high

            sx.set_target(target)

        self.maestro.set_speed(sx, vt)
        self.maestro.set_target(sx)

        return target

    def scan(self, direction=None):
        """
        Scan the head either right or left. Ignores direction
        :param direction: -1 towards minimum, +1 towards maximum.
        """

        head = self.robot.head
        sx = head[0]

        self.maestro.get_position(sx)
        current = sx.get_position()
        low, high = sx.get_range()

    @staticmethod
    def plot_gait(frames):
        """
        Plot a gait given some frames. Used for debugging.
        :param frames: Frames generated by execute.
        """

        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')

        x = frames[:, 0, 0]
        y = frames[:, 0, 1]
        z = frames[:, 0, 2]

        ax.plot(x, y, z, marker='o')
        plt.show()

    def execute(self, gait, steps=100, debug=False):
        """
        Execute a given gait class.
        This class is (will be) thread safe.
        :param gait: The gait class.
        :param steps: Number of steps per iteration of the gait.
        :param debug: Show gait in a graph.
        """

        # Define body for quick access.
        body = self.robot.body

        # Get gait properties.
        ground = gait.ground()
        dt = gait.time() / steps

        # Get all legs and servos for quick access.
        legs = self.robot.legs
        servos = [servo for leg in legs for servo in leg]

        # Allocate array for frames.
        frames = np.zeros((steps, len(legs), 3), dtype=float)

        # Debug. Currently only supports crawl.
        assert(gait.num_supports() == 3)

        # Run static analysis.
        for t in range(steps):
            frame = frames[t]

            for i in range(len(legs)):
                frame[i] = gait.evaluate(legs[i], t)

        # Debugging.
        if debug:
            self.plot_gait(frames)

        # Update initial leg locations.
        self.maestro.get_multiple_positions(servos)

        for leg in legs:
            leg.get_position()

        # Copy frames for comparison.
        original = frames.copy()

        # Iterate and perform static analysis.
        for t in range(steps):
            # Look ahead to check which legs are about to lift. Compare to original.
            next_frame = original[(t + 1) % steps]
            off = next_frame[:, 2] > ground

            if np.any(off):
                # If any legs are off, perform center of mass adjustments accordingly.
                body.adjust_com(off, next_frame)
            else:
                body.bias = np.zeros((4, 3), dtype=float)

            frame = frames[t] - (body.bias + body.com)

            # Do nothing if current frame is the same as the last frame.
            for i in range(len(legs)):
                target = frame[i]
                legs[i].target(target)

            self.maestro.end_together(servos, time=dt)

            while not self.is_at_target(servos):
                time.sleep(0.01)

    def center_head(self):
        servo = self.robot.head[0]
        self.maestro.set_speed(servo, 20)
        servo.set_target(0)
        self.maestro.set_target(servo)

    def move_body(self, x, y, z, t=0):
        legs = self.robot.legs
        servos = legs[0] + legs[1] + legs[2] + legs[3]

        self.maestro.get_multiple_positions(servos)

        for leg in legs:
            angles = [l.get_position() for l in leg]
            a, b, c = Finesse.forward_pack(leg.lengths, angles)
            a -= x
            b -= y
            c -= z
            self.target_euclidean(leg, (-x, -y, -sum(leg.lengths) - z))

        self.maestro.end_together(servos, time=t)

        while not self.is_at_target():
            # Sleep for a short time to drastically save CPU cycles.
            time.sleep(0.0005)

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

        for leg in self.robot.legs:
            for servo in leg:
                servo.set_target(0)
                channel = settings.channelSettings[servo.channel]
                channel.mode = ChannelMode.Servo
                channel.homeMode = HomeMode.Goto
                channel.home = servo.target
                channel.minimum = (servo.min_pwm // 64) * 64
                channel.maximum = -(-servo.max_pwm // 64) * 64

        for servo in self.robot.head:
            servo.set_target(0)
            channel = settings.channelSettings[servo.channel]
            channel.mode = ChannelMode.Servo
            channel.homeMode = HomeMode.Goto
            channel.home = servo.target
            channel.minimum = (servo.min_pwm // 64) * 64
            channel.maximum = -(-servo.max_pwm // 64) * 64

        self.usc.setUscSettings(settings, False)

    def go_home(self):
        """
        Let the Maestro return all servos to home.
        """

        self.maestro.go_home()

    def zero(self):
        """
        Manual return home by resetting all leg servo targets.
        """

        for leg in self.robot.legs:
            for servo in leg:
                servo.set_target(0)
                self.maestro.set_speed(servo, 30)
                self.maestro.set_target(servo)

        for servo in self.robot.head:
            servo.set_target(0)
            self.maestro.set_speed(servo, 50)
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
            self.maestro.get_multiple_positions(servos)

            if all(servo.at_target() for servo in servos):
                return True

            return False
