from agility.main import Servo, Leg, Robot, Head, Body
from finesse.eclipse import Finesse
from theia.eye import Camera


################
# Define robot.
################

class Android:
    camera = Camera(0, 90, 60)

    # Leg 1.
    servo1 = Servo(0, -180, 90, 500, 2500, 150, bias=2, direction=1)
    servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=5, direction=1)
    servo3 = Servo(2, -135, 135, 500, 2500, 150, bias=0, direction=-1)
    leg1 = Leg(servo1, servo2, servo3, (6.3, 7.13), 0, Finesse.inverse_pack, Finesse.forward_pack)

    # Leg 2.
    servo4 = Servo(3, -90, 180, 500, 2500, 150, bias=0, direction=-1)
    servo5 = Servo(4, -225, 45, 500, 2500, 150, bias=-3, direction=1)
    servo6 = Servo(5, -135, 135, 500, 2500, 150, bias=4, direction=1)
    leg2 = Leg(servo4, servo5, servo6, (6.3, 7.13), 1, Finesse.inverse_pack, Finesse.forward_pack)

    # Leg 3.
    servo7 = Servo(6, -90, 180, 500, 2500, 150, bias=-6, direction=1)
    servo8 = Servo(7, -45, 225, 500, 2500, 150, bias=3, direction=1)
    servo9 = Servo(8, -135, 135, 500, 2500, 150, bias=3, direction=-1)
    leg3 = Leg(servo7, servo8, servo9, (6.3, 7.13), 2, Finesse.inverse_pack, Finesse.forward_pack)

    # Leg 4 .
    servo10 = Servo(9, -180, 90, 500, 2500, 150, bias=-5, direction=-1)
    servo11 = Servo(10, -225, 45, 500, 2500, 150, bias=0, direction=1)
    servo12 = Servo(11, -135, 135, 500, 2500, 150, bias=0, direction=1)
    leg4 = Leg(servo10, servo11, servo12, (6.3, 7.13), 3, Finesse.inverse_pack, Finesse.forward_pack)

    # Head
    head_lr = Servo(17, -90, 90, 400, 2400, 100, bias=6, direction=1, left_bound=-45, right_bound=45)
    head_ud = Servo(16, -90, 90, 400, 2400, 100, bias=0, direction=1, left_bound=-20, right_bound=20)
    head = Head(head_lr, head_ud, camera)

    # Body
    body = Body(length=16.5, width=15.5, cx=0.66, cy=0.1, mb=20, ml=0)

    # Robot.
    robot = Robot(leg1, leg2, leg3, leg4, body, head)


#######################
# Connection variables.
#######################

class Crossbar:
    # Crossbar.
    ip = '192.168.43.245'
    realm = 'lycanthrope'
    authid = 'DOG-1E5'
    secret = 'de2432k,/s-=/8Eu'
    prefix = 'pack1'
