from cerebral.manager import manager
import logging
from logging.handlers import QueueHandler
from concurrent.futures import ThreadPoolExecutor


class Handler(QueueHandler):
    """
    An asyncio friendly logging handler that also works outside of the event loop.
    """

    def __init__(self, *args, **kwargs):
        self.executor = ThreadPoolExecutor(max_workers=2)
        super().__init__(*args, **kwargs)

    def prepare(self, record):
        msg = self.format(record)
        return msg

    def enqueue(self, record):
        self.executor.submit(self.queue.put_nowait, record)


# Register and connect to manager.
manager.register('queue.logging')
manager.connect()

# Obtain logging queue.
queue = manager.get('queue.logging')

# Configure logging.
logger = logging.getLogger('universe')
handler = Handler(queue)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)