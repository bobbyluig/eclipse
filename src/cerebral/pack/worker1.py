from cerebral import logger as l

import Pyro4
from cerebral.nameserver import ports
from agility.gait import Dynamic
from cerebral.pack.hippocampus import Android
from agility.main import Agility
from threading import Thread, Lock, Event

# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])


class SuperAgility:
    def __init__(self):
        self.robot = Android.robot
        self.agility = Agility(self.robot)
        self.gait = Dynamic(self.robot.body)

        # Event and lock.
        self.event = Event()
        self.lock = Lock()

        # Target vector
        self.vector = (0, 0)

        # Cache.
        self.cache = {}

        # Thread.
        self.thread = None

    def start_watch(self):
        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self.watch)
                self.thread.start()
                return True

        return False

    def stop(self):
        with self.lock:
            if self.thread is not None:
                self.event.set()
                self.thread.join()
                self.thread = None
                return True

        return False

    def zero(self):
        with self.lock:
            if self.thread is None:
                self.agility.zero()
                return True

        return False

    def watch(self):
        while not self.event.is_set():
            vector = self.vector

            if vector == (0, 0):
                return

            id = hash(vector)

            if id in self.cache:
                frames, dt = self.cache[id]
            else:
                points = self.gait.generate(*vector)
                frames, dt = self.agility.prepare_smoothly(points)
                self.cache[id] = (frames, dt)

            self.agility.execute_frames(frames, dt)


agility = SuperAgility()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker1']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(agility, 'agility')

    # Start event loop.
    daemon.requestLoop()