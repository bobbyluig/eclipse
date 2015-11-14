import numpy as np
from math import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def forward(lengths, angles):
    l1, l2, l3 = lengths
    theta1, theta2, theta3 = angles

    x1 = 0
    y1 = l1 * cos(theta1)
    z1 = -l1 * sin(theta1)

    x2 = x1 + l2 * sin(theta2)
    y2 = y1 - l2 * cos(theta2) * sin(theta1)
    z2 = z1 - l2 * cos(theta2) * cos(theta1)

    x3 = x2 + l3 * sin(theta2 + theta3)
    y3 = y2 - l3 * cos(theta2 + theta3) * sin(theta1)
    z3 = z2 - l3 * cos(theta2 + theta3) * cos(theta1)

    return (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)


def inverse(lengths, target):
    l1, l2, l3 = lengths
    x, y, z = target

    theta1 = atan2(-z, y) - acos(l1 / (y**2 + z**2)**(1/2))

    y1 = l1 * cos(theta1)
    z1 = l1 * sin(theta1)

    theta3 = (l2**2 + l3**2 - x**2 - (y - y1)**2 - (-z - z1)**2) / (2 * l2 * l3)

    if theta3 < -1:
        theta3 = -1
    if theta3 > 1:
        theta3 = 1

    theta3 = pi - acos(theta3)

    theta2 = atan2(x, (-z - z1) / cos(theta1)) - acos((l2**2 - l3**2 + x**2 + (y - y1)**2 + (-z - z1)**2) /
                                                     (2 * l2 * (x**2 + (y - y1)**2 + (-z - z1)**2)**(1/2)))

    return theta1, theta2, theta3


def full_analysis(l1, l2, l3, n):
    d = l2 + l3

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
            angles = inverse((l1, l2, l3), (x[i], y[i], z[i]))
            f = forward((l1, l2, l3), angles)[2]
            assert(np.linalg.norm(np.array(f) - np.array((x[i], y[i], z[i]))) < 0.0001)
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

    fig2 = plt.figure()
    ax1 = fig2.add_subplot(131)
    ax1.set_aspect('equal')
    ax1.scatter(x_good, y_good, c='g', alpha=0.5)
    ax1.scatter(x_bad, y_bad, c='r')
    ax1.set_xlabel('X Points')
    ax1.set_ylabel('Y Points')

    ax2 = fig2.add_subplot(132)
    ax2.set_aspect('equal')
    ax2.scatter(x_good, z_good, c='g', alpha=0.5)
    ax2.scatter(x_bad, z_bad, c='r')
    ax2.set_xlabel('X Points')
    ax2.set_ylabel('Z Points')

    ax3 = fig2.add_subplot(133)
    ax3.set_aspect('equal')
    ax3.scatter(y_good, z_good, c='g', alpha=0.5)
    ax3.scatter(y_bad, z_bad, c='r')
    ax3.set_xlabel('Y Points')
    ax3.set_ylabel('Z Points')

    plt.show()


full_analysis(2, 7, 8, 10000)


def graph():
    x = []
    y = []
    z = []

    for i in range(-180, 190, 10):
        for j in range(-180, 190, 10):
            for k in range(-180, 190, 10):
                f = forward((2, 7, 5), (radians(i), radians(j), radians(k)))
                x.append(f[2][0])
                y.append(f[2][1])
                z.append(f[2][2])

    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(25, 7.5), dpi=80)
    fig.suptitle('Visualization of End Effector Kinematics (Leg 2)', fontsize=16, fontweight='bold')

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

    fig.savefig('leg2.png', bbox_inches='tight')

    plt.show()
