from smbus import SMBus
from enum import IntEnum
import time
import struct

# http:#store.invensense.com/Datasheets/invensense/RM-MPU-9150A-00-v3.0.pdf

class Command(IntEnum):
    WHO_AM_I_AK8975A = 0x00
    INFO = 0x01
    AK8975A_ST1 = 0x02
    AK8975A_ADDRESS = 0x0C
    AK8975A_XOUT_L = 0x03
    AK8975A_XOUT_H = 0x04
    AK8975A_YOUT_L = 0x05
    AK8975A_YOUT_H = 0x06
    AK8975A_ZOUT_L = 0x07
    AK8975A_ZOUT_H = 0x08
    AK8975A_ST2 = 0x09
    AK8975A_CNTL = 0x0A
    AK8975A_ASTC = 0x0C
    AK8975A_ASAX = 0x10
    AK8975A_ASAY = 0x11
    AK8975A_ASAZ = 0x12
    XGOFFS_TC = 0x00
    YGOFFS_TC = 0x01
    ZGOFFS_TC = 0x02
    X_FINE_GAIN = 0x03
    Y_FINE_GAIN = 0x04
    Z_FINE_GAIN = 0x05
    XA_OFFSET_H = 0x06
    XA_OFFSET_L_TC = 0x07
    YA_OFFSET_H = 0x08
    YA_OFFSET_L_TC = 0x09
    ZA_OFFSET_H = 0x0A
    ZA_OFFSET_L_TC = 0x0B
    SELF_TEST_X = 0x0D
    SELF_TEST_Y = 0x0E
    SELF_TEST_Z = 0x0F
    SELF_TEST_A = 0x10
    XG_OFFS_USRH = 0x13
    XG_OFFS_USRL = 0x14
    YG_OFFS_USRH = 0x15
    YG_OFFS_USRL = 0x16
    ZG_OFFS_USRH = 0x17
    ZG_OFFS_USRL = 0x18
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    FF_THR = 0x1D
    FF_DUR = 0x1E
    MOT_THR = 0x1F
    MOT_DUR = 0x20
    ZMOT_THR = 0x21
    ZRMOT_DUR = 0x22
    FIFO_EN = 0x23
    I2C_MST_CTRL = 0x24
    I2C_SLV0_ADDR = 0x25
    I2C_SLV0_REG = 0x26
    I2C_SLV0_CTRL = 0x27
    I2C_SLV1_ADDR = 0x28
    I2C_SLV1_REG = 0x29
    I2C_SLV1_CTRL = 0x2A
    I2C_SLV2_ADDR = 0x2B
    I2C_SLV2_REG = 0x2C
    I2C_SLV2_CTRL = 0x2D
    I2C_SLV3_ADDR = 0x2E
    I2C_SLV3_REG = 0x2F
    I2C_SLV3_CTRL = 0x30
    I2C_SLV4_ADDR = 0x31
    I2C_SLV4_REG = 0x32
    I2C_SLV4_DO = 0x33
    I2C_SLV4_CTRL = 0x34
    I2C_SLV4_DI = 0x35
    I2C_MST_STATUS = 0x36
    INT_PIN_CFG = 0x37
    INT_ENABLE = 0x38
    DMP_INT_STATUS = 0x39
    INT_STATUS = 0x3A
    ACCEL_XOUT_H = 0x3B
    ACCEL_XOUT_L = 0x3C
    ACCEL_YOUT_H = 0x3D
    ACCEL_YOUT_L = 0x3E
    ACCEL_ZOUT_H = 0x3F
    ACCEL_ZOUT_L = 0x40
    TEMP_OUT_H = 0x41
    TEMP_OUT_L = 0x42
    GYRO_XOUT_H = 0x43
    GYRO_XOUT_L = 0x44
    GYRO_YOUT_H = 0x45
    GYRO_YOUT_L = 0x46
    GYRO_ZOUT_H = 0x47
    GYRO_ZOUT_L = 0x48
    EXT_SENS_DATA_00 = 0x49
    EXT_SENS_DATA_01 = 0x4A
    EXT_SENS_DATA_02 = 0x4B
    EXT_SENS_DATA_03 = 0x4C
    EXT_SENS_DATA_04 = 0x4D
    EXT_SENS_DATA_05 = 0x4E
    EXT_SENS_DATA_06 = 0x4F
    EXT_SENS_DATA_07 = 0x50
    EXT_SENS_DATA_08 = 0x51
    EXT_SENS_DATA_09 = 0x52
    EXT_SENS_DATA_10 = 0x53
    EXT_SENS_DATA_11 = 0x54
    EXT_SENS_DATA_12 = 0x55
    EXT_SENS_DATA_13 = 0x56
    EXT_SENS_DATA_14 = 0x57
    EXT_SENS_DATA_15 = 0x58
    EXT_SENS_DATA_16 = 0x59
    EXT_SENS_DATA_17 = 0x5A
    EXT_SENS_DATA_18 = 0x5B
    EXT_SENS_DATA_19 = 0x5C
    EXT_SENS_DATA_20 = 0x5D
    EXT_SENS_DATA_21 = 0x5E
    EXT_SENS_DATA_22 = 0x5F
    EXT_SENS_DATA_23 = 0x60
    MOT_DETECT_STATUS = 0x61
    I2C_SLV0_DO = 0x63
    I2C_SLV1_DO = 0x64
    I2C_SLV2_DO = 0x65
    I2C_SLV3_DO = 0x66
    I2C_MST_DELAY_CTRL = 0x67
    SIGNAL_PATH_RESET = 0x68
    MOT_DETECT_CTRL = 0x69
    USER_CTRL = 0x6A
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C
    DMP_BANK = 0x6D
    DMP_RW_PNT = 0x6E
    DMP_REG = 0x6F
    DMP_REG_1 = 0x70
    DMP_REG_2 = 0x71
    FIFO_COUNTH = 0x72
    FIFO_COUNTL = 0x73
    FIFO_R_W = 0x74
    WHO_AM_I_MPU9150 = 0x75


