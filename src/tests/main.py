#!/usr/bin/env python3.5

# Configure global logging.
import logging
import ssl

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth

# from agility.tests.crawl import Agility
from shared.autoreconnect import ApplicationRunner

##############################
# Create the main application.
##############################

logger = logging.getLogger('universe')

# Constants.
user = 'DOG-1E5'
password = 'de2432k,/s-=/8Eu'

# Agility.
from queue import Queue

q = Queue()
# agility = Agility(q)


class Cerebral(ApplicationSession):
    def onConnect(self):
        logger.info('Connected to server.')
        self.join(self.config.realm, ['wampcra'], user)

    def onChallenge(self, challenge):
        logger.info('Challenge received.')
        if challenge.method == 'wampcra':
            if 'salt' in challenge.extra:
                key = auth.derive_key(password.encode(),
                                      challenge.extra['salt'].encode(),
                                      challenge.extra.get('iterations', None),
                                      challenge.extra.get('keylen', None))
            else:
                key = password.encode()
            signature = auth.compute_wcs(key, challenge.extra['challenge'])
            return signature.decode('ascii')
        else:
            raise Exception('Unknown challenge method: %s' % challenge.method)

    async def onJoin(self, details):
        logger.info('Joined "%s" realm.' % self.config.realm)

        await self.register(self.identify, 'dog.identify')
        await self.register(self.hello, 'dog.hello')
        await self.register(self.walk, 'dog.walk')
        await self.register(self.pushup, 'dog.pushup')
        await self.register(self.stop, 'dog.stop')
        await self.register(self.home, 'dog.home')
        await self.register(self.blue_team, 'dog.blue_team')

    def onDisconnect(self):
        logger.warning('Connection lost!')

    ############
    # Functions.
    ############

    async def identify(self):
        self.call('zeus.speak', "Hello. I am DOG-1E5, Eclipse Technology's first generation quadruped. "
                                "I am designed for Project Lycanthrope by E D D Red Team 2016. "
                                "Rawr."
                  )
        logger.info('Executed identify().')

    async def hello(self):
        self.call('zeus.speak', "Hello world!")
        logger.info('Executed hello().')

    async def blue_team(self):
        self.call('zeus.speak', "I could not find Blue Team's robot. Robot does not exist.")
        logger.info('Executed blue_team().')

    async def walk(self):
        self.call('zeus.speak', "Executing walking sequence.")
        agility.walk()
        logger.info('Executed walk().')

    async def pushup(self):
        self.call('zeus.speak', "Executing push-ups.")
        agility.pushup()
        logger.info('Executed pushup().')

    async def stop(self):
        agility.stop()
        logger.info('Executed stop().')

    async def home(self):
        agility.home()
        logger.info('Executed home().')


if __name__ == '__main__':
    ip = '127.0.0.1'

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False
    pem = ssl.get_server_certificate((ip, 443))
    context.load_verify_locations(cadata=pem)

    runner = ApplicationRunner(url='wss://%s/ws' % ip, realm='lycanthrope',
                               ssl=context)

    runner.run(Cerebral)
