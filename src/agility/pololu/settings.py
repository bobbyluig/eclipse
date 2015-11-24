from agility.pololu.enumeration import uscSerialMode, ChannelMode, HomeMode
from agility.pololu.reader import BytecodeReader


class UscSettings:
    def __init__(self):
        self.servosAvailable = 6
        self.servoPeriod = 156
        self.miniMaestroServoPeriod = 80000
        self.servoMultiplier = 1
        self.serialMode = uscSerialMode.SERIAL_MODE_UART_DETECT_BAUD_RATE
        self.fixedBaudRate = 9600
        self.enableCrc = False
        self.neverSuspend = False
        self.serialDeviceNumber = 12
        self.miniSscOffset = 0
        self.serialTimeout = 0
        self.scriptDone = True
        self.channelSettings = []
        self.enablePullups = True
        self.scriptInconsistent = False
        self.script = None
        self.bytecodeProgram = None

    def setAndCompileScript(self, script):
        self.script = None
        reader = BytecodeReader()
        self.bytecodeProgram = reader.read(script, self.servoCount != 6)
        self.script = script

    def servoCount(self):
        return len(self.channelSettings)


class ChannelSetting:
    def __init__(self):
        self.name = ''
        self.mode = ChannelMode.Servo
        self.homeMode = HomeMode.Off
        self.home = 6000
        self.minimum = 3968
        self.maximum = 8000
        self.neutral = 6000
        self.range = 1905
        self.speed = 0
        self.acceleration = 0