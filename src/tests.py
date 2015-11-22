from agility.maestro import *
import time

if __name__ == '__main__':
    maestro = Maestro()

    print(maestro.get_errors())
    maestro.stop_script()
    # maestro.restart(0)

