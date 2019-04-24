/*
This program makes the Arduino function as an I2C slave so we can test the OBC SPI to I2C bridge as an I2C master that can send write and read commands.

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

    // Slave address 8
    Wire.begin(8);                // join i2c bus with address #8
    Wire.onRequest(requestEvent); // register event (master read request)
    Wire.onReceive(receiveEvent); // register event (master write request)
}

void loop() {
    delay(1);
}

bool req1 = true;

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {
    // Alternate requests
    if (req1) {
        Serial.println("sent hello");
        Wire.write("hello"); // respond with message of 5 bytes
        // as expected by master
    } else {
        Serial.println("sent hi123");
        Wire.write("hi123");
    }

    req1 = !req1;
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
    Serial.print("received ");
    while (Wire.available() > 0) { // loop through all but the last
        char c = Wire.read(); // receive byte as a character
        Serial.print(c);         // print the character
    }
    Serial.println();
}
