#!/usr/bin/env python3.5

from cerebral import logger as l

import asyncio
import logging
import ssl
import time
import os

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from shared.autoreconnect import ApplicationRunner
from concurrent.futures import ThreadPoolExecutor

from cerebral.pack.hippocampus import Crossbar


logger = logging.getLogger('universe')


class Cerebral(ApplicationSession):
    def __init__(self, *args, **kwargs):
        # Path for dynamic spawning.
        self.root = os.path.dirname(__file__)

        # Get loop.
        self.loop = asyncio.get_event_loop()

        # Create a thread executor for slightly CPU-bound async functions.
        self.executor = ThreadPoolExecutor(20)
        self.loop.set_default_executor(self.executor)

        # Init parent.
        super().__init__(*args, **kwargs)

    def onConnect(self):
        logger.info('Connected to server.')
        self.join(self.config.realm, ['wampcra'], Crossbar.authid)

    def onChallenge(self, challenge):
        logger.info('Challenge received.')
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
        self.register(self)
        await self.loop.run_in_executor(None, self.watch_logging)

    def onDisconnect(self):
        logger.info('Connection lost!')

    #####################
    # Blocking Functions.
    #####################

    def watch_logging(self):
        queue = self.manager.get('queue.logging')

        while True:
            message = queue.get()
            topic = '{}.log'.format(Crossbar.prefix)
            self.publish(topic, message)
            print(message)


    ############
    # Functions.
    ############

if __name__ == '__main__':
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
