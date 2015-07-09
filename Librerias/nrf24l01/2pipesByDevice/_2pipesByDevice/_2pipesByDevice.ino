#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"


//nRF24 Cableado utilizado. El pin 9 es CE y 10 a CSN/SS
//     CE       -> 9
//     SS       -> 10
//     MOSI     -> 11
//     MISO     -> 12
//     SCK      -> 13

RF24 radio(9,10);

const uint64_t pipes[6] = {
  0x65646f4e32LL, 0x65646f4e31LL};


char recivido[50]="";
char enviado[50] = "Me ha llegado soy Arduino 1"; 

void setup(void) {
  Serial.begin(57600);

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

  if (radio.available()){
    Serial.println("recibido datos");
    while (radio.available()) {                
      radio.read(&recivido, sizeof(recivido));     
      Serial.print(recivido);
    }
    
      radio.stopListening();
      bool ok = radio.write(&enviado,strlen(enviado));  
      radio.startListening(); 

    Serial.println();
  }  
   Serial.print(".");
  delay(500); 
}
