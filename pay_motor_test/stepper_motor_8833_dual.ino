#include <SoftwareSerial.h>

int AIN1 = 8; // DRV8833 pin 16
int AIN2 = 9; // DRV8833 pin 15
int BIN1 = 10; // DRV8833 pin 9
int BIN2 = 11; // DRV8833 pin 10
int nSLEEP = 7; // DRV8833 pin 1, to enable set to high
//int nFAULT = 6; //DRV8833 pin 8, logic low in fault

int nSLEEP2 = 2;
int AIN1_2 = 3;
int AIN2_2 = 4;
int BIN1_2 = 5;
int BIN2_2 = 6;


void setup() {
  Serial.begin(9600);
  Serial.println("Serial Ready");

  pinMode(AIN1,OUTPUT);
  pinMode(AIN2,OUTPUT);
  pinMode(BIN1,OUTPUT);
  pinMode(BIN2,OUTPUT);
  pinMode(nSLEEP,OUTPUT);
  //pinMode(nFAULT,INPUT);

  pinMode(AIN1_2,OUTPUT);
  pinMode(AIN2_2,OUTPUT);
  pinMode(BIN1_2,OUTPUT);
  pinMode(BIN2_2,OUTPUT);
  pinMode(nSLEEP2,OUTPUT);
}


bool fault = digitalRead(6);

void enableMotor() {
    // Enable motors and disable sleep
    // nSLEEP = HIGH to enable motor
    digitalWrite(nSLEEP,HIGH);
    digitalWrite(nSLEEP2,HIGH);
    Serial.println("Enabled");
    //delay(OnTime);
    //Serial.println("Done test");
}


void disableMotors() {
    // Disable motors and enable sleep
    // nSLEEP LOW to enter sleep mode and reset all internal logic
    digitalWrite(nSLEEP,LOW);
    digitalWrite(nSLEEP2,LOW);
    Serial.println("Disabled");
}


void actuateMotor(uint16_t period, uint16_t num_cycles, bool forward) {
      uint16_t delayTime = period / 4;

      enableMotor();
     for (uint16_t i = 0; i < num_cycles; i++){
        if (forward){
          delay(delayTime);
          digitalWrite(AIN1, HIGH);
          digitalWrite(AIN1_2, HIGH);
          digitalWrite(AIN2, LOW);
          digitalWrite(AIN2_2,LOW);
          digitalWrite(BIN1, LOW);
          digitalWrite(BIN1_2, LOW);
          digitalWrite(BIN2, LOW);
          digitalWrite(BIN1_2, LOW);
          
          delay(delayTime);
          //digitalWrite(AIN1, LOW);
          //digitalWrite(AIN2, LOW);
          //digitalWrite(BIN1, HIGH);
          //digitalWrite(BIN2, LOW);

          digitalWrite(AIN1, LOW);
          digitalWrite(AIN1_2, LOW);
          digitalWrite(AIN2, LOW);
          digitalWrite(AIN2_2,LOW);
          digitalWrite(BIN1, HIGH);
          digitalWrite(BIN1_2, HIGH);
          digitalWrite(BIN2, LOW);
          digitalWrite(BIN1_2, LOW);
          
          delay(delayTime);
          //digitalWrite(AIN1, LOW);
          //digitalWrite(AIN2, HIGH);
          //digitalWrite(BIN1, LOW);
          //digitalWrite(BIN2, LOW);

          digitalWrite(AIN1, LOW);
          digitalWrite(AIN1_2, LOW);
          digitalWrite(AIN2, HIGH);
          digitalWrite(AIN2_2,HIGH);
          digitalWrite(BIN1, LOW);
          digitalWrite(BIN1_2, LOW);
          digitalWrite(BIN2, LOW);
          digitalWrite(BIN1_2, LOW);
          
          delay(delayTime);
          //digitalWrite(AIN1, LOW);
          //digitalWrite(AIN2, LOW);
          //digitalWrite(BIN1, LOW);
          //digitalWrite(BIN2, HIGH);

          digitalWrite(AIN1, LOW);
          digitalWrite(AIN1_2, LOW);
          digitalWrite(AIN2, LOW);
          digitalWrite(AIN2_2,LOW);
          digitalWrite(BIN1, LOW);
          digitalWrite(BIN1_2, LOW);
          digitalWrite(BIN2, HIGH);
          digitalWrite(BIN1_2, HIGH);
          }
        // ASSUME DIR = LOW goes backward
        else{
          delay(delayTime);
          digitalWrite(AIN1, LOW);
          digitalWrite(AIN1_2, LOW);
          digitalWrite(AIN2, LOW);
          digitalWrite(AIN2_2,LOW);
          digitalWrite(BIN1, LOW);
          digitalWrite(BIN1_2, LOW);
          digitalWrite(BIN2, HIGH);
          digitalWrite(BIN1_2, HIGH);
          
          delay(delayTime);
          digitalWrite(AIN1, LOW);
          digitalWrite(AIN1_2, LOW);
          digitalWrite(AIN2, HIGH);
          digitalWrite(AIN2_2,HIGH);
          digitalWrite(BIN1, LOW);
          digitalWrite(BIN1_2, LOW);
          digitalWrite(BIN2, LOW);
          digitalWrite(BIN1_2, LOW);
          
          delay(delayTime);
          digitalWrite(AIN1, LOW);
          digitalWrite(AIN1_2, LOW);
          digitalWrite(AIN2, LOW);
          digitalWrite(AIN2_2,LOW);
          digitalWrite(BIN1, HIGH);
          digitalWrite(BIN1_2, HIGH);
          digitalWrite(BIN2, LOW);
          digitalWrite(BIN1_2, LOW);
          
          delay(delayTime);
          digitalWrite(AIN1, HIGH);
          digitalWrite(AIN1_2, HIGH);
          digitalWrite(AIN2, LOW);
          digitalWrite(AIN2_2,LOW);
          digitalWrite(BIN1, LOW);
          digitalWrite(BIN1_2, LOW);
          digitalWrite(BIN2, LOW);
          digitalWrite(BIN1_2, LOW);
        }
      }
      Serial.println("Stepped");
      disableMotors();
}


//int period = 160; //-> This set-up gives exactly one cycle (by eyeballing)
//int cycle = 12;

int period = 60; //-> This also gives a cycle, less jittering/vibration
int cycle = 12; // Note, while switching direction, the first cycle will not be a full cycle

void loop() {
   if (Serial.available() > 0){
    char command = Serial.read();
    if (command == 'a'){
      actuateMotor(period,cycle,true);
      delay(100);
    }
    else if (command == 'd'){
      actuateMotor(period,cycle,false);
      delay(100);
    }
  }
}
