import queue
import Pyro4
from cerebral.nameserver import ports


# Configure pyro.
Pyro4.config.SERIALIZERS_ACCEPTED = frozenset(['pickle', 'serpent'])

# Logging queue.
queue = queue.Queue()


if __name__ == '__main__':
    # Create a daemon.
    port = ports['database']
    daemon = Pyro4.Daemon('localhost', port)

    # Register all objects.
    daemon.register(queue, 'logging')

    # Start event loop.
    daemon.requestLoop()