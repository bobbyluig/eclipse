#!/usr/bin/env python3.5

import os
from cerebral.manager import SharedManager


if __name__ == '__main__':
    # Change directory.
    root = os.path.dirname(__file__)

    address = ('127.0.0.1', 31415)
    authkey = b'cMAmn85PwdU8gUAc'

    m = SharedManager(address=address, authkey=authkey)
    m.connect()

    proxy = m.pub_proxy()

    proxy.publish('a', 'b')
    print(dir(proxy))
