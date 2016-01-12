from agility.maestro import Maestro, Servo
from finesse.main import Finesse
from enum import IntEnum


class LegLocation(IntEnum):
    FR = 1
    RL = 2
    BR = 3
    BL = 4


class Leg:
    def __init__(self, servo1, servo2, servo3, location):
        """
        Create a leg object.
        :param servo1: The first hip servo object.
        :param servo2: The second hip servo object.
        :param servo3: The knee servo object.
        :param location: The leg location. Should be a member of LegLocation.
        """

        self.servos = [servo1, servo2, servo3]
        self.location = location

    def __getitem__(self, key):
        return self.servos[key]

    def __add__(self, other):
        return self.servos + other.servos


class Robot:
    def __init__(self, leg1, leg2, leg3, leg4):
        self.legs = [leg1, leg2, leg3, leg4]
        self.gait = None

        locations = set(leg.location for leg in self.legs)
        if len(locations) != 4:
            raise Exception('Invalid robot configuration. Robot must have 4 unique legs.')

    def __getitem__(self, key):
        return self.legs[key]

    def set_gait(self, gait):
        self.legs = sorted(self.legs, key=lambda leg: int(leg.location))

        if gait == '1243-creeping':
            self.legs = [self.legs[0], self.legs[1], self.legs[3], self.legs[2]]
        elif gait == '1342-creeping':
            self.legs = [self.legs[0], self.legs[2], self.legs[3], self.legs[1]]
        elif gait == '1234-creeping' or gait == 'bound':
            self.legs = [self.legs[0], self.legs[1], self.legs[2], self.legs[3]]
        elif gait == '1324-creeping' or gait == 'pace':
            self.legs = [self.legs[0], self.legs[2], self.legs[1], self.legs[3]]
        elif gait == '1423-creeping' or gait == 'trot':
            self.legs = [self.legs[0], self.legs[3], self.legs[1], self.legs[2]]
        elif gait == 'crawl':
            self.legs = [self.legs[0], self.legs[3], self.legs[1], self.legs[2]]
        else:
            raise Exception('Unknown gait.')

        self.gait = gait


class Agility:
    def __init__(self, robot):
        self.maestro = Maestro()
        self.robot = robot