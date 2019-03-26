# Transceiver simulator that uses python/terminal consol
# Input: String from serial.read()
# Output to microcontroller: hex/bytes using serial.write()
#
# Uses processes (versus threads) to execute two functions, read_board and main
# at once
#
# By: Brytni Richards

# TODO: Check if this program works for windows computers

# Note: This program IS NOT completely error-proof. Incorrect messages may be
# sent to the microcontroller if the user enters wrong values

# https://learn.sparkfun.com/tutorials/terminal-basics/tips-and-tricks

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
        # print("waiting for serial")
        # Read from serial
        # This is a string
        str_read = ser.readline().decode("utf-8", errors='ignore')

        if str_read != '': # If not a blank line
            print("Received UART:", str_read)
            print("Received UART:", bytes_to_string(bytes(str_read, 'utf-8')))

            length = len(str_read)
            if length % 2 == 0: # Even length hex value returned
                print(':'.join([str_read[i:i+2] for i in range(0, length, 2)]))
            else:
                print(str_read[0] + ':', end = '')
                print(':'.join([str_read[i:i+2] for i in range(1, length, 2)]))

def string_to_bytes(s):
    return bytearray(codecs.decode(s.replace(':', ''), 'hex'))

def bytes_to_string(b):
    return ":".join(map(lambda x: "%02x" % x, list(b)))

# string should look something like "00:ff:a3:49:de"
# Use `bytearray` instead of `bytes`
def send_raw_uart(uart_bytes):
    print("Sending UART:", bytes_to_string(uart_bytes))
    ser.write(uart_bytes)

def uint32_to_bytes(num):
    return bytes([(num >> 24) & 0xFF, (num >> 16) & 0xFF, (num >> 8) & 0xFF, num & 0xFF])

def bytes_to_uint32(bytes):
    return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def send_message(type, arg1=0, arg2=0, data=bytes(0)):
    #Special character to indicate start of send_message
    message = b'\x00'
    message += bytes([1 + 4 + 4 + len(data)])
    #checksum = b'\xFF'

    #change length and type to binary
    message += bytes([type])
    message += uint32_to_bytes(arg1)
    message += uint32_to_bytes(arg2)
    message += bytes(data)

    #bytes_message +=  checksum

    send_raw_uart(message)


