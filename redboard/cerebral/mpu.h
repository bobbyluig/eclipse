#ifndef MPU_H
#define MPU_H

// Magnetometer Registers
#define WHO_AM_I_AK8975A    0x00 // should return 0x48
#define INFO                0x01
#define AK8975A_ST1         0x02  // data ready status bit 0
#define AK8975A_ADDRESS     0x0C
#define AK8975A_XOUT_L      0x03  // data
#define AK8975A_XOUT_H      0x04
#define AK8975A_YOUT_L      0x05
#define AK8975A_YOUT_H      0x06
#define AK8975A_ZOUT_L      0x07
#define AK8975A_ZOUT_H      0x08
#define AK8975A_ST2         0x09  // Data overflow bit 3 and data read error status bit 2
#define AK8975A_CNTL        0x0A  // Power down (0000), single-measurement (0001), self-test (1000) and Fuse ROM (1111) modes on bits 3:0
#define AK8975A_ASTC        0x0C  // Self test control
#define AK8975A_ASAX        0x10  // Fuse ROM x-axis sensitivity adjustment value
#define AK8975A_ASAY        0x11  // Fuse ROM y-axis sensitivity adjustment value
#define AK8975A_ASAZ        0x12  // Fuse ROM z-axis sensitivity adjustment value

#define XGOFFS_TC           0x00 // Bit 7 PWR_MODE, bits 6:1 XG_OFFS_TC, bit 0 OTP_BNK_VLD
#define YGOFFS_TC           0x01
#define ZGOFFS_TC           0x02
#define X_FINE_GAIN         0x03 // [7:0] fine gain
#define Y_FINE_GAIN         0x04
#define Z_FINE_GAIN         0x05
#define XA_OFFSET_H         0x06 // User-defined trim values for accelerometer
#define XA_OFFSET_L_TC      0x07
#define YA_OFFSET_H         0x08
#define YA_OFFSET_L_TC      0x09
#define ZA_OFFSET_H         0x0A
#define ZA_OFFSET_L_TC      0x0B
#define SELF_TEST_X         0x0D
#define SELF_TEST_Y         0x0E
#define SELF_TEST_Z         0x0F
#define SELF_TEST_A         0x10
#define XG_OFFS_USRH        0x13  // User-defined trim values for gyroscope, populate with calibration routine
#define XG_OFFS_USRL        0x14
#define YG_OFFS_USRH        0x15
#define YG_OFFS_USRL        0x16
#define ZG_OFFS_USRH        0x17
#define ZG_OFFS_USRL        0x18
#define SMPLRT_DIV          0x19
#define CONFIG              0x1A
#define GYRO_CONFIG         0x1B
#define ACCEL_CONFIG        0x1C
#define FF_THR              0x1D  // Free-fall
#define FF_DUR              0x1E  // Free-fall
#define MOT_THR             0x1F  // Motion detection threshold bits [7:0]
#define MOT_DUR             0x20  // Duration counter threshold for motion interrupt generation, 1 kHz rate, LSB = 1 ms
#define ZMOT_THR            0x21  // Zero-motion detection threshold bits [7:0]
#define ZRMOT_DUR           0x22  // Duration counter threshold for zero motion interrupt generation, 16 Hz rate, LSB = 64 ms
#define FIFO_EN             0x23
#define I2C_MST_CTRL        0x24
#define I2C_SLV0_ADDR       0x25
#define I2C_SLV0_REG        0x26
#define I2C_SLV0_CTRL       0x27
#define I2C_SLV1_ADDR       0x28
#define I2C_SLV1_REG        0x29
#define I2C_SLV1_CTRL       0x2A
#define I2C_SLV2_ADDR       0x2B
#define I2C_SLV2_REG        0x2C
#define I2C_SLV2_CTRL       0x2D
#define I2C_SLV3_ADDR       0x2E
#define I2C_SLV3_REG        0x2F
#define I2C_SLV3_CTRL       0x30
#define I2C_SLV4_ADDR       0x31
#define I2C_SLV4_REG        0x32
#define I2C_SLV4_DO         0x33
#define I2C_SLV4_CTRL       0x34
#define I2C_SLV4_DI         0x35
#define I2C_MST_STATUS      0x36
#define INT_PIN_CFG         0x37
#define INT_ENABLE          0x38
#define DMP_INT_STATUS      0x39  // Check DMP interrupt
#define INT_STATUS          0x3A
#define ACCEL_XOUT_H        0x3B
#define ACCEL_XOUT_L        0x3C
#define ACCEL_YOUT_H        0x3D
#define ACCEL_YOUT_L        0x3E
#define ACCEL_ZOUT_H        0x3F
#define ACCEL_ZOUT_L        0x40
#define TEMP_OUT_H          0x41
#define TEMP_OUT_L          0x42
#define GYRO_XOUT_H         0x43
#define GYRO_XOUT_L         0x44
#define GYRO_YOUT_H         0x45
#define GYRO_YOUT_L         0x46
#define GYRO_ZOUT_H         0x47
#define GYRO_ZOUT_L         0x48
#define EXT_SENS_DATA_00    0x49
#define EXT_SENS_DATA_01    0x4A
#define EXT_SENS_DATA_02    0x4B
#define EXT_SENS_DATA_03    0x4C
#define EXT_SENS_DATA_04    0x4D
#define EXT_SENS_DATA_05    0x4E
#define EXT_SENS_DATA_06    0x4F
#define EXT_SENS_DATA_07    0x50
#define EXT_SENS_DATA_08    0x51
#define EXT_SENS_DATA_09    0x52
#define EXT_SENS_DATA_10    0x53
#define EXT_SENS_DATA_11    0x54
#define EXT_SENS_DATA_12    0x55
#define EXT_SENS_DATA_13    0x56
#define EXT_SENS_DATA_14    0x57
#define EXT_SENS_DATA_15    0x58
#define EXT_SENS_DATA_16    0x59
#define EXT_SENS_DATA_17    0x5A
#define EXT_SENS_DATA_18    0x5B
#define EXT_SENS_DATA_19    0x5C
#define EXT_SENS_DATA_20    0x5D
#define EXT_SENS_DATA_21    0x5E
#define EXT_SENS_DATA_22    0x5F
#define EXT_SENS_DATA_23    0x60
#define MOT_DETECT_STATUS   0x61
#define I2C_SLV0_DO         0x63
#define I2C_SLV1_DO         0x64
#define I2C_SLV2_DO         0x65
#define I2C_SLV3_DO         0x66
#define I2C_MST_DELAY_CTRL  0x67
#define SIGNAL_PATH_RESET   0x68
#define MOT_DETECT_CTRL     0x69
#define USER_CTRL           0x6A  // Bit 7 enable DMP, bit 3 reset DMP
#define PWR_MGMT_1          0x6B  // Device defaults to the SLEEP mode
#define PWR_MGMT_2          0x6C
#define DMP_BANK            0x6D  // Activates a specific bank in the DMP
#define DMP_RW_PNT          0x6E  // Set read/write pointer to a specific start address in specified DMP bank
#define DMP_REG             0x6F  // Register in DMP from which to read or to which to write
#define DMP_REG_1           0x70
#define DMP_REG_2           0x71
#define FIFO_COUNTH         0x72
#define FIFO_COUNTL         0x73
#define FIFO_R_W            0x74
#define WHO_AM_I_MPU9150    0x75  // Should return 0x68

