#!/usr/bin/env python3.5

from shared.finesse.helper import *
import time, sys
import copy

__author__ = 'Lujing Cen'
__copyright__ = 'Copyright (c) 2015-2016 Eclipse Technologies'

EPSILON = sys.float_info.epsilon

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


def ssa(a, b, A):
    sinB = math.sin(A) * b / a
    if abs(sinB - 1) < 100 * EPSILON:
        # Right triangle. Solution is unique.
        B = math.pi / 2
    else:
        B = math.asin(sinB)

    return B


class EndEffector:
    def __init__(self, point):
        self.point = np.asarray(point)
        self.length = 0

    @staticmethod
    def get_angle(self):
        return 0

    def update(self, suggestion, joints):
        self.point = suggestion
        return

    def update_angle(self, joints):
        return


class Hip:
    def __init__(self, point, length, yaw, roll, constraints=None):
        self.point = np.asarray(point)
        self.length = length
        self.yaw = yaw
        self.roll = roll
        self.constraints = constraints

    def update(self, suggestion, joints):
        self.point = suggestion

        if self.constraints is not None:
            self.update_angle(joints)

    def update_angle(self, joints):
        v = joints[1].point - self.point
        self.yaw = math.atan2(v[0], -v[2])


class Knee:
    def __init__(self, point, length, angle, constraints=None):
        self.point = np.asarray(point)
        self.length = length
        self.angle = angle
        self.constraints = constraints

    def update(self, suggestion, joints):
        self.point = suggestion

        if self.constraints is not None:
            self.update_angle(joints)

    def update_angle(self, joints):
        v = self.point - joints[0].point
        joints[0].yaw = math.atan2(v[0], -v[2])
        # self.angle = signed_angle(joints[2].point - self.point, self.point - joints[0].point, _AXES['y'])
        self.angle = signed_angle2d(joints[2].point - self.point, self.point - joints[0].point)


def fabrik(joints, target, tolerance):
    # Singularity protection.
    target = np.asarray(target, dtype=float)
    # target[target == 0] = 1e-10

    # The distance between root and target.
    dist = np.linalg.norm(joints[0].point - target)

    # Rotate all effectors to xz plane.
    q1 = quaternion(_AXES['x'], -joints[0].roll)
    joints[1].point = np.dot(joints[1].point, q1)
    joints[2].point = np.dot(joints[2].point, q1)

    # Rotate target to xz plane.
    roll = -math.atan2(target[2], target[1]) - math.pi/2
    q2 = quaternion(_AXES['x'], -roll)
    target = np.dot(target, q2)
    # print('Roll:', np.degrees(roll))

    # Define the normal plane.
    n = np.array([0, 1, 0])

    # Set roll.
    joints[0].roll = roll

    # print('New points:', [x.point for x in joints])
    # print('New target:', target)

    # Check if target is within reach.
    if dist > sum(j.length for j in joints):
        # Target is unreachable.
        print('Target is unreachable!', dist)

        for i in range(len(joints) - 1):
            # Find the distance r, between the target t and the joint position p_i.
            r = np.linalg.norm(target - joints[i].point)
            delta = joints[i].length / r

            # Find the new joint positions p_i.
            joints[i+1].point = (1 - delta) * joints[i].point + delta * target
    else:
        # The target is reachable; thus, set as b the initial position of the joint p_i.
        b = np.copy(joints[0].point)

        # Check whether the distance between the end effector pn and the target t is greater than a tolerance.
        dif = np.linalg.norm(joints[-1].point - target)

        while dif > tolerance:
            # print('Forward Stage.')
            # STAGE 1: FORWARD REACHING.
            # Set the end effector p_n as target t.
            joints[-1].point = target

            for i in reversed(range(len(joints) - 1)):
                # Find the distance ri between the new joint position p_i+1 and the joint p_i.
                r = np.linalg.norm(joints[i+1].point - joints[i].point)
                delta = joints[i].length / r

                # Find the new joint position p_i. Suggest the point to the joint.
                suggestion = (1 - delta) * joints[i+1].point + delta * joints[i].point
                joints[i].update(suggestion, joints)

            # print('Backward Stage.')
            # STAGE 2: BACKWARD REACHING.
            # Set the root p_1 its initial position.
            joints[0].point = np.copy(b)

            for i in range(len(joints) - 1):
                # Find the distance ri between the new joint position p_i and the joint p_i+1.
                r = np.linalg.norm(joints[i+1].point - joints[i].point)
                delta = joints[i].length / r

                # Find the new joint positions p_i+1. Suggest the point to the joint.
                suggestion = (1 - delta) * joints[i].point + delta * joints[i+1].point
                joints[i+1].update(suggestion, joints)

            dif = np.linalg.norm(joints[-1].point - target)

    # print([x.point for x in joints])

    for j in joints:
        j.update_angle(joints)

    # Roll all joints back to target plane.
    q = quaternion(_AXES['x'], joints[0].roll)
    joints[1].point = np.dot(joints[1].point, q)
    joints[2].point = np.dot(joints[2].point, q)

    # print([x.point for x in joints])

    return [joints[0].yaw, joints[0].roll, joints[1].angle]


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


hip = Hip([0, 0, 0], 7, 0, 0)
knee = Knee([0, 0, -7], 12, 0)
end = EndEffector([0, 0, -19])
joints = [hip, knee, end]

target = [5, 3, -3]
fab = fabrik(joints, target, 1e-5)
print(fab)
f = forward_kinematics([7, 12], [fab[0], fab[1], fab[2]])

error = np.linalg.norm(np.array(target) - f[2])
print('Error:', error)

# Revert
target = [10, 3, -3]
joints = [hip, knee, end]
fab = fabrik(joints, target, 1e-5)

f = forward_kinematics([7, 12], [fab[0], fab[1], fab[2]])

error = np.linalg.norm(np.array(target) - f[2])
print('Error:', error)



