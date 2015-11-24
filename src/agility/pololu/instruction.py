from agility.pololu.enumeration import Opcode


class BytecodeInstruction:
    def __init__(self, op, filename, lineNumber, columnNumber, **kwargs):

        if kwargs.get('literalArguments') is not None:
            self.literalArguments = [kwargs.get('literalArguments')]
        else:
            self.literalArguments = []

        self.filename = filename
        self.lineNumber = lineNumber
        self.columnNumber = columnNumber
        self.opcode = op

        self.isLabel = kwargs.get('isLabel')
        self.isJumpToLabel = kwargs.get('isJumpToLabel')
        self.labelName = kwargs.get('labelName')
        self.isSubroutine = kwargs.get('isSubroutine')
        self.isCall = kwargs.get('isCall')

    def addLiteralArgument(self, value, isMiniMaestro):
        self.literalArguments.append(value)
        if not isMiniMaestro and len(self.literalArguments) > 32:
            raise Exception('Too many literals (> 32) in a row: this will overflow the stack.')
        if len(self.literalArguments) > 126:
            raise Exception('Too many literals (> 126) in a row: this will overflow the stack.')

    def setOpcode(self, value):
        if self.opcode != Opcode.QUIT:
            raise Exception('The opcode has already been set.')
        self.opcode = value

    def toByteList(self):
        list = bytearray()

        if self.isLabel or self.isSubroutine:
            return list

        list.extend((self.opcode,))

        if self.opcode == Opcode.LITERAL or self.opcode == Opcode.JUMP or (self.opcode == Opcode.JUMP_Z or self.opcode == Opcode.CALL):
            if len(self.literalArguments) == 0:
                list.extend((0, 0))
            else:
                list.extend((self.literalArguments[0] % 256, self.literalArguments[0] // 256))
        elif self.opcode == Opcode.LITERAL8:
            list.extend((self.literalArguments[0],))
        elif self.opcode == Opcode.LITERAL_N:
            list.extend((len(self.literalArguments) * 2,))
            for num in self.literalArguments:
                list.extend((num % 256, num // 256))
        elif self.opcode == Opcode.LITERAL8_N:
            list.extend((len(self.literalArguments),))
            for num in self.literalArguments:
                list.extend((num,))

        return list

    def error(self, msg):
        raise Exception('%s:%s:%s:%s' % (self.filename, self.lineNumber, self.columnNumber, msg))

    @staticmethod
    def newSubroutine(name, filename, column_number, line_number):
        return BytecodeInstruction(Opcode.QUIT, filename, column_number, line_number, isSubroutine=True, labelName=name)

    @staticmethod
    def newCall(name, filename, column_number, line_number):
        return BytecodeInstruction(Opcode.QUIT, filename, column_number, line_number, isCall=True, labelName=name)

    @staticmethod
    def newLabel(name, filename, column_number, line_number):
        return BytecodeInstruction(Opcode.QUIT, filename, column_number, line_number, isLabel=True, labelName=name)

    @staticmethod
    def newJumpToLabel(name, filename, column_number, line_number):
        return BytecodeInstruction(Opcode.JUMP, filename, column_number, line_number, isJumpToLabel=True, labelName=name)

    @staticmethod
    def newConditionalJumpToLabel(name, filename, column_number, line_number):
        return BytecodeInstruction(Opcode.JUMP_Z, filename, column_number, line_number, isJumpToLabel=True, labelName=name)

    def completeLiterals(self):
        if self.opcode != Opcode.LITERAL:
            return
        flag = False
        for num in self.literalArguments:
            if num > 255 or num < 0:
                flag = True
        if flag and len(self.literalArguments) > 1:
            self.opcode = Opcode.LITERAL_N
        elif flag and len(self.literalArguments) == 1:
            self.opcode = Opcode.LITERAL
        elif len(self.literalArguments) > 1:
            self.opcode = Opcode.LITERAL8_N
        else:
            self.opcode = Opcode.LITERAL8

