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


class uscRequest(IntEnum):
    REQUEST_GET_PARAMETER = 0x81
    REQUEST_SET_PARAMETER = 0x82
    REQUEST_GET_VARIABLES = 0x83
    REQUEST_SET_SERVO_VARIABLE = 0x84
    REQUEST_SET_TARGET = 0x85
    REQUEST_CLEAR_ERRORS = 0x86
    REQUEST_GET_SERVO_SETTINGS = 0x87

    # GET STACK and GET CALL STACK are only used on the Mini Maestro.
    REQUEST_GET_STACK = 0x88
    REQUEST_GET_CALL_STACK = 0x89
    REQUEST_SET_PWM = 0x8A

    REQUEST_REINITIALIZE = 0x90
    REQUEST_ERASE_SCRIPT = 0xA0
    REQUEST_WRITE_SCRIPT = 0xA1
    REQUEST_SET_SCRIPT_DONE = 0xA2  # value.low.b is 0 for go 1 for stop 2 for single-step
    REQUEST_RESTART_SCRIPT_AT_SUBROUTINE = 0xA3
    REQUEST_RESTART_SCRIPT_AT_SUBROUTINE_WITH_PARAMETER = 0xA4
    REQUEST_RESTART_SCRIPT = 0xA5
    REQUEST_START_BOOTLOADER = 0xFF