#define MPU9150_ADDRESS     0x68  // Device address when ADO = 0
#define AK8975A_ADDRESS     0x0C  // Address of magnetometer

// Set initial input parameters
enum Ascale {
    AFS_2G = 0,
    AFS_4G,
    AFS_8G,
    AFS_16G
};

enum Gscale {
    GFS_250DPS = 0,
    GFS_500DPS,
    GFS_1000DPS,
    GFS_2000DPS
};

class MPU 
{
public:
    bool initialize();
    bool test();
    bool calibrate();
    bool updateAll();

    // Data output.
    void getData(float * destination);
    void writeData();

     // Scale resolutions per LSB for the sensors.
    float aRes, gRes, mRes;

    int16_t accelCount[3];  // Stores the 16-bit signed accelerometer sensor output
    int16_t gyroCount[3];   // Stores the 16-bit signed gyro sensor output
    int16_t magCount[3];    // Stores the 16-bit signed magnetometer sensor output
    float magCalibration[3] = {0, 0, 0}; // Factory mag calibration
    float gyroBias[3] = {0, 0, 0}, accelBias[3] = {0, 0, 0};      // Bias corrections for gyro and accelerometer
    int16_t tempCount;     // Stores the raw internal chip temperature counts
    float temperature;     // temperature in degrees Centigrade
    float selfTest[6];

    // Manually set these values.
    float magBias[3] = {0, 0, 0}; // magnetometer x, y, z bias.
    uint32_t magRate = 50;  // read rate for magnetometer data.

    float ax, ay, az, gx, gy, gz, mx, my, mz; // variables to hold latest sensor data values   

private:
    // Scales.
    void getAres();
    void getGres();

    // Helper functions.
    static void initMPU9150(uint8_t Gscale, uint8_t Ascale);
    static void initAK8975A(float * destination);
    static void runTests(float * destination);
    static void calibrateDevice(float * dest1, float * dest2);

