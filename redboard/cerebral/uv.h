// Pin definitions.
int UVOUT = A0; // Analog output from the sensor.
int REF_3V3 = A1; //3.3V power on the Arduino board.

class UV
{
  public:
    float writeIntensity();
    void update();
  private:
    static int averageAnalogRead(int pinToRead);
    static float mapFloat(float x, float in_min, float in_max, float out_min, float out_max);

    float uvIntensity = 0;
};

// Takes an average of readings on a given pin.
// Returns the average.
int UV::averageAnalogRead(int pinToRead)
{
  byte numberOfReadings = 8;
  unsigned int runningValue = 0; 

  for(int x = 0 ; x < numberOfReadings ; x++) {
    runningValue += analogRead(pinToRead);
  }
  runningValue /= numberOfReadings;

  return runningValue;  
}

// The Arduino Map function but for floats.
// From: http://forum.arduino.cc/index.php?topic=3922.0
float UV::mapFloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

// Update sensor reading.
void UV::update()
{
  int uvLevel = averageAnalogRead(UVOUT);
  int refLevel = averageAnalogRead(REF_3V3);

  float outputVoltage = 3.3 / refLevel * uvLevel;
  uvIntensity = mapFloat(outputVoltage, 0.99, 2.8, 0.0, 15.0);
}

float UV::writeIntensity()
{
  // byte * pointer = (byte *) &uvIntensity;
  // Serial.write(pointer, 4);
  Serial.println(uvIntensity, 6);
}

