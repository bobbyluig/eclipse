from cerebral.manager import manager
import queue


##################
# Logging systems.
##################

logging_queue = queue.Queue()

manager.register('queue.logging', callable=lambda: logging_queue)

###################
# Position systems.
###################

gps = {
    'valid': False,             # Is the current position valid? (Is tracking successful?)
    'position': (0, 0, 0),      # Current position of robot, in (x, y, z).
    'last_update': 0,           # When position was last valid. A cache for time.time() at acquisition.
}

manager.register('db.gps', callable=lambda: gps)

#################
# Vision systems.
#################

vision = {
    'target': (0, 0),           # Position of tracked target, in (x, y).
    'valid': False,             # Whether the tracking was successful.
}

manager.register('db.vision', callable=lambda: vision)

##################
# Walking systems.
##################

motion = {
    'gait': 0,                  # Gait number, as defined by Agility.
    'vector': (0, 0),           # Walking target. Either (x, y) or (dx/dt, dy/dt, dr/dt).
}

manager.register('db.motion', callable=lambda: motion)

###########################
# Create server, and serve!
###########################

if __name__ == '__main__':
    address = ('127.0.0.1', 31415)
    authkey = b'cMAmn85PwdU8gUAc'

    server = manager.get_server()
    server.serve_forever()