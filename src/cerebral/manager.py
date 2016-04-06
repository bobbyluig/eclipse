from multiprocessing.managers import BaseManager
import asyncio
from functools import partial


class MemoryManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, attr):
        if not hasattr(self, attr):
            self.register(attr)

        return getattr(self, attr)()

    def call(self, attr, *args, **kwargs):
        if not hasattr(self, attr):
            self.register(attr)

        return getattr(self, attr)(*args, **kwargs)


# Configure manager for import.
address = ('127.0.0.1', 31415)
authkey = b'cMAmn85PwdU8gUAc'
manager = MemoryManager(address=address, authkey=authkey)
