import usb, logging, time, pickle
from agility.pololu.structure import *
from agility.pololu.settings import UscSettings, ChannelSetting
from agility.pololu.enumeration import uscRequest, uscParameter, Opcode, ChannelMode, HomeMode

logger = logging.getLogger('universe')


class Range:
    def __init__(self, numBytes, minimumValue, maximumValue):
        self.bytes = numBytes
        self.minimumValue = minimumValue
        self.maximumValue = maximumValue

    def signed(self):
        return self.minimumValue < 0

    @staticmethod
    def u16():
        return Range(2, 0, 0xFFFF)

    @staticmethod
    def u12():
        return Range(2, 0, 0x0FFF)

    @staticmethod
    def u10():
        return Range(2, 0, 0x03FF)

    @staticmethod
    def u8():
        return Range(1, 0, 0xFF)

    @staticmethod
    def u7():
        return Range(1, 0, 0x7F)

    @staticmethod
    def boolean():
        return Range(1, 0, 1)


class Usc:
    vendorID = 0x1ffb
    productIDArray = [0x0089, 0x008a, 0x008b, 0x008c]
    INSTRUCTION_FREQUENCY = 12000000
    servoParameterBytes = 9
    MicroMaestroStackSize = 32
    MicroMaestroCallStackSize = 10
    MiniMaestroStackSize = 126
    MiniMaestroCallStackSize = 126

    def __init__(self):
        self.dev = usb.core.find(idVendor=self.vendorID)

        if self.dev is None:
            raise ConnectionError('Unable to connect to Mini Maestro.')

        self.productID = self.dev.idProduct

        if self.productID == self.productIDArray[0]:
            self.servoCount = 6
        elif self.productID == self.productIDArray[1]:
            self.servoCount = 12
        elif self.productID == self.productIDArray[2]:
            self.servoCount = 18
        elif self.productID == self.productIDArray[3]:
            self.servoCount = 24
        else:
            raise Exception('Unknown product ID %02x.' % self.productID)

        self.serialNumber = self.dev.serial_number
        self.isMiniMaestro = self.servoCount != 6
        self.subroutineOffsetBlocks = 512 if self.isMiniMaestro else 64
        self.maxScriptLength = 8192 if self.isMiniMaestro else 1024
        self.firmwareVersionString = self.getFirmwareVersion()

    def close(self):
        self.dev.close()

    def specifyServo(self, p, servo):
        return p + servo * self.servoParameterBytes

    @staticmethod
    def exponentialSpeedToNormalSpeed(exponentialSpeed):
        mantissa = exponentialSpeed >> 3
        exponent = exponentialSpeed & 7
        return mantissa * (1 << exponent)

    @staticmethod
    def normalSpeedToExponentialSpeed(normalSpeed):
        mantissa = normalSpeed
        exponent = 0

        while True:
            if mantissa < 32:
                return exponent + (mantissa << 3)

            if exponent == 7:
                return 0xFF

            exponent += 1
            mantissa >>= 1

    @staticmethod
    def channelToPort(channel):
        if channel <= 3:
            return channel
        elif channel < 6:
            return channel + 2
        else:
            raise Exception('Invalid channel number %s.' % channel)

    def convertSpbrgToBps(self, spbrg):
        if spbrg == 0:
            return 0
        else:
            return int((self.INSTRUCTION_FREQUENCY + (spbrg + 1) / 2) / (spbrg + 1))

    def convertBpsToSpbrg(self, bps):
        if bps == 0:
            return 0
        else:
            return int((self.INSTRUCTION_FREQUENCY - bps / 2) / bps)

    def setSubroutines(self, subroutineAddresses, subroutineCommands):
        subroutineData = bytearray((0xFF,) * 256)

        for name, value in subroutineAddresses.items():
            bytecode = subroutineCommands[name]

            if bytecode == Opcode.CALL:
                continue

            subroutineData[2 * (bytecode - 128)] = value % 256
            subroutineData[2 * (bytecode - 128) + 1] = value >> 8

        for block in range(16):
            block_bytes = bytearray((0x00,) * 16)

            for j in range(16):
                block_bytes[j] = subroutineData[block * 16 + j]

            self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_WRITE_SCRIPT, 0, block + self.subroutineOffsetBlocks,
                                   block_bytes)

    def writeScript(self, bytecode):
        for block in range((len(bytecode) + 15) // 16):
            block_bytes = bytearray((0x00,) * 16)

            for j in range(16):
                if block * 16 + j < len(bytecode):
                    block_bytes[j] = bytecode[block * 16 + j]
                else:
                    block_bytes[j] = 0xFF

            self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_WRITE_SCRIPT, 0, block, block_bytes)

    def eraseScript(self):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_ERASE_SCRIPT, 0, 0)

    def restartScriptAtSubroutine(self, subroutine):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_RESTART_SCRIPT_AT_SUBROUTINE, 0, 0, subroutine)

    # Places a parameter on the stack to be consumed by the subroutine.
    def restartScriptAtSubroutineWithParameter(self, subroutine, parameter):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_ERASE_SCRIPT_WITH_PARAMETER, parameter, subroutine)

    def restartScript(self):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_RESTART_SCRIPT, 0, 0)

    # Stop or starts the script (at the beginning).
    # 1 is stop and 0 is start.
    def setScriptDone(self, value):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_SET_SCRIPT_DONE, value, 0)

    def reinitialize(self, waitTime):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_REINITIALIZE, 0, 0)
        time.sleep(waitTime / 1000)

    def clearErrors(self):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_CLEAR_ERRORS, 0, 0)

    def getFirmwareVersion(self):
        buffer = self.dev.ctrl_transfer(0x80, 6, 0x0100, 0x0000, 0x0012)
        firmwareVersionMinor = (buffer[12] & 0xF) + (buffer[12] >> 4 & 0xF) * 10
        firmwareVersionMajor = (buffer[13] & 0xF) + (buffer[13] >> 4 & 0xF) * 10
        return '%s.%s' % (firmwareVersionMajor, firmwareVersionMinor)

    def getRawParameter(self, parameter):
        parameterRange = Usc.getRange(parameter)
        array = self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_PARAMETER, 0, parameter, parameterRange.bytes)

        if parameterRange.bytes == 1:
            return int(struct.unpack('<B', array)[0])
        else:
            return int(struct.unpack('<H', array)[0])

    @staticmethod
    def requireArgumentRange(argumentValue, minimum, maximum, argumentName):
        if argumentValue < minimum or argumentValue > maximum:
            raise Exception('The %s must be between %s and %s but the value given was %s.'
                            % (argumentName, minimum, maximum, argumentValue))

    def setRawParameter(self, parameter, value):
        parameterRange = Usc.getRange(parameter)
        Usc.requireArgumentRange(value, parameterRange.minimumValue, parameterRange.maximumValue, parameter)
        self.setRawParameterNoChecks(parameter, value, parameterRange.bytes)

    def setRawParameterNoChecks(self, parameter, value, numBytes):
        index = (numBytes << 8) + parameter
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_SET_PARAMETER, value, index)

    @staticmethod
    def getRange(parameterId):
        if parameterId in [uscParameter.PARAMETER_INITIALIZED,
                           uscParameter.PARAMETER_SERVOS_AVAILABLE,
                           uscParameter.PARAMETER_SERVO_PERIOD,
                           uscParameter.PARAMETER_MINI_MAESTRO_SERVO_PERIOD_L,
                           uscParameter.PARAMETER_SERVO_MULTIPLIER,
                           uscParameter.PARAMETER_CHANNEL_MODES_0_3,
                           uscParameter.PARAMETER_CHANNEL_MODES_4_7,
                           uscParameter.PARAMETER_CHANNEL_MODES_8_11,
                           uscParameter.PARAMETER_CHANNEL_MODES_12_15,
                           uscParameter.PARAMETER_CHANNEL_MODES_16_19,
                           uscParameter.PARAMETER_CHANNEL_MODES_20_23,
                           uscParameter.PARAMETER_ENABLE_PULLUPS]:
            return Range.u8()
        elif parameterId in [uscParameter.PARAMETER_MINI_MAESTRO_SERVO_PERIOD_HU,
                             uscParameter.PARAMETER_SERIAL_TIMEOUT,
                             uscParameter.PARAMETER_SERIAL_FIXED_BAUD_RATE,
                             uscParameter.PARAMETER_SCRIPT_CRC]:
            return Range.u16()
        elif parameterId in [uscParameter.PARAMETER_SERIAL_NEVER_SUSPEND,
                             uscParameter.PARAMETER_SERIAL_ENABLE_CRC,
                             uscParameter.PARAMETER_SCRIPT_DONE]:
            return Range.boolean()
        elif parameterId == uscParameter.PARAMETER_SERIAL_DEVICE_NUMBER:
            return Range.u7()
        elif parameterId == uscParameter.PARAMETER_SERIAL_MODE:
            return Range(1, 0, 3)
        elif parameterId == uscParameter.PARAMETER_SERIAL_BAUD_DETECT_TYPE:
            return Range(1, 0, 1)
        elif parameterId == uscParameter.PARAMETER_SERIAL_MINI_SSC_OFFSET:
            return Range(1, 0, 254)
        else:
            servoParameter = ((int(parameterId) - int(uscParameter.PARAMETER_SERVO0_HOME)) % 9) \
                             + int(uscParameter.PARAMETER_SERVO0_HOME)
            if servoParameter in [int(uscParameter.PARAMETER_SERVO0_SPEED),
                                  int(uscParameter.PARAMETER_SERVO0_MAX),
                                  int(uscParameter.PARAMETER_SERVO0_MIN),
                                  int(uscParameter.PARAMETER_SERVO0_ACCELERATION)]:
                return Range.u8()
            elif servoParameter in [int(uscParameter.PARAMETER_SERVO0_HOME),
                                    int(uscParameter.PARAMETER_SERVO0_NEUTRAL)]:
                return Range(2, 0, 32440)
            elif servoParameter == int(uscParameter.PARAMETER_SERVO0_RANGE):
                return Range(1, 1, 50)
            else:
                raise Exception('Invalid parameterId %s, can not determine the range of this parameter.'
                                % int(parameterId))

    def restoreDefaultConfiguration(self):
        self.setRawParameterNoChecks(uscParameter.PARAMETER_INITIALIZED, 0xFF, 1)
        self.reinitialize(1500)

    def setPWM(self, dutyCycle, period):
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_SET_PWM, dutyCycle, period)

    def getUscSettings(self):
        settings = UscSettings()

        settings.serialMode = self.getRawParameter(uscParameter.PARAMETER_SERIAL_MODE)
        settings.fixedBaudRate = self.convertSpbrgToBps(
            self.getRawParameter(uscParameter.PARAMETER_SERIAL_FIXED_BAUD_RATE))
        settings.enableCrc = self.getRawParameter(uscParameter.PARAMETER_SERIAL_ENABLE_CRC) != 0
        settings.neverSuspend = self.getRawParameter(uscParameter.PARAMETER_SERIAL_NEVER_SUSPEND) != 0
        settings.serialDeviceNumber = self.getRawParameter(uscParameter.PARAMETER_SERIAL_DEVICE_NUMBER)
        settings.miniSscOffset = self.getRawParameter(uscParameter.PARAMETER_SERIAL_MINI_SSC_OFFSET)
        settings.serialTimeout = self.getRawParameter(uscParameter.PARAMETER_SERIAL_TIMEOUT)
        settings.scriptDone = self.getRawParameter(uscParameter.PARAMETER_SCRIPT_DONE) != 0

        if not self.isMiniMaestro:
            settings.servosAvailable = self.getRawParameter(uscParameter.PARAMETER_SERVOS_AVAILABLE)
            settings.servoPeriod = self.getRawParameter(uscParameter.PARAMETER_SERVO_PERIOD)
        else:
            tmp = self.getRawParameter(uscParameter.PARAMETER_MINI_MAESTRO_SERVO_PERIOD_HU) << 8
            tmp |= self.getRawParameter(uscParameter.PARAMETER_MINI_MAESTRO_SERVO_PERIOD_L)
            settings.miniMaestroServoPeriod = tmp

            settings.servoMultiplier = self.getRawParameter(uscParameter.PARAMETER_SERVO_MULTIPLIER) + 1

        if self.servoCount > 18:
            settings.enablePullups = self.getRawParameter(uscParameter.PARAMETER_ENABLE_PULLUPS) != 0

        ioMask = 0
        outputMask = 0
        channelModeBytes = []

        if not self.isMiniMaestro:
            ioMask = self.getRawParameter(uscParameter.PARAMETER_IO_MASK_C)
            outputMask = self.getRawParameter(uscParameter.PARAMETER_OUTPUT_MASK_C)
        else:
            for i in range(6):
                channelModeBytes.append(self.getRawParameter(uscParameter.PARAMETER_CHANNEL_MODES_0_3 + i))

        for i in range(self.servoCount):
            setting = ChannelSetting()

            if not self.isMiniMaestro:
                bitmask = 1 << Usc.channelToPort(i)
                if (ioMask & bitmask) == 0:
                    setting.mode = ChannelMode.Servo
                elif (outputMask & bitmask) == 0:
                    setting.mode = ChannelMode.Input
                else:
                    setting.mode = ChannelMode.Output
            else:
                setting.mode = (channelModeBytes[i >> 2] >> ((i & 3) << 1)) & 3

            home = self.getRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_HOME, i))

            if home == 0:
                setting.homeMode = HomeMode.Off
                setting.home = 0
            elif home == 1:
                setting.homeMode = HomeMode.Ignore
                setting.home = 0
            else:
                setting.homeMode = HomeMode.Goto
                setting.home = home

            setting.minimum = 64 * self.getRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_MIN, i))
            setting.maximum = 64 * self.getRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_MAX, i))
            setting.neutral = self.getRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_NEUTRAL, i))
            setting.range = 127 * self.getRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_RANGE, i))
            setting.speed = self.exponentialSpeedToNormalSpeed(
                self.getRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_SPEED, i)))
            setting.acceleration = self.getRawParameter(
                self.specifyServo(uscParameter.PARAMETER_SERVO0_ACCELERATION, i))

            settings.channelSettings.append(setting)

        return settings

    def setUscSettings(self, settings, newScript):
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_MODE, settings.serialMode)
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_FIXED_BAUD_RATE,
                             self.convertBpsToSpbrg(settings.fixedBaudRate))
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_ENABLE_CRC, int(settings.enableCrc))
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_NEVER_SUSPEND, int(settings.neverSuspend))
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_DEVICE_NUMBER, settings.serialDeviceNumber)
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_MINI_SSC_OFFSET, settings.miniSscOffset)
        self.setRawParameter(uscParameter.PARAMETER_SERIAL_TIMEOUT, settings.serialTimeout)
        self.setRawParameter(uscParameter.PARAMETER_SCRIPT_DONE, int(settings.scriptDone))

        if not self.isMiniMaestro:
            self.setRawParameter(uscParameter.PARAMETER_SERVOS_AVAILABLE, settings.servosAvailable)
            self.setRawParameter(uscParameter.PARAMETER_SERVO_PERIOD, settings.servoPeriod)
        else:
            self.setRawParameter(
                uscParameter.PARAMETER_MINI_MAESTRO_SERVO_PERIOD_L, settings.miniMaestroServoPeriod & 0xFF)
            self.setRawParameter(
                uscParameter.PARAMETER_MINI_MAESTRO_SERVO_PERIOD_HU, settings.miniMaestroServoPeriod >> 8)

            if settings.servoMultiplier < 1:
                multiplier = 0
            elif settings.servoMultiplier > 256:
                multiplier = 255
            else:
                multiplier = settings.servoMultiplier - 1

            self.setRawParameter(uscParameter.PARAMETER_SERVO_MULTIPLIER, multiplier)

        if self.servoCount > 18:
            self.setRawParameter(uscParameter.PARAMETER_ENABLE_PULLUPS, int(settings.enablePullups))

        ioMask = 0
        outputMask = 0
        channelModeBytes = bytearray((0,) * 6)

        for i in range(self.servoCount):
            setting = settings.channelSettings[i]

            if not self.isMiniMaestro:
                if setting.mode == ChannelMode.Input or setting.mode == ChannelMode.Output:
                    ioMask |= 1 << self.channelToPort(i)

                if setting.mode == ChannelMode.Output:
                    outputMask |= 1 << self.channelToPort(i)
            else:
                channelModeBytes[i >> 2] |= setting.mode << ((i & 3) << 1)

            correctedHomeMode = setting.homeMode

            if setting.mode == ChannelMode.Input:
                correctedHomeMode = HomeMode.Ignore

            if correctedHomeMode == HomeMode.Off:
                home = 0
            elif correctedHomeMode == HomeMode.Ignore:
                home = 1
            else:
                home = setting.home

            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_HOME, i), home)
            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_MIN, i), int(setting.minimum / 64))
            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_MAX, i), int(setting.maximum / 64))
            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_NEUTRAL, i), setting.neutral)
            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_RANGE, i), int(setting.range / 127))
            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_SPEED, i),
                                 self.normalSpeedToExponentialSpeed(setting.speed))
            self.setRawParameter(self.specifyServo(uscParameter.PARAMETER_SERVO0_ACCELERATION, i), setting.acceleration)

        if newScript:
            self.loadProgram(settings.bytecodeProgram, CRC=True)

    def fixSettings(self, settings):
        warnings = []

        if len(settings) > self.servoCount:
            warnings.append('The settings loaded include settings for %s channels, '
                            'but this device has only %s channels. The extra channel settings will be ignored.'
                            % (len(settings), self.servoCount))
            del settings.channelSettings[self.servoCount:]

        if len(settings) < self.servoCount:
            warnings.append('The settings loaded include settings for only %s channels, '
                            'but this device has %s channels. '
                            'The other channels will be initialized with default settings.'
                            % (len(settings), self.servoCount))
            while len(settings) < self.servoCount:
                cs = ChannelSetting()
                if not self.isMiniMaestro and settings.servosAvailable <= len(settings):
                    cs.mode = ChannelMode.Input
                settings.channelSettings.append(cs)

        for cs in settings.channelSettings:
            if cs.mode == ChannelMode.Input:
                cs.homeMode = HomeMode.Ignore
                cs.minimum = 0
                cs.maximum = 1024
                cs.speed = 0
                cs.acceleration = 0
                cs.neutral = 1024
                cs.range = 1905
            elif cs.mode == ChannelMode.Output:
                cs.minimum = 3986
                cs.maximum = 8000
                cs.speed = 0
                cs.acceleration = 0
                cs.neutral = 6000
                cs.range = 1905

        if settings.serialDeviceNumber >= 128:
            settings.serialDeviceNumber = 12
            warnings.append('The serial device number must be less than 128. It will be changed to 12.')

    def getVariables(self, out):
        if not self.isMiniMaestro:
            variables, servos = self.getVariableMicroMaestro()

            if out == 'variables':
                return variables
            elif out == 'servos':
                return servos
            elif out == 'stack':
                return variables.stack
            elif out == 'callStack':
                return variables.callStack
            else:
                raise Exception('Unknown type of desired output %s.' % out)

        else:
            return self.getVariableMiniMaestro(out)

    def getVariableMicroMaestro(self):
        packed = self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_VARIABLES, 0, 0,
                                        MicroMaestroVariables.struct.size + self.servoCount * ServoStatus.struct.size)

        var_packed = packed[0:MicroMaestroVariables.struct.size]
        servo_packed = packed[MicroMaestroVariables.struct.size:]

        variables = MicroMaestroVariables(var_packed)

        servos = []
        for i in range(self.servoCount):
            servos.append(ServoStatus(servo_packed[i*ServoStatus.struct.size:(i+1)*ServoStatus.struct.size]))

        return variables, servos

    def getVariableMiniMaestro(self, out):
        if out == 'variables':
            packed = self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_VARIABLES, 0, 0,
                                            MiniMaestroVariables.struct.size)

            if len(packed) != MiniMaestroVariables.struct.size:
                raise Exception('Short read: %s < %s.' % (len(packed), MiniMaestroVariables.struct.size))

            return MiniMaestroVariables(packed)

        elif out == 'servos':
            packed = self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_SERVO_SETTINGS, 0, 0,
                                            self.servoCount * ServoStatus.struct.size)

            if len(packed) != ServoStatus.struct.size * self.servoCount:
                raise Exception('Short read: %s < %s.' % (len(packed), ServoStatus.struct.size))

            servos = []
            for i in range(self.servoCount):
                servos.append(ServoStatus(packed[i*ServoStatus.struct.size:(i+1)*ServoStatus.struct.size]))

            return servos

        elif out == 'stack':
            packed = self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_STACK, 0, 0, 2 * self.MiniMaestroStackSize)
            return packed.tolist()

        elif out == 'callStack':
            packed = self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_CALL_STACK, 0, 0,
                                            2 * self.MiniMaestroCallStackSize)
            return packed.tolist()

        else:
            raise Exception('Unknown type of desired output %s.' % out)

    @staticmethod
    def saveSettings(settings, file):
        f = open(file, 'wb')
        pickle.dump(settings, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()

    @staticmethod
    def loadSettings(file):
        f = open(file, 'rb')
        settings = pickle.load(f)
        f.close()

        return settings

    # Custom function to load script. Can be called externally.
    def loadProgram(self, program, CRC=False):
        self.setScriptDone(1)
        byteList = program.getByteList()

        if len(byteList) > self.maxScriptLength:
            raise Exception('Script is too long for device (%s bytes).' % len(byteList))

        if len(byteList) < self.maxScriptLength:
            byteList.append(Opcode.QUIT)

        self.eraseScript()
        self.setSubroutines(program.subroutineAddresses, program.subroutineCommands)
        self.writeScript(byteList)

        if CRC:
            self.setRawParameter(uscParameter.PARAMETER_SCRIPT_CRC, program.getCRC())

        self.reinitialize(100)
