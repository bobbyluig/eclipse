class Gait:
    def ground(self):
        """
        Define the ground (z-axis). Usually a negative float.
        This helps Agility determine when center of mass should be shifted.
        :return: A float representing the ground.
        """

        raise NotImplementedError

    def num_supports(self):
        """
        Define the minimum number of support legs on ground at all times.
        :return: An integer from 2 to 3.
        """

        raise NotImplementedError

    def legs(self):
        """
        Define the legs used. Array contains at least one and at most 4 integers from 0-3.
        :return: An array of leg indices.
        """

        raise NotImplementedError

    def time(self):
        """
        The amount of time the gait should last in ms.
        Gait is guaranteed to be at least this long. However actual gait will be longer.
        :return: A float representing the total time for one cycle.
        """

    def evaluate(self, leg, t):
        """
        Evaluate a leg position at a time t.
        :param leg: A leg object.
        :param t: The time t, a float such that t is in [0, 100).
        :return: A point (x, y, z).
        """

        raise NotImplementedError


class LiftLeg(Gait):
    def __init__(self, leg):
        self.lift = leg

    def ground(self):
        return -12

    def num_supports(self):
        return 3

    def time(self):
        return 5000

    def legs(self):
        return [0, 1, 2, 3]

    def evaluate(self, leg, t):
        if t < 25 or t > 75 or leg.index != self.lift:
            return 0, 0, -12
        else:
            return 0, 0, -7
