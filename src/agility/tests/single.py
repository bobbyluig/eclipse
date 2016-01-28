from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from agility.maestro import Maestro
from agility.main import Servo
from finesse.main import Finesse
import math, time

###########################
# Front right leg only!
# Currently the white one.
###########################

# usc = Usc()
maestro = Maestro()

# Define servos.
servo4 = Servo(3, -90, 180, 500, 2500, 150, bias=10, direction=-1)
servo5 = Servo(4, -225, 45, 500, 2500, 150, bias=5, direction=1)
servo6 = Servo(5, -135, 135, 500, 2500, 150, bias=10, direction=1)
servos = [servo4, servo5, servo6]

# Configure velocity.
maestro.set_speed(servo4, servo4.max_vel)
maestro.set_speed(servo5, servo5.max_vel)
maestro.set_speed(servo6, servo6.max_vel)
maestro.flush()

# Go home.
def goHome():
    for servo in servos:
        servo.set_target(0)
        maestro.set_target(servo)

    maestro.flush()

# Set position.
def moveToEuclidean(position, a3=False):
    angles = Finesse.inverse((7.5, 7.5), position, a3=a3)

    if angles is not None:
        servo4.set_target(angles[0])
        servo5.set_target(angles[1])
        servo6.set_target(angles[2])
        maestro.end_together(servos, update=True, time=200)
    else:
        print('Unable to reach position (%s, %s, %s)!' % position)
        goHome()


# Are servos at their targets?
def isAtTarget(servos):
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
            moveToEuclidean(point)

            while not isAtTarget(servos):
                pass


def dig(servos):
    for servo in servos:
        maestro.get_position(servo)

    while True:
        for point in DIG:
            moveToEuclidean(point, a3=True)

            while not isAtTarget(servos):
                pass


BASIC_WALK = [(0, 0, -8), (5, 0, -10), (3, 0, -12), (0, 0, -12.1), (-3, 0, -12)]
MOTION_RANGE = [(0, 0, -15), (0, -15, 0), (15, 0, 0)]
UPPER_CUT = [(-2, 0, -5), (13, 0, -2)]
FORWARD_PUNCH = [(-3, 0, -10), (15, 0, 0)]
DIG = [(10, 0, -10), (-3, 0, -10), (-3, 0, -10), (10, 0, -10)]

goHome()

time.sleep(3)

# moveToPoints(servos, DIG)

# moveToEuclidean((12, 3, 0), a3=True)

dig(servos)