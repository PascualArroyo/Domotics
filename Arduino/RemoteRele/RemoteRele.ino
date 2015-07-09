#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

RF24 radio(9,10);

const uint64_t pipes[2] = {0x1049000001LL, 0x1049000002LL};

char recivido[50]="";
char enviado[50] = "";

int estado = 1;
int valueSensor = 0;
int valueRele = 0;

int pinRele = 5;
int pinSensor = 2;

void setup(void) {
  Serial.begin(9600);
  
  pinMode(pinRele, OUTPUT);
  pinMode(pinSensor, INPUT);

  //nRF24 configuración
  radio.begin();
  radio.setChannel(0x4c);
  radio.setAutoAck(1);
  radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.openReadingPipe(1,pipes[0]);
  radio.openWritingPipe(pipes[1]);
  radio.startListening();
  radio.powerUp();
}

void loop() {

    if (radio.available()) {                
      radio.read(&recivido, sizeof(recivido));     
      Serial.print(recivido);
      
      switch (recivido[0])
      {
        case'0':
          
          Serial.print("Estado");
         
          if(estado == 0)
          {
              //Alarm
              enviado[0] = '0';
          }
          else
          {
              //ok
              enviado[0] = '1';
          }
          
          estado = 1;
        
          radio.stopListening();
          radio.write(&enviado,strlen(enviado));  
          radio.startListening();
          break;
          
        case'1':
          Serial.print("Estado Rele");
          
          if(valueRele == 0)
          {
            //off
            enviado[0] = '0';
          }
          else
          {
            //on
            enviado[0] = '1';
          }
          
          radio.stopListening();
          radio.write(&enviado,strlen(enviado));  
          radio.startListening();
          break;
          
         case'2':
          Serial.print("Encender");
          digitalWrite(pinRele, HIGH);
          valueRele = 1;
          enviado[0] = '1';
          radio.stopListening();
          radio.write(&enviado,strlen(enviado));  
          radio.startListening();
          break;
        
        case'3':
          Serial.print("Apagar");
          digitalWrite(pinRele, LOW);
          valueRele = 0;
          enviado[0] = '0';
          radio.stopListening();
          radio.write(&enviado,strlen(enviado));  
          radio.startListening();
          break;
 
      }
      
    }
    
    valueSensor = digitalRead(pinSensor);
    Serial.print(valueSensor);
    if(valueSensor == LOW)
    {
      estado = 0;
    }
    
    delay(500); 
}
