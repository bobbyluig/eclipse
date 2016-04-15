from cerebral.pack.hippocampus import Android
from cerebral.pack.commands import Commands
from agility.main import Agility, IR
from finesse.eclipse import Finesse
from threading import Thread
import time


# Define agility.
robot = Android.robot
agility = Agility(robot)

# Threading variables.
run = False


class Target:
    @staticmethod
    def crawl():
        global run

        tau = 1000
        beta = 0.8
        x, y = agility.generate_crawl(tau, beta)
        intro, main = agility.generate_ir(tau, x, y)
        agility.execute_ir(intro)

        while run:
            agility.execute_ir(main)

    @staticmethod
    def pushup():
        global run

        instructions = []
        targets = [
            (0, 0, -8),
            (0, 0, -13)
        ]
        tau = 750

        for target in targets:
            for leg in range(4):
                angles = Finesse.inverse_pack(robot.legs[leg].lengths, target)
                instructions.append((IR.MOVE, leg, angles, tau/len(targets)))
            instructions.append((IR.WAIT_ALL,))

        while run:
            agility.execute_ir(instructions)

    @staticmethod
    def transform():
        global run

        instructions = []
        target = (-14, 0, 0)

        for leg in range(4):
            angles = Finesse.inverse_pack(robot.legs[leg].lengths, target)
            instructions.append((IR.MOVE, leg, angles, 0))

        instructions.append((IR.WAIT_ALL,))

        agility.execute_ir(instructions)

        run = False

    @staticmethod
    def go_home():
        global run

        agility.zero()
        run = False

# Global thread.
thread = Thread()

# Worker is ready.
run = True
Target.go_home()


