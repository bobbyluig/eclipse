from numpy.linalg import norm
from math import sin, cos, asin, acos, atan2, pi, degrees


class Finesse:
    @staticmethod
    def inverse_pack(lengths, target, a2=False, a3=False, deg=True):
        """
        Computes the inverse kinematics for the legs of Amadeus and Mozart.
        :param lengths: An array of lengths (l1, l2, l3, l5).
        :param target: The coordinate of the target (x, y, z).
        :param deg: Return the result in degrees if True and radians otherwise.
        :return: (theta1, theta2, theta3)
        """

        if lengths is None or target is None:
            return None

        dist = norm(target)

        if dist > sum(lengths):
            return None

        l1, l2, l3, l5 = lengths
        x, y, z = target

        z += l5

        try:
            li = ((x ** 2 + y ** 2) ** 0.5) - l1
            l4 = (z ** 2 + li ** 2) ** 0.5

            theta1 = -atan2(y, x)
            theta4 = atan2(li, -z)
            theta5 = acos((l4 ** 2 + l2 ** 2 - l3 ** 2) / (2 * l4 * l2))
            theta2 = (pi / 2) - (theta5 + theta4)
            theta3 = pi - acos((l2 ** 2 + l3 ** 2 - l4 ** 2) / (2 * l2 * l3))
        except (ValueError, ZeroDivisionError):
            return None

        if deg:
            return degrees(theta1), degrees(theta2), degrees(theta3)
        else:
            return theta1, theta2, theta3

    @staticmethod
    def forward_pack(lengths, angles):
        """
        Computes the forward kinematics for the legs of Amadeus and Mozart.
        :param lengths: An array of lengths (l1, l2, l3).
        :param angles: An array of angles (theta1, theta2, theta3).
        :return (x, y, z)
        """

        t1, t2, t3 = angles
        l1, l2, l3 = lengths
        i1 = (l2 * cos(t2)) + (l3 * cos(t2 + t3))
        x = (i1 + l1) * cos(t1)
        y = (i1 + l1) * sin(t1)
        z = (l2 * sin(t2)) + (l3 * sin(t2 + t3))

        return x, y, z
