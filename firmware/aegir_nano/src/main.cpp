/*Data packet building and transmitting portion of Leak Detector System.

Receives incoming data values from sensor,
builds these values into a struct, then sends this data packet out.
Runs on Arduino Nano Every.

James Foster
*/
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_BME280.h>

// Define the pins to receive temperature, humidity, and fault detected data
#define RSE_PIN 12
#define FAULT_PIN 2

Adafruit_BME280 bme;

// Define data structure
typedef struct aegir_data {
  unsigned int adc_val1;
  unsigned int adc_val2;
  unsigned int adc_val3;
  unsigned int adc_val4;

  float temp;
  float humidity;
  float probe1;
  float probe2;

  bool leak_detected;
  bool cont;
  bool fault;
  byte checksum;
  const unsigned int eop = 0xA5A5;
} aegir_data;

aegir_data tx_data;

// Create a checksum value for validation purposes
int checkSum(){
  unsigned int sum = 0;
  unsigned char *p = (unsigned char *)&tx_data;
  for (unsigned int i=0; i<(sizeof(tx_data)-sizeof(tx_data.checksum)-sizeof(tx_data.eop)); i++){
    sum ^= p[i];
  }
  return sum;
}

void setup() {
  
  // Open serial communications and wait for port to open:
  Serial.begin(57600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.println("aegir startup!");

  // set the data rate for the Serial port
  Serial1.begin(57600);

  // Slave transmits data to master so set RSE pin high
  pinMode(RSE_PIN, OUTPUT);
  digitalWrite(RSE_PIN, HIGH);

  unsigned status = bme.begin();  

  // If invalid sensor, print an error
  if (!status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
      Serial.print("SensorID was: 0x"); Serial.println(bme.sensorID(),16);
      Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
      Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
      Serial.print("        ID of 0x60 represents a BME 280.\n");
      Serial.print("        ID of 0x61 represents a BME 680.\n");
      while (1) delay(10);
  }

  // Initialise 
  tx_data.adc_val1 = 1;
  tx_data.adc_val2 = 2;
  tx_data.adc_val3 = 3;
  tx_data.adc_val4 = 4;

  tx_data.temp = 0;
  tx_data.humidity = 0;
  tx_data.probe1 = 1;
  tx_data.probe2 = 2;

  tx_data.leak_detected = false;
  tx_data.cont = false;
  tx_data.fault = false;

  tx_data.checksum = 0;
  
  pinMode(FAULT_PIN, INPUT);

}

void loop() 
{
  // Receive temperature, humidity, and fault detected values from digital pins
  Serial.print("Temperature = ");
  Serial.print(bme.readTemperature());
  Serial.println(" °C");

  Serial.print("Humidity = ");
  Serial.print(bme.readHumidity());
  Serial.println(" %");

  int fault_val = digitalRead(FAULT_PIN);
  Serial.print("Fault = ");
  Serial.println(fault_val);

  Serial.println();

  tx_data.temp = (bme.readTemperature());
  tx_data.humidity = (bme.readHumidity());
  tx_data.checksum = checkSum();

  // Index counter into data structure
  byte idx = 0;

  // Pointer to start of data structure
  byte* ptr = (byte *)&tx_data;

  // Loop over data structure, writing byte to serial port and
  // incrementing index until whole structure is sent
  while (idx < sizeof(tx_data))
  {
    Serial1.write(ptr[idx]);
    idx++;
  }

  // Set data structure fault value to digital read fault_val.
  tx_data.fault = (bool)fault_val;

  // Delay 1s before next loop
  delay(1000);

}