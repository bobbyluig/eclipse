from psutil import pid_exists
import os.path
from subprocess import Popen
import time
import sys


def pidfile_exists(file):
    if not os.path.isfile(file):
        return False

    with open(file, 'r') as f:
        pid = f.read()

        try:
            pid = int(pid)
        except ValueError:
            return False

    return pid_exists(pid)


def pid_spawn(path, name):
    pid_path = os.path.abspath(os.path.join(path, '%s.pid' % name))
    process_path = os.path.abspath(os.path.join(path, '%s.py' % name))
    if not pidfile_exists(pid_path):
        process = Popen([sys.executable, process_path])
        time.sleep(0.5)
        if not pid_exists(process.pid):
            return False
        else:
            with open(pid_path, 'w') as f:
                f.write(str(process.pid))
            return True

    return True