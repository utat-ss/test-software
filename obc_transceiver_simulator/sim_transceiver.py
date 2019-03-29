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

from multiprocessing import Process
import time
import sys
import os
import codecs
import argparse

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: This program requires the pyserial module. To install " +
        "pyserial,\nvisit https://pypi.org/project/pyserial/ or run\n" +
        "    $ pip install pyserial\n" +
        "in the command line.")
    sys.exit(1)

def subsys_consts():
    return "(OBC = 0, EPS = 1, PAY = 2)"

def block_type_consts():
    return "(EPS_HK = 0, PAY_HK = 1, PAY_OPT = 2)"

def print_header(data):
    print("block number = %d, error = %d, date = %s, time = %s" % (bytes_to_uint24(data[0:3]), data[3], bytes_to_string(data[4:7]), bytes_to_string(data[7:10])))

def data_to_fields(data):
    fields = []
    for i in range(0, len(data), 3):
        fields.append(bytes_to_uint24(data[i:i+3]))
    return fields

def print_field(fields, index, name, conv):
    print("Field %d (%s): 0x%.6x = %s" % (index, name, fields[index], conv))

def print_block(arg1, data):
    print_header(data[0:10])
    fields = data_to_fields(data[10:])

    if arg1 == 0:
        print("EPS_HK")
        print_field(fields, 0, "BB Vol", "%f V" % ...)
        print_field(fields, 1, "BB Cur", "%f V" % ...)
        print_field(fields, 2, "-Y Vol", "%f V" % ...)
        print_field(fields, 3, "+X Vol", "%f V" % ...)
        print_field(fields, 4, "+Y Vol", "%f V" % ...)
        print_field(fields, 5, "-X Vol", "%f V" % ...)
        print_field(fields, 6, "Bat Temp 1", "%f V" % ...)
        print_field(fields, 7, "Bat Temp 2", "%f V" % ...)
        print_field(fields, 8, "Bat Vol", "%f V" % ...)
        print_field(fields, 9, "Bat Cur", "%f V" % ...)
        print_field(fields, 10, "BT Cur", "%f V" % ...)
        print_field(fields, 11, "BT Vol", "%f V" % ...)
        print_field(fields, 12, "Bat Heater Setpoint 1", "%f V" % ...)
        print_field(fields, 13, "Bat Heater Setpoint 2", "%f V" % ...)
        print_field(fields, 14, "IMU Acceleration X", "")
        print_field(fields, 15, "IMU Acceleration Y", "")
        print_field(fields, 16, "IMU Acceleration Z", "")
        print_field(fields, 17, "IMU Gyroscope X", "")
        print_field(fields, 18, "IMU Gyroscope Y", "")
        print_field(fields, 19, "IMU Gyroscope Z", "")
        print_field(fields, 20, "IMU Magnetometer X", "")
        print_field(fields, 21, "IMU Magnetometer Y", "")
        print_field(fields, 22, "IMU Magnetometer Z", "")

    if arg1 == 1:
        print("PAY_HK")
        print_field(fields, 0, "Temperature", "%f C" % ...)
        print_field(fields, 1, "Humidity", "%f %%RH" % ...)
        print_field(fields, 2, "Pressure", "%f kPa" % ...)
        print_field(fields, 3, "MF Temp 0", "%f C" % ...)
        print_field(fields, 4, "MF Temp 1", "%f C" % ...)
        print_field(fields, 5, "MF Temp 2", "%f C" % ...)
        print_field(fields, 6, "MF Temp 3", "%f C" % ...)
        print_field(fields, 7, "MF Temp 4", "%f C" % ...)
        print_field(fields, 8, "MF Temp 5", "%f C" % ...)
        print_field(fields, 9, "MF Temp 6", "%f C" % ...)
        print_field(fields, 10, "MF Temp 7", "%f C" % ...)
        print_field(fields, 11, "MF Temp 8", "%f C" % ...)
        print_field(fields, 12, "MF Temp 9", "%f C" % ...)
        print_field(fields, 13, "MF Heater Setpoint 1", "%f C" % ...)
        print_field(fields, 14, "MF Heater Setpoint 2", "%f C" % ...)
        print_field(fields, 15, "Left Proximity", "")
        print_field(fields, 16, "Right Proximity", "")

    if arg1 == 2:
        print("PAY_OPT")
        for i in range(36):
            print_field(fields, i, "Well %d" % i, "%f %%" % ...)


# Process to poll for information from the board. It prints out values
# in the string buffer every 5 seconds. Otherwise, it does not print out data
# Values read from the board are assumed to be bytes
def read_board(ser):
    while True:
        # print("waiting for serial")
        # Read from serial
        # This is a string
        str_read = ser.readline().decode("utf-8", errors='ignore')
        bytes_read = bytes(str_read, 'utf-8')

        if str_read != '': # If not a blank line
            print("Received UART (string):", str_read)
            print("Received UART (hex):", bytes_to_string(bytes_read))

            decode_rx_msg(bytes_read)

