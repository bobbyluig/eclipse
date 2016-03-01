from numpy.linalg import norm
from math import sin, cos, asin, acos, atan2, pi, degrees


class Finesse:
    @staticmethod
    def forward_alpha(lengths, angles):
        """
        Computes the forward kinematics for the back legs of Alpha.
        :param lengths: An array of lengths (l1, l2).
        :param angles: An array of angles (theta1, theta2, theta3).
        :return: (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)
        """

        l1, l2 = lengths
        theta1, theta2, theta3 = angles

        x1, y1, z1 = 0, 0, 0

        x2 = -l1 * sin(theta1)
        y2 = 0
        z2 = -l1 * cos(theta1)

        x3 = x2 - l2 * cos(theta1) * cos(theta2) * sin(theta3) - l2 * cos(theta3) * sin(theta1)
        y3 = y2 - l2 * sin(theta2) * sin(theta3)
        z3 = z2 + l2 * sin(theta1) * sin(theta3) * cos(theta2) - l2 * cos(theta1) * cos(theta3)

        return (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)

    @staticmethod
    def forward_dog(lengths, angles):
        """
        Computes the forward kinematics for the legs of DOG.
        :param lengths: An array of lengths (l1, l2).
        :param angles: An array of angles (theta1, theta2, theta3).
        :return: (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)
        """

        l1, l2 = lengths
        theta1, theta2, theta3 = angles

        x1, y1, z1 = 0, 0, 0

        x2 = -l1 * sin(theta1) * cos(theta2)
        y2 = l1 * sin(theta2)
        z2 = -l1 * cos(theta1) * cos(theta2)

        x3 = x2 - l2 * cos(theta1) * sin(theta3) - l2 * cos(theta2) * cos(theta3) * sin(theta1)
        y3 = y2 + l2 * cos(theta3) * sin(theta2)
        z3 = z2 + l2 * sin(theta1) * sin(theta3) - l2 * cos(theta1) * cos(theta2) * cos(theta3)

        return (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)

    @staticmethod
    def inverse(lengths, target, a2=False, a3=False, deg=True):
        """
        Computes the inverse kinematics for the legs of DOG and Alpha
        For the back legs of Alpha, pass 0 for y.
        :param lengths: An array of lengths (l1, l2).
        :param target: The coordinate of the target (x, y, z).
        :param a2: Returns an alternate solution for theta2.
        :param a3: Returns an alternate solution for theta3.
        :param deg: Return the result in degrees if True and radians otherwise.
        :return: (theta1, theta2, theta3)
        """

        if lengths is None or target is None:
            return None

        l1, l2 = lengths
        x, y, z = target
        dist = norm(target)

        if dist > sum(lengths):
            return None

        # theta3 *= -1
        # Returns [0, 180]. +/- expands solution to [-180, 180].
        try:
            theta3 = (l1**2 + l2**2 - dist**2) / (2 * l1 * l2)
            theta3 = acos(theta3) - pi
            if a3:
                theta3 *= -1
        except (ValueError, ZeroDivisionError):
            return None

        # theta2 = (pi - theta2)
        # Returns [-90, 90]. (pi - theta2) expands solution to [-180, 180].
        try:
            theta2 = y / (l1 + l2 * cos(theta3))
            theta2 = asin(theta2)
            if a2:
                theta2 = pi - theta2
        except (ValueError, ZeroDivisionError):
            return None

        # theta1 -= 2 * pi
        # Sometimes (theta1 - 2 * pi). Doesn't matter. Either is cool.
        try:
            theta1 = atan2(z, -x) + atan2((l1 + l2 * cos(theta3)) * cos(theta2), l2 * sin(theta3))
        except (ValueError, ZeroDivisionError):
            return None

        if deg:
            return degrees(theta1), degrees(theta2), degrees(theta3)
        else:
            return theta1, theta2, theta3