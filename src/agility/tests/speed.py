from tools.timer import time_it
from agility.maestro import Maestro, Servo
from agility.main import Agility, Leg, LegLocation, Servo

maestro = Maestro()

servo1 = Servo(0, -90, 180, 500, 2500, 150, bias=0, direction=-1)
servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo3 = Servo(3, -135, 135, 500, 2500, 150, bias=-2, direction=-1)

leg = Leg(servo1, servo2, servo3, (7.5, 7.5), LegLocation.FR)


@time_it(10000)
def is_running():
    maestro.get_moving_state()


@time_it(10000)
def target():
    Agility.target_euclidean(leg, (2, 1, 10))


@time_it(10000)
def set_and_send():
    Agility.target_euclidean(leg, (2, 1, 10))
    for servo in leg:
        maestro.set_target(servo)

    maestro.flush()


data = bytearray(b'\x84\x00J@\x84\x01NE\x84\x03\x11D')


@time_it(10000)
def send_only():
    maestro.data = data
    maestro.flush()


@time_it(10000)
def read_location():
    maestro.get_multiple_positions(leg)


read_location()