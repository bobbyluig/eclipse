from tkinter import *
from threading import Thread, Lock
import math
from agility.gait import Dynamic
from cerebral.pack1.hippocampus import Android
from agility.main import Agility
import time, math


# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Generic crawl.
crawl = Dynamic(robot)

# Tkinter.
root = Tk()

# Define vector.
vector = [0, 0]
v = 0.5
r = math.radians(5)


def run_gait():
    agility.zero()

    while True:
        try:
            gait = crawl.generate(*vector)
            frames, dt = agility.prepare_smoothly(gait)
            agility.execute_frames(frames, dt)
        except:
            pass


def key_down(event):
    char = event.char

    if char == 'w':
        vector[0] += v
    elif char == 's':
        vector[0] -= v
    elif char == 'a':
        vector[1] += r
    elif char == 'd':
        vector[1] -= r

    print('Target vector:', vector)


# Set up tkinter.
frame = Frame(root, width=200, height=200)
root.bind('<KeyPress>', key_down)
frame.pack()

# Set up threading.
thread = Thread(target=run_gait)

# Start threads.
thread.start()
root.mainloop()