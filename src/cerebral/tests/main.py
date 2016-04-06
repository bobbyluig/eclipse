#!/usr/bin/env python3.5

from cerebral.database import manager
from cerebral import logger as l
import logging
import time


if __name__ == '__main__':
    manager.connect()

    logger = logging.getLogger('universe')
    logger.debug('Hello! This is an info log.')

    gps = manager.get('db.gps')

    start = time.time()
    for i in range(10000):
        x = gps['valid']
    print(time.time() - start)

    queue = manager.get('queue.logging')
    print(dir(queue))
