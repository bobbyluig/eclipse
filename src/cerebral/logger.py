from cerebral.manager import manager
import logging
import asyncio
from logging.handlers import QueueHandler


class Handler(QueueHandler):
    """
    An asyncio friendly logging handler that also works outside of the event loop.
    """

    def prepare(self, record):
        msg = self.format(record)
        return msg

    def enqueue(self, record):
        loop = asyncio.get_event_loop()

        if loop.is_running():
            loop.run_in_executor(None, self.queue.put_nowait, record)
        else:
            self.queue.put_nowait(record)


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