    // Read functions.
    static void readAccelData(int16_t * destination);
    static void readGyroData(int16_t * destination);
    static void readMagData(int16_t * destination);
    static int16_t readTempData();
    
    // Wire.h methods.
    static void writeByte(uint8_t address, uint8_t subAddress, uint8_t data);
    static uint8_t readByte(uint8_t address, uint8_t subAddress);
    static void readBytes(uint8_t address, uint8_t subAddress, uint8_t count, uint8_t * dest);

    // Configuration.
    bool initialized = false;

    // Specify sensor full scale.
    uint8_t Gscale = GFS_250DPS;
    uint8_t Ascale = AFS_2G;
};

bool MPU::initialize()
{
    if (initialized) {
        return false;
    }

    Wire.begin();

    // Read the WHO_AM_I register, this is a good test of communication.
    uint8_t c = readByte(MPU9150_ADDRESS, WHO_AM_I_MPU9150);
    delay(500);
    
    if (c != 0x68) {
        return false;
    }

    // Initialize gyroscope and accelerometer.
    initMPU9150(Gscale, Ascale);

    // Initialize magnetometer.
    initAK8975A(magCalibration);

    // Get resolutions.
    getAres();
    getGres();
    mRes = 10. * 1229. / 4096.; // Conversion from 1229 microTesla full scale (4096) to 12.29 Gauss full scale.

    // Wait to be safe.
    delay(500);

    return true;    
}

bool MPU::updateAll()
{
    if (!initialized) {
        return false;
    }

    if (!(readByte(MPU9150_ADDRESS, INT_STATUS) & 0x01)) {
        return false;     
    }

    // Read acceleration and convert. Units of (g's).
    readAccelData(accelCount);
    ax = (float) accelCount[0] * aRes;
    ay = (float) accelCount[1] * aRes;
    az = (float) accelCount[2] * aRes;

    // Read gyroscope values and convert to (degress/second).
    readGyroData(gyroCount);
    gx = (float) gyroCount[0] * gRes;
    gy = (float) gyroCount[1] * gRes;
    gz = (float) gyroCount[2] * gRes;

    // Read magnetometer data and convert to (milliGauss).
    readMagData(magCount);
    mx = (float) magCount[0] * mRes * magCalibration[0] - magBias[0];
    my = (float) magCount[1] * mRes * magCalibration[1] - magBias[1];
    mz = (float) magCount[2] * mRes * magCalibration[2] - magBias[2];

    // Read temperature and covert to (degrees Celcius).
    tempCount = readTempData();
    temperature = ((float) tempCount) / 340. + 36.53;

    return true;
}

void MPU::writeData()
{
    byte * ax_pointer = (byte *) &ax; Serial.write(ax_pointer, 4);
    byte * ay_pointer = (byte *) &ay; Serial.write(ay_pointer, 4);
    byte * az_pointer = (byte *) &az; Serial.write(az_pointer, 4);
    byte * gx_pointer = (byte *) &gx; Serial.write(gx_pointer, 4);
    byte * gy_pointer = (byte *) &gy; Serial.write(gy_pointer, 4);
    byte * gz_pointer = (byte *) &gz; Serial.write(gz_pointer, 4);
    byte * mx_pointer = (byte *) &mx; Serial.write(mx_pointer, 4);
    byte * my_pointer = (byte *) &my; Serial.write(my_pointer, 4);
    byte * mz_pointer = (byte *) &mz; Serial.write(mz_pointer, 4);
    byte * temperature_pointer = (byte *) &temperature; Serial.write(temperature_pointer, 4);
}

void MPU::getData(float * destination)
{
    // Construct array of all data;
    destination[0] = ax; destination[1] = ay; destination[2] = az;
    destination[3] = gx; destination[4] = gy; destination[5] = gz;
    destination[6] = mx; destination[7] = my; destination[8] = mz;
    destination[10] = temperature;
}

bool MPU::test()
{
    runTests(selfTest);

    if (selfTest[0] > 1.0f || selfTest[1] > 1.0f || selfTest[2] > 1.0f || selfTest[3] > 1.0f || selfTest[4] > 1.0f || selfTest[5] > 1.0f) {
        return false;
    } 
    else {
        return true;
    }
}

bool MPU::calibrate()
{
    calibrateDevice(gyroBias, accelBias);
    return true;
}

void MPU::getGres()
{
    switch (Gscale) {
    case GFS_250DPS:
        gRes = 250.0/32768.0;
        break;
    case GFS_500DPS:
        gRes = 500.0/32768.0;
        break;
    case GFS_1000DPS:
        gRes = 1000.0/32768.0;
        break;
    case GFS_2000DPS:
        gRes = 2000.0/32768.0;
        break;
    }
}

