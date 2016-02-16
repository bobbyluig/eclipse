from cerebral.dog1.hippocampus import Android
import numpy as np
from finesse.main import Finesse
import bisect
from enum import IntEnum

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

# Compute length.
length = len(sequence)

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
cumulative = np.roll(cumulative, 1)
cumulative[0] = 0

# Convert points to angles for legs, assuming all are the same length.
angles = [np.array(Finesse.inverse(robot[0].lengths, point)) for point in sequence]


# Wrap-around function.
def wrap(value, low, high):
    delta = high - low
    return value - ((value - low) // delta) * delta


# Function to explicitly find angles using linear interpolation.
def interpolate(angles, times, t, offset=0):
    mod = len(angles)

    # Wrap around for time with given offset. >= allows 1000 to be 0.
    t = wrap(t + offset, 0, tau)

    i = bisect.bisect(times, t)

    return angles[i - 1] + (angles[i % mod] - angles[i - 1]) * (t - times[i - 1]) / times[i]


# Function to explicitly find interpolate a reference leg, returning best servo to check.
def inter_ref(angles, times, t, offset=0):
    mod = len(angles)

    # Wrap around for time with given offset. >= allows 1000 to be 0.
    t = wrap(t + offset, 0, tau)

    i = bisect.bisect(times, t)

    # Compute a delta.
    delta = angles[i % mod] - angles[i - 1]

    # Find max angle change.
    best = np.argmax(np.abs(delta))

    # Interpolate angle for the best one of three.
    angle = angles[i - 1][best] + delta[best] * (t - times[i - 1]) / times[i]

    # Wait until angle is greater? (or less if false)
    greater = delta[best] > 0

    # Return data (index, angle).
    return best, angle, greater


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


# Instruction enum.
class ByteCode(IntEnum):
    WAIT_ALL = 1
    WAIT_GR = 2
    WAIT_LE = 3
    MOVE = 4


# Instruction array.
instructions = []

# Iterate through sequence and build instructions.
for i in range(len(unique_kf)):
    # Easier definition.
    frame = unique_kf[i]

    # Identify which legs are active.
    active = np.where(key_frames == frame)

    # Determine when the frame should begin.
    if len(active[0]) == 4:
        # All legs begin together.
        instructions.append((ByteCode.WAIT_ALL,))
    else:
        inactive = np.delete(np.arange(4), active[0])

        # Assume all legs are moving, choose lowest index to check.
        # This is not optimal, but should suffice.
        reference = inactive[0]

        # Interpolate that leg's position.
        out = inter_ref(angles, cumulative, frame, offset=tau / 4 * reference)

        # Convert servo relative to leg to channel.
        best = out[0]
        channel = robot[reference][best].channel

        # Create instruction.
        ctrl = ByteCode.WAIT_GR if out[2] else ByteCode.WAIT_LE
        ins = (ctrl, channel, out[1])

        # Append instruction.
        instructions.append(ins)

    # Create instructions to move servos.
    move = []

    for i in range(len(active[0])):
        leg = active[0][i]
        ang = angles[(active[1][i] + 1) % length]
        t = times[active[1][i]]

        move.append((leg, ang, t))

    instructions.append((ByteCode.MOVE, move))
