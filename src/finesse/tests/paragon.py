from math import *


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


L = [1.75, 4, 5]
P = [0,-5.75,-5.5]
A = list(kinematics(L, P))
for x in [0, 1, 2]:
    A[x] *= (180 / pi)
print(A)
