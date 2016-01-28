#!/usr/bin/env python3.5

import os
import sys
import socket
from subprocess import Popen
import psutil
import time

if __name__ == '__main__':
    # Get the current directory.
    root = os.path.dirname(__file__)

    # Try to determine robot automatically.
    hostname = socket.gethostname()

    robots = {
        'DOG-1E5': os.path.join(root, 'cerebral', 'dog1', 'main.py'),
        'DOG-4S1': os.path.join(root, 'cerebral', 'dog4', 'main.py'),
        'ALPHA': os.path.join(root, 'cerebral', 'alpha', 'main.py')
    }

    file = robots.get(hostname.upper())

    if file is None:
        # Unknown hostname. Manually enter host.
        print('Unable to determine host system. Please manually indicate the robot type.')
        print('Choices: ' + ', '.join(sorted(list(robots.keys()))) + '.')
        s = input('> ')

        file = robots.get(s.upper())

        if file is None:
            print('Invalid choice "%s".' % s)
            sys.exit(0)

    process = Popen([sys.executable, file])

    time.sleep(0.5)

    if not psutil.pid_exists(process.pid):
        print('Error. Event loop spawning failed.')

