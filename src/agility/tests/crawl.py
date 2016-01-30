from agility.maestro import Maestro
from agility.main import Servo
from finesse.main import Finesse
import math, time, sys
import collections
import numpy as np
from itertools import chain

#############################
# This test will save us all.
#############################

maestro = Maestro()

# Leg 1 servos.
servo1 = Servo(0, -180, 90, 500, 2500, 150, bias=-10, direction=1)
servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=0, direction=1)
servo3 = Servo(2, -135, 135, 500, 2500, 150, bias=0, direction=-1)
leg1 = [servo1, servo2, servo3]

# Leg 2 servos.
servo4 = Servo(3, -90, 180, 500, 2500, 150, bias=10, direction=-1)
servo5 = Servo(4, -225, 45, 500, 2500, 150, bias=0, direction=1)
servo6 = Servo(5, -135, 135, 500, 2500, 150, bias=0, direction=1)
leg2 = [servo4, servo5, servo6]

# Leg 3 servos.
servo7 = Servo(6, -90, 180, 500, 2500, 150, bias=0, direction=1)
servo8 = Servo(7, -45, 225, 500, 2500, 150, bias=0, direction=1)
servo9 = Servo(8, -135, 135, 500, 2500, 150, bias=0, direction=-1)
leg3 = [servo7, servo8, servo9]

# Leg 4 servos.
servo10 = Servo(9, -180, 90, 500, 2500, 150, bias=10, direction=-1)
servo11 = Servo(10, -225, 45, 500, 2500, 150, bias=0, direction=1)
servo12 = Servo(11, -135, 135, 500, 2500, 150, bias=-10, direction=1)
leg4 = [servo10, servo11, servo12]

# Testing.
t = [
    [0, 125, 500, 875],
    [125, 250, 375, 750],
    [0, 375, 500, 625],
    [250, 625, 750, 875]
]

p = [
    [(5, 0, -9), (3, 0, -12), (0, 0, -12.2), (-3, 0, -12)],
    [(-3, 0, -12), (5, 0, -9), (3, 0, -12), (0, 0, -12.2)],
    [(0, 0, -12.2), (-3, 0, -12), (5, 0, -9), (3, 0, -12)],
    [(0, 0, -12.2), (-3, 0, -12), (5, 0, -9), (3, 0, -12)]
]


# Configure velocity.
for servo in leg1 + leg2 + leg3 + leg4:
    maestro.set_speed(servo, servo.max_vel)
maestro.flush()


# Go home.
def go_home(servos):
    for servo in servos:
        servo.set_target(0)
        maestro.set_speed(servo, servo.max_vel)
        maestro.set_target(servo)

    maestro.flush()


# Set position.
def target_euclidean(leg, position, a3=False):
    angles = Finesse.inverse((7.5, 7.5), position, a3=a3)

    if angles is not None:
        leg[0].set_target(angles[0])
        leg[1].set_target(angles[1])
        leg[2].set_target(angles[2])
    else:
        print('Unable to reach position (%s, %s, %s)!' % position)
        go_home(leg)


# Are servos at their targets?
def is_at_target(servos):
    for servo in servos:
        maestro.get_position(servo)

    if all(servo.at_target() for servo in servos):
        return True

    return False


# Animate the 1423 crawl gait.
def animate(gait, leg1, leg2, leg3, leg4):
    gait = collections.deque(gait)
    frame_time = 60

    leg1_points = gait.copy()
    leg2_points = gait.copy()
    leg3_points = gait.copy()
    leg4_points = gait.copy()

    # Rotate.
    leg4_points.rotate(-2)
    leg2_points.rotate(-4)
    leg3_points.rotate(-6)

    while True:
        for i in range(len(gait)):
            target_euclidean(leg1, leg1_points[i])
            target_euclidean(leg2, leg2_points[i])
            target_euclidean(leg3, leg3_points[i])
            target_euclidean(leg4, leg4_points[i])
            maestro.get_multiple_positions(leg1 + leg2 + leg3 + leg4)
            maestro.end_together(leg1 + leg2 + leg3 + leg4, time=frame_time, update=False)

            # No need to check all.
            while not is_at_target(leg1):
                pass