void MPU::getAres() 
{
    switch (Ascale) {
    case AFS_2G:
        aRes = 2.0/32768.0;
        break;
    case AFS_4G:
        aRes = 4.0/32768.0;
        break;
    case AFS_8G:
        aRes = 8.0/32768.0;
        break;
    case AFS_16G:
        aRes = 16.0/32768.0;
        break;
    }
}

void MPU::readAccelData(int16_t * destination)
{
    uint8_t rawData[6];  // x/y/z accel register data stored here
    readBytes(MPU9150_ADDRESS, ACCEL_XOUT_H, 6, &rawData[0]);  // Read the six raw data registers into data array
    destination[0] = ((int16_t)rawData[0] << 8) | rawData[1] ;  // Turn the MSB and LSB into a signed 16-bit value
    destination[1] = ((int16_t)rawData[2] << 8) | rawData[3] ;
    destination[2] = ((int16_t)rawData[4] << 8) | rawData[5] ;
}


void MPU::readGyroData(int16_t * destination)
{
    uint8_t rawData[6];  // x/y/z gyro register data stored here
    readBytes(MPU9150_ADDRESS, GYRO_XOUT_H, 6, &rawData[0]);  // Read the six raw data registers sequentially into data array
    destination[0] = ((int16_t)rawData[0] << 8) | rawData[1] ;  // Turn the MSB and LSB into a signed 16-bit value
    destination[1] = ((int16_t)rawData[2] << 8) | rawData[3] ;
    destination[2] = ((int16_t)rawData[4] << 8) | rawData[5] ;
}

void MPU::readMagData(int16_t * destination)
{
    uint8_t rawData[6];  // x/y/z gyro register data stored here
    writeByte(AK8975A_ADDRESS, AK8975A_CNTL, 0x01); // toggle enable data read from magnetometer, no continuous read mode!
    delay(10);
    // Only accept a new magnetometer data read if the data ready bit is set and
    // if there are no sensor overflow or data read errors
    if(readByte(AK8975A_ADDRESS, AK8975A_ST1) & 0x01) { // wait for magnetometer data ready bit to be set
        readBytes(AK8975A_ADDRESS, AK8975A_XOUT_L, 6, &rawData[0]);  // Read the six raw data registers sequentially into data array
        destination[0] = ((int16_t)rawData[1] << 8) | rawData[0] ;  // Turn the MSB and LSB into a signed 16-bit value
        destination[1] = ((int16_t)rawData[3] << 8) | rawData[2] ;
        destination[2] = ((int16_t)rawData[5] << 8) | rawData[4] ;
    }
}

int16_t MPU::readTempData()
{
    uint8_t rawData[2];  // x/y/z gyro register data stored here
    readBytes(MPU9150_ADDRESS, TEMP_OUT_H, 2, &rawData[0]);  // Read the two raw data registers sequentially into data array
    return ((int16_t)rawData[0] << 8) | rawData[1] ;  // Turn the MSB and LSB into a 16-bit value
}

void MPU::initAK8975A(float * destination)
{
    uint8_t rawData[3];  // x/y/z gyro register data stored here
    writeByte(AK8975A_ADDRESS, AK8975A_CNTL, 0x00); // Power down
    delay(10);
    writeByte(AK8975A_ADDRESS, AK8975A_CNTL, 0x0F); // Enter Fuse ROM access mode
    delay(10);
    readBytes(AK8975A_ADDRESS, AK8975A_ASAX, 3, &rawData[0]);  // Read the x-, y-, and z-axis calibration values
    destination[0] =  (float)(rawData[0] - 128)/256. + 1.; // Return x-axis sensitivity adjustment values
    destination[1] =  (float)(rawData[1] - 128)/256. + 1.;
    destination[2] =  (float)(rawData[2] - 128)/256. + 1.;
}

