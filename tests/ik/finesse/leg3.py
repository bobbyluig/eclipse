import numpy as np
from math import *


def forward(lengths, angles):
    l1, l2 = lengths
    theta1, theta2, theta3 = angles

    x1 = 0
    y1 = 0
    z1 = 0

    x2 = l1 * sin(theta1)
    y2 = 0
    z2 = -l1 * cos(theta1)

    x3 = x2 + l2 * cos(theta3) * sin(theta1) + l2 * cos(theta1) * cos(theta2) * sin(theta3)
    y3 = -l2 * sin(theta2) * sin(theta3)
    z3 = z2 + l2 * cos(theta2) * sin(theta1) * sin(theta3) - l2 * cos(theta1) * cos(theta3)

    return (x1, y1, z1), (x2, y2, z2), (x3, y3, z3)


def graph():
    x = []
    y = []
    z = []

    for i in range(-180, 190, 10):
        for j in range(-180, 190, 10):
            for k in range(-180, 190, 10):
                f = forward((7, 5), (radians(i), radians(j), radians(k)))
                x.append(f[2][0])
                y.append(f[2][1])
                z.append(f[2][2])

    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(25, 7.5), dpi=80)
    fig.suptitle('Visualization of End Effector Kinematics (Leg 3)', fontsize=16, fontweight='bold')

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

    fig.savefig('leg3.png', bbox_inches='tight')

    plt.show()

graph()
