from cerebral.pack1.hippocampus import Android
from agility.main import Agility, IR
from finesse.eclipse import Finesse
import time

# Robot by reference.
robot = Android.robot
agility = Agility(robot)


def test():
    points = [
        (7.5, 0, -7.5),
        (-7.5, 0, -7.5)
    ]
    sequence = [
        [(points[0], 0), (points[1], 500)],
        [(points[0], 0), (points[1], 250), (points[0], 500), (points[1], 750)],
        [(points[0], 0), (points[1], 500)],
        [(points[0], 0), (points[1], 250), (points[0], 500), (points[1], 750)]
    ]

    a, b = agility.unwind(sequence)
    intro, main = agility.generate_ir(1000, a, b)

    for ir in intro:
        print(ir)

    print('-' * 100)

    for ir in main:
        print(ir)

    agility.zero()
    time.sleep(3)

    agility.execute_ir(intro)

    while True:
        agility.execute_ir(main)


def test1():
    points = [
        (0, 0, -15),
        (0, 0, -13),
        (0, 0, -11),
        (0, 0, -9)
    ]
    sequence = [
        [(points[0], 0), (points[1], 250), (points[2], 500), (points[3], 750)],
        [(points[0], 0), (points[1], 300), (points[2], 500), (points[3], 750)],
        [(points[0], 0), (points[1], 300), (points[2], 500), (points[3], 750)],
        [(points[0], 0), (points[1], 300), (points[2], 500), (points[3], 750)]
    ]

    a, b = agility.unwind(sequence)
    intro, main = agility.generate_ir(1000, a, b)

    for ir in intro:
        print(ir)

    print('-' * 100)

    for ir in main:
        print(ir)


def crawl():
    # Constants.
    beta = 0.50     # Percent of time each leg is on the ground.
    tau = 5000      # Time (in ms) for an entire frame of all 4 legs.

    x, y = agility.generate_crawl(tau, beta)
    intro, main = agility.generate_ir(tau, x, y)

    agility.zero()
    time.sleep(3)

    agility.execute_ir(intro)

    while True:
        agility.execute_ir(main)


def transform():
    instructions = []
    target = (-15, 0, 0)

    agility.zero()
    time.sleep(3)

    for leg in range(2, 4):
        angles = Finesse.inverse_pack(robot.legs[leg].lengths, target)
        instructions.append((IR.MOVE, leg, angles, 0))

    instructions.append((IR.WAIT_ALL,))

    agility.execute_ir(instructions)


def lift(leg):
    instructions = []
    target = (15, 0, 0)

    agility.zero()
    time.sleep(3)

    angles = Finesse.inverse_pack(robot.legs[leg].lengths, target)
    instructions.append((IR.MOVE, leg, angles, 0))

    instructions.append((IR.WAIT_ALL,))

    agility.execute_ir(instructions)


def jump():
    agility.zero()
    time.sleep(3)

    a0 = Finesse.inverse_pack(robot.legs[0].lengths, (0, 0, -12))
    a1 = Finesse.inverse_pack(robot.legs[1].lengths, (0, 0, -12))

    instructions = []
    instructions.append((IR.MOVE, 0, a0, 500))
    instructions.append((IR.MOVE, 1, a1, 500))

    instructions.append((IR.WAIT_ALL,))

    a0 = Finesse.inverse_pack(robot.legs[0].lengths, (0, 0, -15))
    a1 = Finesse.inverse_pack(robot.legs[1].lengths, (0, 0, -15))
    a2 = Finesse.inverse_pack(robot.legs[2].lengths, (14, 0, 0))
    a3 = Finesse.inverse_pack(robot.legs[3].lengths, (14, 0, 0))

    instructions.append((IR.MOVE, 0, a0, 1))
    instructions.append((IR.MOVE, 1, a1, 1))
    instructions.append((IR.MOVE, 2, a2, 130))
    instructions.append((IR.MOVE, 3, a3, 130))

    instructions.append((IR.WAIT_ALL,))

    agility.execute_ir(instructions)


def body():
    from math import cos, sin

    agility.zero()
    time.sleep(3)

    agility.move_body(0, 0, -3, t=1000)

    for t in range(100000):
        agility.move_body(2*cos(0.05 * t), 2*sin(0.05* t), -3)

if __name__ == '__main__':
    body()