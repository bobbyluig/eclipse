import numpy as np
import math, time, sys

__author__ = 'Lujing Cen'

EPSILON = sys.float_info.epsilon


def fabrik(p, d, t, tolerance, step=False):
    if step:
        ret = []

    # The distance between root and target.
    dist = np.linalg.norm(t - p[0])

    # Check if target is within reach.
    if dist > np.sum(d):
        # Target is unreachable.

        for i in range(len(p) - 1):
            # Find the distance r, between the target t and the joint position p_i.
            r = np.linalg.norm(p[i] - t)
            delta = d[i] / r

            # Find the new joint positions p_i.
            p[i+1] = (1-delta)*p[i] + delta*t

        return None
    else:
        # The target is reachable; thus, set as b the initial position of the joint p_i.
        b = p[0].copy()

        # Check whether the distance between the end effector pn and the target t is greater than a tolerance.
        dif = np.linalg.norm(t - p[-1])

        while dif > tolerance:
            # STAGE 1: FORWARD REACHING.
            # Set the end effector p_n as target t.
            p[-1] = t

            if step:
                ret.append(p.copy())

            for i in reversed(range(len(p) - 1)):
                # Find the distance ri between the new joint position p_i+1 and the joint p_i.
                r = np.linalg.norm(p[i+1] - p[i])
                delta = d[i] / r

                # Find the new joint position p_i.
                p[i] = (1-delta)*p[i+1] + delta*p[i]
                if step:
                    ret.append(p.copy())

            # STAGE 2: BACKWARD REACHING.
            # Set the root p_1 its initial position.
            p[0] = b
            if step:
                ret.append(p.copy())

            for i in range(len(p) - 1):
                # Find the distance ri between the new joint position p_i and the joint p_i+1.
                r = np.linalg.norm(p[i+1] - p[i])
                delta = d[i] / r

                # Find the new joint positions p_i.
                p[i+1] = (1-delta)*p[i] + delta*p[i+1]
                if step:
                    ret.append(p.copy())

            dif = np.linalg.norm(t - p[-1])
    if step:
        return ret
    else:
        return p
