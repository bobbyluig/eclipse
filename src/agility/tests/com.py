from agility.gait import LiftLeg
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time

# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
gait0 = LiftLeg(0)
gait1 = LiftLeg(1)
gait2 = LiftLeg(2)
gait3 = LiftLeg(3)

# Main
agility.execute(gait0)
agility.execute(gait1)
agility.execute(gait2)
agility.execute(gait3)