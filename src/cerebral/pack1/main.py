#!/usr/bin/env python3.5

from cerebral import logger as l

import asyncio
import logging
import ssl
import time
import os
import socket

from autobahn.asyncio.wamp import ApplicationSession
from autobahn import wamp
from autobahn.wamp import auth
from shared.autoreconnect import ApplicationRunner
from concurrent.futures import ThreadPoolExecutor

from cerebral.pack1.hippocampus import Crossbar

import Pyro4
from cerebral.nameserver import lookup

logger = logging.getLogger('universe')


class Cerebral(ApplicationSession):
    def __init__(self, *args, **kwargs):
        # Path for dynamic spawning.
        self.root = os.path.dirname(__file__)

        # Get loop.
        self.loop = asyncio.get_event_loop()

        # Get remote objects.
        self.super_agility = Pyro4.Proxy(lookup('worker1', 'super_agility'))
        self.super_ares = Pyro4.Proxy(lookup('worker3', 'super_ares'))

        # Create a thread executor for slightly CPU-bound async functions.
        self.executor = ThreadPoolExecutor(20)

        # Init parent.
        super().__init__(*args, **kwargs)

    def onConnect(self):
        logger.info('Connected to server.')
        self.join(self.config.realm, ['wampcra'], Crossbar.authid)

    def onChallenge(self, challenge):
        logger.debug('Challenge received.')
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
        logger.info('Joined "%s" realm.' % self.config.realm)

        # Register all procedures.
        self.register(self)

        # Start logging.
        self.run(self.watch_logging)

    def onDisconnect(self):
        logger.info('Connection lost!')

    ####################
    # Special functions.
    ####################

    def run(self, fn, *args, **kwargs):
        return asyncio.wrap_future(self.executor.submit(fn, *args, **kwargs))

    ########################
    # Main remote functions.
    ########################

    @wamp.register('{}.read_rfid'.format(Crossbar.prefix))
    async def read_rfid(self):
        future = self.run(self.super_ares.read)
        data = await future

        if data is None:
            return False
        else:
            return data

    @wamp.register('{}.set_vector'.format(Crossbar.prefix))
    async def set_vector(self, a, b):
        await self.run(self.super_agility.set_vector, (a, b))
        return True

    @wamp.register('{}.set_head'.format(Crossbar.prefix))
    async def set_head(self, a, b):
        await self.run(self.super_agility.set_head, (a, b))
        return True

    @wamp.register('{}.stop'.format(Crossbar.prefix))
    async def stop(self):
        future = self.run(self.super_agility.stop)
        success = await future
        return success

    @wamp.register('{}.pushup'.format(Crossbar.prefix))
    async def pushup(self):
        future = self.run(self.super_agility.start_pushup)
        success = await future
        return success

    @wamp.register('{}.start_watch'.format(Crossbar.prefix))
    async def start_watch(self):
        future = self.run(self.super_agility.start_watch)
        success = await future
        return success

    @wamp.register('{}.zero'.format(Crossbar.prefix))
    async def zero(self):
        future = self.run(self.super_agility.zero)
        success = await future
        return success

    #####################
    # Blocking functions.
    #####################

    def watch_logging(self):
        uri = lookup('database', 'logging')
        queue = Pyro4.Proxy(uri)

        while True:
            message = queue.get()
            topic = '{}.log'.format(Crossbar.prefix)
            self.publish(topic, *message)

if __name__ == '__main__':
    # Configure SSL.
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.check_hostname = False
    pem = ssl.get_server_certificate((Crossbar.ip, 443))
    context.load_verify_locations(cadata=pem)

    # Create application runner.
    runner = ApplicationRunner(url='wss://%s/ws' % Crossbar.ip, realm=Crossbar.realm,
                               ssl=context)

    # Run forever.
    runner.run(Cerebral)
