# Transceiver simulator that uses python/terminal consol
# Input: String from serial.read()
# Output to microcontroller: hex/bytes using serial.write()
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

from conversions import *

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: This program requires the pyserial module. To install " +
        "pyserial,\nvisit https://pypi.org/project/pyserial/ or run\n" +
        "    $ pip install pyserial\n" +
        "in the command line.")
    sys.exit(1)


# Global Variables
ser = None # One port is used
# Output files for data
eps_hk_file = None
pay_hk_file = None
pay_opt_file = None

COMMON_HEADER = [
    "Block Number",
    "Error",
    "Date",
    "Time"
]

# Name, unit, mapping for reordering measurements
EPS_HK_MAPPING = [
    ("BB Vol",                  "V",        6   ),
    ("BB Cur",                  "A",        7   ),
    ("-Y Cur",                  "A",        5   ),
    ("+X Cur",                  "A",        2   ),
    ("+Y Cur",                  "A",        3   ),
    ("-X Cur",                  "A",        4   ),
    ("Bat Temp 1",              "C",        10  ),
    ("Bat Temp 2",              "C",        11  ),
    ("Bat Vol",                 "V",        0   ),
    ("Bat Cur",                 "A",        1   ),
    ("BT Cur",                  "A",        8   ),
    ("BT Vol",                  "V",        9   ),
    ("Heater Setpoint 1",       "C",        12  ),
    ("Heater Setpoint 2",       "C",        13  ),
    ("IMU Gyroscope (Uncal) X", "rad/s",    14  ),
    ("IMU Gyroscope (Uncal) Y", "rad/s",    15  ),
    ("IMU Gyroscope (Uncal) Z", "rad/s",    16  ),
    ("IMU Gyroscope (Cal) X",   "rad/s",    17  ),
    ("IMU Gyroscope (Cal) Y",   "rad/s",    18  ),
    ("IMU Gyroscope (Cal) Z",   "rad/s",    19  )
]

PAY_HK_MAPPING = [
    ("Temperature",          "C",   0   ),
    ("Humidity",             "%RH", 1   ),
    ("Pressure",             "kPa", 2   ),
    ("MF Temp 0",            "C",   3   ),
    ("MF Temp 1",            "C",   4   ),
    ("MF Temp 2",            "C",   5   ),
    ("MF Temp 3",            "C",   6   ),
    ("MF Temp 4",            "C",   7   ),
    ("MF Temp 5",            "C",   8   ),
    ("MF Temp 6",            "C",   9   ),
    ("MF Temp 7",            "C",   10  ),
    ("MF Temp 8",            "C",   11  ),
    ("MF Temp 9",            "C",   12  ),
    ("Heater Setpoint 1",    "C",   13  ),
    ("Heater Setpoint 2",    "C",   14  ),
    ("Left Proximity",       "",    15  ),
    ("Right Proximity",      "",    16  )
]

PAY_OPT_MAPPING = [("Well #%d" % (i + 1), "V", i) for i in range(32)]



eps_hk_sat_block_num = 0
pay_hk_sat_block_num = 0
pay_opt_sat_block_num = 0

eps_hk_file_block_num = 0
pay_hk_file_block_num = 0
pay_opt_file_block_num = 0



# Create or append to file
# Adapted from https://stackoverflow.com/questions/20432912/writing-to-a-new-file-if-it-doesnt-exist-and-appending-to-a-file-if-it-does
def load_file(name, mapping):
    if os.path.exists(name):
        print("Found existing file", name)
        print("Appending to file")

        # https://stackoverflow.com/questions/2757887/file-mode-for-creatingreadingappendingbinary
        f = open(name, 'a+')   
        return f

    else:
        print("Did not find existing file", name)
        print("Creating new file")

        f = open(name, 'a+')
        # Write header
        values = []
        values.extend(COMMON_HEADER)
        values.extend(map(lambda x : x[0] + " (" + x[1] + ")", mapping))
        f.write(", ".join(values) + "\n")
        f.flush()
        return f

    

def subsys_consts():
    return "(OBC = 0, EPS = 1, PAY = 2)"

def block_type_consts():
    return "(EPS_HK = 0, PAY_HK = 1, PAY_OPT = 2)"

def print_header(data):
    print("block number = %d, error = %d, date = %s, time = %s" % (bytes_to_uint24(data[0:3]), data[3], date_time_to_str(data[4:7]), date_time_to_str(data[7:10])))

def data_to_fields(data):
    fields = []
    for i in range(0, len(data), 3):
        fields.append(bytes_to_uint24(data[i:i+3]))
    return fields

def print_field(mapping, fields, converted, index):
    print("Field %d (%s): 0x%.6x = %f %s" % (index, mapping[index], fields[index], converted[index], mapping[index][1]))

