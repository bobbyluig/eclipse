#!/usr/bin/env python3.5

import asyncio, logging

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from shared.cerebral.autoreconnect import ApplicationRunner
from shared.cerebral.hippocampus import Memory

__author__ = 'Lujing Cen'
__copyright__ = 'Copyright (c) 2015-2016 Eclipse Technologies'

#############################
# Define shared memory class.
#############################

memory = Memory()

#####################
# Servo control test.
#####################

def move_servo(channel, degrees):
    servo = memory.servos[channel]
    servo.target = degrees
    memory.maestro.set_target(servo)
    # memory.maestro.flush()
    logging.info('Executed move_servo(%s, %s).' % (channel, degrees))

    return True

##############################
# Create the main application.
##############################

class Cerebral(ApplicationSession):
    def onConnect(self):
        logging.info('Connected to server.')
        self.join(self.config.realm, ['wampcra'], memory.whoami)

    def onChallenge(self, challenge):
        logging.info('Challenge received.')
        if challenge.method == 'wampcra':
            if 'salt' in challenge.extra:
                key = auth.derive_key(memory.password.encode(),
                                      challenge.extra['salt'].encode(),
                                      challenge.extra.get('iterations', None),
                                      challenge.extra.get('keylen', None))
            else:
                key = memory.password.encode()
            signature = auth.compute_wcs(key, challenge.extra['challenge'])
            return signature.decode('ascii')
        else:
            raise Exception('Unknown challenge method: %s' % challenge.method)

    async def onJoin(self, details):
        logging.info('Joined "%s" realm.' % self.config.realm)
        await self.register(move_servo, 'com.agility')

    async def onDisconnect(self):
        logging.warning('Connection lost!')

if __name__ == '__main__':
    ip = '192.168.0.7'
    runner = ApplicationRunner(url='ws://%s:8080/ws' % ip, realm='lycanthrope')
    runner.run(Cerebral)