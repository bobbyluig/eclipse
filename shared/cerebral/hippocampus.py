from shared.agility.maestro import *
import logging

__author__ = 'Lujing Cen'
__copyright__ = 'Copyright (c) 2015-2016 Eclipse Technologies'

####################
# Servo Definitions
####################

hip1 = Servo(0, 0, 180, 1000, 2000)
hip2 = Servo(1, 0, 270, 500, 2500)
knee = Servo(2, 0, 270, 500, 2500)
servos = [hip1, hip2, knee]

################################
# Maestro Controller Definition
################################

maestro = Maestro()

###################
# Class definition.
###################

class Memory:
    def __init__(self):
        # Create variables.
        self.servos = servos
        self.maestro = maestro
        self.whoami = 'DOG-1E5'
        self.password = 'de2432k,/s-=/8Eu'

