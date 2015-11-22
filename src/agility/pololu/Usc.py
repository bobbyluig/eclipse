import usb, logging, time
from agility.pololu.reader import BytecodeReader
from agility.pololu.enumeration import uscRequest, uscParameter, Opcode

logger = logging.getLogger('universe')


class Usc:
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x1ffb)
        self.subroutineOffsetBlocks = 512
        self.firmwareVersionString = None

        if self.dev is None:
            raise Exception('Unable to connect to Mini Maestro.')

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

            self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_WRITE_SCRIPT, 0, block + self.subroutineOffsetBlocks, block_bytes)

    def writeScipt(self, bytecode):
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
        self.dev.ctrl_transfer(0x40, uscRequest.REQUEST_ERASE_SCRIPT_WITH_PARAMETER, 0, 0)

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
        self.firmwareVersionString = '%s.%s' % (firmwareVersionMajor, firmwareVersionMinor)

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
        self.writeScipt(byteList)
