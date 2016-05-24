from agility.gait import Dynamic
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time, math


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
crawl = Dynamic(robot.body)
gait = crawl.generate(3, 0)

# Main
agility.configure()
agility.zero()
agility.prepare_lift(0, (2, 0, -13), 1, 1000)
# frames, dt = agility.prepare_gait(gait)
# agility.execute_forever(frames, dt)
