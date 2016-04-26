from scipy import interpolate
import numpy as np
from functools import partial


class Gait:
    def ground(self):
        """
        Define the ground (z-axis). Usually a negative float.
        This helps Agility determine when center of mass should be shifted.
        :return: A float representing the ground.
        """

        raise NotImplementedError

    def bulk(self):
        """
        Define if the gait can accept numpy arrays as t values for evaluate.
        :return: True if the gait can, else False.
        """

        raise NotImplementedError

    def time(self):
        """
        The amount of time the gait should last in ms.
        Gait is guaranteed to be at least this long. However actual gait will be longer.
        :return: A float representing the total time for one cycle.
        """

        raise NotImplementedError

    def evaluate(self, leg, t):
        """
        Evaluate a leg position at a time t.
        :param leg: A leg object.
        :param t: The time t, a float such that t is in [0, 100).
        :return: A point (x, y, z).
        """

        raise NotImplementedError


class Linear(Gait):
    def __init__(self, sequence, ground, time):
        """
        A sequence of key frames.
        :param sequence:
        """

        self._ground = ground
        self._time = time

        self._fn = [self.interpolate(s) for s in sequence]

    @staticmethod
    def interpolate(sequence):
        # Sort.
        s = sorted(sequence, key=lambda x: x[1])

        # Fill in edge gaps.
        first = s[0]
        last = s[-1]

        if first[1] > 0:
            s.insert(0, (first[0], 100 - last[1]))

        if last[1] < 100:
            s.append((last[0], 100 + first[1]))

        # Unzip.
        p, t = zip(*sequence)
        p = np.array(p, dtype=float)

        # Interpolate.
        tck, _ = interpolate.splprep(p.T, u=t, s=0, k=1)
        return partial(interpolate.splev, tck=tck)

    def evaluate(self, leg, t):
        index = leg.index
        fn = self._fn[index]
        p = np.array(fn(t))

        return p.T

    def ground(self):
        return self._ground

    def time(self):
        return self._time

    def bulk(self):
        return True


class Generic(Gait):
    def __init__(self, body, speed, rotation, ground):
        self.l = body.length
        self.w = body.width
        self.g = ground
        self.theta = rotation
        self.v = speed

    def ground(self):
        return self.g

    def time(self):
        return 2000

    def bulk(self):
        return True

    def evaluate(self, leg, t):
        if leg.index % 2:
            self.w *= -1

        if leg.index > 1:
            self.l *= -1

        r = self.w ** 2 + self.l ** 2
        w = self.w / r
        l = self.l / r

        


class Crawl(Gait):
    def ground(self):
        return -12

    def time(self):
        return 3000

    def bulk(self):
        return False

    def evaluate(self, leg, t):
        t = (t + 25 * leg.index) % 100

        if t < 5:
            x = -2
            y = 0
            z = -12 + 2 / 5 * t
        elif t < 20:
            x = -2 + 4 / 15 * (t - 5)
            y = 0
            z = -10
        elif t < 25:
            x = 2
            y = 0
            z = -10 - 2 / 5 * (t - 20)
        else:
            x = 2 - 4 / 75 * (t - 25)
            y = 0
            z = -12

        return x, y, z
