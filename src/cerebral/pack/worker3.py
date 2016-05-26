from cerebral import logger as l

import logging

import Pyro4
from ares.main import Ares
from cerebral.nameserver import lookup, ports
from cerebral.pack.hippocampus import Android
from threading import RLock, Thread, Event
import time

# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])
Pyro4.config.SERIALIZER = 'pickle'

super_agility = Pyro4.Proxy(lookup('worker1', 'super_agility'))
agility = Pyro4.Proxy(lookup('worker1', 'agility'))
super_theia = Pyro4.Proxy(lookup('worker2', 'super_theia'))


class SuperAres:
    def __init__(self):
        self.ares = Ares(Android.robot, Android.camera, Android.info)

        self.thread = None
        self.lock = RLock()
        self.event = Event()

    def start_follow(self):
        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self._follow)
                self.thread.start()
                return True

        return False

    def stop(self):
        with self.lock:
            super_agility.stop()
            super_theia.stop_track()
            super_theia.stop_find()

            if self.thread is not None:
                self.event.set()
                self.thread.join()
                self.thread = None
                self.event.clear()

        return True

    def _follow(self):
        # Stop robot, zero, and center head.
        super_agility.stop()
        super_agility.set_vector((0, 0))
        agility.center_head()

        if self.event.is_set():
            return

        # Find thing to follow.
        blob = super_theia.find()

        if blob is None:
            return

        # Get target information.
        target_area = blob[2] * blob[3]

        # Begin gait watcher.
        super_agility.start_watch()

        # Main loop.
        lost_counter = 0

        while not self.event.is_set():
            found, bb, center = super_theia.get_status()

            if found:
                lost_counter = 0

                # Target is good. First, get current data.
                hr = agility.head_rotation()
                area = bb[2] * bb[3]
                x = center[0]

                # Set head. This is more important than moving.
                head_data = agility.look_at(center[0], center[1])
                agility.move_head(head_data)

                # Compute and set the direction vector.
                vector = self.ares.compute_vector(target_area, area, x, hr)
                super_agility.set_vector(vector)
            else:
                lost_counter += 1

                if lost_counter > 10:
                    # A lot of lost frames. Target is probably out of head range. Center head, rotate body.
                    agility.center_head()
                    super_agility.set_vector((0, 0.15))
                elif center is not None:
                    # Might have temporarily gone out of view. Scan head, auto velocity control.
                    agility.look_at(center[0], center[1])
                    agility.scan(0)

            # Rest a bit. You don't need to go super super fast.
            # Like, human response time is around 200 ms.
            time.sleep(0.05)


super_ares = SuperAres()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker3']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(super_ares, 'super_ares')

    # Start event loop.
    daemon.requestLoop()
