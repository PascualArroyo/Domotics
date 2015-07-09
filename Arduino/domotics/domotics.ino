int dato;
int value;
int alarma;
float valueAux;

void setup()
{
  
  pinMode(13,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(10,OUTPUT); 
  pinMode(9,OUTPUT); 
  pinMode(8,OUTPUT);
  pinMode(7,OUTPUT); 
  pinMode(6,OUTPUT); 
  pinMode(5,OUTPUT); 
  pinMode(4,INPUT);
  pinMode(3,INPUT); 
  pinMode(2,INPUT);  
  
  digitalWrite(13, LOW);
  digitalWrite(12, LOW);
  digitalWrite(11, LOW);
  digitalWrite(10, LOW);
  digitalWrite(9, LOW);
  digitalWrite(8, LOW);
  digitalWrite(7, LOW);
  digitalWrite(6, LOW);
  digitalWrite(5, LOW);
  
  //Serial.begin(115200);
  Serial.begin(9600);
  Serial.println("Ready");
  
}

void loop()
{   
  
  if(Serial.available()> 0)
  { 

    dato = (int) Serial.read();
    delay(50);
    
    switch(dato)  
    { 
      
      case 1:
        // Digital Pin HIGH
        dato = (int) Serial.read();
        delay(50);
        digitalWrite(dato, HIGH);
  
        break;
       
      case 2:
        // Digital Pin LOW
        dato = (int) Serial.read();
        delay(50);
        digitalWrite(dato, LOW);
  
        break;
       
      case 3:
        // Digital Pin Read
        dato = (int) Serial.read();
        delay(50);
        value = digitalRead(dato);
        Serial.println(value);
       
        break;
       
      case 10:
        // PWM
        dato = (int) Serial.read();
        delay(50);
        value = (int) Serial.read();
        delay(50);
        analogWrite(dato, map(value,0,100,0,255));
        
        break;
       
      case 20:
        // AnalogRead
        valueAux = analogRead(Serial.read());
        delay(50);
        Serial.println(valueAux);
        
        break;
       
       
      case 21:
        // AnalogRead temp
        //valueAux = (5.0 * analogRead(Serial.read()) * 100.0) / 1024;
        valueAux = 0.4883 * analogRead(Serial.read());
        delay(50);
        Serial.println(valueAux);
    
        break;
    
      case 50:
        // Alarma
        Serial.println(alarma);
       
        break;
     
      case 51:
        alarma = 0;
       
        break;
     
      case 52:
        alarma = 1;
       
        break;
    
    }
  }
 
 /*
  else
  {
      
    delay(50);
    valueAux = analogRead(SENSORALARMA);
       
    if (valueAux < 500 && alarma == 0)
    {
      alarma = 1;
    }
      
  }*/
  
  delay(100);
   
}
  
