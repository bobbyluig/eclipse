from agility.maestro import *
import logging

####################
# Servo Definitions
####################

s1 = Servo(0, 0, 270, 500, 2500, 160)
s2 = Servo(1, 0, 270, 500, 2500, 160)
s3 = Servo(2, 0, 270, 500, 2500, 160)
s4 = Servo(3, 0, 270, 500, 2500, 160)
s5 = Servo(4, 0, 270, 500, 2500, 160)

servos = [s1, s2, s3, s4, s5]

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