def decode_rx_msg(msg):
    if len(msg) < 11:
        print("Message too short")
        return

    if msg[0] != 0:
        print("Bad start character")
    if msg[1] != len(msg) - 2:
        print("Bad length")

    dec_msg = msg[2:]
    print("dec_msg:", bytes_to_string(dec_msg))

    type = dec_msg[0]
    arg1 = bytes_to_uint32(dec_msg[1:5])
    arg2 = bytes_to_uint32(dec_msg[5:9])
    data = dec_msg[9:]

    print("type = %d (0x%x), arg1 = %d (0x%x), arg2 = %d (0x%x), data (%d bytes) = %s" % (type, type, arg1, arg1, arg2, arg2, len(data), bytes_to_string(data)))

    if type == 0x00:
        print("Status/ping")
    if type == 0x01:
        print("Restart/uptime")
        print("restart count = %d, restart date = %s, restart time = %s, uptime = %d" % (bytes_to_uint32(data[0:4]), bytes_to_string(data[4:7]), bytes_to_string(data[7:10]), bytes_to_uint32(data[10:14])))
    if type == 0x02:
        print("Get RTC")
        print("date = %s, time = %s" % (bytes_to_string(data[0:3]), bytes_to_string(data[3:6])))
    if type == 0x03:
        print("Set RTC")
    if type == 0x04:
        print("Read memory")
        print("data = %s" % bytes_to_string(data))
    if type == 0x05:
        print("Erase memory")
    if type == 0x06:
        print("Collect block")
        print("block number = %d" % bytes_to_uint32(data[0:4]))
    if type == 0x07:
        print("Read local block")
        print_block(arg1, data)
    if type == 0x08:
        print("Read memory block")
        print_block(arg1, data)
    if type == 0x09:
        print("Enable/disable auto data collection")
    if type == 0x0A:
        print("Set auto data collection period")
    if type == 0x0B:
        print("Resync auto data collection")
    if type == 0x0C:
        print("Set EPS heater setpoints")
    if type == 0x0D:
        print("Set PAY heater setpoints")
    if type == 0x0E:
        print("Actuate PAY motors")
    if type == 0x0F:
        print("Reset")
    if type == 0x10:
        print("Send CAN message to EPS")
    if type == 0x11:
        print("Send CAN message to PAY")
    if type == 0x12:
        print("Read EEPROM")
    if type == 0x13:
        print("Get current block number")


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

# Take 4 bytes
def bytes_to_uint32(bytes):
    return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

