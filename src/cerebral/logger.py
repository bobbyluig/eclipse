import Pyro4
import logging
from logging.handlers import QueueHandler
from cerebral.nameserver import lookup


class Handler(QueueHandler):
    """
    An asynchronous logger using a proxy-based queue.
    """

    def prepare(self, record):
        msg = self.format(record)
        return msg

# Configure pyro.
Pyro4.config.SERIALIZER = 'pickle'

# Connect to queue.
uri = lookup('database', 'logging')
proxy = Pyro4.Proxy(uri)
proxy._pyroTimeout = 1.0
queue = Pyro4.async(proxy)

# Configure logging.
logger = logging.getLogger('universe')
handler = Handler(queue)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)