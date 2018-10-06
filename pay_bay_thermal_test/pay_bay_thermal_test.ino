#include <SPI.h>
#include <SD.h>

const int VCC = 5; // Sensor input voltage from Arduino.
const int TIME_INTERVAL = 5000; // Intervals between data recording.
const int TIME_STOP = 21600; // Equals 6 hours in milliseconds. Defines maximum duration of data collection.
const int startPin = 7; // Digital pin connected to the start button.
const int stopPin = 8; // Digital pin connected to the stop button.

int startTime; // Records the time of start button press after power on.
bool startRecorded = false; // Sets to true once if the start button was pressed.

File thermalDataLog; // File object declaration for data log.

/* Records start time of recording after registering press of the start button */
bool startCheck(){
  if (digitalRead(startPin)) {
    if (!startRecorded){
      startTime = millis();
      startRecorded = true;
      thermalDataLog = SD.open("dataLog.txt", FILE_WRITE);
    }
    return true;
  }
  
  return false;
}

/* Checks for press of stop button and if time since start is more than 6 hours. */
bool stopCheck() {
  if (digitalRead(stopPin) || (millis() - startTime > TIME_STOP)) {
    thermalDataLog.close();
    return true;
  }
  
  return false;
}

/* Defines necessary pins and ensures proper communication with SD card */
void setup() {
  pinMode(startPin, INPUT);
  pinMode(stopPin, INPUT);
  pinMode(10, OUTPUT); // Required for connection with SD card.

  // Rapid blinking if connection with SD card is not established.
  while (!SD.begin(4)) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
    delay(50);
  }
  digitalWrite(LED_BUILTIN, HIGH); // Continuous LED glow if the SD card setup is successful.
  
  if (SD.exists("dataLog.txt")) SD.remove("dataLog.txt"); // Removes any pre-existing file with the same name.
  thermalDataLog.println("Time: VA0, VA1, VA2, VA3"); // Specifies datastream format on the first line of data log.
}

/* Achieves function only when start button is pressed until the stop */
void loop() {
  if (startCheck()) {
    int VA0, VA1, VA2, VA3; // Declare and reset voltage input records.

    // Record thermistor voltages from the analog inputs.
    while (!stopCheck()) {
      VA0 = VCC - analogRead(A0); // Voltage across thermistor #1.
      VA1 = VCC - analogRead(A1); // Voltage across thermistor #2.
      VA2 = VCC - analogRead(A2); // Voltage across thermistor #3.
      VA3 = VCC - analogRead(A3); // Voltage across thermistor #4.
      thermalDataLog.print(millis()); thermalDataLog.print(": "); thermalDataLog.print(VA0); 
      thermalDataLog.print(", "); thermalDataLog.print(VA1); thermalDataLog.print(", "); 
      thermalDataLog.print(VA2); thermalDataLog.print(", "); thermalDataLog.println(VA3);
      break;
    }
    delay(TIME_INTERVAL);
  }
}
