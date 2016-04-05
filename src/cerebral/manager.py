from multiprocessing.managers import BaseManager


class MemoryManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, attr):
        if not hasattr(self, attr):
            self.register(attr)

        return getattr(self, attr)()


# Configure manager for import.
address = ('127.0.0.1', 31415)
authkey = b'cMAmn85PwdU8gUAc'
manager = MemoryManager(address=address, authkey=authkey)
