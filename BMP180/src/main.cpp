#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>

Adafruit_BMP085 bmp;

void setup() {
  Serial.begin(9600);
  Wire.begin(21, 22); 
  
  if (!bmp.begin()) {
    Serial.println("Could not find BMP180 sensor!");
    while (1) {}
  }
}

void loop() {
  Serial.println(bmp.readTemperature());
  delay(1000);
}