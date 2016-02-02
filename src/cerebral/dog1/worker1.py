from tools.queue import SharedMemory
from cerebral.dog1.hippocampus import Manager, Android
from cerebral.dog1.commands import Commands
from agility.main import Agility
from collections import deque
from threading import Thread
import time

# Get queues.
memory = SharedMemory(Manager.address, Manager.authkey)
q_out = memory.get_queue(2)     # To main
q_in = memory.get_queue(1)      # From main

# Define agility.
agility = Agility(Android.robot)


# Generate crawl gait.
class Crawl:
    crawl = [
        (6, 0, -9),         # Top of descent
        (3, 0, -12),        # Drag 1
        (2, 0, -12.1),      # Drag 2
        (1, 0, -12.2),      # Drag 3
        (0, 0, -12.2),      # Drag 4
        (-1, 0, -12.2),     # Drag 5
        (-2, 0, -12.1),     # Drag 6
        (-3, 0, -12),       # Drag 7
    ]
    sequence = {
        'frame_time': 150,
        'length': 8
    }
    for i in range(4):
        q = deque(crawl)
        q.rotate(-2 * i)
        sequence['leg%s' % i] = list(q)


class Pushup:
    pushup = [
        (0, 0, -9),
        (0, 0, -14),
    ]
    sequence = {
        'frame_time': 400,
        'length': 2
    }
    for i in range(4):
        sequence['leg%s' % i] = list(pushup)


# Generate flex single.
class Flex:
    # Punch.
    punch = [(0, 0, -15), (0, 0, -7)]

    # Sequence single.
    QUARTER = 552
    EIGHTH = 276
    SIXTEENTH = 138

    sequence1 = [
        (1, EIGHTH, punch),
        (None, EIGHTH + QUARTER, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, EIGHTH, punch),
        (None, QUARTER * 2, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, EIGHTH, punch),
        (None, QUARTER * 2, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, EIGHTH + QUARTER * 4, punch),
        (None, 80, None),
    ]

    sequence2 = [
        (1, EIGHTH, punch),
        (None, EIGHTH + QUARTER, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, EIGHTH, punch),
        (None, QUARTER * 2 + EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, EIGHTH, punch),
        (None, EIGHTH + QUARTER, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, SIXTEENTH, punch),
        (None, EIGHTH, None),
        (1, EIGHTH + QUARTER * 4, punch),
        (None, 80, None),
    ]

    sequence = sequence1 + sequence2 + sequence1 * 2
    sequence = deque(sequence)

# Threading variables.
run = False


# Thread functions.
def animate(sequence):
    global run

    while run:
        agility.animate_synchronized(sequence)


def animate_flex(sequence):
    global run
    sequence = sequence.copy()

    while run:
        try:
            agility.animate_single(sequence.popleft())
        except IndexError:
            run = False

def go_home():
    global run

    agility.zero()
    run = False

# Global thread.
thread = Thread()

# Worker is ready.
q_out.put(Commands.READY)

# Main.
while True:
    # Block main thread until a command is received.
    cmd = q_in.get()

    if cmd == Commands.WALK_FORWARD:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=animate, args=(Crawl.sequence,))
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.HOME:
        if not run:
            thread = Thread(target=go_home)
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.DO_PUSHUPS:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=animate, args=(Pushup.sequence,))
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.FLEX:
        if not run:
            run = True
            q_out.put(Commands.SUCCESS)
            thread = Thread(target=animate_flex, args=(Flex.sequence,))
            thread.start()
        else:
            q_out.put(Commands.FAILURE)

    elif cmd == Commands.STOP:
        if run:
            run = False
            q_out.put(Commands.SUCCESS)
        else:
            q_out.put(Commands.FAILURE)



