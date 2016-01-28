from multiprocessing.managers import BaseManager


class QueueManager(BaseManager):
    def __init__(self, *args, **kwargs):
        for i in range(4):
            self.register('queue%s' % i)

        super().__init__(*args, **kwargs)


class SharedMemory:
    def __init__(self, address, authkey):
        self.manager = QueueManager(address=address, authkey=authkey)
        self.manager.connect()

    def get_queue(self, i):
        try:
            return getattr(self.manager, 'queue%s' % i)()
        except AttributeError:
            return None




