from cerebral.dog1.hippocampus import Android
import numpy as np
from finesse.main import Finesse
import bisect

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

# Locate starting intervals using bisection.
start = [bisect.bisect(cumulative, i * 250) for i in range(4)]

# Convert points to angles for legs, assuming all are the same length.
angles = [np.array(Finesse.inverse(robot[0].lengths, point)) for point in sequence]

# Get starting positions.
mod = len(sequence)
start_pos = []
for leg in range(4):
    i = start[leg]
    j = (i + 1) % mod
    prev_t = cumulative[i - 1] if i > 0 else 0
    pos = angles[i] + (angles[j] - angles[i]) * (tau / 4 * leg - prev_t) / times[i]
    start_pos.append(pos)

# Compute animation key frames.
cumulative = np.roll(cumulative, 1)
cumulative[0] = 0   # 1000 == 0

key_frames = np.array([
    cumulative,
    cumulative - tau / 4,
    cumulative - tau / 4 * 2,
    cumulative - tau / 4 * 3
])
key_frames[key_frames < 0] += 1000

# Only keep unique key frames.
unique_kf = np.unique(key_frames)
