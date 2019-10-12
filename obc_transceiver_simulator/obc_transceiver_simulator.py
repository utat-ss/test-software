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

from command_utilities import *
from commands import *
from common import *
from constants import *
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



def run_sim_cmd():
    print("a. Send Arbitrary Command")
    print("b. Send Raw UART")
    print("c. Set Standard Auto Data Collection Parameters")
    print("d. Disable All Auto Data Collection")
    print("e. Read All Missing Blocks")
    print("f. Set Ground Station File Block Number")
    print("g. Set Ground Station Password")

    cmd = input("Enter command: ")

    if cmd == "a":  # Arbitrary command
        opcode = input_int("Enter opcode: ")
        arg1 = input_int("Enter argument 1: ")
        arg2 = input_int("Enter argument 2: ")
        send_and_receive_packet(opcode, arg1, arg2, Global.password)

    elif cmd == "b":  # Raw UART
        send_raw_uart(string_to_bytes(input("Enter raw hex for UART: ")))
        rx_packet = receive_rx_packet()
        process_rx_packet(rx_packet)

    elif cmd == "c": #Auto-Data Collection
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
    
    elif cmd == "d": #Auto-Data Collection
        # Enables
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.OBC_HK, 0)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.EPS_HK, 0)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_HK, 0)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_OPT, 0)

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
    
    elif cmd == "g":  # Change password
        Global.password = input("Enter new password: ")
        assert len(Global.password) == 4

def main_loop():
    while True:
        # TODO - command to disable all auto data collection

        # Print top-level command groups
        print("a. Simulator Options")
        print("q. Quit Simulator")
        for (num, desc) in g_command_groups:
            print("%d. %s" % (num, desc))
        
        cmd = input("Enter command group: ") # User input typed through terminal console
        if cmd == "a":
            run_sim_cmd()
            
        elif cmd == "q":
            Global.serial.close() # Close serial port when program done
            print("Quitting simulator")
            sys.exit(0)

        else:
            # A base opcode covers a group of 16 numbers
            base_opcode = str_to_int(cmd) << 4
            # List the commands within this group of opcodes
            for command in g_all_commands:
                if base_opcode <= command.opcode and command.opcode < base_opcode + 0x10:
                    print("%d. %s" % (command.opcode - base_opcode, command.name))

            end_opcode = input_int("Enter command: ")
            # Check which command it corresponds to
            for command in g_all_commands:
                if base_opcode + end_opcode == command.opcode:
                    command.run_tx()


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
        Global.serial = serial.Serial(uart, baud, timeout=0.1)
        print("Using port " + uart + " for UART")
    except serial.SerialException as e:
        print("ERROR: Port " + uart + " is in use")
        sys.exit(1)

    for section in g_all_sections:
        section.load_file()
    
    main_loop()
    
    for section in g_all_sections:
        section.data_file.close()

    Global.serial.close() # Close serial port when program done
    print("Quit Transceiver Simulator")
