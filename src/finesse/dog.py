import numpy as np
from math import *


def forward(lengths, angles):
    l1, l2 = lengths
    theta1, theta2, theta3 = angles

    x1, y1, z1 = 0, 0, 0

    x2 = l1 * sin(theta1) * cos(theta2)
    y2 = -l1 * sin(theta2)
    z2 = -l1 * cos(theta1) * cos(theta2)

    x3 = x2 + l2 * cos(theta1) * sin(theta3) + l2 * cos(theta2) * cos(theta3) * sin(theta1)
    y3 = y2 - l2 * cos(theta3) * sin(theta2)
    z3 = z2 + l2 * sin(theta1) * sin(theta3) - l2 * cos(theta1) * cos(theta2) * cos(theta3)

    return (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)


def inverse(lengths, target, deg=True):
    l1, l2 = lengths
    x, y, z = target
    dist = np.linalg.norm(target)

    if dist > sum(lengths):
        return None

    # theta3 *= -1
    # Returns [0, 180]. +/- expands solution to [-180, 180].
    try:
        theta3 = (l1**2 + l2**2 - dist**2) / (2 * l1 * l2)
        theta3 = pi - acos(theta3)
    except (ValueError, ZeroDivisionError):
        return None

    # theta2 = (pi - theta2)
    # Returns [-90, 90]. (pi - theta2) expands solution to [-180, 180].
    try:
        theta2 = -y / (l1 + l2 * cos(theta3))
        theta2 = asin(theta2)
    except (ValueError, ZeroDivisionError):
        return None

    # theta1 += 2 * pi
    # Sometimes (2 * pi + theta1). Doesn't matter. Either is cool.
    try:
        theta1 = atan2(z, x) - atan2((-l1 - l2 * cos(theta3)) * cos(theta2), l2 * sin(theta3))
    except (ValueError, ZeroDivisionError):
        return None

    if deg:
        return degrees(theta1), degrees(theta2), degrees(theta3)
    else:
        return theta1, theta2, theta3


def fixingOtherPeoplesProblems(lengths, target, deg=True):
    l1, l2, l3 = lengths
    x, y ,z = target
    dist = np.linalg.norm(target)

    if dist > sum(lengths):
        return None

    theta4 = atan(l1 / l2)
    theta3 = (l1**2 + l2**2 + l3**2 - dist**2) / (2 * (l1**2 + l2**2)**(1/2) * l3**2)
    theta3 = acos(theta3)
    theta3 = pi - (theta3 - theta4)
    print


fixingOtherPeoplesProblems((1, 7.5, 7.5), (8.5, 0, -7.5))