# prompt is the send_message information
# Valid len is the amount of characters that the user must type
# Sends data back as a string (ascii)
def argument(prompt, valid_len, string, max_val = float("inf")):
    while True:
        ret = input(prompt)
        if len(ret) != valid_len:
            print("Error! Input must be ", valid_len, " character(s) long")
        elif string == False:
            try : #Check to see if input is an integer
                int(ret)
            except serial.SerialException as e:
                print("Error! Input must be an integer")
            else:
                if int(ret) > max_val:
                    print("Error! Input value must be equal or less than", max_val)
                else: #Valid send_message and not wanted as a string
                    ret = (int(ret)).to_bytes(valid_len, byteorder = "little")
                    break
        else: #Input wanted as string and valid
            break

    return ret

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

    ser = None # One port is used
    for p in ports:
        # TODO - kind of hacky
        p = p[0].replace("cu", "tty")
        print("Port: " + p)

        #Mac, linux system, UART port
        if os.name == 'posix' and p.startswith ('/dev/tty') and p.endswith('4'):
            print("Testing port " + p)
            try :
                ser = serial.Serial(p, baud_rate, timeout = 1)
                print("Using port " + p + " for simulation")
                break
            except serial.SerialException as e:
                print("Port " + p + " is in use")
        #Windows
        elif os.name == 'nt' and p[0].startswith('COM'):
            print("Testing port " + p[0])
            try :
                ser = serial.Serial(p[0], baud_rate, timeout = 1)
                print("Using port " + p[0] + " for simulation")
                break
            except serial.SerialException as e:
                print("Port " + p[0] + " is in use")


    print("Reading and writing board info from", ser.port)
    proc = Process(target = read_board, args=(ser,))
    proc.start() #Start process/reading from board


    cmd = None # Command to board
    while cmd != ("quit"): # Enter quit to stop program
        print("0. Send Raw UART")
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
        cmd = input("Enter command number: ") # User input typed through terminal consol

        if cmd == ("quit"):
            proc.terminate()
        elif cmd == ("0"):  # Raw UART
            send_raw_uart(string_to_bytes(input("Enter raw hex for UART: ")))
        elif cmd == ("1"): #Ping
            #arguments = send_message type, length, make data in hex?, data, data2
            send_message(0, 0)
        elif cmd == ("2"): #Get restart info
            send_message(1, 0)
        elif cmd == ("3"): #Get RTC
            send_message(2, 0)
        elif cmd == ("4"): #Set RTC
            arg1 = argument("Type in year: ", 2, True)
            arg1 += argument("Type in month: ", 2, True)
            arg1 += argument("Type in day: ", 2, True)

            arg2 = argument("Type in time in hours: ", 2, True)
            arg2 += argument("Type in time in minutes: ", 2, True)
            arg2 += argument("Type in time in seconds: ", 2, True)
            send_message (3, 7, True, arg1, arg2)
        elif cmd == ("5"): #Memory
            print("Enter a number corresponding to the command")
            print("1. Read Flash Memory")
            print("2. Erase Flash Memory")
            print("3. Read EEPROM")
            next_cmd = input()

            if next_cmd == ("1"):
                arg1 = argument("Type starting address (hex): ", 4, True)
                arg2 = argument("Type ending address: ", 4, True)
                send_message(4, 8, True, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = argument("Type starting address (hex): ", 4, True)
                arg2 = argument("Type ending address: ", 4, True)
                send_message(5, 8, True, arg1, arg2)
            elif next_cmd == ("3"):
                arg1 = argument("Type in subsystem: ", 1, True) + "0"
                arg2  = argument("Type in address (hex): ", 4, True)
                send_message(18, 8, True, arg1, arg2)
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
                send_message(6, 1, False, arg1)
            elif next_cmd == ("2"):
                send_message(7, 1, False, arg1)
            elif next_cmd == ("3"):
                arg2 = argument("Type block number: ", 4, False, 65526)
                send_message(8, 8, False, arg1, arg2)
            elif next_cmd == ("4"):
                send_message(19, 1, False, arg1)
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
                send_message(9, 1, False, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = argument("Type block type: ", 1, False, 2)
                arg2 = argument("Type period in seconds: ", 4, False, 65526)
                send_message(10, 8, False, arg1, arg2)
            elif next_cmd == ("3"):
                send_message(11, 0)
            else:
                print("Invalid command")
        elif cmd == ("8"): #Heater DAC Setpoints
            print("Enter a number corresponding to the command")
            print("1. Set EPS DAC Setpoints")
            print("2. Set PAY DAC Setpoints")
            next_cmd = input()

            arg1 = "0" + argument("Type 0 or 1: ", 1, True)
            arg2 = argument("Type setpoint (hex): ", 3, True) + "0"


            if next_cmd == ("1"):
                send_message(12, 7, True, arg1, arg2)
            elif next_cmd == ("2"):
                send_message(13, 7, True, arg1, arg2)
            else:
                print("Invalid command")
        elif cmd == ("9"): #Pay Control
            arg1 = argument("Move plate up (1) or down (2): ", 1, False, 2)
            send_message(14, 1, False, arg1)

        elif cmd == ("10"): #Reset
            arg1 = argument("Type in subsystem: ", 1, False, 2)
            send_message(15, 1, False, arg1)
        elif cmd == ("11"): #CAN Messages
            print("Enter a number corresponding to the command")
            print("1. Send CAN to EPS")
            print("2. Send CAN to PAY")
            next_cmd = input()

            arg1 = argument("Type 1st 4 bytes of send_message (hex): ", 4, True)
            arg2 = argument("Type last 4 bytes of send_message (hex): ", 4, True)

            if next_cmd == ("1"):
                send_message(16, 8, True, arg1, arg2)
            elif next_cmd == ("2"):
                send_message(17, 8, True, arg1, arg2)
            else:
                print("Invalid command")
        else:
            print("Invalid option")

        time.sleep(1) #Wait for reply

    ser.close() # Close serial port when program done

    print("Quit Transceiver Simulator")