def save_row(file, header, converted):
    # Write row
    values = []
    values.extend([bytes_to_uint24(header[0:3]), header[3], date_time_to_str(header[4:7]), date_time_to_str(header[7:10])])
    values.extend(map(str, converted))
    file.write(", ".join(map(str, values)) + "\n")
    file.flush()


def print_block(arg1, data):
    print_header(data[0:10])
    fields = data_to_fields(data[10:])

    if arg1 == 0:
        print("EPS_HK")
        num_fields = len(EPS_HK_MAPPING)
        converted = [0 for i in range(num_fields)]
        converted[0] = adc_raw_data_to_eps_vol(fields[0])
        converted[1] = adc_raw_data_to_eps_cur(fields[1])
        converted[2] = adc_raw_data_to_eps_cur(fields[2])
        converted[3] = adc_raw_data_to_eps_cur(fields[3])
        converted[4] = adc_raw_data_to_eps_cur(fields[4])
        converted[5] = adc_raw_data_to_eps_cur(fields[5])
        converted[6] = adc_raw_data_to_therm_temp(fields[6])
        converted[7] = adc_raw_data_to_therm_temp(fields[7])
        converted[8] = adc_raw_data_to_eps_vol(fields[8])
        converted[9] = adc_raw_data_to_eps_cur(fields[9]) - 2.5
        converted[10] = adc_raw_data_to_eps_cur(fields[8])
        converted[11] = adc_raw_data_to_eps_vol(fields[8])
        converted[12] = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[12])))
        converted[13] = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[13])))
        converted[14] = imu_raw_data_to_gyro(fields[14])
        converted[15] = imu_raw_data_to_gyro(fields[15])
        converted[16] = imu_raw_data_to_gyro(fields[16])
        converted[17] = imu_raw_data_to_gyro(fields[17])
        converted[18] = imu_raw_data_to_gyro(fields[18])
        converted[19] = imu_raw_data_to_gyro(fields[19])

        # Print to screen
        for i in range(num_fields):
            print_field(EPS_HK_MAPPING, fields, converted, i)

        # Write to file
        save_row(eps_hk_file, data[0:10], converted)
        print("Added to file")


    if arg1 == 1:
        print("PAY_HK")
        num_fields = len(PAY_HK_MAPPING)
        converted = [0 for i in range(num_fields)]
        converted[0]    = temp_raw_data_to_temperature(fields[0])
        converted[1]    = hum_raw_data_to_humidity(fields[1])
        converted[2]    = pres_raw_data_to_pressure(fields[2])
        converted[3]    = adc_raw_data_to_therm_temp(fields[3])
        converted[4]    = adc_raw_data_to_therm_temp(fields[4])
        converted[5]    = adc_raw_data_to_therm_temp(fields[5])
        converted[6]    = adc_raw_data_to_therm_temp(fields[6])
        converted[7]    = adc_raw_data_to_therm_temp(fields[7])
        converted[8]    = adc_raw_data_to_therm_temp(fields[8])
        converted[9]    = adc_raw_data_to_therm_temp(fields[9])
        converted[10]   = adc_raw_data_to_therm_temp(fields[10])
        converted[11]   = adc_raw_data_to_therm_temp(fields[11])
        converted[12]   = adc_raw_data_to_therm_temp(fields[12])
        converted[13]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[13])))
        converted[14]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[14])))
        converted[15]   = 0
        converted[16]   = 0

        # Print to screen
        for i in range(num_fields):
            print_field(PAY_HK_MAPPING, fields, converted, i)

        # Write to file
        save_row(pay_hk_file, data[0:10], converted)
        print("Added to file")

    if arg1 == 2:
        print("PAY_OPT")
        num_fields = len(PAY_OPT_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = opt_adc_raw_data_to_vol(fields[i], 1)
        
        # Print to screen
        for i in range(num_fields):
            print_field(PAY_OPT_MAPPING, fields, converted, i)

        # Write to file
        save_row(pay_opt_file, data[0:10], converted)
        print("Added to file")


def print_div():
    print("-" * 80)

def date_time_to_str(data):
    return "%02d %02d %02d" % (data[0], data[1], data[2])

def subsys_num_to_str(num):
    if num == 0:
        return "OBC"
    elif num == 1:
        return "EPS"
    elif num == 2:
        return "PAY"
    else:
        return "UNKNOWN"

def decode_rx_msg(enc_msg):
    if len(enc_msg) < 20:
        print("Message too short")
        return

    if enc_msg[0] != 0:
        print("Bad start character")
        return
    if enc_msg[1] != len(enc_msg) - 2:
        print("Bad length")
        return
    
    dec_msg = bytes(0)
    for i in range(2, len(enc_msg), 2):
        dec_msg += bytes([int(enc_msg[i : i + 2], 16)])

    print_div()
    print("enc_msg (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))
    print("dec_msg (%d bytes):" % len(dec_msg), bytes_to_string(dec_msg))

    type = dec_msg[0]
    arg1 = bytes_to_uint32(dec_msg[1:5])
    arg2 = bytes_to_uint32(dec_msg[5:9])
    data = dec_msg[9:]

    print("type = %d (0x%x)" % (type, type))
    print("arg1 = %d (0x%x)" % (arg1, arg1))
    print("arg2 = %d (0x%x)" % (arg2, arg2))
    print("data (%d bytes) = %s" % (len(data), bytes_to_string(data)))

    if type == 0x00:
        print("Status/ping")
    if type == 0x01:
        print("Restart/uptime")
        print("restart count =", bytes_to_uint32(data[0:4]))
        print("restart date =", date_time_to_str(data[4:7]))
        print("restart time =", date_time_to_str(data[7:10]))
        print("uptime =", bytes_to_uint32(data[10:14]))
    if type == 0x02:
        print("Get RTC")
        print("date =", date_time_to_str(data[0:3]))
        print("time =", date_time_to_str(data[3:6]))
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
        print("message =", bytes_to_string(data))
    if type == 0x11:
        print("Send CAN message to PAY")
        print("message =", bytes_to_string(data))
    if type == 0x12:
        print("Read EEPROM")
    if type == 0x13:
        print("Get current block number")
        print(subsys_num_to_str(arg1))
        block_num = bytes_to_uint32(data[0:4])
        print("block number = %d" % block_num)

        if arg1 == 0:
            global eps_hk_sat_block_num
            eps_hk_sat_block_num = block_num
        if arg1 == 1:
            global pay_hk_sat_block_num
            pay_hk_sat_block_num = block_num
        if arg1 == 2:
            global pay_opt_sat_block_num
            pay_opt_sat_block_num = block_num

    print_div()


def string_to_bytes(s):
    return bytearray(codecs.decode(s.replace(':', ''), 'hex'))

def bytes_to_string(b):
    return ":".join(map(lambda x: "%02x" % x, list(b)))

# string should look something like "00:ff:a3:49:de"
# Use `bytearray` instead of `bytes`
def send_raw_uart(uart_bytes):
    print("Sending UART (%d bytes):" % len(uart_bytes), bytes_to_string(uart_bytes))
    ser.write(uart_bytes)

def uint32_to_bytes(num):
    return bytes([(num >> 24) & 0xFF, (num >> 16) & 0xFF, (num >> 8) & 0xFF, num & 0xFF])

# Take 4 bytes
def bytes_to_uint32(bytes):
    return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

# Only take 3 bytes
def bytes_to_uint24(bytes):
    return (bytes[0] << 16) | (bytes[1] << 8) | bytes[2]

def encode_message(dec_msg):
    enc_msg = b''
    enc_msg += b'\x00'
    enc_msg += bytes([len(dec_msg) * 2])
    for byte in dec_msg:
        s = "%.2x" % byte
        enc_msg += bytes(s, 'utf-8')
    #Special character to indicate start of send_message
    return enc_msg

#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def send_message(type, arg1=0, arg2=0, data=bytes(0)):
    #change length and type to binary
    dec_msg = b''
    dec_msg += bytes([type])
    dec_msg += uint32_to_bytes(arg1)
    dec_msg += uint32_to_bytes(arg2)
    dec_msg += bytes(data)

    enc_msg = encode_message(dec_msg)

    print("Sending decoded message (%d bytes):" % len(dec_msg), bytes_to_string(dec_msg))
    print("Sending encoded message (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))
    send_raw_uart(enc_msg)


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


def receive_enc_msg():
    # Read from serial to bytes
    # DO NOT DECODE IT WITH UTF-8, IT DISCARDS ANY CHARACTERS > 127
    # See https://www.avrfreaks.net/forum/serial-port-data-corrupted-when-sending-specific-pattern-bytes
    # See https://stackoverflow.com/questions/14454957/pyserial-formatting-bytes-over-127-return-as-2-bytes-rather-then-one
    
    raw = bytes(0)
    enc_msg = bytes(0)

    for i in range(20):
        new = ser.read(2 ** 16)
        print("%d new bytes" % len(new))
        raw += new

        start_index = raw.find(0x00)
        print("start_index =", start_index)

        if start_index != -1 and start_index < len(raw) - 1 and raw[start_index + 1] == len(raw) - start_index - 2:
            enc_msg = raw[start_index:]
            print("Received UART (raw):", bytes_to_string(raw))
            print("Received UART (enc_msg):", bytes_to_string(enc_msg))
            return enc_msg

    else:
        print("Received UART (raw):", bytes_to_string(raw))
        print("No message found")
    
    return None

def print_block_nums():
    print("eps_hk_sat_block_num = %d" % eps_hk_sat_block_num)
    print("pay_hk_sat_block_num = %d" % pay_hk_sat_block_num)
    print("pay_opt_sat_block_num = %d" % pay_opt_sat_block_num)

    print("eps_hk_file_block_num = %d" % eps_hk_file_block_num)
    print("pay_hk_file_block_num = %d" % pay_hk_file_block_num)
    print("pay_opt_file_block_num = %d" % pay_opt_file_block_num)

def get_last_read_block_nums():
    print("reading block numbers from files")
    nums = [0, 0, 0]

    for i, f in enumerate((eps_hk_file, pay_hk_file, pay_opt_file)):
        f.seek(0, 0)
        all_lines = f.readlines()
        print("all_lines =", all_lines)
        if len(all_lines) > 1:
            last_line = all_lines[-1]
            nums[i] = int(last_line.split(",")[0].strip()) + 1
        f.seek(0, 2)

    global eps_hk_file_block_num, pay_hk_file_block_num, pay_opt_file_block_num
    (eps_hk_file_block_num, pay_hk_file_block_num, pay_opt_file_block_num) = nums
    print_block_nums()

def get_sat_block_nums():
    for section in range(3):
        send_message(19, section)
        print("Waiting for response...")
        enc_msg = receive_enc_msg()
        if enc_msg is not None:
            decode_rx_msg(enc_msg)
    print_block_nums()


def read_all_missing_blocks():
    print("Reading all missing blocks...")

    get_sat_block_nums()
    get_last_read_block_nums()
    last_nums = (eps_hk_file_block_num, pay_hk_file_block_num, pay_opt_file_block_num)
    cur_nums = (eps_hk_sat_block_num, pay_hk_sat_block_num, pay_opt_sat_block_num)

    for i in range(3):
        print("Need to fetch", last_nums[i], "to", cur_nums[i] - 1)
        for block_num in range(last_nums[i], cur_nums[i]):
            print("block_num =", block_num)
            print("Reading block #", block_num)
            send_message(8, i, block_num)
            print("Waiting for response...")
            enc_msg = receive_enc_msg()
            if enc_msg is not None:
                decode_rx_msg(enc_msg)


def main_loop():
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
            print("Quitting program")
            continue

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
            print("5. Get All Missing Blocks")
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
            elif next_cmd == ("5"):
                read_all_missing_blocks()
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
            print("1. Set EPS DAC Setpoint")
            print("2. Set PAY DAC Setpoint")
            next_cmd = input("Enter command number: ")

            heater = input_int("Enter 1 (heater 1) or 2 (heater 2): ")
            setpoint = float(input("Enter setpoint (in C): "))
            arg2 = dac_vol_to_raw_data(therm_res_to_vol(therm_temp_to_res(setpoint)))

            if next_cmd == ("1"):
                send_message(12, heater - 1, arg2)
            elif next_cmd == ("2"):
                send_message(13, heater - 1, arg2)
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
            print("Invalid command")

        print("Waiting for response...")
        enc_msg = receive_enc_msg()
        if enc_msg is not None:
            decode_rx_msg(enc_msg)




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

    print("Transceiver simulation starting...")


    # It is necessary for the user to specify the UART port
    parser = argparse.ArgumentParser(description=("Transceiver simulator"))
    # Method arguments include (in order), expected shell text, name of that argument (used below),
    # nargs specifies the number of arguments, with '+' inserting arguments of that type into a list
    # required is self-explanatory, metavar assigns a displayed name to each argument when using the help argument
    parser.add_argument('-u', '--uart', required=True,
            metavar=('uart'), help='UART port on programmer')
    parser.add_argument('-b', '--baud', required=False, default=9600,
            metavar=('baud'), help='Baud rate')

    # Converts strings to objects, which are then assigned to variables below
    args = parser.parse_args()
    uart = args.uart
    baud = args.baud
    
    try:
        # TODO - figure out inter_byte_timeout
        ser = serial.Serial(uart, baud, timeout=0.1)
        print("Using port " + uart + " for UART")
    except serial.SerialException as e:
        print("ERROR: Port " + uart + " is in use")


    eps_hk_file = load_file("eps_hk.csv", EPS_HK_MAPPING)
    pay_hk_file = load_file("pay_hk.csv", PAY_HK_MAPPING)
    pay_opt_file = load_file("pay_opt.csv", PAY_OPT_MAPPING)
    
    get_last_read_block_nums()
    print_block_nums()

    main_loop()
    
    eps_hk_file.close()
    pay_hk_file.close()
    pay_opt_file.close()

    ser.close() # Close serial port when program done
    print("Quit Transceiver Simulator")
