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

# Generate gait.
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
crawl_sequence = {
    'frame_time': 150,
    'length': 8
}
for i in range(4):
    q = deque(crawl)
    q.rotate(-2 * i)
    crawl_sequence['leg%s' % i] = list(q)

# Threading variables.
run = False

# Thread functions.
def animate(sequence):
    while run:
        agility.animate_synchronized(sequence)

# Global thread.
thread = Thread()

# Worker is ready.
q_out.put(Commands.WORKER_READY)

# Main.
while True:
    # Block main thread until a command is received.
    cmd = q_in.get()

    if cmd == Commands.WALK_FORWARD:
        run = True
        thread = Thread(target=animate, args=(crawl_sequence,))
        thread.start()

    elif cmd == Commands.STOP:
        run = False