void MPU::initMPU9150(uint8_t Gscale, uint8_t Ascale)
{
    // wake up device
    writeByte(MPU9150_ADDRESS, PWR_MGMT_1, 0x00); // Clear sleep mode bit (6), enable all sensors
    delay(100); // Delay 100 ms for PLL to get established on x-axis gyro; should check for PLL ready interrupt
    
    // get stable time source
    writeByte(MPU9150_ADDRESS, PWR_MGMT_1, 0x01);  // Set clock source to be PLL with x-axis gyroscope reference, bits 2:0 = 001
    delay(200);
    
    // Configure Gyro and Accelerometer
    // Disable FSYNC and set accelerometer and gyro bandwidth to 44 and 42 Hz, respectively;
    // DLPF_CFG = bits 2:0 = 010; this sets the sample rate at 1 kHz for both
    // Minimum delay time is 4.9 ms which sets the fastest rate at ~200 Hz
    writeByte(MPU9150_ADDRESS, CONFIG, 0x03);
    
    // Set sample rate = gyroscope output rate/(1 + SMPLRT_DIV)
    writeByte(MPU9150_ADDRESS, SMPLRT_DIV, 0x04);  // Use a 200 Hz rate; the same rate set in CONFIG above
    
    // Set gyroscope full scale range
    // Range selects FS_SEL and AFS_SEL are 0 - 3, so 2-bit values are left-shifted into positions 4:3
    uint8_t c =  readByte(MPU9150_ADDRESS, GYRO_CONFIG);
    writeByte(MPU9150_ADDRESS, GYRO_CONFIG, c & ~0xE0); // Clear self-test bits [7:5]
    writeByte(MPU9150_ADDRESS, GYRO_CONFIG, c & ~0x18); // Clear AFS bits [4:3]
    writeByte(MPU9150_ADDRESS, GYRO_CONFIG, c | Gscale << 3); // Set full scale range for the gyro
    
    // Set accelerometer configuration
    c =  readByte(MPU9150_ADDRESS, ACCEL_CONFIG);
    writeByte(MPU9150_ADDRESS, ACCEL_CONFIG, c & ~0xE0); // Clear self-test bits [7:5]
    writeByte(MPU9150_ADDRESS, ACCEL_CONFIG, c & ~0x18); // Clear AFS bits [4:3]
    writeByte(MPU9150_ADDRESS, ACCEL_CONFIG, c | Ascale << 3); // Set full scale range for the accelerometer

    // Configure Interrupts and Bypass Enable
    // Set interrupt pin active high, push-pull, and clear on read of INT_STATUS, enable I2C_BYPASS_EN so additional chips
    // can join the I2C bus and all can be controlled by the Arduino as master
    writeByte(MPU9150_ADDRESS, INT_PIN_CFG, 0x22);
    writeByte(MPU9150_ADDRESS, INT_ENABLE, 0x01);  // Enable data ready (bit 0) interrupt
}

