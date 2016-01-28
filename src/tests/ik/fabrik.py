import numpy as np
import math, time, sys

__author__ = 'Lujing Cen'

EPSILON = sys.float_info.epsilon


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """

    axis /= math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2)
    b, c, d = -axis*math.sin(theta/2)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])


def ssa(a, b, A):
    sinB = math.sin(A) * b / a
    if abs(sinB - 1) < 100 * EPSILON:
        # Right triangle. Solution is unique.
        B = np.pi / 2
    else:
        B = math.asin(sinB)

    return B


class Joint:
    def __init__(self, point, length, angle, constraints, n=None):
        self.point = np.array(point)
        self.length = length
        self.angle = angle
        self.constraints = np.array(constraints) * np.pi / 180
        self.n = n

    def update_angle(self, p0, p2):
        if self.n is None:
            n = np.cross(self.point - p0.point, self.point - p2.point)
            # n /= np.linalg.norm(n)
        else:
            n = self.n

        x = self.point - p0.point
        y = p2.point - self.point

        cross = np.cross(x, y)
        angle = np.arctan2(np.linalg.norm(cross), np.dot(x, y))

        if np.dot(n, cross) < 0:
            angle = -angle

        self.angle = angle
        print('Angle', angle)

        self.constrain(p0, p2, n)

    def constrain(self, p0, p2, n):
        lower = self.constraints[0]
        upper = self.constraints[1]

        if not lower <= self.angle <= upper:
            print('Constraining!')

            # Find the furthest bound to the constraint.
            idx = (np.abs(self.constraints - self.angle)).argmax()
            closest = self.constraints[idx]

            # Find the side lengths of the triangle.
            a = np.linalg.norm(p2.point - p0.point)
            b = self.length
            c = np.linalg.norm(self.point - p0.point)

            print('Points:', self.point, p0.point, p2.point)
            print('Lengths:', a, b, c)

            # Find the only angle that is known.
            A = np.pi - abs(closest)
            print('Target A:', np.degrees(A))

            # Apply what I never learned in Iseri's class. (Law of Cosines)
            cosC = (a**2 + b**2 - c**2) / (2 * a * b)
            C = math.acos(cosC)
            print('Current C:', np.degrees(C))

            if A == 0:
                newC = 0
            else:
                # Apply SSA to find the target C.
                B = ssa(a, b, A)
                newC = np.pi - A - B
                print('Target B:', np.degrees(B))
                print('Target C:', np.degrees(newC))

            # Compute rotational theta based on current A.
            if np.sign(self.angle) != np.sign(closest) and A !=0:
                theta = (newC * -1 - C) * np.sign(self.angle)
            else:
                theta = (newC - C) * np.sign(self.angle)
            print('Theta:', np.degrees(theta))

            # Generate a rotation matrix.
            r = rotation_matrix(n, theta)

            # self.angle = closest
            self.point = np.dot(r, self.point - p2.point) + p2.point
            print('Final point:', self.point)

            # sys.exit(0)


class Root:
    def __init__(self, point, length, angle, constraints, s=np.array([1,0,0]), n=np.array([0,0,1])):
        self.point = np.array(point)
        self.length = length
        self.angle = angle
        self.constraints = np.array(constraints) * np.pi / 180
        self.n = n
        self.s = s

    def update_angle(self, p2):
        y = p2.point - self.point

        cross = np.cross(self.s, y)
        angle = np.arctan2(np.linalg.norm(cross), np.dot(self.s, y))

        if np.dot(self.n, cross) < 0:
            angle = -angle

        self.angle = angle

        # self.constrain(self.s, y)

    def constrain(self, x, y):
        lower = self.constraints[0]
        upper = self.constraints[1]

        if not lower <= self.angle <= upper:
            idx = (np.abs(self.constraints - self.angle)).argmin()
            closest = self.constraints[idx]
            theta = (self.angle - closest) * np.pi / 180
            r = rotation_matrix(self.n, theta)

            self.angle = closest
            self.point = np.dot(r, self.point)


class End:
    def __init__(self, point):
        self.point = np.array(point)


def fabrik(joints, target, tolerance):
    # The distance between root and target.
    dist = np.linalg.norm(joints[0].point - target)

    # Check if target is within reach.
    if dist > sum(j.length if not isinstance(j, End) else 0 for j in joints):
        # Target is unreachable.
        print('Target is unreachable!')

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
            print('Forward Stage.')
            # STAGE 1: FORWARD REACHING.
            # Set the end effector p_n as target t.
            joints[-1].point = target

            for i in reversed(range(len(joints) - 1)):
                # Find the distance ri between the new joint position p_i+1 and the joint p_i.
                r = np.linalg.norm(joints[i+1].point - joints[i].point)
                delta = joints[i].length / r

                # Find the new joint position p_i.
                joints[i].point = (1 - delta) * joints[i+1].point + delta * joints[i].point

                if isinstance(joints[i], Root):
                    joints[i].update_angle(joints[i+1])
                elif isinstance(joints[i], Joint):
                    joints[i].update_angle(joints[i-1], joints[i+1])

            print('Backward Stage.')
            # STAGE 2: BACKWARD REACHING.
            # Set the root p_1 its initial position.
            joints[0].point = b

            for i in range(len(joints) - 1):
                # Find the distance ri between the new joint position p_i and the joint p_i+1.
                r = np.linalg.norm(joints[i+1].point - joints[i].point)
                delta = joints[i].length / r

                # Find the new joint positions p_i.
                joints[i+1].point = (1 - delta) * joints[i].point + delta * joints[i+1].point

                if isinstance(joints[i+1], Root):
                    joints[i+1].update_angle(joints[i], joints[i+2])
                elif isinstance(joints[i+1], Joint):
                    joints[i+1].update_angle(joints[i], joints[i+2])

            dif = np.linalg.norm(joints[-1].point - target)

    return [j.angle * 180 / np.pi if not isinstance(j, End) else 0 for j in joints]


def forward_kinematics(p, lengths, angles):
    points = [np.array(p)]
    n = len(lengths)

    for i in range(n):
        delta = np.array([
            lengths[i] * math.cos(angles[i]),
            lengths[i] * math.sin(angles[i])
        ])
        end = points[i] + delta
        points.append(end)

    return points

# p = forward_kinematics([0,0], [10,5], [np.pi/2, np.pi*2/3])

j1 = Root([0.0,0.0,0.0], 5, 0, [-180, 0])
j2 = Joint([3.0,4.0,0.0], 4, 0, [0, 179])
j3 = End([7.0,4.0,0.0])

start = time.time()
p = fabrik([j1, j2, j3], np.array([5, 0, 0]), 0.01)
print('Time:', (time.time() - start) * 1000, 'ms')
print(p)

'''
start = time.time()
pp = fabrik(
    np.copy(p),
    [5,3],
    [np.array([-180, 180]), np.array([-180, 180])],
    np.array([6,0]),
    0.01)
print(time.time() - start)
print(pp)
'''