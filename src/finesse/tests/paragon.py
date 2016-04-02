from math import *
from finesse.paragon import Finesse
import serial, struct, time


def kinematics(lengths, pos):
    for x in range(0, 3):
        pos[x] += 1e-20
    l1, l2, l3 = lengths
    x, y, z = pos
    z+=0.5
    z*=-1

    li = ((x ** 2 + y ** 2) ** 0.5) - l1
    l4 = (z ** 2 + li ** 2) ** 0.5

    t1 = -atan2(y,x)
    t4 = atan2(li,z)
    t5 = acos((l4 ** 2 + l2 ** 2 - l3 ** 2) / (2 * l4 * l2))
    t2 = (pi / 2) - (t5 + t4)
    t3 = (pi) - acos((l2 ** 2 + l3 ** 2 - l4 ** 2) / (2 * l2 * l3))

    return t1, t2, t3


def invkinematics(lengths, angles):
    t1, t2, t3 = angles
    l1, l2, l3 = lengths
    i1 = (l2 * cos(t2)) + (l3 * cos(t2 + t3))
    x = (i1 + l1) * cos(t1)
    y = (i1 + l1) * sin(t1)
    z = (l2 * sin(t2)) + (l3 * sin(t2 + t3))
    return x, y, z


usb = serial.Serial('COM5')
lengths = (1.75, 4, 5, 0.5)
x, y, z = (4, -4, -5)
t = 0
k = 5
r = 3
a = 4

while True:
    target = (x + r * sin(k * t), y, z + (cos(k * t) / abs(cos(k * t))) * (1 - sin(k * t) ** a) ** (1 / a))
    t1, t2, t3 = Finesse.inverse_pack(lengths, target)
    # print(t1, t2, t3)
    data = struct.pack('<fff', t1, t2, t3)
    usb.write(data)
    time.sleep(0.05)
    t += 0.05
