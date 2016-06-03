from cerebral.pack1.hippocampus import Android
from agility.main import Agility
import numpy as np


# Robot by reference.
robot = Android.robot
agility = Agility(robot)


agility.zero()

agility.lift_leg(0, 1, 2000)