import numpy as np
from math import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def pure_math(lengths, angles):
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


def inverse(lengths, target, a2=False, a3=False, deg=False):
    l1, l2 = lengths
    x, y, z = target
    dist = np.linalg.norm(target)

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


def full_analysis(l1, l2, n):
    d = l1 + l2

    phi = np.random.uniform(0, 2*pi, n)
    costheta = np.random.uniform(-1, 1, n)
    u = np.random.uniform(0, 1, n)

    theta = np.arccos(costheta)
    r = d * u**(1/3)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    x_good, x_bad = [], []
    y_good, y_bad = [], []
    z_good, z_bad = [], []

    for i in range(len(x)):
        try:
            angles = inverse((l1, l2), (x[i], y[i], z[i]))
            forward = pure_math((l1, l2), angles)[2]
            assert(np.linalg.norm(np.array(forward) - np.array((x[i], y[i], z[i]))) < 0.0001)
            x_good.append(x[i])
            y_good.append(y[i])
            z_good.append(z[i])
        except:
            x_bad.append(x[i])
            y_bad.append(y[i])
            z_bad.append(z[i])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_aspect('equal')
    ax.scatter([-d, d, 0, 0, 0, 0], [0, 0, -d, d, 0, 0], [0, 0, 0, 0, -d, d], alpha=0)
    # ax.scatter(x_good, y_good, z_good, c='g', alpha=0.7)
    ax.scatter(x_bad, y_bad, z_bad, c='r')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    fig2 = plt.figure(figsize=(25, 7.5), dpi=80)
    fig2.suptitle('Dead Zone Analysis (Configuration 1)', fontsize=16, fontweight='bold')

    ax1 = fig2.add_subplot(131)
    ax1.set_aspect('equal')
    ax1.scatter(x_good, y_good, c='g', alpha=0.5)
    ax1.scatter(x_bad, y_bad, c='r')
    ax1.set_xlabel('X Axis')
    ax1.set_ylabel('Y Axis')

    ax2 = fig2.add_subplot(132)
    ax2.set_aspect('equal')
    ax2.scatter(x_good, z_good, c='g', alpha=0.5)
    ax2.scatter(x_bad, z_bad, c='r')
    ax2.set_xlabel('X Axis')
    ax2.set_ylabel('Z Axis')

    ax3 = fig2.add_subplot(133)
    ax3.set_aspect('equal')
    ax3.scatter(y_good, z_good, c='g', alpha=0.5)
    ax3.scatter(y_bad, z_bad, c='r')
    ax3.set_xlabel('Y Axis')
    ax3.set_ylabel('Z Axis')

    fig2.savefig('analysis.png', bbox_inches='tight')

    plt.show()


full_analysis(7.5, 7.5, 10000)


close = []

def test():
    for i in range(-180, 190, 5):
        for j in range(-180, 190, 5):
            for k in range(-180, 190, 5):
                a, b, c = radians(i), radians(j), radians(k)
                target = pure_math((5, 5), (a, b, c))
                c = np.linalg.norm(np.array(target[2]) - np.array([1, 5, 1]))
                if c < 3:
                    print(i, j, k)
                continue

                angles = inverse((5, 7), (target[2][0], target[2][1], target[2][2]))
                ik = pure_math((5, 7), angles)
                error = np.linalg.norm(np.array(ik[2]) - np.array(target[2]))
                if error > 0.00001:
                   print('Accuracy Error:', (i, j, k))


# test()
# print(min(close))


def graph():
    x = []
    y = []
    z = []

    for i in range(-170, 100, 10):
        for j in range(-170, 100, 10):
            for k in range(-170, 100, 10):
                forward = pure_math((5, 5), (radians(i), radians(j), radians(k)))
                x.append(forward[2][0])
                y.append(forward[2][1])
                z.append(forward[2][2])

    fig = plt.figure(figsize=(25, 7.5), dpi=80)
    fig.suptitle('Visualization of End Effector Kinematics (Leg 1)', fontsize=16, fontweight='bold')

    ax1 = plt.subplot(131)
    ax1.set_aspect('equal')
    ax1.scatter(x, y, c='r')
    ax1.set_xlabel('X Points')
    ax1.set_ylabel('Y Points')

    ax2 = plt.subplot(132)
    ax2.set_aspect('equal')
    ax2.scatter(x, z, c='r')
    ax2.set_xlabel('X Points')
    ax2.set_ylabel('Z Points')

    ax3 = plt.subplot(133)
    ax3.set_aspect('equal')
    ax3.scatter(y, z, c='r')
    ax3.set_xlabel('Y Points')
    ax3.set_ylabel('Z Points')

    fig.savefig('leg1.png', bbox_inches='tight')

    plt.show()

# graph()

def analyze():
    x = []
    y = []
    z = []

    for i in range(-170, 100, 10):
        for j in range(-170, 100, 10):
            for k in range(-170, 100, 10):
                forward = pure_math((5, 5), (radians(i), radians(j), radians(k)))
                x.append(forward[2][0])
                y.append(forward[2][1])
                z.append(forward[2][2])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_aspect('equal')
    ax.scatter(x, y, z, c='g')

    plt.show()


# solve a = n * Cos[x] * Sin[z] + n * Cos[z] * Sin[x] * Cos[y] + m * Sin[x] * Cos[y] for x
# solve b = -m * Sin[y] - n * Cos[z] * Sin[y]
# solve c = n * Sin[x] * Sin[z] - m * Cos[x] * Cos[y] - n * Cos[x] * Cos[y] * Cos[z] for x
