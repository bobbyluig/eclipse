import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from presentation.fabrik import fabrik
import math

__author__ = 'Lujing Cen'

def f(x):
    conds = [(x > -2) & (x < 2), x >= 2, x <= -2]
    funcs = [-0.5, lambda x: 0.5 * x - 1.5, lambda x: -0.5 * x - 1.5]
    return np.piecewise(x, conds, funcs)

# Generate x and y points.
x = np.linspace(4, -4, 1000)
y = f(x)

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
ax.plot((-4, 4), (0, 0), color='#ff0000', linestyle='dashed', zorder=1)
ax.text(0, 0.15, 'Ground Plane', verticalalignment='center', horizontalalignment='center', zorder=0, fontsize=15, fontweight='bold')

# Create dynamic.
j1, = ax.plot([], [], marker='.', linestyle='-', color='#00ff00', markeredgecolor='#ff0000', markerfacecolor='#ff0000', markersize=15, linewidth=3, zorder=100)
j2, = ax.plot([], [], marker='.', linestyle='-', color='#00ff00', markeredgecolor='#ff0000', markerfacecolor='#ff0000', markersize=15, linewidth=3, zorder=100)
t, = ax.plot([], [], marker='8', markeredgecolor='#ff0000', markerfacecolor='None', markersize=15, zorder=99)
r, = ax.plot([], [], marker='8', markeredgecolor='#ff0000', markerfacecolor='None', markersize=15, zorder=99)
text1 = ax.text(0, 0, '', horizontalalignment='center', zorder=200, fontsize=15, fontweight='bold')
text2 = ax.text(0, 0, '', horizontalalignment='center', zorder=200, fontsize=15, fontweight='bold')


def init():
    j1.set_data([], [])
    j2.set_data([], [])
    j1.set_linestyle('-')
    j2.set_linestyle('-')
    t.set_data([], [])
    r.set_data([], [])
    text1.set_text('')
    text2.set_text('')
    text1.set_position((0, 0))
    text2.set_position((0, 0))
    return j1, j2, t, r, text1, text2


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


def angle(a, b, c, n=np.array([0, 0, 1]), x=None):
    if x is None:
        x = b - a
    y = c - b
    cross = np.cross(x, y)
    ang = np.arctan2(np.linalg.norm(cross), np.dot(x, y))

    if np.dot(n, cross) < 0:
        ang = -ang

    return np.degrees(ang)


base = [0, 3, 0]
lengths = [2, 3]
angles = [-np.pi * 0, -np.pi/2]
p = forward_kinematics(base, lengths, angles)
p = fabrik(p, lengths, np.array([x[10], y[10], 0]), 1e-5)
p[0] = np.array(base)
p = np.array(p)
fab = fabrik(p.copy(), lengths, np.array([x[250], y[250], 0]), 1e-5, step=True)
fab = np.array(fab)


def a1():
    x = p.T[0]
    y = p.T[1]
    j1.set_data([x[0], x[1]], [y[0], y[1]])
    j2.set_data([x[1], x[2]], [y[1], y[2]])


def a2():
    t.set_data(x[250], y[250])
    r.set_data(p[0][0], p[0][1])
    text1.set_text('Target')
    text2.set_text('Root')
    text1.set_position((x[250], y[250] - 0.25))
    text2.set_position((p[0][0], p[0][1] + 0.25))



def a3():
    p = fab[0]
    j2.set_data([p[2][0]], [p[2][1]])

def a4():
    p = fab[0]
    j2.set_data([p[1][0], p[2][0]], [p[1][1], p[2][1]])
    j2.set_linestyle('--')

def a5():
    p = fab[1]
    j2.set_data([p[1][0], p[2][0]], [p[1][1], p[2][1]])
    j2.set_linestyle('-')

def a6():
    p = fab[1]
    j1.set_data([p[0][0], p[1][0]], [p[0][1], p[1][1]])
    j1.set_linestyle('--')

def a7():
    p = fab[2]
    j1.set_data([p[0][0], p[1][0]], [p[0][1], p[1][1]])
    j1.set_linestyle('-')

def a8():
    p = fab[3]
    j1.set_data(p[0][0], p[0][1])

def a9():
    p = fab[3]
    j1.set_data([p[0][0], p[1][0]], [p[0][1], p[1][1]])
    j1.set_linestyle('--')

def a10():
    p = fab[4]
    j1.set_data([p[0][0], p[1][0]], [p[0][1], p[1][1]])
    j1.set_linestyle('-')

def a11():
    p = fab[4]
    j2.set_data([p[1][0], p[2][0]], [p[1][1], p[2][1]])
    j2.set_linestyle('--')

def a12():
    p = fab[5]
    j2.set_data([p[1][0], p[2][0]], [p[1][1], p[2][1]])
    j2.set_linestyle('-')


def animate(i):
    if i == 0:
        init()
    elif i <= 12:
        exec('a%s()' % i)

    return j1, j2, t, r, text1, text2

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=15, interval=1000, blit=True)
anim.save('alpha.mp4', bitrate=6000)
plt.show()