# Animate the trot gait.
def animate_trot(gait, leg1, leg2, leg3, leg4):
    gait = collections.deque(gait)
    frame_time = 100

    leg14_points = gait.copy()
    leg23_points = gait.copy()

    # Rotate.
    leg23_points.rotate(-2)

    while True:
        for i in range(len(gait)):
            target_euclidean(leg1, leg14_points[i])
            target_euclidean(leg2, leg23_points[i])
            target_euclidean(leg3, leg23_points[i])
            target_euclidean(leg4, leg14_points[i])
            maestro.get_multiple_positions(leg1 + leg2 + leg3 + leg4)
            maestro.end_together(leg1 + leg2 + leg3 + leg4, time=frame_time, update=False)

            while not is_at_target(leg1):
                pass


CRAWL_GAIT = [
    (6, 0, -9),         # Top of descent
    (3, 0, -12),        # Drag 1
    (2, 0, -12.1),      # Drag 2
    (1, 0, -12.2),      # Drag 3
    (0, 0, -12.2),      # Drag 4
    (-1, 0, -12.2),     # Drag 5
    (-2, 0, -12.1),     # Drag 6
    (-3, 0, -12),       # Drag 7
]


TROT_GAIT = [
    (5, 0, -10),         # Top of descent
    (4, 0, -12.2),      # Drag 1
    (0, 0, -12.3),      # Drag 2
    (-4, 0, -12.2),     # Drag 3
]


from threading import Thread


class Agility:
    def __init__(self, queue):
        self.queue = queue
        self.t = None

    def walk(self):
        if self.t is not None:
            self.stop()

        self.t = Thread(target=self.walk_method, args=(self.queue,))
        self.t.start()

    def pushup(self):
        if self.t is not None:
            self.stop()

        self.t = Thread(target=self.pushup_method, args=(self.queue,))
        self.t.start()

    @staticmethod
    def pushup_method(queue):
        sequence = [(2, 0, -10), (2, 0, -14)]
        frame_time = 400

        while queue.empty():
            for i in range(len(sequence)):
                target_euclidean(leg1, sequence[i])
                target_euclidean(leg2, sequence[i])
                target_euclidean(leg3, sequence[i])
                target_euclidean(leg4, sequence[i])
                maestro.get_multiple_positions(leg1 + leg2 + leg3 + leg4)
                maestro.end_together(leg1 + leg2 + leg3 + leg4, time=frame_time, update=False)

                # No need to check all.
                while not is_at_target(leg1):
                    pass

        with queue.mutex:
            queue.queue.clear()

    @staticmethod
    def walk_method(queue):

        gait = collections.deque(CRAWL_GAIT)
        frame_time = 150

        leg1_points = gait.copy()
        leg2_points = gait.copy()
        leg3_points = gait.copy()
        leg4_points = gait.copy()

        # Rotate.
        leg4_points.rotate(-2)
        leg2_points.rotate(-4)
        leg3_points.rotate(-6)

        while queue.empty():
            for i in range(len(gait)):
                target_euclidean(leg1, leg1_points[i])
                target_euclidean(leg2, leg2_points[i])
                target_euclidean(leg3, leg3_points[i])
                target_euclidean(leg4, leg4_points[i])
                maestro.get_multiple_positions(leg1 + leg2 + leg3 + leg4)
                maestro.end_together(leg1 + leg2 + leg3 + leg4, time=frame_time, update=False)

                # No need to check all.
                while not is_at_target(leg1):
                    pass

        with queue.mutex:
            queue.queue.clear()

    def home(self):
        go_home(leg1 + leg2 + leg3 + leg4)

    def stop(self):
        self.queue.put(0)
        self.t.join()
        self.t = None


from queue import Queue

q = Queue()
a = Agility(q)
a.home()
# a.walk()