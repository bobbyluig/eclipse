from agility.maestro import Maestro, Servo
from finesse.kinematics import Finesse
import math, time
import collections

###########################
# Front right leg only!
# Currently the white one.
###########################

maestro = Maestro()

# Define servos.
servo1 = Servo(0, -90, 180, 500, 2500, 150, bias=0, direction=-1)
servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo3 = Servo(3, -135, 135, 500, 2500, 150, bias=-2, direction=-1)
servo4 = Servo(6, -180, 90, 500, 2500, 150, bias=0, direction=-1)
servo5 = Servo(8, -45, 225, 500, 2500, 150, bias=180, direction=1)
servo6 = Servo(10, -135, 135, 500, 2500, 150, bias=-2, direction=-1)

# Define legs.
leg2 = [servo1, servo2, servo3]
leg4 = [servo4, servo5, servo6]

# Configure velocity.
maestro.set_speed(servo1, servo1.max_vel)
maestro.set_speed(servo2, servo2.max_vel)
maestro.set_speed(servo3, servo3.max_vel)
maestro.set_speed(servo4, servo4.max_vel)
maestro.set_speed(servo5, servo5.max_vel)
maestro.set_speed(servo6, servo6.max_vel)
maestro.flush()


# Go home.
def go_home(servos):
    for servo in servos:
        servo.set_target(0)
        maestro.set_target(servo)

    maestro.flush()


# Set position.
def target_euclidean(leg, position, a3=False):
    angles = Finesse.inverse((7.5, 7.5), position, a3=a3)
    print(angles)

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


CRAWL_GAIT = [
    (5, 0, -9),     # Top of descent
    (3, 0, -12),    # Drag 1
    (2, 0, -12),    # Drag 2
    (1, 0, -12.1),  # Drag 3
    (0, 0, -12.2),  # Drag 4
    (-1, 0, -12.2), # Drag 5
    (-2, 0, -12.1), # Drag 6
    (-3, 0, -12),   # Drag 7
]


# Only for 2 legs. 1423 crawl gait.
def animate(gait, leg2, leg4):
    gait = collections.deque(gait)
    frame_time = 150

    leg4_points = gait.copy()
    leg2_points = gait.copy()
    leg2_points.rotate(-2)

    while True:
        for i in range(len(gait)):
            target_euclidean(leg4, leg4_points[i])
            target_euclidean(leg2, leg2_points[i])
            maestro.get_multiple_positions(leg4 + leg2)
            maestro.end_together(leg4 + leg2, time=frame_time, update=False)

            # No need to check all.
            while not is_at_target(leg4):
                pass

go_home(leg4 + leg2)
time.sleep(2)
animate(CRAWL_GAIT, leg2, leg4)