class Ascale(IntEnum):
    AFS_2G = 0
    AFS_4G = 1
    AFS_8G = 2
    AFS_16G = 3


class Gscale(IntEnum):
    GFS_250DPS = 0
    GFS_500DPS = 1
    GFS_1000DPS = 2
    GFS_2000DPS = 3


class Address(IntEnum):
    MPU9150_ADDRESS = 0x68
    AK8975A_ADDRESS = 0x0C


class MPU:
    # Define all constants.
    def __init__(self, port=1, aScale=Ascale.AFS_2G, gScale=Gscale.GFS_250DPS):
        self.bus = SMBus(port)
        self.initialized = False

        self.int16x1 = struct.Struct('>h')
        self.int16x3 = struct.Struct('>hhh')

        self.aScale = aScale
        self.gScale = gScale
        self.aRes = self.getAres(self.aScale)
        self.gRes = self.getGres(self.gScale)
        self.mRes = 10 * 1229 / 4096 # Conversion from 1229 microTesla full scale (4096) to 12.29 Gauss full scale.

        self.gyroBias = [0, 0, 0]
        self.accelBias = [0, 0, 0]
        self.magCalibration = [0, 0, 0]

    def initialize(self):
        if self.initialized:
            return False

        c = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.WHO_AM_I_MPU9150)
        if c != 0x68:
            return False

        self.initMPU9150()
        self.initAK8975A()

        self.initialized = True

        return True

    @staticmethod
    def getAres(scale):
        if scale == Ascale.AFS_2G:
            return 2 / 32768
        elif scale == Ascale.AFS_4G:
            return 4 / 32768
        elif scale == Ascale.AFS_8G:
            return 8 / 32768
        elif scale == Ascale.AFS_16G:
            return 16 / 32768

    @staticmethod
    def getGres(scale):
        if scale == Gscale.GFS_250DPS:
            return 250 / 32768
        elif scale == Gscale.GFS_500DPS:
            return 500 / 32768
        elif scale == Gscale.GFS_1000DPS:
            return 1000.0 / 32768.0
        elif scale == Gscale.GFS_2000DPS:
            return 2000.0 / 32768.0

    def getAll(self):
        if not self.initialized:
            return None

        if not self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.INT_STATUS) & 0x01:
            return None

        ax, ay, az = self.readAccelData()
        ax *= self.aRes
        ay *= self.aRes
        az *= self.aRes

        gx, gy, gz = self.readGyroData()
        gx *= self.gRes
        gy *= self.gRes
        gz *= self.gRes

        mag = self.readMagData()
        if mag is not None:
            mx, my, mz = mag
            mx *= self.mRes * self.magCalibration[0]
            my *= self.mRes * self.magCalibration[1]
            mz *= self.mRes * self.magCalibration[2]
        else:
            mx, my, mz = 0, 0, 0

        temp = self.readTempData()
        temp = temp / 340 + 36.5

        return ax, ay, az, gx, gy, gz, mx, my, mz, temp

    def readAccelData(self):
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.ACCEL_XOUT_H, 6)

        return self.int16x3.unpack(data)

    def readGyroData(self):
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.GYRO_XOUT_H, 6)

        return self.int16x3.unpack(data)

    def readMagData(self):
        self.bus.write_byte_data(Address.AK8975A_ADDRESS, Command.AK8975A_CNTL, 0x01)
        time.sleep(0.01)

        if self.bus.read_byte_data(Address.AK8975A_ADDRESS, Command.AK8975A_ST1) & 0x01:
            data = self.bus.read_i2c_block_data(Address.AK8975A_ADDRESS, Command.AK8975A_XOUT_L, 6)

            return self.int16x3.unpack(data)
        else:
            return None

    def readTempData(self):
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.TEMP_OUT_H, 2)

        return self.int16x1.unpack(data)[0]

    def calibrateDevice(self):
        # Reset device, reset all registers, clear gyro and accelerometer bias registers.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.PWR_MGMT_1, 0x80) # Write a one to bit 7 reset bit toggle reset device.Command.
        time.sleep(0.1)
    
        # Get stable time source.
        # Set clock source to be PLL with x-axis gyroscope reference, bits 2:0 = 001.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.PWR_MGMT_1, 0x01)
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.PWR_MGMT_2, 0x00)
        time.sleep(0.2)
    
        # Configure device for bias calculation.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.INT_ENABLE, 0x00)   # Disable all interrupts
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.FIFO_EN, 0x00)      # Disable FIFO
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.PWR_MGMT_1, 0x00)   # Turn on internal clock source
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_MST_CTRL, 0x00) # Disable I2C master
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.USER_CTRL, 0x00)    # Disable FIFO and I2C master modes
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.USER_CTRL, 0x0C)    # Reset FIFO and DMP
        time.sleep(0.015)
    
        # Configure MPU6050 gyro and accelerometer for bias calculation.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.CONFIG, 0x01)      # Set low-pass filter to 188 Hz
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.SMPLRT_DIV, 0x00)  # Set sample rate to 1 kHz
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.GYRO_CONFIG, 0x00)  # Set gyro full-scale to 250 degrees per second, maximum sensitivity
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ACCEL_CONFIG, 0x00) # Set accelerometer full-scale to 2 g, maximum sensitivity
    
        gyro_sensitivity  = 131 # = 131 LSB/degrees/sec
        accel_sensitivity = 16384 # = 16384 LSB/g
    
        # Configure FIFO to capture accelerometer and gyro data for bias calculation.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.USER_CTRL, 0x40)   # Enable FIFO
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.FIFO_EN, 0x78)     # Enable gyro and accelerometer sensors for FIFO  (max size 1024 bytes in MPU-6050)
        time.sleep(0.08) # accumulate 80 samples in 80 milliseconds = 960 bytes
    
        # At end of sample accumulation, turn off FIFO sensor read
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.FIFO_EN, 0x00)        # Disable gyro and accelerometer sensors for FIFO
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.FIFO_COUNTH, 2) # read FIFO sample count
        fifo_count = self.int16x1.unpack(data)[0]
        packet_count = int(fifo_count // 12) # How many sets of full gyro and accelerometer data for averaging

        a_bias = [0, 0, 0]
        g_bias = [0, 0, 0]

        for ii in range(packet_count):
            data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.FIFO_R_W, 12) # read data for averaging
            ax, ay, az = self.int16x3.unpack(data[0:6])
            gx, gy, gz = self.int16x3.unpack(data[6:12])

            a_bias[0] += ax
            a_bias[1] += ay
            a_bias[2] += az
            g_bias[0] += gx
            g_bias[1] += gy
            g_bias[2] += gz

        # Normalize sums to get average count biases.
        a_bias[0] /= packet_count
        a_bias[1] /= packet_count
        a_bias[2] /= packet_count
        g_bias[0] /= packet_count
        g_bias[1] /= packet_count
        g_bias[2] /= packet_count

        # Remove gravity from the z-axis accelerometer bias calculation.
        if a_bias[2] > 0:
            a_bias[2] -= accel_sensitivity
        else:
            a_bias[2] += accel_sensitivity

        # Construct the gyro biases for push to the hardware gyro bias registers, which are reset to zero upon device startup
        g_bias_write = self.int16x3.pack(int(-g_bias[0] // 4), int(-g_bias[1] // 4), int(-g_bias[2] // 4))

        # Push gyro biases to hardware registers
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.XG_OFFS_USRH, g_bias_write[0])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.XG_OFFS_USRL, g_bias_write[1])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.YG_OFFS_USRH, g_bias_write[2])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.YG_OFFS_USRL, g_bias_write[3])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ZG_OFFS_USRH, g_bias_write[4])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ZG_OFFS_USRL, g_bias_write[5])
    
        # Construct the accelerometer biases for push to the hardware accelerometer bias registers. These registers contain
        # factory trim values which must be added to the calculated accelerometer biases on boot up these registers will hold
        # non-zero values. In addition, bit 0 of the lower byte must be preserved since it is used for temperature
        # compensation calculations. Accelerometer bias registers expect bias input as 2048 LSB per g, so that
        # the accelerometer biases calculated above must be divided by 8.
        accel_bias_reg = [0] * 3 # A place to hold the factory accelerometer trim biases
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.XA_OFFSET_H, 2) # Read factory accelerometer trim values
        accel_bias_reg[0] = self.int16x1.unpack(data)[0]
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.YA_OFFSET_H, 2)
        accel_bias_reg[1] = self.int16x1.unpack(data)[0]
        data = self.bus.read_i2c_block_data(Address.MPU9150_ADDRESS, Command.ZA_OFFSET_H, 2)
        accel_bias_reg[2] = self.int16x1.unpack(data)[0]

        mask_bit = [0] * 3

        for i in range(3):
            if accel_bias_reg[i] & 1:
                mask_bit[i] = 0x01 # If temperature compensation bit is set, record that fact in mask_bit
    
        # Construct total accelerometer bias, including calculated average accelerometer bias from above
        accel_bias_reg[0] -= a_bias[0] / 8 # Subtract calculated averaged accelerometer bias scaled to 2048 LSB/g (16 g full scale)
        accel_bias_reg[1] -= a_bias[1] / 8
        accel_bias_reg[2] -= a_bias[2] / 8

        a_bias_write = self.int16x3.pack(int(accel_bias_reg[0]), int(accel_bias_reg[1]), int(accel_bias_reg[2]))
        a_bias_write = bytearray(a_bias_write) # Allow editing.

        a_bias_write[1] |= mask_bit[0] # preserve temperature compensation bit
        a_bias_write[3] |= mask_bit[1] # preserve temperature compensation bit
        a_bias_write[5] |= mask_bit[2] # preserve temperature compensation bit

        # Push accelerometer biases to hardware registers
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.XA_OFFSET_H, a_bias_write[0])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.XA_OFFSET_L_TC, a_bias_write[1])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.YA_OFFSET_H, a_bias_write[2])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.YA_OFFSET_L_TC, a_bias_write[3])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ZA_OFFSET_H, a_bias_write[4])
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ZA_OFFSET_L_TC, a_bias_write[5])

        # Output scaled gyro biases for display in the main program.
        self.gyroBias[0] = g_bias[0] / gyro_sensitivity
        self.gyroBias[1] = g_bias[1] / gyro_sensitivity
        self.gyroBias[2] = g_bias[2] / gyro_sensitivity

        # Output scaled accelerometer biases for display in the main program
        self.accelBias[0] = a_bias[0] / accel_sensitivity
        self.accelBias[1] = a_bias[1] / accel_sensitivity
        self.accelBias[2] = a_bias[2] / accel_sensitivity

    def runTests(self):
        rawData = [0] * 4
        selfTest = [0] * 6
        factoryTrim = [0] * 6

        # Configure the accelerometer for self-test.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ACCEL_CONFIG, 0xF0) # Enable self test on all three axes and set accelerometer range to +/- 8 g
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.GYRO_CONFIG,  0xE0) # Enable self test on all three axes and set gyro range to +/- 250 degrees/s
    
        time.sleep(0.25)  # Delay a while to let the device execute the self-test.
    
        rawData[0] = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.SELF_TEST_X) # X-axis self-test results
        rawData[1] = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.SELF_TEST_Y) # Y-axis self-test results
        rawData[2] = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.SELF_TEST_Z) # Z-axis self-test results
        rawData[3] = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.SELF_TEST_A) # Mixed-axis self-test results
    
        # Extract the acceleration test results first
        selfTest[0] = (rawData[0] >> 3) | (rawData[3] & 0x30) >> 4  # XA_TEST result is a five-bit unsigned integer
        selfTest[1] = (rawData[1] >> 3) | (rawData[3] & 0x0C) >> 4  # YA_TEST result is a five-bit unsigned integer
        selfTest[2] = (rawData[2] >> 3) | (rawData[3] & 0x03) >> 4  # ZA_TEST result is a five-bit unsigned integer
    
        # Extract the gyration test results first
        selfTest[3] = rawData[0] & 0x1F  # XG_TEST result is a five-bit unsigned integer
        selfTest[4] = rawData[1] & 0x1F  # YG_TEST result is a five-bit unsigned integer
        selfTest[5] = rawData[2] & 0x1F  # ZG_TEST result is a five-bit unsigned integer
    
        # Process results to allow final comparison with factory set values
        factoryTrim[0] = (4096 * 0.34) * (0.92/0.34) ** ((selfTest[0] - 1) / 30) # FT[Xa] factory trim calculation
        factoryTrim[1] = (4096 * 0.34) * (0.92/0.34) ** ((selfTest[1] - 1) / 30) # FT[Ya] factory trim calculation
        factoryTrim[2] = (4096 * 0.34) * (0.92/0.34) ** ((selfTest[2] - 1) / 30) # FT[Za] factory trim calculation
        factoryTrim[3] = ( 25 * 131) * 1.046 ** (selfTest[3] - 1) # FT[Xg] factory trim calculation
        factoryTrim[4] = (-25 * 131) * 1.046 ** (selfTest[4] - 1) # FT[Yg] factory trim calculation
        factoryTrim[5] = ( 25 * 131) * 1.046 ** (selfTest[5] - 1) # FT[Zg] factory trim calculation

        # Report results as a ratio of (STR - FT)/FT the change from Factory Trim of the Self-Test Response
        # To get to percent, must multiply by 100 and subtract result from 100.
        error = [100 + 100 * (selfTest[i] - factoryTrim[i]) / factoryTrim[i] for i in range(6)]
        success = not any(e > 1 for e in error)

        return success, error

    def initAK8975A(self):
        self.bus.write_byte_data(Address.AK8975A_ADDRESS, Command.AK8975A_CNTL, 0x00) # Power down
        time.sleep(0.01)
        self.bus.write_byte_data(Address.AK8975A_ADDRESS, Command.AK8975A_CNTL, 0x0F) # Enter Fuse ROM access mode
        time.sleep(0.01)
        data = self.bus.read_i2c_block_data(Address.AK8975A_ADDRESS, Command.AK8975A_ASAX, 3) # Read the x-, y-, and z-axis calibration values
        self.magCalibration[0] = (data[0] - 128) / 256 + 1
        self.magCalibration[1] = (data[1] - 128) / 256 + 1
        self.magCalibration[2] = (data[2] - 128) / 256 + 1

    def initMPU9150(self):
        # Wake up device.
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.PWR_MGMT_1, 0x00)
        time.sleep(0.1)

        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.PWR_MGMT_1, 0x01)
        time.sleep(0.2)

        # Configure Gyro and Accelerometer
        # Disable FSYNC and set accelerometer and gyro bandwidth to 44 and 42 Hz, respectively;
        # DLPF_CFG = bits 2:0 = 010; this sets the sample rate at 1 kHz for both
        # Minimum delay time is 4.9 ms which sets the fastest rate at ~200 Hz
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.CONFIG, 0x03)

        # Set sample rate = gyroscope output rate/(1 + SMPLRT_DIV)
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.SMPLRT_DIV, 0x04) # Use a 200 Hz rate; the same rate set in CONFIG above

        # Set gyroscope full scale range
        # Range selects FS_SEL and AFS_SEL are 0 - 3, so 2-bit values are left-shifted into positions 4:3
        c = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.GYRO_CONFIG)
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.GYRO_CONFIG, c & ~0xE0) # Clear self-test bits [7:5]
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.GYRO_CONFIG, c & ~0x18) # Clear AFS bits [4:3]
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.GYRO_CONFIG, c | self.gScale << 3) # Set full scale range for the gyro
    
        # Set accelerometer configuration
        c = self.bus.read_byte_data(Address.MPU9150_ADDRESS, Command.ACCEL_CONFIG)
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ACCEL_CONFIG, c & ~0xE0) # Clear self-test bits [7:5]
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ACCEL_CONFIG, c & ~0x18) # Clear AFS bits [4:3]
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.ACCEL_CONFIG, c | self.gScale << 3) # Set full scale range for the accelerometer

        '''
        # Configure Magnetometer for FIFO
        # Initialize AK8975A for write
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV1_ADDR, 0x0C)  # Write address of AK8975A
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV1_REG, 0x0A)   # Register from within the AK8975 to which to write
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV1_DO, 0x01)    # Register that holds output data written into Slave 1 when in write mode
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV1_CTRL, 0x81)  # Enable Slave 1

        # Set up auxilliary communication with AK8975A for FIFO read
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV0_ADDR, 0x8C) # Enable and read address (0x0C) of the AK8975A
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV0_REG, 0x03)  # Register within AK8975A from which to start data read
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.I2C_SLV0_CTRL, 0x86) # Read six bytes and swap bytes

        # Configure FIFO
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.INT_ENABLE, 0x00) # Disable all interrupts
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.FIFO_EN, 0x00)    # Disable FIFO
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.USER_CTRL, 0x02)  # Reset I2C master and FIFO and DMP
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.USER_CTRL, 0x00)  # Disable FIFO

        time.sleep(0.1)
        '''

        # Configure Interrupts and Bypass Enable
        # Set interrupt pin active high, push-pull, and clear on read of INT_STATUS, enable I2C_BYPASS_EN so additional chips
        # can join the I2C bus and all can be controlled by the Arduino as master
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.INT_PIN_CFG, 0x22)
        self.bus.write_byte_data(Address.MPU9150_ADDRESS, Command.INT_ENABLE, 0x01)  # Enable data ready (bit 0) interrupt


mpu = MPU()
mpu.calibrateDevice()
mpu.initialize()
print(mpu.getAll())