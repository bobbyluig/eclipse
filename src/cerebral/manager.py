from multiprocessing.managers import BaseManager
import queue
import os
from psutil import pid_exists


class QueueManager(BaseManager):
    pass

if __name__ == '__main__':
    q1 = queue.Queue()
    q2 = queue.Queue()
    q3 = queue.Queue()
    q4 = queue.Queue()
    QueueManager.register('queue1', callable=lambda: q1)
    QueueManager.register('queue2', callable=lambda: q2)
    QueueManager.register('queue3', callable=lambda: q3)
    QueueManager.register('queue4', callable=lambda: q4)

    if os.name == 'nt':
        # Running on Windows, create a pipe.
        address = '\\\\.\\pipe\\eclipse'
    else:
        # Running on Linux, create a socket.
        address = 'listener-eclipse'

    m = QueueManager(address=address, authkey=b'eclipse4lyfe')
    s = m.get_server()
    s.serve_forever()
