from agility.maestro import Maestro
from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.usc import Usc
from finesse.eclipse import Finesse
from shared.debug import Dummy
from enum import IntEnum
from bisect import bisect
import numpy as np
import math
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

        # Define constants.
        self.length = length
        self.width = width
        self.cx = cx
        self.cy = cy
        self.com = np.array((cx, cy, 0))

        # Define quick access array.
        self.j = np.array((
            (2, 1),
            (0, 3),
            (3, 0),
            (1, 2)
        ))

        # Define static vertices.
        x = 0.5 * self.length
        y = 0.5 * self.width

        self.vertices = np.array((
            (x, y, 0),
            (x, -y, 0),
            (-x, y, 0),
            (-x, -y, 0)
        ))

        # Dynamic bias.
        self.bias = None
        self.default_bias()

    def default_bias(self):
        """
        Zeros vertices and bias.
        :return: Bias.
        """

        self.bias = np.zeros((4, 3)) - self.com
        return self.bias

    @staticmethod
    def rotation_matrix(axis, theta):
        """
        Return the rotation matrix associated with counterclockwise rotation about the given axis by theta radians.
        http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector (by unutbu).
        :param axis: A numpy vector.
        :param theta: A float.
        :return: The quaternion.
        """

        axis /= math.sqrt(np.dot(axis, axis))
        a = math.cos(theta / 2.0)
        b, c, d = -axis * math.sin(theta / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array(((aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)),
                         (2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)),
                         (2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc)))

    def tilt_body(self, vertices, air, theta, lock=True):
        """
        Tilt the body to give additional stability.
        :param vertices: Vertices of the translated rectangle (4 x 3).
        :param air: The index of the leg lifted in the air.
        :param theta: Degrees to rotate in radians.
        :param lock: Whether or not to lock z-value (usually 0) of the lifted leg.
        :return: The tilted vertices.
        """

        # Compute rotation axis.
        legs = self.j[air]
        r0, r1 = vertices[legs]
        axis = r1 - r0

        # Rotate about axis.
        q = self.rotation_matrix(axis, theta)
        r = np.dot(vertices, q.T)

        if lock:
            # Lock the lifted leg back to original position.
            delta = vertices[air] - r[air]
            vertices = r + delta
        else:
            # No need to lock. Vertices is simply r.
            vertices = r

        return vertices

    def adjust_com(self, off, next_frame, sigma):
        """
        Adjust the center of mass based on grounded leg positions.
        :param off: An array of True or False indicating if a leg is up.
        :param next_frame: An array representing the next frame (4 x 3).
        :param sigma: Safety boundary.
        :return: Bias.
        """

        # Get indices.
        air = np.where(off)[0]

        # No static com adjustments can be made for trot.
        if len(air) != 1:
            return

        air = int(air)

        # Relative to absolute.
        original = next_frame + self.vertices

        # Get points.
        legs = self.j[air]
        p = original[legs]
        x1, y1, z1 = p[0]
        x2, y2, z2 = p[1]

        # Define center of mass as (0, 0).
        cx, cy = 0, 0

        # Compute Alastair's magic.
        m = (y2 - y1) / (x2 - x1)
        b1 = y1 - m * x1
        b3 = cy + (cx / m)
        x0 = (b3 - b1) / (m + 1 / m)
        y0 = m * x0 + b1

        # Compute theta.
        theta = math.atan2((y2 - y1), (x2 - x1))

        # Compute rho.
        rx = sigma * math.sin(theta) + x0
        ry = -sigma * math.cos(theta) + y0
        rz = 0

        rho = np.array([rx, ry, rz])

        # Adjust vertices.
        new = original + rho

        # Perform tilt.
        new = self.tilt_body(new, air, 0.05)

        # Compute bias.
        self.bias = new - original

        return self.bias

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
        # Define legs.
        self.legs = [leg1, leg2, leg3, leg4]
        self.leg_servos = [servo for leg in self.legs for servo in leg]

        # Define head.
        self.head = head
        self.head_servos = [servo for servo in head]

        # Define body.
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
            logger.info("Successfully attached to Maestro's low-level interface.")
        except ConnectionError:
            self.usc = Dummy()
            logger.warn("Failed to attached to Maestro's low-level interface. "
                        "If not debugging, consider this a fatal error.")

        # Set up virtual COM and TTL ports.
        try:
            self.maestro = Maestro()
            logger.info("Successfully attached to Maestro's command port.")
        except ConnectionError:
            self.maestro = Dummy()
            logger.warn("Failed to attached to Maestro's command port. "
                        "If not debugging, consider this a fatal error.")

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

    def execute(self, frames, dt):
        # Get all legs and servos for quick access.
        legs = self.robot.legs
        servos = self.robot.leg_servos

        # Update initial leg locations.
        self.maestro.get_multiple_positions(servos)

        for leg in legs:
            leg.get_position()

        while True:
            for frame in frames:
                for i in range(len(legs)):
                    legs[i].target(frame[i])

                self.maestro.end_together(servos, time=dt)
                self.wait(servos)

    def prepare(self, gait, steps=100, debug=False):
        """
        Execute a given gait class.
        This class is (will be) thread safe.
        :param gait: The gait class.
        :param steps: Number of steps per iteration of the gait.
        :param debug: Show gait in a graph.
        :return: (frames, dt) ready for execution.
        """

        # Define body for quick access.
        body = self.robot.body

        # Get gait properties.
        ground = gait.ground
        dt = gait.time / steps
        ts = np.linspace(0, 1000, num=steps, endpoint=False)

        # Get all legs for quick access.
        legs = self.robot.legs

        # Compute shape.
        shape = (steps, len(legs), 3)
        frames = np.zeros(shape, dtype=float)

        # Run static analysis.
        f = [gait.evaluate(leg, ts) for leg in legs]
        frames = np.concatenate(f).reshape(shape, order='F')

        # Debugging.
        if debug:
            self.plot_gait(frames)

        # Copy frames for comparison.
        original = frames.copy()

        # Iterate and perform static analysis.
        for t in range(steps):
            # Look ahead to check which legs are about to lift. Compare to original.
            next_frame = original[(t + 1) % steps]
            off = next_frame[:, 2] > ground

            if np.any(off):
                # If any legs are off, perform center of mass adjustments accordingly.
                bias = body.adjust_com(off, next_frame, 0.5)
            else:
                bias = body.default_bias()

            print(frames[t])
            frames[t] -= bias

        return frames, dt

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
        self.wait(servos)

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

    def wait(self, servos=None):
        """
        Block until all servos have reached their targets.
        :param servos: An array of servos. If None, checks if all servos have reached their targets (more efficient).
        """

        while not self.is_at_target(servos=servos):
            time.sleep(0.005)

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
