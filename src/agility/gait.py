from scipy import interpolate
import numpy as np
from functools import partial


class Gait:
    def __init__(self, ground, time):
        # Define the ground (z-axis). Usually a negative float.
        # This helps Agility determine when center of mass should be shifted.
        self.ground = ground

        # The amount of time the gait should last in ms.
        # Gait is guaranteed to be at least this long. However actual gait will be longer.
        self.time = time

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
    def __init__(self, sequence, ground, time):
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

        super().__init__(ground, time)

        # Generate private functions called during evaluation.
        self._fn = [self.interpolate(s) for s in sequence]
        assert len(self._fn) == 4

    @staticmethod
    def interpolate(sequence):
        """
        Create parametric functions given a sequence of points.
        :param sequence: A sequence of points.
        :return: A function to interpolate points at times t.
        """

        # Create numpy array.
        sequence = np.array(sequence, dtype=float)

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

        # Interpolate.
        tck, _ = interpolate.splprep(p.T, u=t, s=0, k=1)
        return partial(interpolate.splev, tck=tck)

    def evaluate(self, leg, t):
        index = leg.index
        fn = self._fn[index]
        p = np.array(fn(t))

        return p.T


class Crawl:
    def __init__(self, body):
        self.body = body

        # Cache reusable variables.
        self.b = np.array((body.width, body.length), dtype=float)
        self.n = np.array((
            (-1 , 1),
            (1, 1),
            (-1, -1),
            (1, -1)
        ))

        # Cache for gait objects.
        self.cache = {}

    def clear(self):
        """
        Clear the cache.
        """

        self.cache.clear()

    def generate(self, forward, rotation):
        """
        Generate a gait.
        :param forward: Forward speed in cm/second.
        :param rotation: Rotation speed in degrees/second.
        :return: A Linear object.
        """

        # Hash table lookup.
        h = hash((forward, rotation))

        # If gait is in cache, return it.
        if h in self.cache:
            return self.cache[h]

        # Compute parameters here.
        lift = 2
        ground = -10
        time = 1000
        beta = 0.75
        theta = rotation
        v = forward

        # Generate sequence.
        sequence = self.get(theta, v, beta, ground, lift)

        # Create object and add to cache.
        gait = Linear(sequence, ground, time)
        self.cache[h] = gait

        return gait

    def get(self, theta, v, beta, ground, lift):
        """
        Get a sequence. If none exists in cache, generate it.
        :param theta: Rotation motion.
        :param v: Forward motion.
        :param beta: Amount of time that the leg is on the ground.
        :param ground: Ground plane. Usually negative z.
        :param lift: How much to lift the leg on return.
        :return: A sequence to pass into Linear.
        """

        # Ground time of less than 75% is unstable.
        assert beta >= 0.75

        # Compute air and ground times.
        at = (1 - beta) * 1000
        gt = beta * 1000

        # Create empty sequence.
        sequence = []

        # Iterate and generate.
        for i in range(4):
            # Compute offset.
            o = i * 250

            # Compute x and y.
            x, y = theta * self.b * self.n[i]
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