from agility.maestro import Maestro, Servo
from agility.main import Agility, Robot, Leg, Servo

# Define servos.
servo1 = Servo(0, -90, 180, 500, 2500, 150, bias=0, direction=-1)
servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo3 = Servo(3, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo4 = Servo(6, -180, 90, 500, 2500, 150, bias=0, direction=-1)
servo5 = Servo(8, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo6 = Servo(10, -135, 135, 500, 2500, 150, bias=-2, direction=-1)

# Fake servos
servo7 = Servo(11, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo8 = Servo(12, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo9 = Servo(13, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo10 = Servo(14, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo11 = Servo(15, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo12 = Servo(16, -135, 135, 500, 2500, 150, bias=-2, direction=-1)

# Define legs.
leg2 = Leg(servo1, servo2, servo3, (7.5, 7.5))
leg4 = Leg(servo4, servo5, servo6, (7.5, 7.5))

leg1 = Leg(servo7, servo8, servo9, (7.5, 7.5))
leg3 = Leg(servo10, servo11, servo12, (7.5, 7.5))

# Define robot.
robot = Robot(leg1, leg2, leg3, leg4)

# Create agility.
agility = Agility(robot)

# Do stuff.
