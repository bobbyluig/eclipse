from agility.gait import Crawl
from cerebral.pack.hippocampus import Android
from agility.main import Agility
import time

# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Gait.
crawl = Crawl()

# Main
agility.execute(crawl)