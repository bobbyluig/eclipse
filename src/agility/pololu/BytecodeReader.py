import re

from agility.pololu.BytecodeProgram import BytecodeProgram
from agility.pololu.Enumeration import Opcode, Mode, Keyword, BlockType

from agility.pololu.BytecodeInstruction import BytecodeInstruction


class BytecodeReader:
    def __init__(self):
        self.mode = None

    def read(self, program, isMiniMaestro):
        bytecode_program = BytecodeProgram()
        self.mode = Mode.NORMAL

        if program is None:
            program = ""

        strArray = program.splitlines()

        line_number = 1

        while line_number <= len(strArray):
            str1 = strArray[line_number - 1]
            bytecode_program.addSourceLine(str1)
            column_number = 1

            str2 = re.sub(r"#.*", r"", str1)

            for str3 in str2.split():
                if str3 == '':
                    column_number += 1
                else:
                    s = str3.upper()
                    if self.mode == Mode.NORMAL:
                        self.parseString(s, bytecode_program, 'script', line_number, column_number, isMiniMaestro)
                    elif self.mode == Mode.GOTO:
                        self.parseGoto(s, bytecode_program, 'script', line_number, column_number)
                    elif self.mode == Mode.SUBROUTINE:
                        self.parseSubroutine(s, bytecode_program, 'script', line_number, column_number)
                    column_number += len(s) + 1
            line_number += 1

        if bytecode_program.blockIsOpen():
            currentBlockStartLabel = bytecode_program.getCurrentBlockStartLabel()
            bytecode_program.findLabelInstruction(currentBlockStartLabel).error('BEGIN block was never closed.')
        bytecode_program.completeLiterals()
        bytecode_program.completeCalls(isMiniMaestro)
        bytecode_program.completeJumps()

        return bytecode_program

    def parseGoto(self, s, bytecode_program, filename, line_number, column_number):
        bytecode_program.addInstruction(BytecodeInstruction.newJumpToLabel('USER_' + s, filename, line_number, column_number))
        self.mode = Mode.NORMAL

    def parseSubroutine(self, s, bytecode_program, filename, line_number, column_number):
        if BytecodeReader.looksLikeLiteral(s):
            raise Exception('The name %s is not valid as a subroutine name (it looks like a number).' % s)
        if s in Opcode.__members__:
            raise Exception('The name %s is not valid as a subroutine name (it is a built-in command).' % s)
        if s in Keyword.__members__:
            raise Exception('The name %s is not valid as a subroutine name (it is a keyword).' % s)

        bytecode_program.addInstruction(BytecodeInstruction.newSubroutine(s, filename, line_number, column_number))
        self.mode = Mode.NORMAL

    @staticmethod
    def looksLikeLiteral(s):
        if not re.match(r"^-?[0-9.]+$", s):
            return bool(re.match("^0[xX][0-9a-fA-F.]+$", s))
        return True

    def parseString(self, s, bytecode_program, filename, line_number, column_number, isMiniMaestro):
        try:
            if BytecodeReader.looksLikeLiteral(s):
                if s.startswith('0X'):
                    try:
                        num = int(s, 16)
                    except ValueError:
                        raise Exception('Value %s must be an integer.' % s)
                    if num > 65535 or num < 0:
                        raise Exception('Value %s is not in the allowed range of 0 to 65525.' % s)
                else:
                    try:
                        num = int(s)
                    except ValueError:
                        raise Exception('Value %s must be an integer.' % s)
                    if num > 65535 or num < 0:
                        raise Exception('Value %s is not in the allowed range of 0 to 65525.' % s)

                literal = (num % 65535)
                bytecode_program.addLiteral(literal, filename, line_number, column_number, isMiniMaestro)
                return 
        except Exception as ex:
            raise Exception('Error parsing %s: %s' % (s, ex))

        if s == 'GOTO':
            self.mode = Mode.GOTO
        elif s == 'SUB':
            self.mode = Mode.SUBROUTINE
        else:
            match = re.match(r"(.*):$", s)
            if match:
                bytecode_program.addInstruction(BytecodeInstruction.newLabel('USER_%s' % match.group(1), filename, line_number, column_number))
            elif s == 'BEGIN':
                bytecode_program.openBlock(BlockType.BEGIN, filename, line_number, column_number)
            elif s == 'WHILE':
                if bytecode_program.getCurrentBlockType() != BlockType.BEGIN:
                    raise Exception('WHILE must be inside a BEGIN...REPEAT block')
                bytecode_program.addInstruction(BytecodeInstruction.newConditionalJumpToLabel(bytecode_program.getCurrentBlockEndLabel(), filename, line_number, column_number))
            elif s == 'REPEAT':
                try:
                    if bytecode_program.getCurrentBlockType() != BlockType.BEGIN:
                        raise Exception('REPEAT must end a BEGIN...REPEAT block')
                    bytecode_program.addInstruction(BytecodeInstruction.newJumpToLabel(bytecode_program.getCurrentBlockStartLabel(), filename, line_number, column_number))
                    bytecode_program.closeBlock(filename, line_number, column_number)
                except:
                    raise Exception('%s:%s:%s: Found REPEAT without a corresponding BEGIN.' % (filename, line_number, column_number))
            elif s == 'IF':
                bytecode_program.openBlock(BlockType.IF, filename, line_number, column_number)
                bytecode_program.addInstruction(BytecodeInstruction.newConditionalJumpToLabel(bytecode_program.getCurrentBlockEndLabel(), filename, line_number, column_number))
            elif s == 'ENDIF':
                try:
                    if bytecode_program.getCurrentBlockType() != BlockType.IF and bytecode_program.getCurrentBlockType() != BlockType.ELSE:
                        raise Exception('ENDIF must end an IF...ENDIF or an IF...ELSE...ENDIF block.')
                    bytecode_program.closeBlock(filename, line_number, column_number)
                except:
                    raise Exception('%s:%s:%s: Found ENDIF without a corresponding IF.' % (filename, line_number, column_number))
            elif s == 'ELSE':
                try:
                    if bytecode_program.getCurrentBlockType() != BlockType.IF:
                        raise Exception('ELSE must be part of an IF...ELSE...ENDIF block.')
                    bytecode_program.addInstruction(BytecodeInstruction.newJumpToLabel(bytecode_program.getNextBlockEndLabel(), filename, line_number, column_number))
                    bytecode_program.closeBlock(filename, line_number, column_number)
                    bytecode_program.openBlock(BlockType.ELSE, filename, line_number, column_number)
                except:
                    raise Exception('%s:%s:%s: Found ELSE without a corresponding IF.' % (filename, line_number, column_number))
            else:
                try:
                    op = Opcode[s]
                    if op == Opcode.LITERAL or op == Opcode.LITERAL8 or op == Opcode.LITERAL_N or op == Opcode.LITERAL8_N:
                        raise Exception('%s:%s:%s: Literal commands may not be used directly in a program. Integers should be entered directly.' % (filename, line_number, column_number))
                    elif op == Opcode.JUMP or op == Opcode.JUMP_Z:
                        raise Exception('%s:%s:%s: Jumps may not be used directly in a program.' % (filename, line_number, column_number))
                    else:
                        if not isMiniMaestro and op >= 50:
                            raise Exception('%s:%s:%s: is only available on the Mini Maestro 12, 18, and 24.' % (filename, line_number, column_number))
                        bytecode_program.addInstruction(BytecodeInstruction(op, filename, line_number, column_number))
                except KeyError:
                    bytecode_program.addInstruction(BytecodeInstruction.newCall(s, filename, line_number, column_number))
