
#include <AFMotor.h>

int LR=14; 
int LL=15;
int cont=0;

AF_DCMotor light(4);
AF_Stepper motor(48, 1);

int cmd=0;
byte state=0;

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  light.setSpeed(255);
  pinMode(LR,OUTPUT); 
  pinMode(LL,OUTPUT); 
  motor.setSpeed(40);
}


void loop(){
  
  
  cmd = int(Serial.read()) - 48;
  
  if(Serial.available()<1)
  {
   
   Serial.println(cmd);
 
   switch(cmd){

     //do a lap
     case 0:
       motor.step(400, FORWARD, INTERLEAVE); 
       break;
       
     //do step
     case 1: 
       motor.step(1, FORWARD, INTERLEAVE); 
       break;
     
     //laser L ON
     case 2:
       bitSet(state,0);
       digitalWrite(LL,HIGH);
       Serial.print(state, BIN);
       break;
          
     //laser L OFF
     case 3: 
       bitClear(state,0);
       digitalWrite(LL,LOW);
       Serial.print(state, BIN);
       break;
       
     //laser R ON
     case 4: 
       bitSet(state,1);
       digitalWrite(LR,HIGH);
       Serial.print(state, BIN);
       break;
       
      //laser R OFF
     case 5: 
       bitClear(state,1);
       digitalWrite(LR,LOW);
       Serial.print(state, BIN);
       break;
       
     //turn light .ON
     case 6: 
       bitSet(state,2);
       light.run(FORWARD);
       break;
       
      //turn led OFF
     case 7: 
       bitClear(state,2);
       light.run(RELEASE);
       break;
     
     case 8:
       Serial.println("RAVE MODE!!!!");
       light.run(RELEASE);
       digitalWrite(LR,LOW);
       digitalWrite(LL,LOW);
       
       cont=0;
       while(cont<10)
       {
         light.run(FORWARD);
         delay(100);
         light.run(RELEASE);
         delay(100);
         cont++;
       }
       
       cont=0;
       while(cont<10)
       {
         digitalWrite(LL,HIGH);
         digitalWrite(LR,LOW);
         delay(100);
         digitalWrite(LL,LOW);
         digitalWrite(LR,HIGH);
         delay(100);
         cont++;
       }
       
       cont=0;
       while(cont<10)
       {
           digitalWrite(LL,LOW);
           digitalWrite(LR,LOW);
           light.run(FORWARD);
           delay(100);
           digitalWrite(LL,HIGH);
           digitalWrite(LR,HIGH);
           light.run(RELEASE);
           delay(100);
           cont++;
       }
     
     light.run(RELEASE);
     digitalWrite(LR,LOW);
     digitalWrite(LL,LOW);
 
   }  
   
  }
  
  
  
  
  
  
  /*
  digitalWrite(LR,HIGH);
  digitalWrite(LL,HIGH);
  light.run(FORWARD);
  delay(100);
  digitalWrite(LR,LOW);
  digitalWrite(LL,LOW);
  light.run(RELEASE);
  delay(100);
  */

}
