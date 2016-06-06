from cerebral import logger as l

import Pyro4
from cerebral.nameserver import ports
from agility.gait import Dynamic
from cerebral.pack2.hippocampus import Android
from agility.main import Agility, ServoError
from threading import Thread, Lock, Event
from functools import lru_cache
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

        # Walking stuff.
        self.leg_stop = Event()
        self.new_vector = Event()
        self.leg_lock = Lock()
        self.vector = (0, 0)
        self.leg_thread = None

        # Head stuff.
        self.new_position = Event()
        self.head_thread = Thread(target=self._head)
        self.position = (0, 0)
        self.head_thread.start()

    def start_watch(self):
        """
        Readies the robot for executing vectors.
        :return: True if the thread was started, otherwise False.
        """

        if not self.leg_lock.acquire(blocking=False):
            return False

        try:
            if self.leg_thread is not None:
                return False

            self.leg_thread = Thread(target=self._watch)
            self.leg_thread.start()
        finally:
            self.leg_lock.release()

        return True

    def start_pushup(self):
        """
        Begins the pushup thread.
        :return: True if the thread was started, otherwise False.
        """

        if not self.leg_lock.acquire(blocking=False):
            return False

        try:
            if self.leg_thread is not None:
                return False

            self.leg_thread = Thread(target=self._pushup)
            self.leg_thread.start()
        finally:
            self.leg_lock.release()

        return True

    def emergency(self):
        """
        Force stop all wait in agility.
        """

        self.agility.stop()
        time.sleep(0.2)
        self.agility.clear()

    def stop(self):
        """
        Global stop. Stops all threads in module.
        :return: True if a thread exists and was stopped, False otherwise.
        """

        if not self.leg_lock.acquire(blocking=False):
            return False

        try:
            if self.leg_thread is None:
                return False

            # Set stop events.
            self.leg_stop.set()
            self.new_vector.set()

            # Wait for termination.
            self.leg_thread.join()
            self.leg_thread = None

            # Clear all events.
            self.leg_stop.clear()
            self.new_vector.clear()
        finally:
            self.leg_lock.release()

        return True

    def zero(self):
        """
        Calls the zero function of Agility.
        :return: True if function was executed, False otherwise.
        """

        if not self.leg_lock.acquire(blocking=False):
            return False

        try:
            if self.leg_thread is not None:
                return False

            self.agility.zero()
        finally:
            self.leg_lock.release()

        return True

    def lift_leg(self, leg, lift, t):
        """
        From the current pose, move the robot to lift a leg.
        :return: True if function was executed, False otherwise.
        """

        if not self.leg_lock.acquire(blocking=False):
            return False

        try:
            if self.leg_thread is not None:
                return False

            self.agility.lift_leg(leg, lift, t)
        finally:
            self.leg_lock.release()

        return True

    def target_point(self, leg, point, t):
        """
        Move a leg to a given point. Be careful.
        :return: True if function was executed, False otherwise.
        """

        if not self.leg_lock.acquire(blocking=False):
            return False

        try:
            if self.leg_thread is not None:
                return False

            self.agility.target_point(leg, point, t)
        finally:
            self.leg_lock.release()

        return True

    def set_head(self, position):
        """
        Set the position of the head.
        :param position: Input position (LR rotation, UD rotation).
        """

        if self.position != position:
            self.position = position
            self.new_position.set()

    def set_vector(self, vector):
        """
        Set the target vector.
        :param vector: Input vector of (forward, rotation).
        """

        if self.vector != vector:
            self.vector = vector
            self.new_vector.set()

    def _pushup(self):
        while not self.leg_stop.is_set():
            self.agility.move_body(0, 0, -4, 1000)
            self.agility.move_body(0, 0, 0, 1000)

    def _watch(self):
        self.agility.ready(self.gait.ground)

        while not self.leg_stop.is_set():
            vector = self.vector

            if vector == (0, 0):
                self.new_vector.wait()
                continue

            frames, dt = self._generate(vector)
            self.agility.execute_frames(frames, dt)

    @lru_cache()
    def _generate(self, vector):
        g = self.gait.generate(*vector)
        return self.agility.prepare_smoothly(g)

    def _head(self):
        while True:
            self.new_position.wait()
            position = self.position

            try:
                self.agility.set_head(position)
            except ServoError:
                pass

            self.new_position.clear()


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