import usb, logging, time
from agility.pololu.reader import BytecodeReader
from agility.pololu.settings import UscSettings
from agility.pololu.enumeration import uscRequest, uscParameter, Opcode

logger = logging.getLogger('universe')


class Range:
    def __init__(self, numBytes, minimumValue, maximumValue):
        self.bytes = numBytes
        self.minimumValue = minimumValue
        self.maximumValue = maximumValue

    def signed(self):
        return self.minimumValue < 0

    @staticmethod
    def u32():
        return Range(4, 0, 0x7FFFFFFF)

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
    def __init__(self):
        self.vendorID = 0x1ffb
        self.productIDArray = [0x0089, 0x008a, 0x008b, 0x008c]
        self.dev = usb.core.find(idVendor=self.vendorID)

        if self.dev is None:
            raise Exception('Unable to connect to Mini Maestro.')

        self.isMiniMaestro = self.dev.idProduct != self.productIDArray[0]
        self.subroutineOffsetBlocks = 512 if self.isMiniMaestro else 64
        self.maxScriptLength = 8192 if self.isMiniMaestro else 1024
        self.firmwareVersionString = self.getFirmwareVersion()
        self.settings = UscSettings()

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
        return self.dev.ctrl_transfer(0xC0, uscRequest.REQUEST_GET_PARAMETER, 0, parameter, parameterRange.bytes)

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
            servoParameter = (int(parameterId) - int(uscParameter.PARAMETER_SERVO0_HOME) % 9) \
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
                raise Exception('Invalid parameterId %s, can not determine the range of this parameter.' % int(parameterId))

    def restoreDefaultConfiguration(self):
        self.setRawParameterNoChecks(uscParameter.PARAMETER_INITIALIZED, 0xFF, 1)
        self.reinitialize(1500)

    def getUscSettings(self):
        return

    # Custom function to load script.
    def loadProgram(self, program):
        self.setScriptDone(1)
        self.eraseScript()

        byteList = program.getByteList()

        if len(byteList) > 8192:
            raise Exception('Script is too long for device (%s bytes).' % len(byteList))

        if len(byteList) < 8192:
            byteList.append(Opcode.QUIT)

        # Set up subroutines.
        self.setSubroutines(program.subroutineAddresses, program.subroutineCommands)

        # Load script.
        self.writeScript(byteList)
