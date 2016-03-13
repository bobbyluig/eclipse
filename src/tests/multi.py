#!/usr/bin/env python3.5

# Configure global logging.
import asyncio
import logging
import multiprocessing as mp
import ssl
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth

from agility.main import Leg, Robot, Servo
from lykos.apollo import Apollo
from shared.autoreconnect import ApplicationRunner

######################
# Linguistics library.
######################

conversation = {
    'hello': "Hello World!",
    'identify': "Hello. I am DOG-1E5, Eclipse Technology's first generation quadruped. "
                "I am designed for Project Lycanthrope by E D D Red Team 2016. "
                "Rawr."
}

###################################################
# Locks and variables to be locked, because Python.
###################################################

lock = threading.Lock()


###########################################
# Define potential CPU-intensive functions.
###########################################

def async_initialize():
    # Leg 1.
    servo1 = Servo(0, -180, 90, 500, 2500, 150, bias=0, direction=1)
    servo2 = Servo(1, -45, 225, 500, 2500, 150, bias=0, direction=1)
    servo3 = Servo(2, -135, 135, 500, 2500, 150, bias=0, direction=-1)
    leg1 = Leg(servo1, servo2, servo3, (7.5, 7.5), 0)

    # Leg 2.
    servo4 = Servo(3, -90, 180, 500, 2500, 150, bias=0, direction=-1)
    servo5 = Servo(4, -225, 45, 500, 2500, 150, bias=0, direction=1)
    servo6 = Servo(5, -135, 135, 500, 2500, 150, bias=0, direction=1)
    leg2 = Leg(servo4, servo5, servo6, (7.5, 7.5), 1)

    # Leg 3.
    servo7 = Servo(6, -90, 180, 500, 2500, 150, bias=0, direction=1)
    servo8 = Servo(7, -45, 225, 500, 2500, 150, bias=0, direction=1)
    servo9 = Servo(8, -135, 135, 500, 2500, 150, bias=0, direction=-1)
    leg3 = Leg(servo7, servo8, servo9, (7.5, 7.5), 2)

    # Leg 4 .
    servo10 = Servo(9, -180, 90, 500, 2500, 150, bias=0, direction=-1)
    servo11 = Servo(10, -225, 45, 500, 2500, 150, bias=0, direction=1)
    servo12 = Servo(11, -135, 135, 500, 2500, 150, bias=0, direction=1)
    leg4 = Leg(servo10, servo11, servo12, (7.5, 7.5), 3)

    return Robot(leg1, leg2, leg3, leg4)

##############################
# Create the main application.
##############################

logger = logging.getLogger('universe')

# Constants.
user = 'DOG-1E5'
password = 'de2432k,/s-=/8Eu'


class Cerebral(ApplicationSession):
    def __init__(self, *args, **kwargs):
        # Create a thread executor for slightly CPU-bound async functions.
        self.executor = ThreadPoolExecutor(4)
        self.robot = None

        # Multiprocessing.
        manager = mp.Manager()
        self.d = manager.dict()
        self.d['run'] = False
        process = mp.Process(target=AsyncApollo, args=(self.d, -2))
        process.start()

        # Init parent.
        super().__init__(*args, **kwargs)

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

        await self.register(self.initialize, 'dog.initialize')
        await self.register(self.walk, 'dog.walk')
        await self.register(self.pushup, 'dog.pushup')
        await self.register(self.stop, 'dog.stop')
        await self.register(self.home, 'dog.home')
        await self.register(self.listen, 'dog.listen')

        await self.register(self.converse, 'dog.converse')

    def onDisconnect(self):
        logger.warning('Connection lost!')

    ############
    # Functions.
    ############

    async def converse(self, phrase):
        response = conversation.get(phrase.lower())
        if response is not None:
            await self.call('zeus.info', response)
        else:
            await self.call('zeus.info', 'I do not understand that command.')

    async def initialize(self):
        loop = asyncio.get_event_loop()
        try:
            self.robot = await loop.run_in_executor(self.executor, async_initialize)
            self.call('zeus.info', 'Successfully initialized!')
        except:
            self.call('zeus.info', 'Failed to initialized!')

    async def listen(self):
        self.d['run'] = True

    async def walk(self):
        self.call('zeus.info', "Executing walking sequence.")
        agility.walk()
        logger.info('Executed walk().')

    async def pushup(self):
        self.call('zeus.info', "Executing push-ups.")
        agility.pushup()
        logger.info('Executed pushup().')

    async def stop(self):
        agility.stop()
        logger.info('Executed stop().')

    async def home(self):
        agility.home()
        logger.info('Executed home().')


class AsyncApollo(Apollo):
    def __init__(self, d, *args, **kwargs):
        self.d = d
        super().__init__(*args, **kwargs)

        while True:
            if self.d['run']:
                self.d['run'] = False
                super().blockingDetect()

            time.sleep(0.0001)


if __name__ == '__main__':
    ip = '192.168.12.18'

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False
    pem = ssl.get_server_certificate((ip, 443))
    context.load_verify_locations(cadata=pem)

    runner = ApplicationRunner(url='wss://%s/ws' % ip, realm='lycanthrope',
                               ssl=context)

    runner.run(Cerebral)
