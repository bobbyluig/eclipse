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
# agility.configure()
agility.zero()
while True:
    agility.scan(2000)
# frames, dt = agility.prepare_lift(0, (2, 0, -13.75), 2, 1000)
# agility.execute_frames(frames, dt)
# frames, dt = agility.prepare_gait(gait)
# agility.execute_forever(frames, dt)
