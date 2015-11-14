import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib
from presentation.arc import find_a, find_root
from presentation.fabrik import fabrik
import math

__author__ = 'Lujing Cen'

# Generate parabola.
l = 5
c = 0.5
a = find_a(c, l)
root = find_root(a, c)
ends = (-4, 4)

# Generate x and y points.
x = np.linspace(ends[1], ends[0], 1000)
x_leg = np.linspace(3.5, -3.5, 250)
y = a * x**2 - 0.5
y_leg = a * x_leg**2 - 0.5

# Create and plot figure.
fig = plt.figure(figsize=(15, 9))
ax = fig.add_subplot(111)
fig.tight_layout()
ax.set_aspect('equal')
ax.set_axis_bgcolor('#ffffff')
ax.plot(x, y, linewidth=2, zorder=0)

# Hidden point to define max.
ax.plot(0, 4)
ax.plot(0, -1)

# Draw static.
ax.plot((ends[0], ends[1]), (0, 0), color='#ff0000', linestyle='dashed', zorder=1)
ax.text(0, 0.15, 'Ground Plane', verticalalignment='center', horizontalalignment='center', zorder=0, fontsize=15, fontweight='bold')

# Create dynamic.
leg, = ax.plot([], [], marker='.', linestyle='-', color='#00ff00', markeredgecolor='#ff0000', markerfacecolor='#ff0000', markersize=15, linewidth=3, zorder=100)
text1 = ax.text(0, 0, '', horizontalalignment='center', zorder=200, fontsize=15, fontweight='bold')
text2 = ax.text(0, 0, '', horizontalalignment='right', zorder=200, fontsize=15, fontweight='bold')


def forward_kinematics(p, lengths, angles):
    ret = [np.array(p)]

    for i in range(len(lengths)):
        delta = np.array([
            lengths[i] * math.cos(angles[i]),
            lengths[i] * math.sin(angles[i]),
            0
        ])
        end = ret[i] + delta
        ret.append(end)

    return ret


def gen_leg(x, y):
    ret = []

    base = [0, 3, 0]
    lengths = [1.5, 3]
    angles = [-np.pi, -np.pi/2]
    p = forward_kinematics(base, lengths, angles)

    for i in range(len(x)):
        p = fabrik(p, lengths, np.array([x[i], y[i], 0]), 1e-5)
        p[0] = np.array(base)
        ret.append(p.copy())

    ret_stroke = np.linspace(x.min(), x.max(), int(len(x)/4))
    for i in range(len(ret_stroke)):
        p = fabrik(p, lengths, np.array([ret_stroke[i], y.max(), 0]), 1e-5)
        p[0] = np.array(base)
        ret.append(p.copy())

    return np.array(ret)


points = gen_leg(x_leg, y_leg)


def angle(a, b, c, n=np.array([0, 0, 1]), x=None):
    if x is None:
        x = b - a
    y = c - b
    cross = np.cross(x, y)
    ang = np.arctan2(np.linalg.norm(cross), np.dot(x, y))

    if np.dot(n, cross) < 0:
        ang = -ang

    return np.degrees(ang)


def init():
    leg.set_data([], [])
    text1.set_text('')
    text1.set_position((0, 0))
    text2.set_text('')
    text2.set_position((0, 0))
    return leg, text1, text2


def animate(i):
    a, b, c = points[i][0], points[i][1], points[i][2]
    x, y = points[i].T[0], points[i].T[1]
    leg.set_data(x, y)

    text1.set_position((x[0], y[0] + 0.1))
    text1.set_text('Angle: %.2f$\degree$' % angle(np.array([0, 100, 0]), a, b))

    text2.set_position((x[1] - 0.1, y[1]))
    text2.set_text('Angle: %.2f$\degree$' % angle(a, b, c))

    return leg, text1, text2

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(points), interval=20, blit=True)
anim.save('dog.mp4', bitrate=6000)
plt.show()