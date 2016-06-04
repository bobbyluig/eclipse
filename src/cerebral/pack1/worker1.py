from cerebral import logger as l

import Pyro4
from cerebral.nameserver import ports
from agility.gait import Dynamic
from cerebral.pack1.hippocampus import Android
from agility.main import Agility
from threading import Thread, Lock, Event
import time
import logging


# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])
Pyro4.config.SERIALIZER = 'pickle'

# Logging.
logger = logging.getLogger('universe')


class SuperAgility:
    def __init__(self):
        self.robot = Android.robot
        self.agility = Agility(self.robot)
        self.gait = Dynamic(self.robot)

        # Event and lock.
        self.event = Event()
        self.lock = Lock()

        # Target vector.
        self.vector = (0, 0)

        # Thread.
        self.thread = None

    def start_watch(self):
        """
        Readies the robot for executing vectors.
        :return: True if the thread was started, otherwise False.
        """

        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self._watch)
                self.thread.start()
                return True

        return False

    def start_pushup(self):
        """
        Begins the pushup thread.
        :return: True if the thread was started, otherwise False.
        """

        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self._pushup)
                self.thread.start()
                return True

        return False

    def stop(self):
        """
        Global stop. Stops all threads in module.
        :return: True if a thread exists and was stopped, False otherwise.
        """

        with self.lock:
            if self.thread is not None:
                self.event.set()
                self.thread.join()
                self.thread = None
                self.event.clear()
                return True

        return False

    def zero(self):
        """
        Calls the zero function of Agility.
        :return: True if function was executed, False otherwise.
        """

        with self.lock:
            if self.thread is None:
                self.agility.zero()
                return True

        return False

    def set_head(self, position):
        """
        Set the position of the head.
        :param position: Input position (LR rotation, UD rotation).
        """

        self.agility.set_head(position)

    def set_vector(self, vector):
        """
        Set the target vector.
        :param vector: Input vector of (forward, rotation).
        """

        self.vector = vector

    def _pushup(self):
        while not self.event.is_set():
            self.agility.move_body(0, 0, -4, 1000)
            self.agility.move_body(0, 0, 0, 1000)

    def _watch(self):
        self.agility.ready(self.gait.ground)

        prev_hash = hash((0, 0))
        prev = None

        while not self.event.is_set():
            vector = self.vector

            if vector == (0, 0):
                time.sleep(0.001)
                continue

            if hash(vector) == prev_hash and prev is not None:
                frames, dt = prev
            else:
                g = self.gait.generate(*vector)
                frames, dt = self.agility.prepare_smoothly(g)
                prev = frames, dt

            self.agility.execute_frames(frames, dt)


super_agility = SuperAgility()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker1']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(super_agility, 'super_agility')

    # Log server event.
    logger.info('Worker 1 started!')

    # Start event loop.
    daemon.requestLoop()