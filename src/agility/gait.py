from scipy import interpolate
import numpy as np
from functools import partial
import math


class Gait:
    def __init__(self, ground, time, steps):
        # Define the ground (z-axis). Usually a negative float.
        # This helps Agility determine when center of mass should be shifted.
        self.ground = ground

        # The amount of time the gait should last in ms.
        # Gait is guaranteed to be at least this long. However actual gait will be longer.
        self.time = time

        # The number of optimal steps.
        self.steps = steps

    def evaluate(self, leg, t):
        """
        Evaluate a leg position at times t.
        :param leg: A leg object.
        :param t: An array containing t values to be evaluated where t is in [0, 1000).
        :return: An array or points.

        Return value is in the following format:
        [
         [x0, y0, z0],
         [x1, y1, z1],
         [x2, y2, z2],
         ...
        ]
        """

        raise NotImplementedError


class Linear(Gait):
    def __init__(self, sequence, ground, time, steps):
        """
        A sequence of key frames.
        :param sequence: A sequence of points and times.

        Sequence is in the following format:
        [
         [(x0, y0, z0, t0), (x1, y1, z1, t1), ...],
         [(x0, y0, z0, t0), (x1, y1, z1, t1), ...],
         [(x0, y0, z0, t0), (x1, y1, z1, t1), ...],
         [(x0, y0, z0, t0), (x1, y1, z1, t1), ...]
        ]
        """

        super().__init__(ground, time, steps)

        # Generate private functions called during evaluation.
        self._fn = [self.interpolate(s) for s in sequence]
        assert len(self._fn) == 4

    @staticmethod
    def interpolate(sequence):
        """
        Create parametric functions given a sequence of points.
        :param sequence: A numpy sequence of points.
        :return: A function to interpolate points at times t.
        """

        # Boundary constraints.
        t = sequence[:, 3]
        t[t < 0] += 1000
        t[t > 1000] -= 1000

        # Sort.
        sequence = sequence[t.argsort()]

        # Create padding.
        first = sequence[0]
        last = sequence[-1]

        if first[3] > 0:
            value = last.copy()
            value[3] -= 1000
            sequence = np.vstack((value, sequence))

        if last[3] < 1000:
            value = first.copy()
            value[3] += 1000
            sequence = np.vstack((sequence, value))

        # Unravel.
        p = sequence[:, :3]
        t = sequence[:, 3]

        # Unique time assertion.
        assert np.array_equiv(np.unique(t), t)

        # Interpolate.
        tck, _ = interpolate.splprep(p.T, u=t, s=0, k=1)
        return partial(interpolate.splev, tck=tck)

    def evaluate(self, leg, t):
        index = leg.index
        fn = self._fn[index]
        p = np.array(fn(t))

        return p.T


class Dynamic:
    def __init__(self, body):
        self.body = body

        # General constants.
        self.b = np.array((body.width, body.length), dtype=float)
        self.n = np.array((
            (-1 , 1),
            (1, 1),
            (-1, -1),
            (1, -1)
        ))

        # Generation constants.
        self.j0 = 2                 # Transition from slow forward to fast forward.
        self.j1 = math.radians(10)  # Transition from slow rotation to fast rotation.

        self.ground = -13           # The ground plane.
        self.lift = 2               # How much to lift each leg.
        self.beta_crawl = 0.825     # Beta value for crawl gait.
        self.beta_trot = 0.800      # Beta value for trot gait.
        self.t = 2                  # Maximum cycle time.
        self.transition = 5         # Velocity at which to transition from crawl to trot.

        self.max_steps = 100        # Maximum number of dt steps.
        self.min_steps = 20         # Minimum number of dt steps.

        # Rotation constants.
        self.r = self.b / np.linalg.norm(self.b)
        self.k = 0.5 * np.linalg.norm(self.b)

        # Offset constants.
        self.gait_offset = {
            '1243': [0, 250, 750, 500],
            '1423': [0, 500, 750, 250],
            '1234': [0, 250, 500, 750],
            '1342': [0, 750, 250, 500],
            '1324': [0, 500, 250, 750],
            '1432': [0, 750, 500, 250],
            'trot': [0, 500, 500, 0]
        }

    def generate(self, forward, rotation):
        """
        Generate a gait.
        :param forward: Forward speed in cm/second.
        :param rotation: Rotation speed in radians/second.
        :return: A Linear object.
        """

        # Check for no solution.
        assert not (forward == 0 and rotation == 0)

        # Check which type of gait to use.
        if abs(forward) >= self.transition:
            # Use trot.
            offset = 'trot'
            beta = self.beta_trot
        else:
            # Use crawl.
            offset = '1423'
            beta = self.beta_crawl

        # Create t decision array.
        t = [0, 0]

        # Compute parameters here. It is all Alastair's fault.
        if abs(forward) <= self.j0:
            t[0] = self.t
        else:
            t[0] = self.t * self.j0 / abs(forward)

        if abs(rotation) <= self.j1:
            t[1] = self.t
        else:
            t[1] = self.t * self.j1 / abs(rotation)

        # Pick lower t. Minimize size.
        t = min(t)

        # Convert /second to /cycle.
        v = forward * t
        theta = rotation * t

        # Convert t to milliseconds.
        t *= 1000

        # Compute steps. 50 Hz maximum.
        steps = round(int(t / 20))

        if steps > self.max_steps:
            steps = self.max_steps
        elif steps < self.min_steps:
            steps = self.min_steps

        # Generate sequence.
        sequence = self.get(theta, v, beta, self.ground, self.lift, offset)
        sequence = np.array(sequence, dtype=float)

        # Create object and add to cache.
        gait = Linear(sequence, self.ground, t, steps)

        return gait

    def get(self, theta, v, beta, ground, lift, offset):
        """
        Get a sequence. If none exists in cache, generate it.
        :param theta: Rotation (radian/iteration).
        :param v: Forward (cm/iteration).
        :param beta: Amount of time that the leg is on the ground.
        :param ground: Ground plane. Usually negative z.
        :param lift: How much to lift the leg on return.
        :param offset: Offset order. (Gait pattern).
        :return: A sequence to pass into Linear.
        """

        # Compute air and ground times.
        at = (1 - beta) * 1000
        gt = beta * 1000

        # Forward motion is half on each side.
        v /= 2

        # Get offset.
        offset = self.gait_offset[offset]

        # Create empty sequence.
        sequence = []

        # Iterate and generate.
        for i in range(4):
            # Compute offset.
            o = offset[i]

            # Compute rotation.
            x, y = self.n[i] * math.tan(0.5 * theta) * self.k * self.r

            # Add in linear motion.
            x += v

            # Generate times.
            mag = (x**2 + y**2)**(1/2) * 2
            unit = at / (mag + 2 * lift)

            t0 = 0
            t1 = gt / 2
            t2 = t1 + unit * lift
            t3 = t2 + unit * mag
            t4 = 1000 - t1

            # Generate points.
            p0 = (0, 0, ground, t0 + o)

            p1 = (-x, -y, ground, t1 + o)
            p2 = (-x, -y, ground + lift, t2 + o)
            p3 = (x, y, ground + lift, t3 + o)
            p4 = (x, y, ground, t4 + o)

            # Create and add sequence.
            s = (p0, p1, p2, p3, p4)
            sequence.append(s)

        return sequence
