from cerebral.pack1.hippocampus import Android
from agility.main import Agility
import numpy as np


# Robot by reference.
robot = Android.robot
agility = Agility(robot)


agility.zero()

target = np.array((
    (0, 0, -10),
    (2, 0, -10),
    (2, 0, -9),
    (0, 0, -10)
))

frames, dt = agility.target_pose(target, 1000)

print(frames)
