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

    def num_supports(self):
        """
        Define the minimum number of support legs on ground at all times.
        :return: An integer from 2 to 3.
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
    def __init__(self, sequence):
        """
        A sequence of key frames.
        :param sequence:
        """

    def bulk(self):
        return True


class Crawl(Gait):
    def ground(self):
        return -12

    def num_supports(self):
        return 3

    def time(self):
        return 3000

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
