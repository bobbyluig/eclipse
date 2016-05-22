from agility.gait import Dynamic
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time, math


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
crawl = Dynamic(robot.body)
gait = crawl.generate(6, 0)

# Main
# agility.configure()
agility.zero()
frames, dt = agility.prepare(gait)
agility.execute_forever(frames, dt)
