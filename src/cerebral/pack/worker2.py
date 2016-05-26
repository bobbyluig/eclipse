from cerebral import logger as l
import logging

import Pyro4
from cerebral.nameserver import ports

from theia.main import Oculus, Theia
from theia.eye import Eye, Camera
from cerebral.pack.hippocampus import Android

from threading import Thread, Lock, Event

# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])
Pyro4.config.SERIALIZER = 'pickle'

# Logging.
logger = logging.getLogger('universe')


class SuperTheia:
    def __init__(self):
        self.eye = Eye(Android.camera)
        self.oculus = None

        # Current status.
        self.found = False
        self.position = None
        self.center = None

        # Event and lock.
        self.event = Event()
        self.event2 = Event()
        self.lock = Lock()

        # Start.
        self.thread = None

    def start_track(self, frame):
        with self.lock:
            if self.thread is None:
                self.thread = Thread(target=self._track)
                self.thread.start()
                return True

        return False

    def find(self):
        with self.lock:
            # Ensure tracker is not running.
            if self.thread is not None:
                return None

            # Reset.
            self.found = False
            self.position = None
            self.center = None
            self.event2.clear()
            self.oculus = Oculus()

        # Locate the moving object.
        blob = None
        frame = None

        # Loop until capture.
        while blob is None and not self.event2.is_set():
            mask, frame = Theia.get_foreground(self.eye, 100, self.event)

            # Check early exit condition.
            if mask is not None:
                blob = Theia.bound_blobs(mask, 1)
            else:
                return None

        # Check early exit condition.
        if blob is None:
            return None

        # Blob exists.
        bb = blob[0]

        # Initialize tracker with bounding box.
        success = self.oculus.initialize(frame, bb)

        if not success:
            logger.error('Unable to initialize tracker. Stopping Theia.')
            return None
        else:
            if not self.start_track(frame):
                return None
            else:
                return bb

    def stop_find(self):
        self.event2.set()
        return True

    def stop_track(self):
        with self.lock:
            if self.thread is not None:
                self.event.set()
                self.thread.join()
                self.thread = None
                self.event.clear()
                return True

        return False

    def get_status(self):
        return self.found, self.position, self.center

    def _track(self):
        while not self.event.is_set():
            frame = self.eye.get_color_frame()
            self.found, self.position, self.center = self.oculus.track(frame)


super_theia = SuperTheia()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker2']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(super_theia, 'super_theia')

    # Start event loop.
    daemon.requestLoop()