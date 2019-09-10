# Transceiver simulator that uses python/terminal consol
# Input: String from serial.read()
# Output to microcontroller: hex/bytes using serial.write()
#
# By: Brytni Richards

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
from encoding import *
from sections import *

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
# UART serial port
ser = None # One port is used

password = "UTAT"   # To send to OBC



def subsys_num_to_str(num):
    if num == 0:
        return "OBC"
    elif num == 1:
        return "EPS"
    elif num == 2:
        return "PAY"
    else:
        return "UNKNOWN"

def section_num_to_str(num):
    if num == 0:
        return "EPS_HK"
    elif num == 1:
        return "PAY_HK"
    elif num == 2:
        return "PAY_OPT"
    else:
        return "UNKNOWN"

def parse_data(data):
    header = data[0:10]
    
    fields = []
    for i in range(10, len(data), 3):
        fields.append(bytes_to_uint24(data[i : i+3]))

    return (header, fields)


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
            print(e)
            print("Error! Input must be an integer or in hex")

def input_subsys():
    return input_int("Enter subsystem (OBC = 0, EPS = 1, PAY = 2): ")

def input_block_type():
    return input_int("Enter block type (EPS_HK = 0, PAY_HK = 1, PAY_OPT = 2): ")


def print_div():
    print("-" * 80)

def print_header(header):
    print("Block number = %d" % bytes_to_uint24(header[0:3]))
    print("Error = %d" % header[3])
    print("Date = %s" % date_time_to_str(header[4:7]))
    print("Time = %s" % date_time_to_str(header[7:10]))

