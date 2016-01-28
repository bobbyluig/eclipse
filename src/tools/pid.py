from psutil import pid_exists
import os.path


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


def pid_spawn(base, file):
    pass