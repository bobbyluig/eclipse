#include "Wire.h"
#include "mpu.h"

MPU mpu; // Create MPU9150 object.
int cmd; // Command byte.

// Enumeration for all possible commands.
enum Command {
    MPU_INITIALIZE,
    MPU_TEST,
    MPU_CALIBRATE,
    MPU_UPDATE
};

// Execute the command and write the serial output.
void executeCommand(int cmd)
{
    switch (cmd) {
    case MPU_INITIALIZE:
        Serial.write(mpu.initialize());
        break;
    case MPU_TEST:
        Serial.write(mpu.test());
        break;
    case MPU_CALIBRATE:
        Serial.write(mpu.calibrate());
        break;
    case MPU_UPDATE:
        if (mpu.updateAll()) {
            mpu.writeData();
        }
        else {
            Serial.write(0); // Failed to update. No data available. 
        }
        break;
    }

    Serial.println();
}

void setup()
{
    Wire.begin();
    Serial.begin(9600);
}

void loop()
{
    if (Serial.available() > 0) {
        cmd = Serial.read();
        executeCommand(cmd);
    }
}