// Function which accumulates gyro and accelerometer data after device initialization. It calculates the average
// of the at-rest readings and then loads the resulting offsets into accelerometer and gyro bias registers.
void MPU::calibrateDevice(float * dest1, float * dest2)
{
    uint8_t data[12]; // data array to hold accelerometer and gyro x, y, z, data
    uint16_t ii, packet_count, fifo_count;
    int32_t gyro_bias[3]  = {0, 0, 0}, accel_bias[3] = {0, 0, 0};
    
    // reset device, reset all registers, clear gyro and accelerometer bias registers
    writeByte(MPU9150_ADDRESS, PWR_MGMT_1, 0x80); // Write a one to bit 7 reset bit; toggle reset device
    delay(100);
    
    // get stable time source
    // Set clock source to be PLL with x-axis gyroscope reference, bits 2:0 = 001
    writeByte(MPU9150_ADDRESS, PWR_MGMT_1, 0x01);
    writeByte(MPU9150_ADDRESS, PWR_MGMT_2, 0x00);
    delay(200);
    
    // Configure device for bias calculation
    writeByte(MPU9150_ADDRESS, INT_ENABLE, 0x00);   // Disable all interrupts
    writeByte(MPU9150_ADDRESS, FIFO_EN, 0x00);      // Disable FIFO
    writeByte(MPU9150_ADDRESS, PWR_MGMT_1, 0x00);   // Turn on internal clock source
    writeByte(MPU9150_ADDRESS, I2C_MST_CTRL, 0x00); // Disable I2C master
    writeByte(MPU9150_ADDRESS, USER_CTRL, 0x00);    // Disable FIFO and I2C master modes
    writeByte(MPU9150_ADDRESS, USER_CTRL, 0x0C);    // Reset FIFO and DMP
    delay(15);
    
    // Configure MPU6050 gyro and accelerometer for bias calculation
    writeByte(MPU9150_ADDRESS, CONFIG, 0x01);      // Set low-pass filter to 188 Hz
    writeByte(MPU9150_ADDRESS, SMPLRT_DIV, 0x00);  // Set sample rate to 1 kHz
    writeByte(MPU9150_ADDRESS, GYRO_CONFIG, 0x00);  // Set gyro full-scale to 250 degrees per second, maximum sensitivity
    writeByte(MPU9150_ADDRESS, ACCEL_CONFIG, 0x00); // Set accelerometer full-scale to 2 g, maximum sensitivity
    
    uint16_t  gyrosensitivity  = 131;   // = 131 LSB/degrees/sec
    uint16_t  accelsensitivity = 16384;  // = 16384 LSB/g
    
    // Configure FIFO to capture accelerometer and gyro data for bias calculation
    writeByte(MPU9150_ADDRESS, USER_CTRL, 0x40);   // Enable FIFO
    writeByte(MPU9150_ADDRESS, FIFO_EN, 0x78);     // Enable gyro and accelerometer sensors for FIFO  (max size 1024 bytes in MPU-6050)
    delay(80); // accumulate 80 samples in 80 milliseconds = 960 bytes
    
    // At end of sample accumulation, turn off FIFO sensor read
    writeByte(MPU9150_ADDRESS, FIFO_EN, 0x00);        // Disable gyro and accelerometer sensors for FIFO
    readBytes(MPU9150_ADDRESS, FIFO_COUNTH, 2, &data[0]); // read FIFO sample count
    fifo_count = ((uint16_t)data[0] << 8) | data[1];
    packet_count = fifo_count/12; // How many sets of full gyro and accelerometer data for averaging
    
    for (ii = 0; ii < packet_count; ii++) {
        int16_t accel_temp[3] = {0, 0, 0}, gyro_temp[3] = {0, 0, 0};
        readBytes(MPU9150_ADDRESS, FIFO_R_W, 12, &data[0]); // read data for averaging
        accel_temp[0] = (int16_t) (((int16_t)data[0] << 8) | data[1]  ) ;  // Form signed 16-bit integer for each sample in FIFO
        accel_temp[1] = (int16_t) (((int16_t)data[2] << 8) | data[3]  ) ;
        accel_temp[2] = (int16_t) (((int16_t)data[4] << 8) | data[5]  ) ;
        gyro_temp[0]  = (int16_t) (((int16_t)data[6] << 8) | data[7]  ) ;
        gyro_temp[1]  = (int16_t) (((int16_t)data[8] << 8) | data[9]  ) ;
        gyro_temp[2]  = (int16_t) (((int16_t)data[10] << 8) | data[11]) ;
        
        accel_bias[0] += (int32_t) accel_temp[0]; // Sum individual signed 16-bit biases to get accumulated signed 32-bit biases
        accel_bias[1] += (int32_t) accel_temp[1];
        accel_bias[2] += (int32_t) accel_temp[2];
        gyro_bias[0]  += (int32_t) gyro_temp[0];
        gyro_bias[1]  += (int32_t) gyro_temp[1];
        gyro_bias[2]  += (int32_t) gyro_temp[2];
        
    }
    accel_bias[0] /= (int32_t) packet_count; // Normalize sums to get average count biases
    accel_bias[1] /= (int32_t) packet_count;
    accel_bias[2] /= (int32_t) packet_count;
    gyro_bias[0]  /= (int32_t) packet_count;
    gyro_bias[1]  /= (int32_t) packet_count;
    gyro_bias[2]  /= (int32_t) packet_count;
    
    if(accel_bias[2] > 0L) {accel_bias[2] -= (int32_t) accelsensitivity;}  // Remove gravity from the z-axis accelerometer bias calculation
    else {accel_bias[2] += (int32_t) accelsensitivity;}
    
    // Construct the gyro biases for push to the hardware gyro bias registers, which are reset to zero upon device startup
    data[0] = (-gyro_bias[0]/4  >> 8) & 0xFF; // Divide by 4 to get 32.9 LSB per deg/s to conform to expected bias input format
    data[1] = (-gyro_bias[0]/4)       & 0xFF; // Biases are additive, so change sign on calculated average gyro biases
    data[2] = (-gyro_bias[1]/4  >> 8) & 0xFF;
    data[3] = (-gyro_bias[1]/4)       & 0xFF;
    data[4] = (-gyro_bias[2]/4  >> 8) & 0xFF;
    data[5] = (-gyro_bias[2]/4)       & 0xFF;
    
    // Push gyro biases to hardware registers
    writeByte(MPU9150_ADDRESS, XG_OFFS_USRH, data[0]);
    writeByte(MPU9150_ADDRESS, XG_OFFS_USRL, data[1]);
    writeByte(MPU9150_ADDRESS, YG_OFFS_USRH, data[2]);
    writeByte(MPU9150_ADDRESS, YG_OFFS_USRL, data[3]);
    writeByte(MPU9150_ADDRESS, ZG_OFFS_USRH, data[4]);
    writeByte(MPU9150_ADDRESS, ZG_OFFS_USRL, data[5]);
    
    // Output scaled gyro biases for display in the main program
    dest1[0] = (float) gyro_bias[0]/(float) gyrosensitivity;
    dest1[1] = (float) gyro_bias[1]/(float) gyrosensitivity;
    dest1[2] = (float) gyro_bias[2]/(float) gyrosensitivity;
    
    // Construct the accelerometer biases for push to the hardware accelerometer bias registers. These registers contain
    // factory trim values which must be added to the calculated accelerometer biases; on boot up these registers will hold
    // non-zero values. In addition, bit 0 of the lower byte must be preserved since it is used for temperature
    // compensation calculations. Accelerometer bias registers expect bias input as 2048 LSB per g, so that
    // the accelerometer biases calculated above must be divided by 8.
    
    int32_t accel_bias_reg[3] = {0, 0, 0}; // A place to hold the factory accelerometer trim biases
    readBytes(MPU9150_ADDRESS, XA_OFFSET_H, 2, &data[0]); // Read factory accelerometer trim values
    accel_bias_reg[0] = (int16_t) ((int16_t)data[0] << 8) | data[1];
    readBytes(MPU9150_ADDRESS, YA_OFFSET_H, 2, &data[0]);
    accel_bias_reg[1] = (int16_t) ((int16_t)data[0] << 8) | data[1];
    readBytes(MPU9150_ADDRESS, ZA_OFFSET_H, 2, &data[0]);
    accel_bias_reg[2] = (int16_t) ((int16_t)data[0] << 8) | data[1];
    
    uint32_t mask = 1uL; // Define mask for temperature compensation bit 0 of lower byte of accelerometer bias registers
    uint8_t mask_bit[3] = {0, 0, 0}; // Define array to hold mask bit for each accelerometer bias axis
    
    for(ii = 0; ii < 3; ii++) {
        if(accel_bias_reg[ii] & mask) mask_bit[ii] = 0x01; // If temperature compensation bit is set, record that fact in mask_bit
    }
    
    // Construct total accelerometer bias, including calculated average accelerometer bias from above
    accel_bias_reg[0] -= (accel_bias[0]/8); // Subtract calculated averaged accelerometer bias scaled to 2048 LSB/g (16 g full scale)
    accel_bias_reg[1] -= (accel_bias[1]/8);
    accel_bias_reg[2] -= (accel_bias[2]/8);
    
    data[0] = (accel_bias_reg[0] >> 8) & 0xFF;
    data[1] = (accel_bias_reg[0])      & 0xFF;
    data[1] = data[1] | mask_bit[0]; // preserve temperature compensation bit when writing back to accelerometer bias registers
    data[2] = (accel_bias_reg[1] >> 8) & 0xFF;
    data[3] = (accel_bias_reg[1])      & 0xFF;
    data[3] = data[3] | mask_bit[1]; // preserve temperature compensation bit when writing back to accelerometer bias registers
    data[4] = (accel_bias_reg[2] >> 8) & 0xFF;
    data[5] = (accel_bias_reg[2])      & 0xFF;
    data[5] = data[5] | mask_bit[2]; // preserve temperature compensation bit when writing back to accelerometer bias registers
    
    // Push accelerometer biases to hardware registers
    writeByte(MPU9150_ADDRESS, XA_OFFSET_H, data[0]);
    writeByte(MPU9150_ADDRESS, XA_OFFSET_L_TC, data[1]);
    writeByte(MPU9150_ADDRESS, YA_OFFSET_H, data[2]);
    writeByte(MPU9150_ADDRESS, YA_OFFSET_L_TC, data[3]);
    writeByte(MPU9150_ADDRESS, ZA_OFFSET_H, data[4]);
    writeByte(MPU9150_ADDRESS, ZA_OFFSET_L_TC, data[5]);
    
    // Output scaled accelerometer biases for display in the main program
    dest2[0] = (float)accel_bias[0]/(float)accelsensitivity;
    dest2[1] = (float)accel_bias[1]/(float)accelsensitivity;
    dest2[2] = (float)accel_bias[2]/(float)accelsensitivity;
}

