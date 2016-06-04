from agility.gait import Dynamic
from cerebral.pack1.hippocampus import Android
from agility.main import Agility
import time, math


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
crawl = Dynamic(robot)
gait = crawl.generate(2, 0)

# Main
# agility.configure()
agility.zero()
# frames, dt = agility.prepare_smoothly(gait)
# agility.execute_forever(frames, dt)
