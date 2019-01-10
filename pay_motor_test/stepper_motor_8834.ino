#include <SoftwareSerial.h>

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

// parameters for phase enable mode
int periodPhase = 40;
int cyclePhase = 20;

// parameters for microstepping mode
int periodMicro = 40;
int cycleMicro = 50;


void setup() {
  Serial.begin(9600);
  Serial.println("Serial Ready");

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

void enableMotors(uint16_t period, uint16_t num_cycles) {
    // Enable motors and disable sleep
    // nSLEEP = HIGH to enable motor
    //int OnTime = period*num_cycles;
    Serial.println("Enabled");
    digitalWrite(nSLEEP,HIGH);
    //delay(OnTime);
    //Serial.println("Done test");
}

// might not need
void disableMotors() {
    // Disable motors and enable sleep
    // nSLEEP LOW to enter sleep mode and reset all internal logic
    digitalWrite(nSLEEP,LOW);
    digitalWrite(ADECAY,LOW);
    digitalWrite(BDECAY,LOW);
    digitalWrite(nENBL,LOW);
    digitalWrite(STEP,LOW);
    Serial.println("Disabled");
}

void phaseMode(uint16_t period, uint16_t num_cycles) {
    // first enable motor
    int OnTime = period*num_cycles;
    enableMotors(period, num_cycles);
    // set to indexer mode in hardware

    // ADECAY & BDECAY = HIGH (fast decay)
    digitalWrite(ADECAY,HIGH);
    digitalWrite(BDECAY,HIGH);
    // delay(OnTime);

    // AENBL Pin HIGH to enable all outputs
    digitalWrite(nENBL,HIGH);
    digitalWrite(STEP,HIGH);
    //delay(OnTime);
}

void microstepMode(uint16_t period, uint16_t num_cycles) {
    // first enable motor
    //int OnTime = period*num_cycles;
    enableMotors(period, num_cycles);

    // AENBL HIGH to enable all outputs
    digitalWrite(nENBL,HIGH);
    //digitalWrite(STEP,HIGH);
    //delay(OnTime);
}

/*
period - time for one cycle (in ms)
       - this is in the ideal case - only considering delays, assuming pin switching is instantaneous
num_cycles - number of cycles (of `period` ms) to actuate for
forward - true to go "forward", false to go "backward"
        - these are arbitrary and just mean opposite directions
*/
void actuatePhaseMotor(uint16_t period, uint16_t num_cycles, bool forward) {
    uint16_t delayTime = period / 4;

    // Set up Phase Mode
    // ****TO DO****** CONSIDER USING ANALOGWRITE
    // https://cdn.sparkfun.com/assets/resources/4/4/DC_motor_circuits_slides.pdf

    //**2018-12-22
    // Coil A has much higher frequency than Coil B for some reasons
    phaseMode(period, num_cycles);
    for (uint16_t i = 0; i < num_cycles; i++) {
      if (forward) {
          // Using arduino default delay
          // Try using the STEP pin with f_freq
          delay(delayTime);
          // BPHASE HIGH
          digitalWrite(M0,HIGH);

          // APHASE HIGH
          delay(delayTime);
          digitalWrite(DIR,HIGH);

          // BPHASE LOW
          delay(delayTime);
          digitalWrite(M0,LOW);

          // APHASE LOW
          delay(delayTime);
          digitalWrite(DIR,LOW);
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
    Serial.println("done");
}

void actuateMicroMotor(uint16_t period, uint16_t num_cycles, bool forward) {
      uint16_t delayTime = period / 4;

      // Set up Microstepping Mode
      microstepMode(period, num_cycles);

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
      //***2018-12-22
      // Arduino is sending the right signal but there is no response at the motor's end, the motor driver might not be configured correctly
      for (uint16_t i = 0; i < num_cycles; i++) {
          delay(delayTime);
          digitalWrite(STEP,HIGH);
          delay(delayTime);
          digitalWrite(STEP,LOW);
          delay(delayTime);
      }

      disableMotors();
      Serial.println("done");
}

bool fault = digitalRead(3);

void loop() {
  if (Serial.available() > 0){
    char command = Serial.read();
    if (command == 'w'){
      actuatePhaseMotor(periodPhase,cyclePhase,true);
      delay(100);
    }
    else if (command == 's'){
      actuatePhaseMotor(periodPhase,cyclePhase,false);
      delay(100);
    }
    else if (command == 'a'){
      actuateMicroMotor(periodMicro,cycleMicro,true);
      delay(100);
    }
    else if (command == 'd'){
      actuateMicroMotor(periodMicro,cycleMicro,false);
      delay(100);
    }
    else{
      disableMotors();
      Serial.println("Motor Idling");
    }
  }
}
