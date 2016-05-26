# from cerebral import logger as l

import Pyro4
from cerebral.nameserver import ports
from agility.gait import Dynamic
from cerebral.pack.hippocampus import Android
from agility.main import Agility
from threading import Thread, Lock, Event
import time

# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])
Pyro4.config.SERIALIZER = 'pickle'


class SuperAgility:
    def __init__(self, agility):
        self.robot = Android.robot
        self.agility = agility
        self.gait = Dynamic(self.robot.body)

        # Event and lock.
        self.event = Event()
        self.lock = Lock()

        # Target vector.
        self.vector = (0, 0)

        # Thread.
        self.thread = None

    def start_watch(self):
        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self._watch)
                self.thread.start()
                return True

        return False

    def start_pushup(self):
        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self._pushup)
                self.thread.start()
                return True

        return False

    def stop(self):
        with self.lock:
            if self.thread is not None:
                self.event.set()
                self.thread.join()
                self.thread = None
                self.event.clear()
                return True

        return False

    def zero(self):
        with self.lock:
            if self.thread is None:
                self.agility.zero()
                return True

        return False

    def _prepare(self):
        with self.lock:
            if self.thread is None:
                self.agility.ready(self.gait.ground)
                return True

        return False

    def set_vector(self, vector):
        self.vector = vector

    def _pushup(self):
        while not self.event.is_set():
            self.agility.move_body(0, 0, -4, 1000)
            self.agility.move_body(0, 0, 0, 1000)

    def _watch(self):
        self._prepare()

        while not self.event.is_set():
            vector = self.vector

            if vector == (0, 0):
                time.sleep(0.001)
                continue

            g = self.gait.generate(*vector)
            frames, dt = self.agility.prepare_smoothly(g)

            self.agility.execute_frames(frames, dt)


agility = Agility(Android.robot)
super_agility = SuperAgility(agility)


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker1']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(agility, 'agility')
    daemon.register(super_agility, 'super_agility')

    # Start event loop.
    daemon.requestLoop()