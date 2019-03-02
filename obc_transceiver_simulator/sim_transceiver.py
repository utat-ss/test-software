# Transceiver simulator that uses python/terminal consol
# Input: String from serial.read()
# Output to microcontroller: hex/bytes using serial.write()
#
# Uses processes (versus threads) to execute two functions, read_board and main
# at once
#
# By: Brytni Richards

# TODO: Check if this program works for windows computers

from __future__ import print_function
from multiprocessing import Process
import time
import sys
import os
import codecs

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: This program requires the pyserial module. To install " +
        "pyserial,\nvisit https://pypi.org/project/pyserial/ or run\n" +
        "    $ pip install pyserial\n" +
        "in the command line.")
    sys.exit(1)

# Process to poll for information from the board. It prints out values
# in the string buffer every 5 seconds. Otherwise, it does not print out data
# Values read from the board are assumed to be bytes
def read_board(ser):
    while True:
        # Read from serial
        bytes_read = ser.readline().decode("utf-8", errors='ignore')
        if bytes_read != '': # If not a blank line
            length = len(bytes_read)
            if length % 2 == 0: # Even length hex value returned
                print(':'.join([bytes_read[i:i+2] for i in range(0, length, 2)]))
            else:
                print(bytes_read[0] + ':', end = '')
                print(':'.join([bytes_read[i:i+2] for i in range(1, length, 2)]))

def message(type, num_chars, arg1, arg2 = None):
    print("Have yet to implement")
    #Special character to indicate start of message
    start = b'\x00'
    #TODO change length to binary

    #convert arguement into binary hexadecimal
    bytes_data = codecs.decode(arg1, 'hex')

    if arg2 != None:
        bytes_data += codecs.decode(arg2, 'hex')

    bytes_message = start + bytes_data

    ser[0].write(bytes_cmd)

def block_message(sender):
    print("Have yet to implement")

def memory_message():
    print("Have yet to implement")

def heater_message():
    print("have yet to implement")

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

    #Get port names
    ports = list(serial.tools.list_ports.comports())

    baud_rate = 9600

    print("Transceiver simulation starting...")

    ser = [0] # One port is used
    for p in ports:
        #Mac, linux system, UART port
        if os.name == 'posix' and p[0].startswith ('/dev/tty') and p[0].endswith('4'):
            try :
                ser[0] = serial.Serial(p[0], baud_rate, timeout = 5)
            except serial.SerialException as e:
                print("Port " + p[0] + " is in use")
        #Windows
        elif os.name == 'nt' and p[0].startswith('COM'):
            try :
                ser[0] = serial.Serial(p[0], baud_rate, timeout = 5)
            except serial.SerialException as e:
                print("Port " + p[0] + " is in use")

    print("Reading and writing board info from" + ser[0].port)
    proc = Process(target = read_board, args=(ser[0],))
    proc.start() #Start process/reading from board

    cmd = None # Command to board
    while cmd != ("quit"): # Enter quit to stop program
        print("Enter a number corresponding to the command")
        print("1. Status/Ping")
        print("2. EPS Housekeeping")
        print("3. PAY Housekeeping")
        print("4. PAY Optical")
        print("5. PAY Control")
        print("6. Experiment")
        print("7. Memory")
        print("8. Heater DAC Setpoints")
        cmd = input() # User input typed through terminal consol

        if cmd == ("quit"):
            proc.terminate()
        elif cmd == ("1"):
            message(0, 4, "UTAT")
        elif cmd == ("2"):
            block_message("EPS")
        elif cmd == ("3"):
            block_message("PAY H")
        elif cmd == ("4"):
            block_message("PAY O")
        elif cmd == ("5"):
            print("Type 0 to move plate down, 1 to move up")
            option = input() #Failsafe this
            message(0x0A, option)
        elif cmd == ("6"):
            print("For automatic data collection:")
            print("Type 0 to disable, 1 to enable")
            option = input() #Failsafe this
            message(0x0B, option)
        elif cmd == ("7"):
            memory_message()
        elif cmd == ("8"):
            heater_message()
        else:
            print("Invalid option")

        time.sleep(2) #Wait for reply

    ser[0].close() # Close serial port when program done
    print("Quit Transceiver Simulator")
