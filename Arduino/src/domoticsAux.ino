#include "Wire.h"
#include "SPI.h"

#include "nRF24L01.h"
#include "RF24.h"

#include "SparkFunHTU21D.h"
#include "SparkFunTSL2561.h"
#include "Adafruit_BMP085.h"

RF24 radio(9, 10);

SFE_TSL2561 light;
Adafruit_BMP085 bmp;
HTU21D myHumidity;

const uint64_t pipes[2] = {0x<PIPE_SEND>LL, 0x<PIPE_RECV>LL};

char recvComand[2] = "";
char sendComand[2] = "";
char sendInfo[32] = "";

int motionDetected = 0;
int valueSensor = 0;
int valueRele = 0;

int pinSensor = 4;
int pinRele = 7;
int pinLed = 8;

//Sensors
boolean gain = 0;
unsigned int ms;
unsigned char time = 2;
unsigned int data0, data1;

float temp = 0;
float hum = 0;
float pres = 0;
double lux = 0;

char str_temp[6];
char str_hum[6];
char str_pres[8];
char str_lux[10];

void setup(void) {

  pinMode(pinSensor, INPUT);
  pinMode(pinRele, OUTPUT);
  pinMode(pinLed, OUTPUT);

  //nRF24 configuracion
  radio.begin();
  radio.setChannel(0x4c);
  radio.setAutoAck(1);
  radio.setRetries(15, 15);
  radio.setPayloadSize(32);
  radio.openReadingPipe(1, pipes[0]);
  radio.openWritingPipe(pipes[1]);
  radio.startListening();
  radio.powerUp();

  myHumidity.begin();
  bmp.begin();
  light.begin();
  light.setTiming(gain, time, ms);
  light.setPowerUp();

  digitalWrite(pinLed, HIGH);

}

void loop() {

  if (radio.available()) {

    radio.read(&recvComand, sizeof(recvComand));

    switch (recvComand[0])
    {
      case'0':

        sprintf(sendComand, "%d|", motionDetected);
        
        motionDetected = 0;

        radio.stopListening();
        radio.write(&sendComand, strlen(sendComand));
        radio.startListening();
        break;

      case'1':

        sprintf(sendComand, "%d|", valueRele);
        radio.stopListening();
        radio.write(&sendComand, strlen(sendComand));
        radio.startListening();
        break;

      case'2':

        digitalWrite(pinRele, HIGH);
        valueRele = 1;
        sprintf(sendComand, "%d|", valueRele);
        radio.stopListening();
        radio.write(&sendComand, strlen(sendComand));
        radio.startListening();
        break;

      case'3':

        digitalWrite(pinRele, LOW);
        valueRele = 0;
        sprintf(sendComand, "%d|", valueRele);
        radio.stopListening();
        radio.write(&sendComand, strlen(sendComand));
        radio.startListening();
        break;

      case'4':
      
        if (bmp.begin())
        {
          temp = myHumidity.readTemperature();
          hum = myHumidity.readHumidity();
          pres = bmp.readPressure();

          light.getData(data0, data1);
          light.getLux(gain, ms, data0, data1, lux);
        }
        else
        {
          temp = 0;
          hum = 0;
          pres = 0;
          lux = 0;
        }

        dtostrf(temp, 4, 2, str_temp);
        dtostrf(hum, 4, 2, str_hum);
        dtostrf(pres / 100.0, 4, 2, str_pres);
        dtostrf(lux, 4, 2, str_lux);

        sprintf(sendInfo, "%s|%s|%s|%s|", str_temp, str_hum, str_pres, str_lux);
        radio.stopListening();
        radio.write(&sendInfo, strlen(sendInfo));
        radio.startListening();
        
        break;

    }

  }

  valueSensor = digitalRead(pinSensor);

  if (valueSensor == HIGH)
  {
    motionDetected = 1;
  }
  
  delay(100);
  
}
