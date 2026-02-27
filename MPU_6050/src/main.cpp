#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

void setup()
{
  Serial.begin(9600);
  Wire.begin(21,22);

  if (!mpu.begin())
  {
    Serial.println("MPU_6050 sensor not found.");
    while (1){}
  }
}

void loop()
{
  sensors_event_t a ,g ,temp;
  mpu.getEvent(&a,&g,&temp);

  float ay = (float) a.acceleration.y;
  float az = (float) a.acceleration.z;
  float temperature = (float) temp.temperature;

  Serial.print("ay: ");
  Serial.print(ay);
  Serial.print(" ");
  Serial.print("az: ");
  Serial.print(az);
  Serial.print(" ");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" ");
  delay(500);
}