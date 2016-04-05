from multiprocessing.managers import BaseManager
import queue


class MemoryManager(BaseManager):
    pass


#################
# Vision systems.
#################

vision = {
    'target': (0, 0),           # Position of tracked target, in (x, y).
}

MemoryManager.register('db.vision', callable=lambda: vision)

##################
# Walking systems.
##################

motion = {
    'gait': 0,                  # Gait number, as defined by Agility.
    'vector': (0, 0),           # Walking target. Either (x, y) or (dx/dt, dy/dt, dr/dt).
}

MemoryManager.register('db.motion', callable=lambda: motion)

###########################
# Create server, and serve!
###########################

if __name__ == '__main__':
    address = ('127.0.0.1', 31415)
    authkey = b'cMAmn85PwdU8gUAc'

    m = MemoryManager(address=address, authkey=authkey)
    s = m.get_server()
    s.serve_forever()