// Accelerometer and gyroscope self test; check calibration wrt factory settings
void MPU::runTests(float * destination) // Should return percent deviation from factory trim values, +/- 14 or less deviation is a pass
{
    uint8_t rawData[4];
    uint8_t selfTest[6];
    float factoryTrim[6];
    
    // Configure the accelerometer for self-test
    writeByte(MPU9150_ADDRESS, ACCEL_CONFIG, 0xF0); // Enable self test on all three axes and set accelerometer range to +/- 8 g
    writeByte(MPU9150_ADDRESS, GYRO_CONFIG,  0xE0); // Enable self test on all three axes and set gyro range to +/- 250 degrees/s
    
    delay(250);  // Delay a while to let the device execute the self-test
    
    rawData[0] = readByte(MPU9150_ADDRESS, SELF_TEST_X); // X-axis self-test results
    rawData[1] = readByte(MPU9150_ADDRESS, SELF_TEST_Y); // Y-axis self-test results
    rawData[2] = readByte(MPU9150_ADDRESS, SELF_TEST_Z); // Z-axis self-test results
    rawData[3] = readByte(MPU9150_ADDRESS, SELF_TEST_A); // Mixed-axis self-test results
    
    // Extract the acceleration test results first
    selfTest[0] = (rawData[0] >> 3) | (rawData[3] & 0x30) >> 4 ; // XA_TEST result is a five-bit unsigned integer
    selfTest[1] = (rawData[1] >> 3) | (rawData[3] & 0x0C) >> 4 ; // YA_TEST result is a five-bit unsigned integer
    selfTest[2] = (rawData[2] >> 3) | (rawData[3] & 0x03) >> 4 ; // ZA_TEST result is a five-bit unsigned integer
    
    // Extract the gyration test results first
    selfTest[3] = rawData[0] & 0x1F ; // XG_TEST result is a five-bit unsigned integer
    selfTest[4] = rawData[1] & 0x1F ; // YG_TEST result is a five-bit unsigned integer
    selfTest[5] = rawData[2] & 0x1F ; // ZG_TEST result is a five-bit unsigned integer
    
    // Process results to allow final comparison with factory set values
    factoryTrim[0] = (4096.0*0.34)*(pow((0.92/0.34), (((float)selfTest[0] - 1.0)/30.0))); // FT[Xa] factory trim calculation
    factoryTrim[1] = (4096.0*0.34)*(pow((0.92/0.34), (((float)selfTest[1] - 1.0)/30.0))); // FT[Ya] factory trim calculation
    factoryTrim[2] = (4096.0*0.34)*(pow((0.92/0.34), (((float)selfTest[2] - 1.0)/30.0))); // FT[Za] factory trim calculation
    factoryTrim[3] =  ( 25.0*131.0)*(pow(1.046, ((float)selfTest[3] - 1.0) ));            // FT[Xg] factory trim calculation
    factoryTrim[4] =  (-25.0*131.0)*(pow(1.046, ((float)selfTest[4] - 1.0) ));            // FT[Yg] factory trim calculation
    factoryTrim[5] =  ( 25.0*131.0)*(pow(1.046, ((float)selfTest[5] - 1.0) ));            // FT[Zg] factory trim calculation
    
    //  Output self-test results and factory trim calculation if desired
    //  Serial.println(selfTest[0]); Serial.println(selfTest[1]); Serial.println(selfTest[2]);
    //  Serial.println(selfTest[3]); Serial.println(selfTest[4]); Serial.println(selfTest[5]);
    //  Serial.println(factoryTrim[0]); Serial.println(factoryTrim[1]); Serial.println(factoryTrim[2]);
    //  Serial.println(factoryTrim[3]); Serial.println(factoryTrim[4]); Serial.println(factoryTrim[5]);
    
    // Report results as a ratio of (STR - FT)/FT; the change from Factory Trim of the Self-Test Response
    // To get to percent, must multiply by 100 and subtract result from 100
    for (int i = 0; i < 6; i++) {
        destination[i] = 100.0 + 100.0*((float)selfTest[i] - factoryTrim[i])/factoryTrim[i]; // Report percent differences
    }   
}

