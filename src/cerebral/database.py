from cerebral.manager import manager
from multiprocessing.managers import DictProxy, ListProxy
import queue


#######################
# Registration helpers.
#######################

def register(cls, item):
    if type(item) is list:
        manager.register(cls, callable=lambda: item, proxytype=ListProxy)
    elif type(item) is dict:
        manager.register(cls, callable=lambda: item, proxytype=DictProxy)
    elif not callable(item):
        manager.register(cls, callable=lambda: item)
    else:
        manager.register(cls, item)

##################
# Logging systems.
##################

logging_queue = queue.Queue()

register('queue.logging', logging_queue)

###################
# Position systems.
###################

gps = {
    'valid': False,             # Is the current position valid? (Is tracking successful?)
    'position': (0, 0, 0),      # Current position of robot, in (x, y, z).
    'last_update': 0,           # When position was last valid. A cache for time.time() at acquisition.
}

register('db.gps', gps)

#################
# Vision systems.
#################

vision = {
    'target': (0, 0),           # Position of tracked target, in (x, y).
    'valid': False,             # Whether the tracking was successful.
}

register('db.vision', vision)

##################
# Walking systems.
##################

motion = {
    'gait': 0,                  # Gait number, as defined by Agility.
    'vector': (0, 0),           # Walking target. Either (x, y) or (dx/dt, dy/dt, dr/dt).
}

register('db.motion', motion)

###########################
# Create server, and serve!
###########################

if __name__ == '__main__':
    server = manager.get_server()
    server.serve_forever()