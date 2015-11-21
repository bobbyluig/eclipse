from enum import IntEnum


class Mode(IntEnum):
    NORMAL = 0
    GOTO = 1
    SUBROUTINE = 2


class BlockType(IntEnum):
    BEGIN = 0
    IF = 1
    ELSE = 2


class Keyword(IntEnum):
    GOTO = 0
    SUB = 1
    BEGIN = 2
    WHILE = 3
    REPEAT = 4
    IF = 5
    ENDIF = 6
    ELSE = 7


class Opcode(IntEnum):
    QUIT = 0
    LITERAL = 1
    LITERAL8 = 2
    LITERAL_N = 3
    LITERAL8_N = 4
    RETURN = 5
    JUMP = 6
    JUMP_Z = 7
    DELAY = 8
    GET_MS = 9
    DEPTH = 10
    DROP = 11
    DUP = 12
    OVER = 13
    PICK = 14
    SWAP = 15
    ROT = 16
    ROLL = 17
    BITWISE_NOT = 18
    BITWISE_AND = 19
    BITWISE_OR = 20
    BITWISE_XOR = 21
    SHIFT_RIGHT = 22
    SHIFT_LEFT = 23
    LOGICAL_NOT = 24
    LOGICAL_AND = 25
    LOGICAL_OR = 26
    NEGATE = 27
    PLUS = 28
    MINUS = 29
    TIMES = 30
    DIVIDE = 31
    MOD = 32
    POSITIVE = 33
    NEGATIVE = 34
    NONZERO = 35
    EQUALS = 36
    NOT_EQUALS = 37
    MIN = 38
    MAX = 39
    LESS_THAN = 40
    GREATER_THAN = 41
    SERVO = 42
    SERVO_8BIT = 43
    SPEED = 44
    ACCELERATION = 45
    GET_POSITION = 46
    GET_MOVING_STATE = 47
    LED_ON = 48
    LED_OFF = 49
    PWM = 50
    PEEK = 51
    POKE = 52
    SERIAL_SEND_BYTE = 53
    CALL = 54