void MPU::writeByte(uint8_t address, uint8_t subAddress, uint8_t data)
{
    Wire.beginTransmission(address);  // Initialize the Tx buffer
    Wire.write(subAddress);           // Put slave register address in Tx buffer
    Wire.write(data);                 // Put data in Tx buffer
    Wire.endTransmission();           // Send the Tx buffer
}

uint8_t MPU::readByte(uint8_t address, uint8_t subAddress)
{
    uint8_t data; // `data` will store the register data
    Wire.beginTransmission(address);         // Initialize the Tx buffer
    Wire.write(subAddress);                  // Put slave register address in Tx buffer
    Wire.endTransmission(false);             // Send the Tx buffer, but send a restart to keep connection alive
    Wire.requestFrom(address, (uint8_t) 1);  // Read one byte from slave register address
    data = Wire.read();                      // Fill Rx buffer with result
    return data;                             // Return data read from slave register
}

void MPU::readBytes(uint8_t address, uint8_t subAddress, uint8_t count, uint8_t * dest)
{
    Wire.beginTransmission(address);   // Initialize the Tx buffer
    Wire.write(subAddress);            // Put slave register address in Tx buffer
    Wire.endTransmission(false);       // Send the Tx buffer, but send a restart to keep connection alive
    uint8_t i = 0;
    Wire.requestFrom(address, count);  // Read bytes from slave register address
    while (Wire.available()) {
    dest[i++] = Wire.read(); }         // Put read results in the Rx buffer
}

#endif /* MPU_H */
