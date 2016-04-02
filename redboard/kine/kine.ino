/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 8 Nov 2013
  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo s1;  // create servo object to control a servo
Servo s2;
Servo s3;

// twelve servo objects can be created on most boards
float a0 = 180 - 40.0;
float b0 = 18.0;
float c0 = 140.0;

float t1 = 0;
float t2 = 0;
float t3 = 0;

void setup() {
  s1.attach(2);
  s2.attach(3);
  s3.attach(4);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 12) {
    byte buf1[4];
    byte buf2[4];
    byte buf3[4];
    Serial.readBytes(buf1, 4);
    Serial.readBytes(buf2, 4);
    Serial.readBytes(buf3, 4);

    t1 = *(float*) &buf1;
    t2 = *(float*) &buf2;
    t3 = *(float*) &buf3;
  }
      
  s1.write(a0 + t1 * -1);
  s2.write(b0 + t2);
  s3.write(c0 + t3 * -1);
}

