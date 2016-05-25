from agility.maestro import Maestro
from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.usc import Usc
from scipy import interpolate
from finesse.eclipse import Finesse
from shared.debug import Dummy
import numpy as np
import math
from matplotlib.path import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import logging
import sys

logger = logging.getLogger('universe')


class ServoError(Exception):
    pass


class Stepper:
    def __init__(self, c1, c2, steps, direction=1):
        self.c1 = c1  # Direction channel.
        self.c2 = c2  # Step channel.
        self.steps = steps
        self.direction = direction

        self.step = 1
        self.target = 1

    def get_position(self):
        """
        Get the stepper's current position in degrees.
        :return: Output degrees.
        """

        return self.steps_to_deg(self.step)

    def deg_to_steps(self, deg):
        """
        Converts a normalized degree to the nearest integer step.
        :param deg: The input degrees.
        :return: The corresponding steps.
        """

        steps = int(round(deg * (self.steps / 360))) * self.direction

        if steps == 0:
            return self.steps
        else:
            return steps

    def steps_to_deg(self, steps):
        """
        Converts steps to a degree.
        :param steps: The number of steps.
        :return: The corresponding angle.
        """

        return steps * (360 / self.steps) * self.direction

    def step_one(self, direction):
        """
        Increment step counter.
        :param direction: 1 steps up, -1 steps down.
        """

        n = self.step + direction

        if n > self.steps or n < 1:
            self.step = 1
        else:
            self.step = n

    def set_target(self, deg):
        """
        Target a degree. Servo will attempt nearest path to target.
        :param deg: The input degrees.
        :return: The number of steps, either positive or negative.
        """

        # Normalize.
        deg -= 360 * (deg // 360)
        steps = self.deg_to_steps(deg)

        # Compute closest direction.
        target = steps - self.step
        delta = (self.steps / 2 - target) % self.steps - (self.steps / 2)

        # Return.
        return delta


class Servo:
    def __init__(self, channel, min_deg, max_deg, min_pwm, max_pwm, max_vel,
                 bias=0, direction=1, left_bound=None, right_bound=None):
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

        if left_bound is None:
            # Left bound (if not min_deg), with bias.
            self.left_bound = self.min_deg
        else:
            self.left_bound = left_bound

        if right_bound is None:
            # Left bound (if not max_deg), with bias.
            self.right_bound = self.max_deg
        else:
            self.right_bound = right_bound

        assert(self.left_bound >= self.min_deg)
        assert(self.right_bound <= self.max_deg)

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
        Get the maximum and minimum, removing bias.
        :return: (min, max)
        """

        low = self.left_bound - self.bias
        high = self.right_bound - self.bias

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
        if deg > self.right_bound:
            deg -= 360
        elif deg < self.left_bound:
            deg += 360

        if deg > self.right_bound or deg < self.left_bound:
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
    def __init__(self, length, width, cx, cy, cz, mb, ml):
        """
        Create a body object.
        Note that dimensions are between kinematic roots.
        :param length: Length of body (along x-axis).
        :param width: Width of body (along y-axis).
        :param cx: Bias of center of mass along x.
        :param cy: Bias of center of mass along y.
        :param cz: Bias of center of mass along z (relative to kinematic-zero plane).
        :param mb: Mass of body.
        :param ml: Mass of leg.
        """

        # Define constants.
        self.length = length
        self.width = width
        self.cx = cx
        self.cy = cy
        self.cz = cz
        self.mb = mb
        self.ml = ml
        self.com = np.array((cx, cy, cz))

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

    def default_bias(self, next_frame):
        """
        Zeros vertices and bias.
        :return: Bias.
        """

        # Relative to absolute.
        original = next_frame + self.vertices

        # Get com.
        cx, cy = self.get_com(original)

        return np.array((-cx, -cy, 0))

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

    @staticmethod
    def closest(x1, x2, y1, y2, x, y):
        """
        Compute the point along the two supporting legs that is closest to the center of mass.
        This shall be known as "Alastair's magic."
        """

        m = (y2 - y1) / (x2 - x1)
        b1 = y1 - m * x1
        b3 = y + (x / m)
        x0 = (b3 - b1) / (m + 1 / m)
        y0 = m * x0 + b1

        return x0, y0

    def get_com(self, frame):
        """
        Compute the center of mass given the leg positions.
        :param frame: The leg positions.
        :return: com -> [cx, cy].
        """

        com = self.ml * np.sum(frame[:, :2], axis=0) / (self.ml + self.mb)
        com += self.com[:2]

        return com

    def adjust_crawl(self, off, next_frame, sigma=2.0):
        """
        Adjust the center of mass for the crawl gait.
        :param off: An array defining which legs are in the air.
        :param next_frame: An array representing the next frame (4 x 3).
        :param sigma: Safety boundary.
        """

        # Get the leg in the air.
        air = np.where(off)[0]
        air = int(air)
        legs = self.j[air]

        # Relative to absolute.
        original = next_frame + self.vertices

        # Get points.
        p = original[legs]
        x1, y1, z1 = p[0]
        x2, y2, z2 = p[1]

        # Compute center of mass as with leg positions.
        cx, cy = self.get_com(original)

        # Get shortest path from zero-moment point to support triangle (perpendicular).
        x0, y0 = self.closest(x1, x2, y1, y2, cx, cy)

        # Compute additional safety margin.
        theta = math.atan2((y2 - y1), (x2 - x1))
        rx = sigma * math.sin(theta) + x0
        ry = -sigma * math.cos(theta) + y0
        rz = 0

        rho = np.array((rx, ry, rz))

        # Adjust vertices.
        # new = original + rho

        # Perform tilt.
        # new = self.tilt_body(new, air, 0.0)

        # Compute bias.
        # bias = new - original

        return rho

    def adjust_trot(self, off, next_frame):
        """
        Adjust the center of mass for the crawl gait.
        :param off: An array defining which legs are in the air.
        :param next_frame: An array representing the next frame (4 x 3).
        """

        # Get the leg on the ground.
        legs = np.where(~off)[0]

        # Relative to absolute.
        original = next_frame + self.vertices

        # Get points.
        p = original[legs]
        x1, y1, z1 = p[0]
        x2, y2, z2 = p[1]

        # Compute center of mass as with leg positions.
        cx, cy = self.get_com(original)

        # Get closest point from center of mass to support.
        x0, y0 = self.closest(x1, x2, y1, y2, cx, cy)

        # Compute bias.
        rx = x0 - cx
        ry = y0 - cy
        rz = 0

        rho = np.array((rx, ry, rz))

        return rho

    def adjust(self, off, next_frame, count=None):
        """
        Adjust the center of mass.
        :param off: An array indicating whether the leg is in the air.
        :param next_frame: The next frame.
        :param count: The number of legs in the air.
        :return: The bias.
        """

        # Check which (if any) optimization is needed.
        if count is None:
            count = np.count_nonzero(off)

        if count == 1:
            # Crawl gait.
            return self.adjust_crawl(off, next_frame)
        elif count == 2 and off[1] == off[2]:
            # Trot gait.
            return self.adjust_trot(off, next_frame)
        else:
            return self.default_bias(next_frame)

    def translate(self, x, y, z):
        """
        Translate the body and thus the center of mass.
        :param x: Motion along x.
        :param y: Motion along y.
        :param z: Motion along z.
        :return: Bias.
        """

        t = np.array((x, y, z), dtype=float)
        bias = np.array((self.cx, self.cy, 0), dtype=float) + t

        return bias

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

    def target_point(self, point):
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
            logger.error('Leg {} is unable to reach point ({:.2f}, {:.2f}, {:.2f})'.format(self.index, *point))
            return False

        return True

    def target_angle(self, angle):
        """
        Target an angle configuration.
        :param angle: (theta1, theta2, theta3).
        :return: True if target is reachable, else False.
        """
        try:
            self.servos[0].set_target(angle[0])
            self.servos[1].set_target(angle[1])
            self.servos[2].set_target(angle[2])
        except ServoError:
            logger.error('Leg {} is unable to reach angle ({:.2f}, {:.2f}, {:.2f})'.format(self.index, *angle))
            return False

        return True

    def get_angles(self, point):
        """
        Convert a point to angles. Will throw exceptions.
        :param point: (x, y, z).
        :return: The angles.
        """

        return self.ik_solver(self.lengths, point)

    def get_position(self):
        """
        Compute current leg position based on servo data.
        """

        a = self.servos[0].get_position()
        b = self.servos[1].get_position()
        c = self.servos[2].get_position()

        self.position = self.fk_solver(self.lengths, (a, b, c))

        return self.position

    def __getitem__(self, key):
        return self.servos[key]

    def __add__(self, other):
        return self.servos + other.servos

    def __radd__(self, other):
        return other + self.servos

    def __len__(self):
        return len(self.servos)


class Head:
    def __init__(self, servo1, servo2, camera):
        """
        Create a head object.
        :param servo1: Servo object controlling left and right head turns.
        :param servo2: Servo object controlling up and down head turns.
        :param camera: A camera object for configuration.
        """

        self.servos = [servo1, servo2]
        self.camera = camera

        self.angles = [0, 0]
        self.target = [0, 0]

    def at_bound(self):
        """
        Check if the head is at the left or right bound.
        :return: 1 -> left bound, -1 -> right bound, 0 -> not at bound.
        """

        servo = self.servos[0]
        low, high = servo.get_range()
        position = servo.get_position()

        # Within one 0.2 degrees is "there".
        if abs(position - high) < 0.2:
            return 1
        elif abs(position - low) < 0.2:
            return -1
        else:
            return 0

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
        Note that this is an approximation. Best used in a PID loop.
        :param x: x-coordinate of target.
        :param y: y-coordinate of target.
        """

        head = self.robot.head
        camera = head.camera

        # Define velocity constant.
        k = 1.5

        # Compute deltas.
        dx = (x - 0.5 * camera.width) * -1
        dy = (y - 0.5 * camera.height) * -1

        dt = dx / camera.width * (camera.fx / 2)
        dp = dy / camera.height * (camera.fy / 2)

        # Compute suggested velocity. Balance between blur and speed.
        vt = int(round(abs(dt * k)))
        vp = int(round(abs(dt * k)))

        # Construct array.
        data = [dt, vt, dp, vp]

        # Perform motion.
        self.move_head(data)

        # Update target.
        head.target = [x, y]

    def scan(self, t, direction=None):
        """
        Scans head in a direction. If no direction is given, scans toward bound of last known location.
        If at minimum of maximum bounds, automatically selects opposite direction.
        Blocks until completely scanned towards one direction.
        :param t: Time in milliseconds.
        :param direction: A direction, either None, 1, or -1.
        """

        # Obtain definitions.
        head = self.robot.head
        camera = head.camera
        servo = head.servos[0]

        # Get bounds.
        low, high = servo.get_range()

        # Update servo.
        self.maestro.get_position(servo)

        # Check bound.
        bound = head.at_bound()

        # Create direction.
        if bound != 0:
            direction = bound * -1

        if direction is None:
            if head.target[0] < 0.5 * camera.width:
                direction = 1
            else:
                direction = -1

        # Execute.
        if direction == 1:
            servo.set_target(high)
        else:
            servo.set_target(low)

        self.maestro.end_in(servo, t)
        self.wait(servo)

    def center_head(self, t=0):
        """
        Returns head to original position.
        :param t: The time in ms.
        """

        # Obtain definitions.
        head = self.robot.head
        servos = head.servos

        # Target zero.
        for servo in servos:
            servo.set_target(0)

        # Reset to zero.
        head.angles = [0, 0]

        # Execute.
        self.maestro.end_together(servos, t, True)
        self.wait(servos)

    def move_head(self, data):
        """
        Move head based on data parameters. Does not wait for completion.
        :param data: An array given by look_at.
        """

        # Obtain definitions.
        head = self.robot.head
        servos = head.servos

        # Update positions.
        self.maestro.get_multiple_positions(servos)

        for i in range(2):
            servo = head[i]
            current = servo.get_position()

            # Get data.
            delta = data[i * 2]
            velocity = data[i * 2 + 1]

            if velocity == 0:
                # Already at target. Do nothing.
                servo.target = servo.pwm
                target = current
            else:
                # Ensure that head is within bounds.
                low, high = servo.get_range()
                target = current + delta

                if target < low:
                    target = low
                elif target > high:
                    target = high

                servo.set_target(target)

            # Update.
            head.angles[i] = target

            # Set speed.
            self.maestro.set_speed(servo, velocity)

        # Execute.
        self.maestro.set_target(servos)

    @staticmethod
    def plot_gait(frames):
        """
        Plot a gait given some frames. Used for debugging.
        :param frames: Frames generated by execute.
        """

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

    def execute_forever(self, frames, dt):
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
                    legs[i].target_point(frame[i])

                self.maestro.end_together(servos, dt)
                self.wait(servos)

    def execute_frames(self, frames, dt):
        # Get all legs and servos for quick access.
        legs = self.robot.legs
        servos = self.robot.leg_servos

        # Update initial leg locations.
        self.maestro.get_multiple_positions(servos)

        for frame in frames:
            for i in range(len(legs)):
                legs[i].target_point(frame[i])

            self.maestro.end_together(servos, dt)
            self.wait(servos)

    def execute_angles(self, angles, dt):
        # Get all legs and servos for quick access.
        legs = self.robot.legs
        servos = self.robot.leg_servos

        # Update initial leg locations.
        self.maestro.get_multiple_positions(servos)

        for angle in angles:
            for i in range(len(legs)):
                legs[i].target_angle(angle)

            self.maestro.end_together(servos, dt)
            self.wait(servos)

    def anglify(self, frames):
        """
        Converts frames generated by self.prepare to angles.
        :param frames: The input frames.
        :return: The output angles ready for execution.
        """

        # Get all legs and servos for quick access.
        legs = self.robot.legs

        # Allocate memory.
        angles = np.empty(frames.shape)

        for i in range(len(frames)):
            for l in range(len(legs)):
                a = legs[l].get_angles(frames[i][l])
                angles[i][l] = a

        return angles

    @staticmethod
    def smooth(a, b, n):
        """
        Create a smooth transition from a to b in n steps.
        :param a: The first array.
        :param b: The second array.
        :param n: The number of steps.
        :return: An array from [a, b).
        """

        assert(a.shape == b.shape)
        assert(n > 1)

        # Compute delta.
        delta = (b - a) / n

        # Allocate n-1 with dimension d+1.
        shape = (n, *a.shape)
        inter = np.empty(shape)

        for i in range(n):
            inter[i] = a + i * delta

        return inter

    def get_pose(self):
        """
        Get the relative pose of the robot.
        :return: A (4 x 3) matrix representing the current state of the robot.
        """

        # Get all legs for quick access.
        legs = self.robot.legs

        # Iterate through all legs.
        pose = []
        for leg in legs:
            position = leg.get_position()
            pose.append(position)

        return np.array(pose, dtype=float)

    @staticmethod
    def linearize(frames):
        """
        Given frames, compute t based on linear distance.
        :param frames: Frames of [(x1, y1, z1), ...]
        :return: Times (for scipy interpolation).
        """

        delta = np.roll(frames, -1, axis=0) - frames
        dst = np.linalg.norm(delta, axis=1)[:-1]

        t = dst / np.sum(dst) * 1000
        t = np.insert(t, 0, (0,))
        t = np.cumsum(t)

        return t

    def prepare_lift(self, index, target, lift, t):
        """
        Get the leg from a to b by lifting.
        From the current position, lift leg. Move to target, then adjust z.
        :param index: The leg index.
        :param target: The target point.
        :param lift: How much to lift.
        :param t: The time in milliseconds.
        :return: (frames, dt)
        """

        # Get all legs and servos for quick access.
        legs = self.robot.legs
        servos = self.robot.leg_servos

        # Update positions.
        self.maestro.get_multiple_positions(servos)

        # Get pose of all legs.
        pose = self.get_pose()

        # Get "ground".
        ground = np.min(pose[:, 2])

        # Compute steps.
        steps = int(round(t / 50))
        if steps > 100:
            steps = 100
        elif steps < 20:
            steps = 20

        # Compute dt.
        dt = t / steps

        # Construct array.
        x, y, z = pose[index]
        tx, ty, tz = target

        p0 = (x, y, z)
        p1 = (x, y, z + lift)
        p2 = (tx, ty, z + lift)
        p3 = (tx, ty, tz)

        frames = np.array((p0, p1, p2, p3), dtype=float)

        # Linearize.
        times = self.linearize(frames)

        # Interpolate.
        ts = np.linspace(0, 1000, num=steps + 1, endpoint=True)
        tck, _ = interpolate.splprep(frames.T, u=times, s=0, k=1)
        p = np.array(interpolate.splev(ts, tck))
        p = p.T

        # Fill in non-motion frames.
        f = [None] * 4
        f[index] = p

        for i in range(4):
            if i != index:
                l = pose[i].reshape((1, 3))
                f[i] = np.repeat(l, steps + 1, axis=0)

        frames = np.concatenate(f).reshape((steps + 1, 4, 3), order='F')

        return self.prepare_frames(frames, dt, ground)

    def prepare_frames(self, frames, dt, ground):
        """
        Prepare some frames which are non-circular (last frame not linked to first frame).
        :param frames: The input frames.
        :param dt: dt.
        :param ground: Ground.
        :param loop: Whether the gait loops.
        :return: (frames, dt) ready for execution.
        """

        # Define body for quick access.
        body = self.robot.body

        # Create array for biases.
        biases = np.empty(frames.shape)

        # Generate leg state arrays.
        state1 = np.greater(frames[:, :, 2], (ground + 1e-6))     # Defines which legs are in the air.
        state2 = state1.sum(1)                                      # The number of legs in the air.

        # Define.
        steps = len(frames)

        for t in range(steps - 1):
            # Look ahead and pass data to center of mass adjustment algorithms.
            next_frame = frames[t]

            # Determine which legs are off.
            off = state1[t]
            count = state2[t]

            # Perform center of mass adjustments accordingly.
            biases[t] = body.adjust(off, next_frame, count)

        # Adjust frames.
        frames -= biases

        return frames, dt

    def prepare_gait(self, gait, debug=False):
        """
        Prepare a given gait class.
        :param gait: The gait class.
        :param debug: Show gait in a graph.
        :return: (frames, dt) ready for execution.
        """

        # Define body for quick access.
        body = self.robot.body

        # Get gait properties.
        steps = gait.steps
        ground = gait.ground
        dt = gait.time / steps
        ts = np.linspace(0, 1000, num=steps, endpoint=False)

        # Get all legs for quick access.
        legs = self.robot.legs

        # Compute shape.
        shape = (steps, len(legs), 3)

        # Evaluate gait.
        f = [gait.evaluate(leg, ts) for leg in legs]
        frames = np.concatenate(f).reshape(shape, order='F')

        # Debugging.
        if debug:
            self.plot_gait(frames)

        # Create array for biases.
        biases = np.empty(shape)

        # Generate leg state arrays.
        state1 = np.greater(biases[:, :, 2], (ground + 1e-6))     # Defines which legs are in the air.
        state2 = state1.sum(1)                                      # The number of legs in the air.

        # Iterate and perform static analysis.
        for t in range(steps):
            # Look ahead and pass data to center of mass adjustment algorithms.
            next_frame = frames[(t + 1) % steps]

            # Determine which legs are off.
            off = state1[t]
            count = state2[t]

            # Perform center of mass adjustments accordingly.
            biases[t] = body.adjust(off, next_frame, count)

        # Adjust frames.
        frames -= biases

        return frames, dt

    def prepare_smoothly(self, gait):
        """
        Prepare a gait by intelligently applying smoothing. Only works for planar COM adjustments.
        Plus, who doesn't like smooth things? (I'm really tired right now.)
        :param gait: The gait object.
        :return: (frames, dt) ready for execution.
        """

        # Define body for quick access.
        body = self.robot.body

        # Get gait properties.
        steps = gait.steps
        ground = gait.ground
        dt = gait.time / steps
        ts = np.linspace(0, 1000, num=steps, endpoint=False)

        # Get all legs for quick access.
        legs = self.robot.legs

        # Compute shape.
        shape = (steps, len(legs), 3)

        # Evaluate gait.
        f = [gait.evaluate(leg, ts) for leg in legs]
        frames = np.concatenate(f).reshape(shape, order='F')

        # Generate leg state arrays.
        state1 = np.greater(frames[:, :, 2], (ground + 1e-6))  # Defines which legs are in the air.
        state2 = state1.sum(1)  # The number of legs in the air.

        # Get indices of legs in air.
        air = np.where(state2 != 0)[0]
        air = air.tolist()

        # Create array for biases.
        biases = np.empty(shape)

        # Keep track of last air -> ground.
        t = air[-1]
        if state2[(t + 1) % steps] == 0:
            # Last air frame is an air -> ground transition.
            last_ag = t
        else:
            # There will
            last_ag = None

        # Compute biases for each frame that is not on the ground.
        for i in range(len(air)):
            # Get the index relative to all frames.
            t = air[i]

            # Compute bias as usual.
            next_frame = frames[(t + 1) % steps]
            off = state1[t]
            count = state2[t]

            biases[t] = body.adjust(off, next_frame, count)

            # Checks if the current frame represents a ground -> air transition.
            if state2[t - 1] == 0:
                curr_bias = biases[t]
                prev_bias = biases[last_ag]

                # Smooth from [t, last_ag).
                if t > last_ag:
                    n = t - last_ag
                    inter = self.smooth(prev_bias, curr_bias, n)
                    biases[last_ag:t] = inter
                else:
                    n = steps - last_ag + t
                    inter = self.smooth(prev_bias, curr_bias, n)
                    biases[last_ag:] = inter[:(steps - last_ag)]
                    biases[:t] = inter[(steps - last_ag):]

            # Check if the current frame represents an air -> ground transition.
            if state2[(t + 1) % steps] == 0:
                last_ag = t

        # Adjust frames.
        frames -= biases

        return frames, dt

    def move_body(self, x, y, z, t=0):
        legs = self.robot.legs
        servos = self.robot.leg_servos

        self.maestro.get_multiple_positions(servos)

        for leg in legs:
            a, b, c = leg.get_position()
            a -= x
            b -= y
            c -= z
            self.target_euclidean(leg, (-x, -y, -sum(leg.lengths) - z))

        self.maestro.end_together(servos, t)
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

        settings = self.usc.getUscSettings()
        settings.serialMode = uscSerialMode.SERIAL_MODE_USB_DUAL_PORT

        for leg in self.robot.legs:
            for servo in leg:
                servo.zero()
                channel = settings.channelSettings[servo.channel]
                channel.mode = ChannelMode.Servo
                channel.homeMode = HomeMode.Goto
                channel.home = servo.target
                channel.minimum = (servo.min_pwm // 64) * 64
                channel.maximum = -(-servo.max_pwm // 64) * 64

        for servo in self.robot.head:
            servo.zero()
            channel = settings.channelSettings[servo.channel]
            channel.mode = ChannelMode.Servo
            channel.homeMode = HomeMode.Goto
            channel.home = servo.target
            channel.minimum = (servo.min_pwm // 64) * 64
            channel.maximum = -(-servo.max_pwm // 64) * 64

        self.usc.setUscSettings(settings, False)
        self.usc.reinitialize(500)

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
        :param servos: One or more servo objects. If None, checks if all servos have reached their targets (more efficient).
        :return: True if all servos are at their targets, False otherwise.
        """

        if servos is None:
            return not self.maestro.get_moving_state()
        elif isinstance(servos, Servo):
            self.maestro.get_position(servos)

            if servos.at_target():
                return True

            return False
        else:
            self.maestro.get_multiple_positions(servos)

            if all(servo.at_target() for servo in servos):
                return True

            return False

