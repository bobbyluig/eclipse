from agility.gait import Linear
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Sequence.
sequence = (
    [(3, 0, -10, 0), (-3, 0, -10, 750), (-3, 0, -8, 800), (2, 0, -8, 900)],
    [(3, 0, -10, 0), (-3, 0, -10, 750), (-3, 0, -8, 800), (2, 0, -8, 900)],
    [(3, 0, -10, 0), (-3, 0, -10, 750), (-3, 0, -8, 800), (2, 0, -8, 900)],
    [(3, 0, -10, 0), (-3, 0, -10, 750), (-3, 0, -8, 800), (2, 0, -8, 900)]
)

# Gait.
gait = Linear(sequence, -10, 1000)

# Main
# agility.zero()
frames, dt = agility.prepare(gait)
agility.execute(frames, dt)