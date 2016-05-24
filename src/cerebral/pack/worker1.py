from cerebral import logger as l

import Pyro4
from cerebral.nameserver import ports
from agility.gait import Dynamic
from cerebral.pack.hippocampus import Android
from agility.main import Agility
from threading import Thread, Lock, Event

# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])


class Movement:
    def __init__(self):
        self.robot = Android.robot
        self.agility = Agility(self.robot)
        self.gait = Dynamic(self.robot.body)

        # Lock and event.
        self.lock = Lock()
        self.event = Event()

        # Target vector
        self.vector = (0, 0)

        # Cache.
        self.cache = {}

        # Thread.
        self.thread = Thread(target=self.run)

    def start(self):
        try:
            self.event.clear()
            self.thread.start()
            return True
        except RuntimeError:
            return False

    def stop(self):
        self.vector = (0, 0)
        self.event.set()
        self.thread.join()
        self.thread = Thread(target=self.run)

        return True

    def zero(self):
        self.stop()

        with self.lock:
            self.agility.zero()

        return True

    def set_target(self, target):
        self.vector = target

        return True

    def run(self):
        while not self.event.is_set():
            vector = self.vector

            if vector == (0, 0):
                return

            id = hash(vector)

            if id in self.cache:
                frames, dt = self.cache[id]
            else:
                points = self.gait.generate(*vector)
                frames, dt = self.agility.prepare_gait(points)
                self.cache[id] = (frames, dt)

            with self.lock:
                self.agility.execute_frames(frames, dt)


movement = Movement()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker1']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(movement, 'movement')

    # Start event loop.
    daemon.requestLoop()