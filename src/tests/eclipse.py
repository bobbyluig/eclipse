import os
import sys
import socket
from subprocess import Popen


def spawn_python(file):
    """
    Spawn a detached Python process using the same interpreter.
    :param file: The Python file name relative to this file's path.
    :return: A Popen object representing the opened process.
    """

    return Popen([sys.executable, file])


if __name__ == '__main__':
    #


    # Change to the correct directory.
    os.chdir(os.path.dirname(__file__))

    print(sys.executable)