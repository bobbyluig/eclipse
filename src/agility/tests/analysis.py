from cerebral.dog1.hippocampus import Android
from agility.main import Agility, IR
from finesse.main import Finesse
import time

# Robot by reference.
robot = Android.robot
agility = Agility(robot)


def crawl():
    # Constants.
    beta = 0.75     # Percent of time each leg is on the ground.
    tau = 1000      # Time (in ms) for an entire frame of all 4 legs.

    x, y = agility.generate_crawl(tau, beta)
    intro, main = agility.generate_ir(tau, x, y)

    agility.zero()
    time.sleep(3)

    agility.execute_ir(intro)

    while True:
        agility.execute_ir(main)


def transform():
    instructions = []
    target = (0, 0, 15)

    agility.zero()
    time.sleep(3)

    for leg in range(0, 2):
        angles = Finesse.inverse(robot[leg].lengths, target)
        instructions.append((IR.MOVE, leg, angles, 0))

    instructions.append((IR.WAIT_ALL,))

    agility.execute_ir(instructions)


transform()