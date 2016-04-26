from agility.gait import Generic, Linear
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time

# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
gait = Linear()

# Main
frames, dt = agility.prepare(gait, debug=True)