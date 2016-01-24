from multiprocessing.managers import BaseManager
import queue
import os


class QueueManager(BaseManager):
    pass

if __name__ == '__main__':
    q = queue.Queue()
    QueueManager.register('get_queue', callable=lambda: q)

    q.put('WOOOOOOO')

    if os.name == 'nt':
        # Running on Windows, create a pipe.
        address = '\\\\.\\pipe\\eclipse'
    else:
        # Running on Linux, create a socket.
        address = 'listener-eclipse'

    m = QueueManager(address=address, authkey=b'eclipse4lyfe')
    s = m.get_server()
    s.serve_forever()


