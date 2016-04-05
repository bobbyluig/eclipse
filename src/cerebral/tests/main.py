#!/usr/bin/env python3.5

from cerebral.database import manager
from cerebral import logger as l
import logging


if __name__ == '__main__':
    manager.connect()

    logger = logging.getLogger('universe')
    logger.debug('Hello! This is an info log.')

    gps = manager.get('db.gps')
    print(gps)

    queue = manager.get('queue.logging')
    print(queue.get())

