# Transceiver simulator that uses python/terminal consol
# Input: String from serial.read()
# Output to microcontroller: hex/bytes using serial.write()

# Use the following command to run the harness from the lib-common local directory:
# python ./bin/harness.py -p <Programming port> -u <UART port> -d tests

# When the uart port (-u option) is not specified, the program guesses using uart_offset()
# On Mac, port numbers can be found by using the command 'ls /dev/tty.*' in terminal

from __future__ import print_function
import subprocess
import argparse
import select
import time
import sys
import os
import re
from multiprocessing import Process

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: This program requires the pyserial module. To install " +
        "pyserial,\nvisit https://pypi.org/project/pyserial/ or run\n" +
        "    $ pip install pyserial\n" +
        "in the command line.")
    sys.exit(1)

# This function assumes an offset between the programming and uart ports of 2 for
# mac or linux devices (posix)(i.e. uart is 2 more than programming port), or -1 for windows (nt)
# devices. Mac USB serial ports should be of the form /dev/tty.usbmodem00xxxxxx,
# while windows ports have the form COMx.
def uart_offset():
    if os.name == 'posix':
        return 2
    elif os.name == 'nt':
        return -1

def read_board(ser):
    while True:
        feedback = ser.readline().decode("utf-8", errors='ignore')
        #print(':'.join(a+b for a,b in zip(feedback[::2],feedback[1:2])))

if __name__ == "__main__":
    # Detects if correct python version is being run
    if sys.version_info[0] == 2:
        print("You are using Python 2. Please update to Python 3 and try again.")
        sys.exit(1)
    elif sys.version_info[0] == 3:
        print("You are running Python 3.")
    else:
        print("Unknown error. Exiting....")
        sys.exit(1)

    #Get ports
    ports = list(serial.tools.list_ports.comports())

    baud_rate = 9600

    print("Transceiver simulation starting...")

    ser = ['' for x in range (2)] #There are 2 ports in this project, no more, no less
    i = 0
    for p in ports:
        if os.name == 'posix': #Mac, linux system
            if p[0].endswith('4'): #UART Port
                ser[i] = serial.Serial(p[0], baud_rate, timeout = None)
                i += 1
        elif os.name == 'nt': #Windows
            ser[i] = serial.Serial(p[i], baud_rate, timeout = None) #TODO: Check if this is wrong
            i += 1

    print("(Connect Coolterm to) Reading board info from", ser[0].port)
    print("Writing info to board through", ser[1].port)
    proc = Process(target = read_board, args=(ser[0],))
    proc.start() #Start reading from board

    cmd = None #Command to board
    while cmd != ("quit"):
        cmd = input()
        if cmd == ("quit"):
            proc.terminate()
        else:
            bytes_cmd = bytes(cmd+"\r\n", 'utf-8')
            ser[1].write(bytes_cmd)


    for i in range (2):
        ser[i].close()
    print("Quit Transceiver Simulator")
