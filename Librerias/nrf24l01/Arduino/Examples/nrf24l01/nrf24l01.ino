#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

//Debug
int serial_putc( char c, FILE * ) 
{
  Serial.write( c );
  return c;
} 

//Debug
void printf_begin(void)
{
  fdevopen( &serial_putc, 0 );
}

//nRF24 Cableado utilizado. El pin 9 es CE y 10 a CSN/SS
//     CE       -> 9
//     SS       -> 10
//     MOSI     -> 11
//     MISO     -> 12
//     SCK      -> 13

RF24 radio(9,10);

const uint64_t pipes[6] = {
  0x65646f4e32LL,0x65646f4e31LL};

int a=0;
char b[4];
String str;
int msg[1];
String theMessage = "";
char rev[50]="";

void setup(void) {
  Serial.begin(57600);
  printf_begin();      //Debug

  //nRF24 configuración
  radio.begin();
  radio.setChannel(0x4c);
  radio.setAutoAck(1);
  radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.openReadingPipe(1,pipes[0]);
  radio.openWritingPipe(pipes[1]);
  radio.startListening();
  radio.printDetails(); //Debug

  radio.powerUp();
};

void loop() {

  if (radio.available()){
    Serial.println("recibido datos");
    while (radio.available()) {                
      radio.read( &rev, sizeof(rev) );     
      Serial.print(rev);  
    }
    Serial.println();
  }  

  a++;
  str=String(a);
  str.toCharArray(b,4);
  char dato[]="--> DATO ";
  strcat(dato,b);
  radio.stopListening();
  Serial.println("Enviando datos...");
  bool ok = radio.write(&dato,strlen(dato));
  radio.startListening(); 
  delay(2000); 
}
