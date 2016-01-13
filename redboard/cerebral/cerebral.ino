#include "uv.h"

int cmd; // Command byte.
UV uv; // UV object.

// Enumeration for all possible commands.
enum Command {
  UV_READ
};

// Execute the command and write the serial output.
void executeCommand(int cmd)
{
  switch (cmd) {
    case UV_READ:
      uv.update();
      uv.writeIntensity();
      break;
  }
}

void setup()
{
  Serial.begin(9600);

  pinMode(UVOUT, INPUT);
  pinMode(REF_3V3, INPUT);
}

void loop()
{
  if (Serial.available() > 0) {
    cmd = Serial.read();
    executeCommand(cmd);
  }
}
