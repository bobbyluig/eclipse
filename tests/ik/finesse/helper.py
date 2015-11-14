import math
import numpy as np
from numba import jit

_PLANES = {
    'xy': np.array([0, 0, 1]),
    'xz': np.array([0, 1, 0]),
    'yz': np.array([1, 0, 0])
}

_AXES = {
    'x': np.array([1, 0, 0]),
    'y': np.array([0, 1, 0]),
    'z': np.array([0, 0, 1])
}


def euler_single(a, plane):
    p = _PLANES[plane]
    return math.asin(np.dot(a, p) / (np.linalg.norm(a) * np.linalg.norm(p)))


def quaternion(axis, theta):
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2)
    b, c, d = -axis*math.sin(theta/2)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])


def rotate(v, axis, theta):
    axis = _AXES[axis]
    q = quaternion(axis, theta)
    return np.dot(v, q)


def signed_angle(a, b, n):
    cross = np.cross(a, b)
    ang = np.arctan2(np.linalg.norm(cross), np.dot(a, b))

    if np.dot(n, cross) < 0:
        ang = -ang

    return ang


def signed_angle2d(a, b):
    return math.atan2(-b[2], b[0]) - math.atan2(-a[2], a[0])

def unsigned_angle(a, b):
    return np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))