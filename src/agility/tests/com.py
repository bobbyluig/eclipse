from agility.gait import Crawl
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
crawl = Crawl(robot.body)
gait = crawl.generate(3, 0)

# Main
# agility.zero()
frames, dt = agility.prepare(gait)
# agility.execute(frames, dt)
