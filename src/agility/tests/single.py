from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from agility.maestro import Maestro, Servo
from finesse.dog import inverse
import math

###########################
# Front right leg only!
# Currently the white one.
###########################

usc = Usc()
maestro = Maestro()

# Define servos.
servo1 = Servo(0, -90, 180, 500, 2500, 10)
servo2 = Servo(1, -45, 225, 500, 2500, 10)
servo3 = Servo(3, -135, 135, 500, 2500, 10)

# Define home (what IK considers 0, 0, 0).
SERVO1_HOME = 3
SERVO2_HOME = 180
SERVO3_HOME = -2

# Configure velocity.
maestro.set_speed(servo1, servo1.max_vel)
maestro.set_speed(servo2, servo2.max_vel)
maestro.set_speed(servo3, servo3.max_vel)
maestro.flush()


# Go home.
def goHome():
    servo1.target = SERVO1_HOME
    servo2.target = SERVO2_HOME
    servo3.target = SERVO3_HOME
    maestro.set_target(servo1)
    maestro.set_target(servo2)
    maestro.set_target(servo3)
    maestro.flush()

# Set position.
def moveToEuclidean(position):
    angles = inverse((7.5, 7.5), position)
    if angles is not None:
        servo1.target = angles[0] + SERVO1_HOME
        servo2.target = angles[1] + SERVO2_HOME
        servo3.target = angles[2] + SERVO3_HOME
        maestro.end_together(servo1, servo2, servo3)
        # maestro.set_target(servo1)
        # maestro.set_target(servo2)
        # maestro.set_target(servo3)
        # maestro.flush()
    else:
        print('Unable to reach position!')
        goHome()


moveToEuclidean((0, 0, -10))

# Are servos at their targets?
def isAtTarget(*servos):
    for servo in servos:
        maestro.get_position(servo)

    if all(abs(servo.deg - servo.target) < 2 for servo in servos):
        return True

    return False