# Only take 3 bytes
def bytes_to_uint24(bytes):
    return (bytes[0] << 16) | (bytes[1] << 8) | bytes[2]

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
# Sends data back as an int
def input_int(prompt):
    while True:
        in_str = input(prompt)

        try: #Check to see if input is an integer
            # See if the user tried to type in hex
            if in_str.startswith("0x"):
                ret = int(in_str.lstrip("0x"), 16)
            else:
                ret = int(in_str)
            return ret
        except serial.SerialException as e:
            print("Error! Input must be an integer or in hex")


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

    baud_rate = 9600

    print("Transceiver simulation starting...")


    # It is necessary for the user to specify the programming port and appropriate directory
    # In most cases, this should be the tests directory
    # The uart port only needs to be specified when it is not able to be inferred from the
    # uart_offset() method
    parser = argparse.ArgumentParser(description=("Transceiver simulator"))
    # Method arguments include (in order), expected shell text, name of that argument (used below),
    # nargs specifies the number of arguments, with '+' inserting arguments of that type into a list
    # required is self-explanatory, metavar assigns a displayed name to each argument when using the help argument
    parser.add_argument('-p', '--port', required=True,
            metavar=('port1'),
            help='UART port')

    # Converts strings to objects, which are then assigned to variables below
    args = parser.parse_args()
    port = args.port

    print("port =", port)


    ser = None # One port is used

    #Get port names
    # ports = list(serial.tools.list_ports.comports())
    # for p in ports:
    #     # TODO - kind of hacky
    #     p = p[0].replace("cu", "tty")
    #     print("Port: " + p)
    #
    #     #Mac, linux system, UART port
    #     if os.name == 'posix' and p.startswith ('/dev/tty') and p.endswith('4'):
    #         print("Testing port " + p)
    #         try :
    #             ser = serial.Serial(p, baud_rate, timeout = 1)
    #             print("Using port " + p + " for simulation")
    #             break
    #         except serial.SerialException as e:
    #             print("Port " + p + " is in use")
    #     #Windows
    #     elif os.name == 'nt' and p[0].startswith('COM'):
    #         print("Testing port " + p[0])
    #         try :
    #             ser = serial.Serial(p[0], baud_rate, timeout = 1)
    #             print("Using port " + p[0] + " for simulation")
    #             break
    #         except serial.SerialException as e:
    #             print("Port " + p[0] + " is in use")


    try:
        ser = serial.Serial(port, baud_rate, timeout = 1)
        print("Using port " + port + " for simulation")
    except serial.SerialException as e:
        print("Port " + port + " is in use")


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
            send_message(0)

        elif cmd == ("2"): #Get restart info
            send_message(1)

        elif cmd == ("3"): #Get RTC
            send_message(2)

        elif cmd == ("4"): #Set RTC
            year = input_int("Enter year: ")
            month = input_int("Enter month: ")
            day = input_int("Enter day: ")
            arg1 = bytes_to_uint24([year, month, day])

            hour = input_int("Enter hours: ")
            minute = input_int("Enter minutes: ")
            second = input_int("Enter seconds: ")
            arg2 = bytes_to_uint24([hour, minute, second])

            send_message (3, arg1, arg2)

        elif cmd == ("5"): #Memory
            print("1. Read Flash Memory")
            print("2. Erase Flash Memory")
            print("3. Read EEPROM")
            next_cmd = input("Enter command number: ")

            if next_cmd == ("1"):
                arg1 = input_int("Enter starting address: ")
                arg2 = input_int("Enter number of bytes: ")
                send_message(4, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = input_int("Enter starting address: ")
                arg2 = input_int("Enter number of bytes: ")
                send_message(5, arg1, arg2)
            elif next_cmd == ("3"):
                arg1 = input_int("Enter subsystem %s: " % subsys_consts())
                arg2  = input_int("Enter address: ")
                send_message(18,  arg1, arg2)
            else:
                print("Invalid command")

        elif cmd == ("6"): #Blocks
            print("1. Collect Block")
            print("2. Read Local Block")
            print("3. Read Memory Block")
            print("4. Get Current Block number")
            next_cmd = input("Enter command number: ")

            arg1 = input_int("Enter block type %s: " % block_type_consts())

            if next_cmd == ("1"):
                send_message(6, arg1)
            elif next_cmd == ("2"):
                send_message(7, arg1)
            elif next_cmd == ("3"):
                arg2 = input_int("Enter block number: ")
                send_message(8, arg1, arg2)
            elif next_cmd == ("4"):
                send_message(19, arg1)
            else:
                print("Invalid command")

        elif cmd == ("7"): #Auto-Data Collection
            print("1. Enable/Disable")
            print("2. Period")
            print("3. Resync")
            next_cmd = input("Enter command number: ")

            if next_cmd == ("1"):
                arg1 = input_int("Enter block type %s: " % block_type_consts())
                arg2 = input_int("Disable (0) or Enable (1): ")
                send_message(9, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = input_int("Enter block type %s: " % block_type_consts())
                arg2 = input_int("Enter period in seconds: ")
                send_message(10, arg1, arg2)
            elif next_cmd == ("3"):
                send_message(11)
            else:
                print("Invalid command")

        elif cmd == ("8"): #Heater DAC Setpoints
            print("1. Set EPS DAC Setpoints")
            print("2. Set PAY DAC Setpoints")
            next_cmd = input("Enter command number: ")

            arg1 = input_int("Enter 0 (heater 1) or 1 (heater 2): ")
            arg2 = float(input("Enter setpoint (in C): "))
            TODO - convert

            if next_cmd == ("1"):
                send_message(12, arg1, arg2)
            elif next_cmd == ("2"):
                send_message(13, arg1, arg2)
            else:
                print("Invalid command")

        elif cmd == ("9"): #Pay Control
            arg1 = input_int("Move plate up (1) or down (2): ")
            send_message(14, arg1)

        elif cmd == ("10"): #Reset
            arg1 = input_int("Enter subsystem %s: " % subsys_consts())
            send_message(15, arg1)
            # TODO

        elif cmd == ("11"): #CAN Messages
            print("1. Send CAN to EPS")
            print("2. Send CAN to PAY")
            next_cmd = input("Enter command number: ")

            msg = string_to_bytes(input("Enter 8 bytes: "))
            arg1 = bytes_to_uint32(msg[0:4])
            arg2 = bytes_to_uint32(msg[4:8])

            if next_cmd == ("1"):
                send_message(16, arg1, arg2)
            elif next_cmd == ("2"):
                send_message(17, arg1, arg2)
            else:
                print("Invalid command")

        else:
            print("Invalid option")

        # Response should be handled in the RX process
        print("Waiting for response...")
        time.sleep(2) #Wait for reply

    ser.close() # Close serial port when program done

    print("Quit Transceiver Simulator")