def process_rx_block(arg1, arg2, data):
    (header, fields) = parse_data(data)
    print("Expected block number:", arg2)
    print_header(header)

    if arg1 == 0:
        num_fields = len(EPS_HK_MAPPING)
        converted = [0 for i in range(num_fields)]
        converted[0]    = adc_raw_data_to_eps_vol(fields[0])
        converted[1]    = adc_raw_data_to_eps_cur(fields[1])
        converted[2]    = adc_raw_data_to_eps_cur(fields[2])
        converted[3]    = adc_raw_data_to_eps_cur(fields[3])
        converted[4]    = adc_raw_data_to_eps_cur(fields[4])
        converted[5]    = adc_raw_data_to_eps_cur(fields[5])
        converted[6]    = adc_raw_data_to_therm_temp(fields[6])
        converted[7]    = adc_raw_data_to_therm_temp(fields[7])
        converted[8]    = adc_raw_data_to_eps_vol(fields[8])
        converted[9]    = adc_raw_data_to_bat_cur(fields[9])
        converted[10]   = adc_raw_data_to_eps_cur(fields[10])
        converted[11]   = adc_raw_data_to_eps_vol(fields[11])
        converted[12]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[12])))
        converted[13]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[13])))
        converted[14]   = imu_raw_data_to_gyro(fields[14])
        converted[15]   = imu_raw_data_to_gyro(fields[15])
        converted[16]   = imu_raw_data_to_gyro(fields[16])
        converted[17]   = imu_raw_data_to_gyro(fields[17])
        converted[18]   = imu_raw_data_to_gyro(fields[18])
        converted[19]   = imu_raw_data_to_gyro(fields[19])

        # Print to screen
        eps_hk_section.print_fields(fields, converted)
        # Write to file
        eps_hk_section.write_block_to_file(arg2, header, converted)
        

    if arg1 == 1:
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
        pay_hk_section.print_fields(fields, converted)
        # Write to file
        pay_hk_section.write_block_to_file(arg2, header, converted)

    if arg1 == 2:
        num_fields = len(PAY_OPT_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = opt_adc_raw_data_to_vol(fields[i], 1)
        
        # Print to screen
        pay_opt_section.print_fields(fields, converted)
        # Write to file
        pay_opt_section.write_block_to_file(arg2, header, converted)


    

# string should look something like "00:ff:a3:49:de"
# Use `bytearray` instead of `bytes`
def send_raw_uart(uart_bytes):
    print("Sending UART (%d bytes):" % len(uart_bytes), bytes_to_string(uart_bytes))
    ser.write(uart_bytes)


uart_rx_buf = bytes(0)
def clear_uart_rx_buf():
    global uart_rx_buf
    uart_rx_buf = bytes(0)

def receive_enc_msg():
    global uart_rx_buf

    # Read from serial to bytes
    # DO NOT DECODE IT WITH UTF-8, IT DISCARDS ANY CHARACTERS > 127
    # See https://www.avrfreaks.net/forum/serial-port-data-corrupted-when-sending-specific-pattern-bytes
    # See https://stackoverflow.com/questions/14454957/pyserial-formatting-bytes-over-127-return-as-2-bytes-rather-then-one
    
    enc_msg = bytes(0)

    # Make sure to delay for longer than 2 seconds
    # (OBC needs to clear its UART RX buffer after 2 seconds)
    for i in range(30):
        new = ser.read(2 ** 16)
        # print("%d new bytes" % len(new))
        uart_rx_buf += new

        cr_indices = [i for i in range(len(uart_rx_buf)) if uart_rx_buf[i] == ord('\r')]
        # print("cr_indices =", cr_indices)

        # Check length (without '\r')
        if len(cr_indices) >= 2:
            # Get first 2 CR characters
            start_index = cr_indices[0]
            end_index = cr_indices[1]
            # print("Detected two <CR> characters")
            # print("Received UART (raw):", bytes_to_string(uart_rx_buf))

            enc_msg = uart_rx_buf[start_index + 1 : end_index]
            uart_rx_buf = uart_rx_buf[end_index + 1 : ]

            print("Received encoded message (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))

            if len(enc_msg) >= 5 and \
                    enc_msg[0] == 0x00 and \
                    enc_msg[1] - 0x10 == len(enc_msg) - 4 and \
                    enc_msg[2] == 0x00 and \
                    enc_msg[len(enc_msg) - 1] == 0x00:
                return enc_msg
            else:
                print("Invalid message")
                return None

    # Don't clear the buffer here
    clear_uart_rx_buf()
    # print("Received UART (raw):", bytes_to_string(uart_rx_buf))
    print("No encoded message found")
    return None

def process_rx_enc_msg(enc_msg):
    print_div()
    print("Received encoded message (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))
    dec_msg = decode_message(enc_msg)
    print("Received decoded message (%d bytes):" % len(dec_msg), bytes_to_string(dec_msg))

    type = dec_msg[0]
    arg1 = bytes_to_uint32(dec_msg[1:5])
    arg2 = bytes_to_uint32(dec_msg[5:9])
    data = dec_msg[9:]

    print("type = %d (0x%x)" % (type, type))
    print("arg1 = %d (0x%x)" % (arg1, arg1))
    print("arg2 = %d (0x%x)" % (arg2, arg2))
    print("data (%d bytes) = %s" % (len(data), bytes_to_string(data)))

    if type == 0x00:
        print("Ping")
    if type == 0x01:
        print("Subsystem status (OBC)")
        print("Restart count =", bytes_to_uint32(data[0:4]))
        print("Restart date =", date_time_to_str(data[4:7]))
        print("Restart time =", date_time_to_str(data[7:10]))
        print("Uptime =", bytes_to_uint32(data[10:14]))
    if type == 0x02:
        print("Get RTC")
        print("Date =", date_time_to_str(data[0:3]))
        print("Time =", date_time_to_str(data[3:6]))
    if type == 0x03:
        print("Set RTC")
    if type == 0x04:
        print("Read memory")
        print("Data = %s" % bytes_to_string(data))
    if type == 0x05:
        print("Erase memory")
    if type == 0x06:
        print("Collect block")
        print("Block number = %d" % bytes_to_uint32(data[0:4]))
    if type == 0x07:
        print("Read local block")
        process_rx_block(arg1, arg2, data)
    if type == 0x08:
        print("Read memory block")
        process_rx_block(arg1, arg2, data)
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
        print("Received CAN message from EPS")
        print("Message =", bytes_to_string(data))

        msg_type = data[2]
        field_num = data[3]
        rx_data = data[4:8]
        print("Type =", msg_type, ", Field =", field_num, ", Data = ", bytes_to_string(rx_data))
        
        # EPS CTRL
        if msg_type == 1:
            if field_num == 0:
                print("Ping")
            elif field_num == 1:
                print("Battery heater - shadow setpoint 1")
            elif field_num == 2:
                print("Battery heater - shadow setpoint 2")
            elif field_num == 3:
                print("Battery heater - sun setpoint 1")
            elif field_num == 4:
                print("Battery heater - sun setpoint 2")
            elif field_num == 5:
                print("Battery heater mode - lower current threshold")
            elif field_num == 6:
                print("Battery heater mode - upper current threshold")
            elif field_num == 7:
                print("Reset")
            elif field_num == 8:
                print("Read EEPROM")
            elif field_num == 9:
                print("Erase EEPROM")
            elif field_num == 10:
                print("Get restart count")
            elif field_num == 11:
                print("Get restart reason")
            elif field_num == 12:
                print("Get uptime")
            elif field_num == 13:
                print("Start temporary low-power mode")
    if type == 0x11:
        print("Received CAN message from PAY")
        print("Message =", bytes_to_string(data))

        msg_type = data[2]
        field_num = data[3]
        rx_data = data[4:8]
        print("Type =", msg_type, ", Field =", field_num, "Data = ", bytes_to_string(rx_data))
        
        # PAY CTRL
        if msg_type == 4:
            if field_num == 0:
                print("Ping")
            elif field_num == 1:
                print("MF heater - setpoint 1")
            elif field_num == 2:
                print("MF heater - setpoint 2")
            elif field_num == 3:
                print("Move act plate up")
            elif field_num == 4:
                print("Move act plate down")
            elif field_num == 5:
                print("Reset")
            elif field_num == 6:
                print("Read EEPROM")
            elif field_num == 7:
                print("Erase EEPROM")
            elif field_num == 8:
                print("Get restart count")
            elif field_num == 9:
                print("Get restart reason")
            elif field_num == 10:
                print("Get uptime")
            elif field_num == 11:
                print("Start temporary low-power mode")
    if type == 0x12:
        print("Read EEPROM")
    if type == 0x13:
        print("Get current block number")
        print(section_num_to_str(arg1))
        block_num = bytes_to_uint32(data[0:4])
        print("Block number = %d" % block_num)

        if arg1 == 0:
            #global eps_hk_sat_block_num
            eps_hk_section.sat_block_num = block_num
        if arg1 == 1:
            #global pay_hk_sat_block_num
            pay_hk_section.sat_block_num = block_num
        if arg1 == 2:
            #global pay_opt_sat_block_num
            pay_opt_section.sat_block_num = block_num

    print_div()


#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def send_message(type, arg1=0, arg2=0, data=bytes(0)):
    #change length and type to binary
    dec_msg = b''
    dec_msg += bytes([type])
    dec_msg += uint32_to_bytes(arg1)
    dec_msg += uint32_to_bytes(arg2)

    global password
    assert len(password) == 4
    dec_msg += bytes(password)


    dec_msg += bytes(data)
    print("Sending decoded message (%d bytes):" % len(dec_msg), bytes_to_string(dec_msg))

    enc_msg = encode_message(dec_msg)
    print("Sending encoded message (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))
    send_raw_uart(enc_msg)

def receive_message():
    print("Waiting for received message...")
    enc_msg = receive_enc_msg()
    if enc_msg is not None:
        print("Successfully received message")
        process_rx_enc_msg(enc_msg)
        return True
    else:
        print("Failed to receive message")
        return False

def send_and_receive_mult_attempts(type, arg1=0, arg2=0, data=bytes(0)):
    for i in range(10):
        send_message(type, arg1, arg2, data)
        if receive_message():
            return True
    return False

def send_and_receive_eps_can(msg_type, field_num, tx_data=0):
    send_and_receive_mult_attempts(0x10, (msg_type << 8) | field_num, tx_data)

def send_and_receive_pay_can(msg_type, field_num, tx_data=0):
    send_and_receive_mult_attempts(0x11, (msg_type << 8) | field_num, tx_data)

def print_sections():
    for section in all_sections:
        print(section)

def get_sat_block_nums():
    print("Getting satellite block numbers...")
    for i in range(len(all_sections)):
        send_and_receive_mult_attempts(19, i)
    print_sections()


def read_all_missing_blocks():
    get_sat_block_nums()
    print_sections()

    print("Reading all missing blocks...")
    for i, section in enumerate(all_sections):
        for block_num in range(section.file_block_num, section.sat_block_num):
            print("Reading block #", block_num)
            if not send_and_receive_mult_attempts(8, i, block_num):
                return


def main_loop():
    cmd = None # Command to board
    while cmd != ("quit"): # Enter quit to stop program
        print("p. Change Password to Send to OBC")
        print("0. Send Raw UART")
        print("1. Send Arbitrary Command")
        print("2. Ping")
        print("3. Get RTC")
        print("4. Set RTC")
        print("5. Auto-Data Collection")
        print("6. Read All Missing Blocks")
        print("7. Blocks")
        print("8. Memory (Flash and EEPROM)")
        print("9. Heater DAC Setpoints")
        print("10. Pay Control")
        print("11. Reset")
        print("12. CAN")
        print("13. EPS Heater Current Thresholds")
        cmd = input("Enter command number: ") # User input typed through terminal consol

        if cmd == ("quit"):
            print("Quitting program")
            continue

        elif cmd == ("p"):  # Change password
            password = input("Enter new password: ")
            assert len(password) == 4

        elif cmd == ("0"):  # Raw UART
            send_raw_uart(string_to_bytes(input("Enter raw hex for UART: ")))
            receive_message()
        
        elif cmd == ("1"):  # Arbitrary command
            opcode = input_int("Enter opcode: ")
            arg1 = input_int("Enter argument 1: ")
            arg2 = input_int("Enter argument 2: ")
            send_and_receive_mult_attempts(opcode, arg1, arg2)

        elif cmd == ("2"): #Ping
            ss = input_subsys()
            if ss == 0:
                #arguments = send_message type, length, make data in hex?, data, data2
                send_and_receive_mult_attempts(0)
            elif ss == 1:
                send_and_receive_eps_can(1, 0)
            elif ss == 2:
                send_and_receive_pay_can(4, 0)

        elif cmd == ("3"): #Get RTC
            send_and_receive_mult_attempts(2)

        elif cmd == ("4"): #Set RTC
            year = input_int("Enter year: ")
            month = input_int("Enter month: ")
            day = input_int("Enter day: ")
            arg1 = bytes_to_uint24([year, month, day])

            hour = input_int("Enter hours: ")
            minute = input_int("Enter minutes: ")
            second = input_int("Enter seconds: ")
            arg2 = bytes_to_uint24([hour, minute, second])

            send_and_receive_mult_attempts (3, arg1, arg2)
        
        elif cmd == ("5"): #Auto-Data Collection
            print("1. Enable/Disable")
            print("2. Period")
            print("3. Resync")
            print("4. Set Default On Settings")
            next_cmd = input("Enter command number: ")

            if next_cmd == ("1"):
                arg1 = input_block_type()
                arg2 = input_int("Disable (0) or Enable (1): ")
                send_and_receive_mult_attempts(9, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = input_block_type()
                arg2 = input_int("Enter period in seconds: ")
                send_and_receive_mult_attempts(10, arg1, arg2)
            elif next_cmd == ("3"):
                send_and_receive_mult_attempts(11)
            elif next_cmd == ("4"):
                # Periods
                send_and_receive_mult_attempts(10, 0, 60)
                send_and_receive_mult_attempts(10, 1, 120)
                send_and_receive_mult_attempts(10, 2, 300)
                # Enables
                send_and_receive_mult_attempts(9, 0, 1)
                send_and_receive_mult_attempts(9, 1, 1)
                send_and_receive_mult_attempts(9, 2, 1)
                continue    # Don't receive again at bottom of loop
            else:
                print("Invalid command")
        
        elif cmd == ("6"):  # Read missing blocks
            read_all_missing_blocks()

        elif cmd == ("7"): #Blocks
            print("1. Collect Block")
            print("2. Read Local Block")
            print("3. Read Memory Block")
            print("4. Get Satellite Block number")
            print("5. Set Satellite Block number")
            print("6. Set File Block Number")
            print("7. Set Memory Section Start Address")
            print("8. Set Memory Section End Address")
            next_cmd = input("Enter command number: ")

            arg1 = input_block_type()

            if next_cmd == ("1"):
                send_and_receive_mult_attempts(6, arg1)
            elif next_cmd == ("2"):
                send_and_receive_mult_attempts(7, arg1)
            elif next_cmd == ("3"):
                arg2 = input_int("Enter block number: ")
                send_and_receive_mult_attempts(8, arg1, arg2)
            elif next_cmd == ("4"):
                send_and_receive_mult_attempts(19, arg1)
            elif next_cmd == ("5"):
                arg2 = input_int("Enter block number: ")
                send_and_receive_mult_attempts(0x14, arg1, arg2)
            elif next_cmd == ("6"):
                num = input_int("Enter block number: ")
                if arg1 == 0:
                    eps_hk_section.file_block_num = num
                elif arg1 == 1:
                    pay_hk_section.file_block_num = num
                elif arg1 == 2:
                    pay_opt_section.file_block_num = num
                print_sections()
                continue
            elif next_cmd == ("7"):
                arg2 = input_int("Enter start address: ")
                send_and_receive_mult_attempts(0x15, arg1, arg2)
            elif next_cmd == ("8"):
                arg2 = input_int("Enter end address: ")
                send_and_receive_mult_attempts(0x16, arg1, arg2)
            else:
                print("Invalid command")

        elif cmd == ("8"): #Memory
            print("1. Read Flash Memory")
            print("2. Erase Flash Memory Physical Sector")
            print("3. Erase Flash Memory Physical Block")
            print("4. Erase All Flash Memory")
            print("5. Read EEPROM")
            next_cmd = input("Enter command number: ")

            if next_cmd == ("1"):
                arg1 = input_int("Enter starting address: ")
                arg2 = input_int("Enter number of bytes: ")
                send_and_receive_mult_attempts(4, arg1, arg2)
            elif next_cmd == ("2"):
                arg1 = input_int("Enter address: ")
                send_and_receive_mult_attempts(5, arg1)
            elif next_cmd == ("3"):
                arg1 = input_int("Enter address: ")
                send_and_receive_mult_attempts(0x1A, arg1)
            elif next_cmd == ("4"):
                resp = input("ARE YOU SURE? Type 'yes' to confirm, or Enter to cancel: ")
                if resp == "yes":
                    send_and_receive_mult_attempts(0x19)
                    print("Confirmed")
                else:
                    print("Cancelled")
            elif next_cmd == ("5"):
                ss = input_subsys()
                addr = input_int("Enter address: ")
                if ss == 0:
                    send_and_receive_mult_attempts(18, addr, 0)
                elif ss == 1:
                    send_and_receive_eps_can(1, 8)
                elif ss == 2:
                    send_and_receive_pay_can(4, 6)
            else:
                print("Invalid command")

        elif cmd == ("9"): #Heater DAC Setpoints
            print("1. Set EPS - Shadow Setpoint 1")
            print("2. Set EPS - Shadow Setpoint 2")
            print("3. Set EPS - Sun Setpoint 1")
            print("4. Set EPS - Sun Setpoint 2")
            print("5. Set PAY - Setpoint 1")
            print("6. Set PAY - Setpoint 2")
            next_cmd = input("Enter command number: ")

            setpoint = float(input("Enter setpoint (in C): "))
            data = dac_vol_to_raw_data(therm_res_to_vol(therm_temp_to_res(setpoint)))

            if next_cmd == ("1"):
                send_and_receive_eps_can(1, 1, data)
            elif next_cmd == ("2"):
                send_and_receive_eps_can(1, 2, data)
            elif next_cmd == ("3"):
                send_and_receive_eps_can(1, 3, data)
            elif next_cmd == ("4"):
                send_and_receive_eps_can(1, 4, data)
            elif next_cmd == ("5"):
                send_and_receive_pay_can(4, 1, data)
            elif next_cmd == ("6"):
                send_and_receive_pay_can(4, 2, data)
            else:
                print("Invalid command")

        elif cmd == ("10"): #Pay Control
            arg1 = input_int("Move plate up (1) or down (2): ")
            send_and_receive_mult_attempts(0x0E, arg1)

        elif cmd == ("11"): #Reset
            arg1 = input_subsys()
            if arg1 == 0:
                # don't wait for response if it's OBC
                send_message(15, arg1)
            else:
                send_and_receive_mult_attempts(15, arg1)
            
        elif cmd == ("12"): #CAN Messages
            print("1. Send CAN to EPS")
            print("2. Send CAN to PAY")
            next_cmd = input("Enter command number: ")

            msg = string_to_bytes(input("Enter 8 bytes: "))
            arg1 = bytes_to_uint32(msg[0:4])
            arg2 = bytes_to_uint32(msg[4:8])

            if next_cmd == ("1"):
                send_and_receive_mult_attempts(16, arg1, arg2)
            elif next_cmd == ("2"):
                send_and_receive_mult_attempts(17, arg1, arg2)
            else:
                print("Invalid command")
        
        elif cmd == ("13"):
            print("1. Lower")
            print("2. Upper")
            next_cmd = input("Enter command number: ")

            threshold = float(input("Enter threshold (in A): "))
            data = adc_eps_cur_to_raw_data(threshold)

            if next_cmd == ("1"):
                send_and_receive_eps_can(1, 5, data)
            elif next_cmd == ("2"):
                send_and_receive_eps_can(1, 6, data)
            else:
                print("Invalid command")

        else:
            print("Invalid command")




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
            metavar=('baud'), help='Baud rate (e.g. 1200, 9600, 19200, 115200')

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

    for section in all_sections:
        section.load_file()
    
    main_loop()
    
    for section in all_sections:
        section.data_file.close()

    ser.close() # Close serial port when program done
    print("Quit Transceiver Simulator")
