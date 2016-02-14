from cerebral.dog1.hippocampus import Android
import numpy as np
from finesse.main import Finesse
import bisect
import time

# Robot by reference.
robot = Android.robot

# Points in the gait.
sequence = np.array([
    (4, 0, -12),
    (0, 0, -12),
    (-4, 0, -12),
    (-4, 0, -9),
    (2, 0, -9)
])

# Compute distances.
shifted = np.roll(sequence, -1, axis=0)
distances = np.linalg.norm(sequence - shifted, axis=1)

# Constants.
beta = 0.75     # Percent of time each leg is on the ground.
tau = 1000      # Time (in ms) for an entire frame of all 4 legs.

# Normalize time for each segment.
ground = distances[:2]
ground = ground / np.sum(ground)
air = distances[2:]
air = air / np.sum(air)

# Scale using constants.
t_ground = tau * beta
t_air = tau - t_ground
ground *= t_ground
air *= t_air

# Compute combined and cumulative.
times = np.concatenate((ground, air))
cumulative = np.cumsum(times)

# Convert points to angles for legs, assuming all are the same length.
angles = [np.array(Finesse.inverse(robot[0].lengths, point)) for point in sequence]


# Function to explicitly find angles using linear interpolation.
def interpolate(angles, times, t, offset=0):
    mod = len(angles)

    # Wrap around for time with given offset. >= allows 1000 to be 0.
    if t + offset >= tau:
        t += offset - tau
    else:
        t += offset

    i = bisect.bisect(times, t)
    j = (i + 1) % mod
    prev_t = times[i - 1] if i > 0 else 0
    return angles[i] + (angles[j] - angles[i]) * (t - prev_t) / times[i]


# Get starting positions.
start_pos = []
for leg in range(4):
    pos = interpolate(angles, cumulative, tau / 4 * leg)
    start_pos.append(pos)

"""
for pos in start_pos:
    print(Finesse.forward_dog(robot[0].lengths, np.radians(pos))[2])
"""

# Compute animation key frames.
key_frames = np.array([
    cumulative,
    cumulative - tau / 4,
    cumulative - tau / 4 * 2,
    cumulative - tau / 4 * 3
])
key_frames[key_frames < 0] += tau
key_frames[key_frames >= tau] -= tau

# Only keep unique key frames.
unique_kf = np.unique(key_frames)

# Iterate through sequence and build instructions.
for frame in list(unique_kf):
    pass

