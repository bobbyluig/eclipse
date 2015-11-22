from agility.pololu.enumeration import Opcode

from agility.pololu.instruction import BytecodeInstruction


class BytecodeProgram:
    def __init__(self):
        self.sourceLines = []
        self.instructionList = []
        self.openBlocks = []
        self.openBlockTypes = []
        self.subroutineAddresses = {}
        self.subroutineCommands = {}
        self.CRC7_TABLE = tuple(BytecodeProgram.oneByteCRC(i) for i in range(256))
        self.maxBlock = 0
        
    def __getitem__(self, item):
        return self.instructionList[item]

    def __len__(self):
        return len(self.instructionList)

    def blockIsOpen(self):
        return len(self.openBlocks) > 0

    def getSourceLine(self, line):
        return self.sourceLines[line - 1]

    def addSourceLine(self, line):
        self.sourceLines.append(line)

    def getSourceLineCount(self):
        return len(self.sourceLines)

    def addInstruction(self, instruction):
        self.instructionList.append(instruction)

    def addLiteral(self, literal, filename, lineNumber, columnNumber, isMiniMaestro):
        if len(self.instructionList) == 0 or self.instructionList[-1].opcode != Opcode.LITERAL:
            self.addInstruction(BytecodeInstruction(Opcode.LITERAL, filename, lineNumber, columnNumber))
        self.instructionList[-1].addLiteralArgument(literal, isMiniMaestro)

    def getByteList(self):
        list = bytearray()

        for bytecodeInstruction in self.instructionList:
            list.extend(bytecodeInstruction.toByteList())

        return list

    def openBlock(self, blocktype, filename, line_number, column_number):
        self.addInstruction(BytecodeInstruction.newLabel('block_start_%s' % self.maxBlock, filename, line_number, column_number))
        self.openBlocks.append(self.maxBlock)
        self.openBlockTypes.append(blocktype)
        self.maxBlock += 1

    def getCurrentBlockType(self):
        return self.openBlockTypes[-1]

    def getCurrentBlockStartLabel(self):
        return 'block_start_%s' % self.openBlocks[-1]

    def getCurrentBlockEndLabel(self):
        return 'block_end_%s' % self.openBlocks[-1]

    def getNextBlockEndLabel(self):
        return 'block_end_%s' % self.maxBlock

    def findLabelIndex(self, name):
        for index in range(len(self.instructionList)):
            if self.instructionList[index].isLabel and self.instructionList[index].labelName == name:
                return index
        raise Exception('Label not found.')

    def findLabelInstruction(self, name):
        return self.instructionList[self.findLabelIndex(name)]

    def closeBlock(self, filename, line_number, column_number):
        self.addInstruction(BytecodeInstruction.newLabel('block_end_%s' % self.openBlocks.pop(), filename, line_number, column_number))
        num = self.openBlockTypes.pop()

    def completeJumps(self):
        dictionary = {}
        num = 0

        for bytecodeInstruction in self.instructionList:
            if bytecodeInstruction.isLabel:
                if bytecodeInstruction.labelName in dictionary:
                    bytecodeInstruction.error('The label %s has already been used.' % bytecodeInstruction.labelName)
                dictionary[bytecodeInstruction.labelName] = num
            num += len(bytecodeInstruction.toByteList())

        for bytecodeInstruction in self.instructionList:
            try:
                if bytecodeInstruction.isJumpToLabel:
                    bytecodeInstruction.addLiteralArgument(dictionary[bytecodeInstruction.labelName], False)
            except KeyError as ex:
                bytecodeInstruction.error('The label %s was not found.' % bytecodeInstruction.labelName)

    def completeCalls(self, isMiniMaestro):
        num1 = 128

        for bytecodeInstruction in self.instructionList:
            if bytecodeInstruction.isSubroutine:
                if bytecodeInstruction.labelName in self.subroutineCommands:
                    bytecodeInstruction.error('The subroutine %s has already been defined.' % bytecodeInstruction.labelName)
                self.subroutineCommands[bytecodeInstruction.labelName] = num1 if num1 < 256 else 54
                num1 += 1
                if num1 > 255 and not isMiniMaestro:
                    bytecodeInstruction.error('Too many subroutines.  The limit for the Micro Maestro is 128.')

        for bytecodeInstruction in self.instructionList:
            try:
                if bytecodeInstruction.isCall:
                    bytecodeInstruction.setOpcode(self.subroutineCommands[bytecodeInstruction.labelName])
            except KeyError as ex:
                bytecodeInstruction.error("Did not understand '%s'." % bytecodeInstruction.labelName)

        num2 = 0

        for bytecodeInstruction in self.instructionList:
            if bytecodeInstruction.isSubroutine:
                self.subroutineAddresses[bytecodeInstruction.labelName] = num2
            num2 += len(bytecodeInstruction.toByteList())

        for bytecodeInstruction in self.instructionList:
            if bytecodeInstruction.opcode == Opcode.CALL:
                bytecodeInstruction.literalArguments.append(self.subroutineAddresses[bytecodeInstruction.labelName])

    def completeLiterals(self):
        for bytecodeInstruction in self.instructionList:
            bytecodeInstruction.completeLiterals()

    def getInstructionAt(self, program_counter):
        num = 0

        for bytecodeInstruction in self.instructionList:
            list = bytecodeInstruction.toByteList()
            if num >= program_counter and len(list) != 0:
                return bytecodeInstruction

        return None

    def getCRC(self):
        message = bytearray()
        numArray = [0] * 128

        for index in range(len(self.subroutineCommands)):
            if self.subroutineCommands[index] != 54:
                numArray[self.subroutineCommands[index] - 128] = self.subroutineAddresses[index]

        for num in numArray:
            message.extend((num & 255, num >> 8))

        message.extend(self.getByteList())

        return self.CRC(message)

    @staticmethod
    def oneByteCRC(v):
        num = v

        for i in range(8):
            if num & 1:
                num = (num >> 1 ^ 40961)
            else:
                num >>= 1

        return num

    def CRC(self, message):
        num = 0

        for byte in message:
            num = (num >> 8 ^ self.CRC7_TABLE[num ^ byte])

        return num