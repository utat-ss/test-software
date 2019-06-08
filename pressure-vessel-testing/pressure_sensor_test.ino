#include "pressure_sensor_test.h"

uint16_t pres_prom_data[8];


void pres_reset(void){
    digitalWrite(PRES_CS_PIN, LOW);
    SPI.transfer(PRES_RESET_SPI);
    delay(3);
    digitalWrite(PRES_CS_PIN, HIGH);
}

// reads the calibration coefficients from the PROM
uint16_t pres_read_prom(uint8_t address){
    uint16_t data = 0;
    // set the CS pin low
    digitalWrite(PRES_CS_PIN, LOW);
    SPI.transfer((address << 1) | PRES_PROM_BASE);
    data |= ((uint16_t) SPI.transfer(0x00)) << 8;
    data |= ((uint16_t) SPI.transfer(0x00));
    digitalWrite(PRES_CS_PIN, HIGH);
    // set the CS pin high
    return data;
}

// reads the uncompensated pressure or temperature depending on the command given
uint32_t pres_read_raw_uncompensated_data(uint8_t cmd){
    uint32_t data = 0;

    digitalWrite(PRES_CS_PIN, LOW);
    SPI.transfer(cmd);
    delay(10);
    digitalWrite(PRES_CS_PIN, HIGH);

    digitalWrite(PRES_CS_PIN, LOW);
    SPI.transfer(PRES_ADC_READ);
    data |= ((uint32_t) SPI.transfer(0x00)) << 16;
    data |= ((uint32_t) SPI.transfer(0x00)) << 8;
    data |= ((uint32_t) SPI.transfer(0x00));
    digitalWrite(PRES_CS_PIN, HIGH);
    return data;
}

uint32_t pres_read_raw_uncompensated_pressure(void){
    return pres_read_raw_uncompensated_data(PRES_D1_4096);  // pressure
}

uint32_t pres_read_raw_uncompensated_temperature(void){
    return pres_read_raw_uncompensated_data(PRES_D2_4096);  // temperature
}


void setup(){
  uint8_t handshake = 0;
  uint8_t response = 0;
  uint16_t read_prom = 0;

  Serial.begin(9600);
  SPI.begin();
  // Set up the pin for the pressure sensor
  pinMode(PRES_CS_PIN, OUTPUT);
  digitalWrite(PRES_CS_PIN, HIGH);
  Serial.println("Done setting up pin");
  // Reset the pressure sensor
  pres_reset();
  Serial.println("Done resetting pressure sensor");
  // Establish handshake with the computer
  Serial.println("Serial initialized");
  Serial.println("Trying to establish communication");
  while (handshake == 0){
    // Check if there is data written back to the serial line
    if (Serial.available() > 0){
      Serial.println("Something on the serial port");
      response = Serial.read();
      Serial.println(response);
      if (response == 50){
        Serial.println(0x03);
        handshake = 1;
      } // End response check
    } else {
      // Write 1 to the serial port
      Serial.println(0x01);
    }
    delay(1000);
  } // End handshake loop
  for (uint8_t i = 0; i < 8; i++){
    read_prom = pres_read_prom(i);
    pres_prom_data[i] = read_prom;
    Serial.println(read_prom);
  }
} // End setup

void loop() {
  uint32_t D1 = pres_read_raw_uncompensated_pressure();
  uint32_t D2 = pres_read_raw_uncompensated_temperature();
  Serial.print(D1);
  Serial.print(",");
  Serial.println(D2);
  delay(500);
}

