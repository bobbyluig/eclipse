#include "Wire.h"

int incomingByte = 0;

void setup() {
    Wire.begin();
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        incomingByte = Serial.read();
        if (incomingByte == 69) {
            Serial.println("Hello!");
        }
    }
}
