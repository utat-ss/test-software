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

from commands import *
from constants import *
from conversions import *
from encoding import *
from sections import *

import_serial()


def main_loop():
    cmd = None # CommandOpcode to board
    while True: # Enter quit to stop program
        # TODO - update to match opcodes, preferably in a modular way
        # TODO - command to disable all auto data collection
        print("q. Quit Program")
        print("a. Change GS Password")
        print("b. Send Raw UART")
        print("c. Send Arbitrary CommandOpcode")
        print("d. Set Standard Auto Data Collection Parameters")
        print("e. Read All Missing Blocks")
        print("f. Set File Block Number")
        print("0. Ping")
        print("1. Get RTC")
        print("2. Set RTC")
        print("3. Read EEPROM")
        print("4. Erase EEPROM")
        print("5. Read RAM Byte")
        print("6. EPS CAN")
        print("7. PAY CAN")
        print("8. Actuate PAY Motors")
        print("9. Reset Subsystem")
        print("17. Read Data Block")
        print("18. Read Local Block")
        print("19. Read Primary CommandOpcode Blocks")
        print("20. Read Secondary CommandOpcode Blocks")
        print("21. Read Raw Memory Bytes")
        print("22. Erase Flash Memory Physical Sector")
        print("23. Erase Flash Memory Physical Block")
        print("24. Erase All Flash Memory")
        print("32. Collect Data Block")
        print("33. Get Satellite Block number")
        print("34. Set Satellite Block number")
        print("35. Set Memory Section Start Address")
        print("36. Set Memory Section End Address")

        cmd = input("Enter command number: ") # User input typed through terminal console
        opcode = None

        if cmd == "q":
            print("Quitting program")
            sys.exit(0)

        elif cmd == "a":  # Change password
            global g_password
            g_password = input("Enter new password: ")
            assert len(g_password) == 4

        elif cmd == "b":  # Raw UART
            send_raw_uart(string_to_bytes(input("Enter raw hex for UART: ")))
            receive_rx_packet()

        elif cmd == "c":  # Arbitrary command
            opcode = input_int("Enter opcode: ")
            arg1 = input_int("Enter argument 1: ")
            arg2 = input_int("Enter argument 2: ")
            send_and_receive_packet(opcode, arg1, arg2)
        
        elif cmd == "d": #Auto-Data Collection
            # Periods
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.OBC_HK, 60)
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.EPS_HK, 60)
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.PAY_HK, 120)
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.PAY_OPT, 300)

            # Enables
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.OBC_HK, 1)
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.EPS_HK, 1)
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_HK, 1)
            send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_OPT, 1)
        
        elif cmd == "e":  # Read missing blocks
            read_all_missing_blocks()

        elif cmd == "f":
            arg1 = input_block_type()
            num = input_int("Enter block number: ")
            if arg1 == BlockType.EPS_HK:
                eps_hk_section.file_block_num = num
            elif arg1 == BlockType.PAY_HK:
                pay_hk_section.file_block_num = num
            elif arg1 == BlockType.PAY_OPT:
                pay_opt_section.file_block_num = num
            print_sections()
        
        else:
            opcode = 0xFF
        
        # TODO - clean up
        if opcode != 0xFF:
            continue

        opcode = str_to_int(cmd)



 


        

        else:
            print("Invalid command")




if __name__ == "__main__":
    check_python3()

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
        g_serial = serial.Serial(uart, baud, timeout=0.1)
        print("Using port " + uart + " for UART")
    except serial.SerialException as e:
        print("ERROR: Port " + uart + " is in use")
        sys.exit(1)

    for section in g_all_sections:
        section.load_file()
    
    main_loop()
    
    for section in g_all_sections:
        section.data_file.close()

    g_serial.close() # Close serial port when program done
    print("Quit Transceiver Simulator")