class uscParameter(IntEnum):
    PARAMETER_INITIALIZED = 0  # 1 byte - 0 or 0xFF
    PARAMETER_SERVOS_AVAILABLE = 1  # 1 byte - 0-5
    PARAMETER_SERVO_PERIOD = 2  # 1 byte - ticks allocated to each servo/256
    PARAMETER_SERIAL_MODE = 3  # 1 byte unsigned value.  Valid values are SERIAL_MODE_*.  Init variable.
    PARAMETER_SERIAL_FIXED_BAUD_RATE = 4  # 2-byte unsigned value; 0 means autodetect.  Init parameter.
    PARAMETER_SERIAL_TIMEOUT = 6  # 2-byte unsigned value
    PARAMETER_SERIAL_ENABLE_CRC = 8  # 1 byte boolean value
    PARAMETER_SERIAL_NEVER_SUSPEND = 9  # 1 byte boolean value
    PARAMETER_SERIAL_DEVICE_NUMBER = 10  # 1 byte unsigned value 0-127
    PARAMETER_SERIAL_BAUD_DETECT_TYPE = 11  # 1 byte value

    PARAMETER_IO_MASK_C = 16  # 1 byte - pins used for I/O instead of servo
    PARAMETER_OUTPUT_MASK_C = 17  # 1 byte - outputs that are enabled

    PARAMETER_CHANNEL_MODES_0_3 = 12  # 1 byte - channel modes 0-3
    PARAMETER_CHANNEL_MODES_4_7 = 13  # 1 byte - channel modes 4-7
    PARAMETER_CHANNEL_MODES_8_11 = 14  # 1 byte - channel modes 8-11
    PARAMETER_CHANNEL_MODES_12_15 = 15  # 1 byte - channel modes 12-15
    PARAMETER_CHANNEL_MODES_16_19 = 16  # 1 byte - channel modes 16-19
    PARAMETER_CHANNEL_MODES_20_23 = 17  # 1 byte - channel modes 20-23
    PARAMETER_MINI_MAESTRO_SERVO_PERIOD_L = 18  # servo period: 3-byte unsigned values units of quarter microseconds
    PARAMETER_MINI_MAESTRO_SERVO_PERIOD_HU = 19
    PARAMETER_ENABLE_PULLUPS = 21   # 1 byte: 0 or 1
    PARAMETER_SCRIPT_CRC = 22  # 2 bytes - stores a checksum of the bytecode program for comparison
    PARAMETER_SCRIPT_DONE = 24  # 1 byte - copied to scriptDone on startup
    PARAMETER_SERIAL_MINI_SSC_OFFSET = 25  # 1 byte (0-254)
    PARAMETER_SERVO_MULTIPLIER = 26  # 1 byte (0-255)

    # 9 * 24 = 216 so we can safely start at 30
    PARAMETER_SERVO0_HOME = 30  # 2 byte home position (0=off; 1=ignore)
    PARAMETER_SERVO0_MIN = 32  # 1 byte min allowed value (x2^6)
    PARAMETER_SERVO0_MAX = 33  # 1 byte max allowed value (x2^6)
    PARAMETER_SERVO0_NEUTRAL = 34  # 2 byte neutral position
    PARAMETER_SERVO0_RANGE = 36  # 1 byte range
    PARAMETER_SERVO0_SPEED = 37  # 1 byte (5 mantissa3 exponent) us per 10ms
    PARAMETER_SERVO0_ACCELERATION = 38  # 1 byte (speed changes that much every 10ms)
    PARAMETER_SERVO1_HOME = 39  # 2 byte home position (0=off; 1=ignore)
    PARAMETER_SERVO1_MIN = 41  # 1 byte min allowed value (x2^6)
    PARAMETER_SERVO1_MAX = 42  # 1 byte max allowed value (x2^6)
    PARAMETER_SERVO1_NEUTRAL = 43  # 2 byte neutral position
    PARAMETER_SERVO1_RANGE = 45  # 1 byte range
    PARAMETER_SERVO1_SPEED = 46  # 1 byte (5 mantissa3 exponent) us per 10ms
    PARAMETER_SERVO1_ACCELERATION = 47  # 1 byte (speed changes that much every 10ms)
    PARAMETER_SERVO2_HOME = 48  # 2 byte home position (0=off; 1=ignore)
    PARAMETER_SERVO2_MIN = 50  # 1 byte min allowed value (x2^6)
    PARAMETER_SERVO2_MAX = 51  # 1 byte max allowed value (x2^6)
    PARAMETER_SERVO2_NEUTRAL = 52  # 2 byte neutral position
    PARAMETER_SERVO2_RANGE = 54  # 1 byte range
    PARAMETER_SERVO2_SPEED = 55  # 1 byte (5 mantissa3 exponent) us per 10ms
    PARAMETER_SERVO2_ACCELERATION = 56  # 1 byte (speed changes that much every 10ms)
    PARAMETER_SERVO3_HOME = 57  # 2 byte home position (0=off; 1=ignore)
    PARAMETER_SERVO3_MIN = 59  # 1 byte min allowed value (x2^6)
    PARAMETER_SERVO3_MAX = 60  # 1 byte max allowed value (x2^6)
    PARAMETER_SERVO3_NEUTRAL = 61  # 2 byte neutral position
    PARAMETER_SERVO3_RANGE = 63  # 1 byte range
    PARAMETER_SERVO3_SPEED = 64  # 1 byte (5 mantissa3 exponent) us per 10ms
    PARAMETER_SERVO3_ACCELERATION = 65  # 1 byte (speed changes that much every 10ms)
    PARAMETER_SERVO4_HOME = 66  # 2 byte home position (0=off; 1=ignore)
    PARAMETER_SERVO4_MIN = 68  # 1 byte min allowed value (x2^6)
    PARAMETER_SERVO4_MAX = 69  # 1 byte max allowed value (x2^6)
    PARAMETER_SERVO4_NEUTRAL = 70  # 2 byte neutral position
    PARAMETER_SERVO4_RANGE = 72  # 1 byte range
    PARAMETER_SERVO4_SPEED = 73  # 1 byte (5 mantissa3 exponent) us per 10ms
    PARAMETER_SERVO4_ACCELERATION = 74  # 1 byte (speed changes that much every 10ms)
    PARAMETER_SERVO5_HOME = 75  # 2 byte home position (0=off; 1=ignore)
    PARAMETER_SERVO5_MIN = 77  # 1 byte min allowed value (x2^6)
    PARAMETER_SERVO5_MAX = 78  # 1 byte max allowed value (x2^6)
    PARAMETER_SERVO5_NEUTRAL = 79  # 2 byte neutral position
    PARAMETER_SERVO5_RANGE = 81  # 1 byte range
    PARAMETER_SERVO5_SPEED = 82  # 1 byte (5 mantissa3 exponent) us per 10ms
    PARAMETER_SERVO5_ACCELERATION = 83  # 1 byte (speed changes that much every 10ms


class uscSerialMode(IntEnum):
    SERIAL_MODE_USB_DUAL_PORT = 0
    SERIAL_MODE_USB_CHAINED = 1
    SERIAL_MODE_UART_DETECT_BAUD_RATE = 2
    SERIAL_MODE_UART_FIXED_BAUD_RATE = 3


class uscError(IntEnum):
    ERROR_SERIAL_SIGNAL = 0
    ERROR_SERIAL_OVERRUN = 1
    ERROR_SERIAL_BUFFER_FULL = 2
    ERROR_SERIAL_CRC = 3
    ERROR_SERIAL_PROTOCOL = 4
    ERROR_SERIAL_TIMEOUT = 5
    ERROR_SCRIPT_STACK = 6
    ERROR_SCRIPT_CALL_STACK = 7
    ERROR_SCRIPT_PROGRAM_COUNTER = 8


class performanceFlag(IntEnum):
    PERROR_ADVANCED_UPDATE = 0
    PERROR_BASIC_UPDATE = 1
    PERROR_PERIOD = 2


class ChannelMode(IntEnum):
    Servo = 0
    ServoMultiplied = 1
    Output = 2
    Input = 3


class HomeMode(IntEnum):
    Off = 0
    Ignore = 1
    Goto = 2
