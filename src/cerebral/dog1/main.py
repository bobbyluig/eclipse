#!/usr/bin/env python3.5

import asyncio
import logging
import ssl
import time
import os
import sys
from psutil import pid_exists
from subprocess import Popen
from functools import partial

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from tools.autoreconnect import ApplicationRunner
from concurrent.futures import ThreadPoolExecutor

from cerebral.dog1.hippocampus import Crossbar, Conversation, Manager
from cerebral.dog1.commands import Commands
from tools.pid import pidfile_exists
from tools.queue import SharedMemory


class Cerebral(ApplicationSession):
    def __init__(self, *args, **kwargs):
        # Create a thread executor for slightly CPU-bound async functions.
        self.executor = ThreadPoolExecutor(10)

        # Get queues
        self.shared = SharedMemory(Manager.address, Manager.authkey)
        self.q_out = self.shared.get_queue(1)       # To Worker1
        self.q_in = self.shared.get_queue(2)        # From Worker1

        # Init parent.
        super().__init__(*args, **kwargs)

    def onConnect(self):
        print('Connected to server.')
        self.join(self.config.realm, ['wampcra'], Crossbar.authid)

    def onChallenge(self, challenge):
        print('Challenge received.')
        if challenge.method == 'wampcra':
            if 'salt' in challenge.extra:
                key = auth.derive_key(Crossbar.secret.encode(),
                                      challenge.extra['salt'].encode(),
                                      challenge.extra.get('iterations', None),
                                      challenge.extra.get('keylen', None))
            else:
                key = Crossbar.secret.encode()
            signature = auth.compute_wcs(key, challenge.extra['challenge'])
            return signature.decode('ascii')
        else:
            raise Exception('Unknown challenge method: %s' % challenge.method)

    async def onJoin(self, details):
        print('Joined "%s" realm.' % self.config.realm)

        await self.register(self.initialize, 'dog1.initialize')
        await self.register(self.walk, 'dog1.walk')
        await self.register(self.stop, 'dog1.stop')
        await self.register(self.converse, 'dog1.converse')

    def onDisconnect(self):
        print('Connection lost!')

    ##########
    # Helpers.
    ##########

    async def get_queue(self, queue, block=True, timeout=None):
        loop = asyncio.get_event_loop()
        func = partial(queue.get, block=block, timeout=timeout)
        result = await loop.run_in_executor(self.executor, func)
        return result

    async def put_queue(self, queue, item, block=True, timeout=None):
        loop = asyncio.get_event_loop()
        func = partial(queue.put, item, block=block, timeout=timeout)
        result = await loop.run_in_executor(self.executor, func)
        return result

    ############
    # Functions.
    ############

    async def converse(self, phrase):
        response = Conversation.topics.get(phrase.lower())
        if response is not None:
            self.publish('dog1.info', response)
        else:
            self.publish('dog1.info', 'I do not understand that command.')

    async def initialize(self):
        reply = await self.get_queue(self.q_in, timeout=10)
        if reply == Commands.WORKER_READY:
            self.publish('dog1.info', 'Worker successfully started.')
        else:
            self.publish('dog1.info', 'Failed to start worker.')

    async def walk(self):
        await self.put_queue(self.q_out, Commands.WALK_FORWARD)

    async def stop(self):
        await self.put_queue(self.q_out, Commands.STOP)


if __name__ == '__main__':
    # Change directory.
    root = os.path.dirname(__file__)
    os.chdir(root)

    # Check if manager already exists.
    pid_path = os.path.abspath(os.path.join(root, '..', 'manager.pid'))
    process_path = os.path.abspath(os.path.join(root, '..', 'manager.py'))
    if not pidfile_exists(pid_path):
        process = Popen([sys.executable, process_path])
        time.sleep(0.5)
        if not pid_exists(process.pid):
            raise Exception('Unable to spawn manager process.')
        else:
            with open(pid_path, 'w') as f:
                f.write(str(process.pid))

    # Start worker1.
    pid_path = os.path.abspath(os.path.join(root, 'worker1.pid'))
    process_path = os.path.abspath(os.path.join(root, 'worker1.py'))
    if not pidfile_exists(pid_path):
        process = Popen([sys.executable, process_path])
        time.sleep(0.5)
        if not pid_exists(process.pid):
            raise Exception('Unable to spawn worker1 process.')
        else:
            with open(pid_path, 'w') as f:
                f.write(str(process.pid))

    # Configure SSL.
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False
    pem = ssl.get_server_certificate((Crossbar.ip, 443))
    context.load_verify_locations(cadata=pem)

    # Create application runner.
    runner = ApplicationRunner(url='wss://%s/ws' % Crossbar.ip, realm=Crossbar.realm,
                               ssl=context)

    # Run forever.
    runner.run(Cerebral)
