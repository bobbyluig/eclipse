from agility.gait import doggy_crawl
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
gait = doggy_crawl(0.1, 2, robot.body)

# Main
# agility.zero()
frames, dt = agility.prepare(gait)
# agility.execute(frames, dt)
