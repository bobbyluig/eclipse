from cerebral import logger as l

import Pyro4
import logging
from cerebral.nameserver import ports
from ares.main import RFID


# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])
Pyro4.config.SERIALIZER = 'pickle'

# Logging.
logger = logging.getLogger('universe')


class SuperAres:
    def __init__(self):
        self.rfid = RFID()

    def read(self):
        return self.rfid.read()


super_ares = SuperAres()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['worker3']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(super_ares, 'super_ares')

    # Log server event.
    logger.info('Worker 3 started!')

    # Start event loop.
    daemon.requestLoop()