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


def doggy_crawl(theta, stride, body):
    width = body.width
    length = body.length
    ground = -10

    b = np.array((width, length), dtype=float)

    norm = np.array((
        (1, 1),
        (-1, 1),
        (-1, -1),
        (1, -1)
    ))

    sequence = []

    for i in range(4):
        offset = i * 250
        x, y = theta * b * norm[i]
        x += stride

        s = [
            (0, 0, ground, 0 + offset),
            (-x, -y, ground, 375 + offset),
            (-x, -y, ground + 2, 425 + offset),
            (x, y, ground + 2, 575 + offset),
            (x, y, ground, 625 + offset)
        ]

        sequence.append(s)

    return Linear(sequence, ground, 1000)