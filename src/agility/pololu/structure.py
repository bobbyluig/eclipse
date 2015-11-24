import struct


class ServoStatus:
    struct = struct.Struct('<HHHB')

    def __init__(self, packed):
        unpacked = self.struct.unpack(packed)

        self.position = unpacked[0]
        self.target = unpacked[1]
        self.speed = unpacked[2]
        self.acceleration = unpacked[3]


class MaestroVariables:
    struct = struct.Struct('<BBHHBB')

    def __init__(self, packed):
        unpacked = self.struct.unpack(packed)

        self.stackPointer = unpacked[0]
        self.callStackPointer = unpacked[1]
        self.errors = unpacked[2]
        self.programCounter = unpacked[3]
        self.scriptDone = unpacked[4]
        self.performanceFlags = unpacked[5]



class MicroMaestroVariables:
    struct = struct.Struct('<BBH3h32h10HBB')

    def __init__(self, packed):
        unpacked = self.struct.unpack(packed)

        self.stackPointer = unpacked[0]
        self.callStackPointer = unpacked[1]
        self.errors = unpacked[2]
        self.buffer = unpacked[3:6]
        self.stack = unpacked[6:38]
        self.callStack = unpacked[38:48]
        self.scriptDone = unpacked[48]
        self.buffer2 = unpacked[49]


class MiniMaestroVariables:
    struct = struct.Struct('<BBHHBB')

    def __init__(self, packed):
        unpacked = self.struct.unpack(packed)

        self.stackPointer = unpacked[0]
        self.callStackPointer = unpacked[1]
        self.errors = unpacked[2]
        self.programCounter = unpacked[3]
        self.scriptDone = unpacked[4]
        self.performanceFlags = unpacked[5]



