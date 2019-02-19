/*
This program makes the Arduino function as an I2C master so we can test its communication with an Arduino as an I2C slave.

You need to use an Arduino with I2C support (SDA and SCL pins), e.g. the Arduino Due in the lab.

https://www.arduino.cc/en/reference/wire
https://www.arduino.cc/en/Tutorial/MasterReader
https://www.arduino.cc/en/Tutorial/MasterWriter

**THE WIRE LIBRARY USES 7-BIT ADDRESSES**
*/

#include <Wire.h>

void setup() {
    Serial.begin(9600);           // start serial for output
    Serial.print("Started\n");

    Wire.begin(); // join i2c bus (address optional for master)
}

void loop() {
    // write
    Wire.beginTransmission(8); // transmit to device #8
    Wire.write("hi");        // sends two bytes
    Wire.endTransmission();    // stop transmitting

    // read
    Wire.requestFrom(8, 6);    // request 6 bytes from slave device #8
    while (Wire.available()) { // slave may send less than requested
        char c = Wire.read(); // receive a byte as character
        Serial.print(c);         // print the character
    }

    delay(2000);
}
