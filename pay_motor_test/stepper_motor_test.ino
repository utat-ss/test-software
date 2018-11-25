#include <SoftwareSerial.h>
SoftwareSerial mySerial (2,3);//RX pin 2, TX pin 3

void setup() {
  mySerial.begin(9600);
  Serial.begin(9600);

  int nSLEEP = 2; // nSLEEP (DRV8834 pin 1)
  int nFAULT = 3; // nFAULT (DRV8834 pin 16), logic low in fault
  int ADECAY = 5; // ADECAY (DRV8834 pin 3)
  int BDECAY = 6; // BDECAY (DRV8834 pin 2)
  int CONFIG = 7; // this pin will be wired in hardware (DRV8834 pin 15)
  int M0 = 8; // M0/APHASE (DRV8834 pin 13)
  int M1 = 9; // M1 (DRV8834 pin 14)
  int nENBL = 10; // nENBL/AENBL (DRV8834 pin 10)
  int STEP = 11; // STEP/BENBL (DRV8834 pin 11)
  int DIR = 12; // DIR/BPHASE (DRV8834 pin 12)

  pinMode(nSLEEP,OUTPUT); 
  pinMode(nFAULT,INPUT); 
  // AVREF & BVREF not set for now
  pinMode(ADECAY,OUTPUT); 
  pinMode(BDECAY,OUTPUT); 
  pinMode(M0,OUTPUT); 
  pinMode(M1,OUTPUT); 
  pinMode(nENBL,OUTPUT); 
  pinMode(STEP,OUTPUT); 
  pinMode(DIR,OUTPUT); 

}

void enableMotors() {
    // Enable motors and disable sleep
    // nSLEEP = HIGH to enable motor
    digitalWrite(nSLEEP,HIGH);
    Serial.print('Motor Driver enabled');
}

void disableMotors() {
    // Disable motors and enable sleep
    // nSLEEP LOW to enter sleep mode and reset all internal logic
    digitalWrite(nSLEEP,LOW);
    Serial.print('Motor Driver disabled');
}

void phaseMode() {
    // first enable motor
    enableMotors();

    // set to indexer mode in hardware

    // ADECAY & BDECAY = HIGH (fast decay)
    digitalWrite(ADECAY,HIGH);
    digitalWrite(BDECAY,HIGH);

    // AENBL Pin LOW to enable all outputs
    digitalWrite(nENBL,LOW);
}

void microstepMode() {
    // first enable motor
    enableMotors();

    // set to microstep mode in hardware

    // AENBL HIGH to enable all outputs
    digitalWrite(nENBL,HIGH);
    digitalWrite(STEP,HIGH);
}

/*
period - time for one cycle (in ms)
       - this is in the ideal case - only considering delays, assuming pin switching is instantaneous
num_cycles - number of cycles (of `period` ms) to actuate for
forward - true to go "forward", false to go "backward"
        - these are arbitrary and just mean opposite directions
*/
void actuatePhaseMotors(uint16_t period, uint16_t num_cycles, bool forward) {
    enableMotors();
    uint16_t delayTime = period / 4;
    
    // Set up Phase Mode
    phaseMode();
    for (uint16_t i = 0; i < num_cycles; i++) {
      if (forward) {
          // Using arduino default delay
          delay(delayTime);
          // BPHASE HIGH
          digitalWrite(DIR,HIGH);

          // APHASE HIGH
          delay(delayTime);
          digitalWrite(M0,HIGH);

          // BPHASE LOW
          delay(delayTime);
          digitalWrite(DIR,LOW);

          // APHASE LOW
          delay(delayTime);
          digitalWrite(M0,LOW);
      }
      else {
          // APHASE HIGH
          delay(delayTime);
          digitalWrite(M0,HIGH);

          // BPHASE HIGH
          delay(delayTime);
          digitalWrite(DIR,HIGH);

          // APHASE LOW
          delay(delayTime);
          digitalWrite(M0,LOW);

          // BPHASE LOW
          delay(delayTime);
          digitalWrite(DIR,LOW);
        }
    }
    disableMotors();
}

void acturateMicroMotor(uint16_t period, uint16_t num_cycles, bool forward) {
  enableMotors();
  uint16_t delayTime = period / 4;

  // Set up Microstepping Mode
  microstepMode();

  // Full step mode - set both M0 & M1 to LOW (p16/44)
  digitalWrite(M0,LOW);
  digitalWrite(M1,LOW);

  // ASSUME DIR = HIGH goes forward
  if (forward){
    digitalWrite(DIR,HIGH);
    }
  // ASSUME DIR = LOW goes backward
  else{
    digitalWrite(DIR,LOW);
  }
  for (uint16_t i = 0; i < num_cycles; i++) {
      delay(delayTime);
      digitalWrite(STEP,HIGH);
      delay(delayTime);
      digitalWrite(STEP,LOW);
      delay(delayTime);
  }

  disableMotors();
}

void loop() {

  bool fault = digitalRead(3);

  // parameters for phase enable mode
  uint16_t periodPhase = 10;
  uint16_t cyclePhase = 15;

  // parameters for microstepping mode
  uint16_t periodMicro = 10;
  uint16_t cycleMicro = 15;

  while (mySerial.available() > 0){
    char command = mySerial.read();
    if (fault == LOW){
      disableMotors();
      Serial.print('Motors in fault');
    }
    if (command == 'w'){
      actuatePhaseMotors(periodPhase,cyclePhase,true);
      delay(100);
    }
    if (command == 's'){
      actuatePhaseMotors(periodPhase,cyclePhase,false);
      delay(100);
    }
    if (command == 'a'){
      actuateMicroMotors(periodMicro,cycleMicro,true);
      delay(100);
    }
    if (command == 'd'){
      actuateMicroMotors(periodMicro,cycleMicro,false);
      delay(100);
    }
    else{
      disableMotors();
      Serial.print('Motor Idling');
    }
  }
}
