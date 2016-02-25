from tools.queue import SharedMemory
from cerebral.dog1.hippocampus import Manager, Android
from cerebral.dog1.commands import Commands
from agility.main import Agility, IR
from finesse.main import Finesse
from threading import Thread
import time

# Get queues.
memory = SharedMemory(Manager.address, Manager.authkey)
q_out = memory.get_queue(2)     # To main
q_in = memory.get_queue(1)      # From main

# Define agility.
robot = Android.robot
robot.set_gait('crawl')
agility = Agility(robot)

# Threading variables.
run = False


class Target:
    @staticmethod
    def crawl():
        global run

        tau = 1500
        beta = 0.75
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
            (0, 0, -9),
            (0, 0, -14)
        ]
        tau = 2000

        for target in targets:
            for leg in range(4):
                angles = Finesse.inverse(robot[leg].lengths, target)
                instructions.append((IR.MOVE, leg, angles, tau/len(targets)))
            instructions.append((IR.WAIT_ALL,))

        while run:
            agility.execute_ir(instructions)

    @staticmethod
    def transform():
        global run

        instructions = []
        target = (-15, 0, 0)

        for leg in range(4):
            angles = Finesse.inverse(robot[leg].lengths, target)
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
q_out.put(Commands.READY)

# Main.
while True:
    # Block main thread until a command is received.
    cmd = q_in.get()

    if cmd == Commands.WALK_FORWARD:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=Target.crawl())
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.HOME:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=Target.go_home())
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.DO_PUSHUPS:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=Target.pushup())
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.STAND_UP:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=Target.transform())
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.STOP:
        if run:
            run = False
            q_out.put(Commands.SUCCESS)
        else:
            q_out.put(Commands.FAILURE)



