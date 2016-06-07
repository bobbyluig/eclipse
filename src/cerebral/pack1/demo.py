from agility.gait import Dynamic
from cerebral.pack1.hippocampus import Android
from agility.main import Agility
import math


# Definition.
robot = Android.robot

# Initialize objects.
agility = Agility(robot)
gait = Dynamic(robot)


def execute_vector(vector):
    g = gait.generate(*vector)
    frames, dt = agility.prepare_smoothly(g)
    agility.execute_frames(frames, dt)


# Main loop.
while True:
    # Zero.
    agility.zero()

    # Lift each leg.
    for i in range(4):
        agility.lift_leg(i, 3, 1000)

    # Zero again.
    agility.zero()

    # Move head left, right, up, down.
    agility.set_head((30, 0), 500)
    agility.set_head((-30, 0), 1000)
    agility.set_head((0, 20), 500)
    agility.set_head((0, -20), 500)

    # Do three push-ups.
    for i in range(3):
        agility.move_body(0, 0, -4, 1000)
        agility.move_body(0, 0, 0, 1000)

    # Prepare for walk.
    agility.ready(gait.ground)

    # Slow walk. 1 cm/s. 1x.
    execute_vector((1, 0))

    # Fast walk. 4 cm/s. 2x.
    for i in range(2):
        execute_vector((4, 0))

    # Regular trot. 8 cm/s. 4x.
    for i in range(4):
        execute_vector((8, 0))

    # Max speed trot. 13 cm/s. 4x.
    for i in range(4):
        execute_vector((13, 0))

    # Rotate. 4x.
    for i in range(4):
        execute_vector((0, math.degrees(40)))

    # Walk with turn. 4x.
    for i in range(4):
        execute_vector((4, -math.degrees(10)))

    # Trot with turn. 4x.
    for i in range(4):
        execute_vector((10, -math.degrees(10)))

    # Again, backwards.
    execute_vector((-1, 0))

    for i in range(2):
        execute_vector((-4, 0))

    for i in range(4):
        execute_vector((-8, 0))

    for i in range(4):
        execute_vector((-13, 0))

    for i in range(4):
        execute_vector((0, -math.degrees(40)))

    for i in range(4):
        execute_vector((-4, math.degrees(10)))

    for i in range(4):
        execute_vector((-10, math.degrees(10)))

