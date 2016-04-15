#!/usr/bin/env python3.5

from cerebral.database import manager
from cerebral import logger as l
import logging
import time


if __name__ == '__main__':
    manager.connect()

    logger = logging.getLogger('universe')
    logger.debug('Hello! This is an info log.')

    queue = manager.get('queue.logging')
    while True:
        print(queue.get())
