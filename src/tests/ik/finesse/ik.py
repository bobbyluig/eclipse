from shared.finesse.helper import *
import numpy as np
import math, time

__author__ = 'Lujing Cen'
__copyright__ = 'Copyright (c) 2015-2016 Eclipse Technologies'

_AXES = {
    'x': np.array([1, 0, 0]),
    'y': np.array([0, 1, 0]),
    'z': np.array([0, 0, 1])
}


def ik2d(l1, l2, x, y):
    # Compute theta2. There are two solutions.
    t2 = math.acos((x**2 + y**2 - l1**2 - l2**2) / (2 * l1 * l2))
    theta2 = np.array((t2, -t2))

    # Compute theta1.
    xdot = x * (l1 + l2 * np.cos(theta2)) + y * (l2 * np.sin(theta2))
    ydot = y * (l1 + l2 * np.cos(theta2)) - x * (l2 * np.sin(theta2))
    theta1 = np.arctan2(ydot, xdot)

    return theta1, theta2


def fullik(angles, lengths, target, constraints=None, predilection=None):
    target = np.asarray(target, dtype=np.float64)
    dist = np.linalg.norm(target)

    if dist > sum(lengths):
        # Target is unreachable.
        return

    # Rotate target to the xz plane.
    roll = -math.atan2(target[2], target[1]) - math.pi/2
    q2 = quaternion(_AXES['x'], -roll)
    target = np.dot(target, q2)

    theta1, theta2 = ik2d(lengths[0], lengths[1], target[0], target[2])
    theta1 += np.pi/2

    # Apply constraints.
    if constraints is not None:
        c1, c2 = constraints
        c1_index = np.where((theta1 >= c1[0]) & (theta1 <= c1[1]))
        c2_index = np.where((theta2 >= c2[0]) & (theta2 <= c2[1]))

        if len(c1_index) == 1 and len(c2_index) == 1:
            theta1 = theta1[c1_index]
            theta2 = theta2[c2_index]

    # Apply predilection.
    if predilection is not None and len(theta1) > 1 and len(theta2) > 1:
        if predilection == 1:
            c2_index = np.where(theta2 > 0)
            theta1 = theta1[c2_index]
            theta2 = theta2[c2_index]
        else:
            c2_index = np.where(theta2 < 0)
            theta1 = theta1[c2_index]
            theta2 = theta2[c2_index]

    return theta1[0], roll, theta2[0]


def forward(lengths, angles):
    l1 = lengths[0]
    l2 = lengths[1]
    theta1 = angles[0]
    theta2 = angles[1]

    x1 = l1 * math.cos(theta1)
    y1 = l1 * math.sin(theta1)

    x2 = x1 + l2 * math.cos(theta1 + theta2)
    y2 = y1 + l2 * math.sin(theta1 + theta2)

    return np.array((x1, y1)), np.array((x2, y2))


def forward_kinematics(lengths, angles):
    # Set initial points.
    points = [
        np.array([0, 0, 0]),
        np.array([0, 0, -lengths[0]]),
        np.array([0, 0, -lengths[0] + -lengths[1]])
    ]

    # Get angles.
    yaw = angles[0]
    roll = angles[1]

    # Reduction to 2D.
    angle = -math.atan2(points[2][2], points[2][1]) - math.pi/2

    # Roll
    points[1] = rotate(points[1], 'x', roll)
    points[2] = rotate(points[2], 'x', roll)

    # Yaw
    points[1] = rotate(points[1], 'y', yaw)
    points[2] = rotate(points[2], 'y', yaw)

    # Knee
    n = np.array([0, 1, 0])
    n = rotate(n, 'x', roll)
    q = quaternion(n, angles[2])

    points[2] = points[1] + np.dot(points[2] - points[1], q)

    return points


angles = np.array([0, 0, 0])
lengths = np.array([7, 12])
target = np.array([5, 5, 0])
a, b, c = fullik(angles, lengths, target)
print(np.degrees(a), np.degrees(b), np.degrees(c))


f = forward_kinematics(lengths, [a, b, c])
print(f)