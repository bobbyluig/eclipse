from agility.main import Servo, Leg, Robot
import os


################
# Define robot.
################

class Android:
    # Leg 1.
    servo1 = Servo(0, -180, 90, 500, 2500, 150, bias=0, direction=1)
    servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=0, direction=1)
    servo3 = Servo(2, -135, 135, 500, 2500, 150, bias=0, direction=-1)
    leg1 = Leg(servo1, servo2, servo3, (7.5, 7.5), 0)

    # Leg 2.
    servo4 = Servo(3, -90, 180, 500, 2500, 150, bias=0, direction=-1)
    servo5 = Servo(4, -225, 45, 500, 2500, 150, bias=0, direction=1)
    servo6 = Servo(5, -135, 135, 500, 2500, 150, bias=0, direction=1)
    leg2 = Leg(servo4, servo5, servo6, (7.5, 7.5), 1)

    # Leg 3.
    servo7 = Servo(6, -90, 180, 500, 2500, 150, bias=0, direction=1)
    servo8 = Servo(7, -45, 225, 500, 2500, 150, bias=0, direction=1)
    servo9 = Servo(8, -135, 135, 500, 2500, 150, bias=0, direction=-1)
    leg3 = Leg(servo7, servo8, servo9, (7.5, 7.5), 2)

    # Leg 4 .
    servo10 = Servo(9, -180, 90, 500, 2500, 150, bias=0, direction=-1)
    servo11 = Servo(10, -225, 45, 500, 2500, 150, bias=0, direction=1)
    servo12 = Servo(11, -135, 135, 500, 2500, 150, bias=0, direction=1)
    leg4 = Leg(servo10, servo11, servo12, (7.5, 7.5), 3)

    # Robot.
    robot = Robot(leg1, leg2, leg3, leg4)


#######################
# Connection variables.
#######################

class Crossbar:
    # Crossbar.
    ip = '127.0.0.1'
    realm = 'lycanthrope'
    authid = 'DOG-1E5'
    secret = 'de2432k,/s-=/8Eu'


###########################
# Shared manager variables.
###########################

class Manager:
    if os.name == 'nt':
        # Running on Windows, create a pipe.
        address = '\\\\.\\pipe\\eclipse'
    else:
        # Running on Linux, create a socket.
        address = 'listener-eclipse'

    authkey = b'eclipse4lyfe'


#############################
# Basic conversation topics.
#############################

class Conversation:
    topics = {
        'hello': "Hello World!",
        'identify': "Hello. I am DOG-1E5, Eclipse Technology's first generation quadruped. "
                    "I am designed for Project Lycanthrope by E D D Red Team 2016. "
                    "Rawr."
    }


