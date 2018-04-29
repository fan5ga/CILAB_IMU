#include "BNO055.h"
#include "MS5837.h"
#include "TSYS01.h"



union unFC
{
  unsigned char b[4];
  float f;
} trans[9];



BNO055 bno = BNO055(55);
MS5837 sensor;
TSYS01 t_sensor;



void myprint(sensors_event_t event)
{
  //Serial.print("X: ");
  Serial.print(event.orientation.x, 2);
  Serial.print(", ");
  Serial.print(event.orientation.y, 2);
  Serial.print(", ");
  Serial.print(event.orientation.z, 2);

  Serial.print(", ");
  Serial.print(event.acceleration.x, 2);
  Serial.print(", ");
  Serial.print(event.acceleration.y, 2);
  Serial.print(", ");
  Serial.print(event.acceleration.z, 2);

  Serial.print(", ");
  Serial.print(event.magnetic.x, 2);
  Serial.print(", ");
  Serial.print(event.magnetic.y, 2);
  Serial.print(", ");
  Serial.print(event.magnetic.z, 2);
  Serial.print(", ");
  Serial.print(sensor.pressure());
  Serial.print(", ");
  Serial.print(t_sensor.temperature());
  Serial.print("\r\n");


}


void setup(void)
{
  pinMode(49, OUTPUT);
  pinMode(13, OUTPUT);
  digitalWrite(49, HIGH);
  Wire.begin();
  Serial.begin(115200);
  //Serial.print("X: ");
  sensor.init();
  t_sensor.init();
  sensor.setModel(MS5837::MS5837_30BA);
  sensor.setFluidDensity(997); // kg/m^3 (freshwater, 1029 for seawater)
  delay(1000);
  digitalWrite(49, LOW);
  bno.begin();
}

void loop(void)
{
  digitalWrite(13, HIGH);

  sensors_event_t event;
  bno.getEvent(&event);
  sensor.read();
  t_sensor.read();

  digitalWrite(13, LOW);

  myprint(event);
}

