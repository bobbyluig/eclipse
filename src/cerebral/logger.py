from cerebral.manager import manager
import logging
from logging.handlers import QueueHandler

# Register and connect to manager.
manager.register('queue.logging')
manager.connect()

# Obtain logging queue.
queue = manager.get('queue.logging')

# Configure logging.
logger = logging.getLogger('universe')
handler = QueueHandler(queue)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)