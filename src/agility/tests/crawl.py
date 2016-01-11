from agility.maestro import Maestro, Servo
from finesse.dog import inverse
import math, time

###########################
# Front right leg only!
# Currently the white one.
###########################

maestro = Maestro()

# Define servos.
servo1 = Servo(0, -90, 180, 500, 2500, 150, bias=0, direction=-1)
servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo3 = Servo(3, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo4 = Servo(6, -90, 180, 500, 2500, 150, bias=90, direction=-1)
servo5 = Servo(8, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo6 = Servo(10, -135, 135, 500, 2500, 150, bias=-2, direction=-1)

# Define legs.
leg1 = [servo1, servo2, servo3]
leg2 = [servo4, servo5, servo6]

# Configure velocity.
maestro.set_speed(servo1, servo1.max_vel)
maestro.set_speed(servo2, servo2.max_vel)
maestro.set_speed(servo3, servo3.max_vel)
maestro.set_speed(servo4, servo4.max_vel)
maestro.set_speed(servo5, servo5.max_vel)
maestro.set_speed(servo6, servo6.max_vel)
maestro.flush()


# Go home.
def goHome(servos):
    for servo in servos:
        servo.set_target(0)
        maestro.set_target(servo)

    maestro.flush()


# Set position.
def moveToEuclidean(servos, position, a3=False):
    angles = inverse((7.5, 7.5), position, a3=a3)

    if angles is not None:
        servos[0].set_target(angles[0])
        servos[1].set_target(angles[1])
        servos[2].set_target(angles[2])
        maestro.end_together(*servos, update=True, time=300)
    else:
        print('Unable to reach position (%s, %s, %s)!' % position)
        goHome(*servos)


# Are servos at their targets?
def isAtTarget(*servos):
    for servo in servos:
        maestro.get_position(servo)

    if all(servo.at_target() for servo in servos):
        return True

    return False


def moveToPoints(servos, points):
    for servo in servos:
        maestro.get_position(servo)

    while True:
        for point in points:
            moveToEuclidean(servos, point)

            while not isAtTarget(*servos):
                pass


BASIC_WALK = [(0, 0, -8), (5, 0, -10), (3, 0, -12), (0, 0, -12.1), (-3, 0, -12)]
MOTION_RANGE = [(0, 0, -15), (0, -15, 0), (15, 0, 0)]
UPPER_CUT = [(-2, 0, -5), (13, 0, -2)]
FORWARD_PUNCH = [(-3, 0, -10), (15, 0, 0)]
DIG = [(10, 0, -9), (-3, 0, -9), (-3, 0, -8), (10, 0, -8)]

# goHome(*leg1, *leg2)
# time.sleep(3)

goHome(leg2)
# moveToPoints(leg2, BASIC_WALK)