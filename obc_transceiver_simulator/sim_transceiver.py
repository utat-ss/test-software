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

#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def message(type, num_chars, string=False, arg1=None, arg2 = None):
    print("Have yet to implement")
    #Special character to indicate start of message
    start = b'\x00'
    #checksum = b'\xFF'

    if num_chars % 2 != 0: #message must be even-bit lengthed
        num_chars += 1
    #change length and type to binary
    byteType = bytes([type])
    byteLen = bytes([num_chars])

    bytes_message = start + byteType + byteLen

    if string == True: #data in hex string (Change Ascii hex to actual hex)
        #convert argument into binary hexadecimal
        if arg1 != None:
            bytes_message += codecs.decode(arg1, 'hex')
            bytes_message += bytes(4 - int(len(arg1)/2))

        if arg2 != None:
            bytes_message += codecs.decode(arg2, 'hex')
    else: #data not in hex
        if arg1 != None:
            bytes_message += arg1
            bytes_message += bytes(4 - len(arg1))
        if arg2 != None:
            bytes_message += arg2

    #Pad unused message part with zeros
    bytes_message += bytes(4 - len(arg2))

    #bytes_message +=  checksum

    ser[0].write(bytes_message)

# prompt is the message information
# Valid len is the amount of characters that the user must type
# Sends data back as a string (ascii)
def argument(prompt, valid_len, string, max_val = float("inf")):
    while True:
        ret = input(prompt)
        if len(usr) != valid_len:
            print("Error! Input must be ", valid_len, " characters long")
        elif string == False:
            try : #Check to see if input is an integer
                int(ret)
            except serial.SerialException as e:
                print("Error! Input must be an integer")
            else:
                if int(ret) > max_val:
                    print("Error! Input value must be less than", max_val)
                else: #Valid message and not wanted as a string
                    ret = (ret).to_bytes(valid_len, byteorder = "little")
                    break
        else: #Input wanted as string and valid
            break

    return ret

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
        print("2. Get Restart Info")
        print("3. Get RTC")
        print("4. Set RTC")
        print("5. Memory (Flash and EEPROM)")
        print("6. Blocks")
        print("7. Auto-Data Collection")
        print("8. Heater DAC Setpoints")
        print("9. Pay Control")
        print("10. Reset")
        print("11. CAN")
        cmd = input() # User input typed through terminal consol

        if cmd == ("quit"):
            proc.terminate()
        elif cmd == ("1"): #Ping
            #arguments = message type, length, make data in hex?, data, data2
            message(0, 0)
        elif cmd == ("2"): #Get restart info
            message(1, 0)
        elif cmd == ("3"): #Get RTC
            message(2, 0)
        elif cmd == ("4"): #Set RTC
            arg1 = argument("Type in year", 2, True)
            arg1 += argument("Type in month", 2, True)
            arg1 += argument("Type in day", 2, True)

            arg2 = argument("Type in time in hours", 2, True)
            arg2 += argument("Type in time in minutes", 2, True)
            arg2 += argument("Type in time in seconds", 2, True)
            message (3, 7, True, arg1, arg2)
        elif cmd == ("5"): #Memory
            print("Enter a number corresponding to the command")
            print("1. Read Flash Memory")
            print("2. Erase Flash Memory")
            print("3. Read EEPROM")
            next_cmd = input()

            if next_cmd == ("1"):
                arg1 = argument("Type starting address (int): ", 4, False, 65526)
                arg2 = argument("Type ending address: ", 4, False, 65526)
                message(4, 8, False, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = argument("Type starting address (int): ", 4, False, 65526)
                arg2 = argument("Type ending address: ", 4, False, 65526)
                message(5, 8, False, arg1, arg2)
            elif next_cmd == ("3"):
                arg1 = "0" + argument("Type in subsystem: ", 1, True)
                arg2  = argument("Type in address (hex): ", 4, True)
                message(18, 8, True, arg1, arg2)
            else:
                print("Invalid command")
        elif cmd == ("6"): #Blocks
            print("Enter a number corresponding to the command")
            print("1. Collect Block")
            print("2. Read Local Block")
            print("3. Read Memory Block")
            print("4. Get Current Block number")
            next_cmd = input()

            arg1 = argument("Type block type: ", 1, False, 2)

            if next_cmd == ("1"):
                message(6, 1, False, arg1)
            elif next_cmd == ("2"):
                message(7, 1, False, arg1)
            elif next_cmd == ("3"):
                arg2 = argument("Type block number: ", 4, False, 65526)
                message(8, 8, False, arg1, arg2)
            elif next_cmd == ("4"):
                arg1 = argument("Type block type: ", 1, False, 2)
                message(19, 1, False, arg1)
            else:
                print("Invalid command")
        elif cmd == ("7"): #Auto-Data Collection
            print("Enter a number corresponding to the command")
            print("1. Enable/Disable")
            print("2. Period")
            print("3. Resync")
            next_cmd = input()

            if next_cmd == ("1"):
                arg1 = argument("Type block type: ", 1, False, 2)
                arg2 = argument("Disable (0) or Enable (1): ", 1, False, 1)
                message(9, 1, False, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = argument("Type block type: ", 1, False, 2)
                arg2 = argument("Type period in seconds: ", 4, False, 65526)
                message(10, 8, False, arg1, arg2)
            elif next_cmd == ("3"):
                message(11, 0)
            else:
                print("Invalid command")
        elif cmd == ("8"): #Heater DAC Setpoints
            print("Enter a number corresponding to the command")
            print("1. Set EPS DAC Setpoints")
            print("2. Set PAY DAC Setpoints")
            next_cmd = input()

            arg1 = argument("Type 0 or 1: ", 1, True)
            arg2 = "0" #Because 12 bits isn't divisible by 8
            arg2 += argument("Type setpoint (hex): ", 3, True)

            if next_cmd == ("1"):
                message(12, 7, True, arg1, arg2)
            elif next_cmd == ("2"):
                message(13, 7, True, arg1, arg2)
            else:
                print("Invalid command")
        elif cmd == ("9"): #Pay Control
            arg1 = argument("Move plate up (1) or down (2): ", 1, False, 2)
            message(14, 1, False, arg1)

        elif cmd == ("10"): #Reset
            arg1 = argument("Type in subsystem: ", 1, False, 2)
            message(15, 1, False, arg1)
        elif cmd == ("11"): #CAN Messages
            print("Enter a number corresponding to the command")
            print("1. Send CAN to EPS")
            print("2. Send CAN to PAY")
            next_cmd = input()

            arg1 = argument("Type 1st 4 bytes of message (hex): ", 8, True)
            arg2 = argument("Type last 4 bytes of message (hex): ", 8, True)

            if next_cmd == ("1"):
                message(16, 8, True, arg1, arg2)
            elif next_cmd == ("2"):
                message(17, 8, True, arg1, arg2)
            else:
                print("Invalid command")
        else:
            print("Invalid option")

        time.sleep(1) #Wait for reply

    ser[0].close() # Close serial port when program done
    print("Quit Transceiver Simulator")
