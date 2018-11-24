#include <SoftwareSerial.h>
SoftwareSerial mySerial (2,3);//RX pin 2, TX pin 3

void setup() {
  mySerial.begin(9600);
  Serial.begin(9600);
  
  pinMode(2,OUTPUT); // nSLEEP (DRV8834 pin 1)
  pinMode(3,INPUT); // nFAULT (DRV8834 pin 16), logic low in fault

  // AVREF & BVREF not set for now
  pinMode(5,OUTPUT); // ADECAY (DRV8834 pin 3)
  pinMode(6,OUTPUT); // BDECAY (DRV8834 pin 2)
  pinMode(7,OUTPUT); // CONFIG (DRV8834 pin 15)
  pinMode(8,OUTPUT); // M0/APHASE (DRV8834 pin 13)
  pinMode(9,OUTPUT); // M1 (DRV8834 pin 14)
  pinMode(10,OUTPUT); // nENBL/AENBL (DRV8834 pin 10)
  pinMode(11,OUTPUT); // STEP/BENBL (DRV8834 pin 11)
  pinMode(12,OUTPUT); // DIR/BPHASE (DRV8834 pin 12)
  
}

void enableMotors() {
    // Enable motors and disable sleep
    // nSLEEP = HIGH to enable motor
    digitalWrite(2,HIGH);
    Serial.print('Motor Driver enabled');
}

void disableMotors() {
    // Disable motors and enable sleep
    // nSLEEP LOW to enter sleep mode and reset all internal logic
    digitalWrite(2,LOW);
    Serial.print('Motor Driver disabled');
}

void phaseMode() {
    // first enable motor
    enableMotors();

    // set to indexer mode
    digitalWrite(7,HIGH);
    
    // ADECAY & BDECAY = HIGH (fast decay)
    digitalWrite(5,HIGH);
    digitalWrite(6,HIGH);

    // AENBL Pin LOW to enable all outputs
    digitalWrite(10,LOW);
}

void microstepMode() {
    // first enable motor
    enableMotors();

    // set to indexer mode
    digitalWrite(7,LOW);

    // AENBL HIGH to enable all outputs
    digitalWrite(10,HIGH);
    digitalWrite(11,HIGH);
}

/*
period - time for one cycle (in ms)
       - this is in the ideal case - only considering delays, assuming pin switching is instantaneous
num_cycles - number of cycles (of `period` ms) to actuate for
forward - true to go "forward", false to go "backward"
        - these are arbitrary and just mean opposite directions
*/
void actuateMotors(uint16_t period, uint16_t num_cycles, bool forward, String mode) {
    enableMotors();
    uint16_t delayTime = period / 4;

    if (mode == 'microstep'){
      // Set up Microstepping Mode
      microstepMode();

      // Full step mode - set both M0 & M1 to LOW (p16/44)
      digitalWrite(8,LOW);
      digitalWrite(9,LOW);

      // ASSUME DIR = HIGH goes forward
      if (forward){
        digitalWrite(12,HIGH);
      }
      else{
        digitalWrite(12,LOW);
        }
      for (uint16_t i = 0; i < num_cycles; i++) {
          delay(delayTime);
          digitalWrite(11,HIGH);
          delay(delayTime);
          digitalWrite(11,LOW);
          delay(delayTime);
        }
      }
    }

    if (mode == 'phase'){
      // Set up Phase Mode
      phaseMode();
       for (uint16_t i = 0; i < num_cycles; i++) {
        if (forward) {
            // Using arduino default delay
            delay(delayTime);
            // BPHASE HIGH
            digitalWrite(12,HIGH);

            // APHASE HIGH
            delay(delayTime);
            digitalWrite(8,HIGH);

            // BPHASE LOW
            delay(delayTime);
            digitalWrite(12,LOW);

            // APHASE LOW
            delay(delayTime);
            digitalWrite(8,LOW);
        }

        else {
            // APHASE HIGH
            delay(delayTime);
            digitalWrite(8,HIGH);

            // BPHASE HIGH
            delay(delayTime);
            digitalWrite(12,HIGH);

            // APHASE LOW
            delay(delayTime);
            digitalWrite(8,LOW);

            // BPHASE LOW
            delay(delayTime);
            digitalWrite(12,LOW);
        }
      }
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
      actuateMotors(periodPhase,cyclePhase,true,'phase');
      delay(100);
    }
    if (command == 's'){
      actuateMotors(periodPhase,cyclePhase,false,'phase');
      delay(100);
    }
    if (command == 'a'){
      actuateMotors(periodMicro,cycleMicro,true,'microstep');
      delay(100);
    }
    if (command == 'd'){
      actuateMotors(periodMicro,cycleMicro,false,'microstep');
      delay(100);
    }
    else{
      disableMotors();
      Serial.print('doing nothing');
    }
  }
}
