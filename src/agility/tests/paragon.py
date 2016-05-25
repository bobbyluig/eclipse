from agility.maestro import Maestro
from agility.main import Servo
from finesse.paragon import Finesse
import time

maestro = Maestro()

# Define servos.
servo1 = Servo(0, 0, 135, 1000, 2300, 120, bias=0, direction=-1)
servo2 = Servo(1, -45, 90, 780, 2100, 120, bias=0, direction=-1)
servo3 = Servo(2, -120, 80, 500, 2500, 120, bias=0, direction=1)
servos = [servo1, servo2, servo3]


def goHome():
    for servo in servos:
        servo.set_target(0)
        maestro.set_target(servo)


def moveToEuclidean(position, time):
    lengths = (1.75, 4, 5, 0.5)
    angles = Finesse.inverse_pack(lengths, position)

    if angles is not None:
        servo1.set_target(angles[0])
        servo2.set_target(angles[1])
        servo3.set_target(angles[2])
        maestro.end_together(servos, update=True, t=time)
    else:
        print('Unable to reach position (%s, %s, %s)!' % position)
        goHome()


def wait():
    while maestro.get_moving_state():
        time.sleep(0.005)


goHome()
time.sleep(2)

while True:
    moveToEuclidean((5, 6, -6), 200)
    wait()
    moveToEuclidean((0, 6, -6), 1000)
    wait()
    moveToEuclidean((0, 8, -4), 200)
    wait()