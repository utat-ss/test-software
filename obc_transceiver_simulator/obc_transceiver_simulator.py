# Transceiver simulator that uses python/terminal consol
# Input: String from serial.read()
# Output to microcontroller: hex/bytes using serial.write()
#
# By: Bruno Almeida, Brytni Richards

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


def sim_data_col():
    print("a. Print File Info")
    print("b. Read Missing Blocks")
    print("c. Read Missing Secondary Command Log Blocks")
    
    cmd = input("Enter command: ")

    if cmd == "a":
        for section in g_all_sections:
            print(section)
    
    elif cmd == "b":  # Read missing blocks
        read_missing_blocks()
    
    elif cmd == "c":  # Read missing secondary command log blocks
        read_missing_sec_cmd_log_blocks()


def sim_actions():
    print("a. Set File Block Number")
    print("b. Set Standard Auto Data Collection Parameters")
    print("c. Disable All Auto Data Collection")
    print("d. Print Dropped Packet Statistics")
    print("e. Set Ground Station Password")
    print("f. Send Arbitrary Command")
    print("g. Send Raw UART")
    print("h. Reset Command Id")

    cmd = input("Enter command: ")

    if cmd == "a":
        arg1 = input_block_type()
        num = input_int("Enter block number: ")

        if arg1 == BlockType.OBC_HK:
            obc_hk_section.set_file_block_num(num)
        elif arg1 == BlockType.EPS_HK:
            eps_hk_section.set_file_block_num(num)
        elif arg1 == BlockType.PAY_HK:
            pay_hk_section.set_file_block_num(num)
        elif arg1 == BlockType.PAY_OPT:
            pay_opt_section.set_file_block_num(num)
        elif arg1 == BlockType.PRIM_CMD_LOG:
            prim_cmd_log_section.set_file_block_num(num)
        elif arg1 == BlockType.SEC_CMD_LOG:
            sec_cmd_log_section.set_file_block_num(num)

    elif cmd == "b": #Auto-Data Collection
        # Set periods
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.OBC_HK, 60)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.EPS_HK, 60)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.PAY_HK, 120)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, BlockType.PAY_OPT, 300)

        # Enable all
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.OBC_HK, 1)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.EPS_HK, 1)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_HK, 1)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_OPT, 1)
    
    elif cmd == "c": #Auto-Data Collection
        # Disable all
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.OBC_HK, 0)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.EPS_HK, 0)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_HK, 0)
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, BlockType.PAY_OPT, 0)
    
    elif cmd == "d":
        uplink_pct = 0.0 if Global.total_uplink_packets == 0 else Global.dropped_uplink_packets / Global.total_uplink_packets * 100.0
        downlink_pct = 0.0 if Global.total_downlink_packets == 0 else Global.dropped_downlink_packets / Global.total_downlink_packets * 100.0

        print_div()
        print("Dropped packets:")
        print("Uplink: %d/%d (%.1f%%)" % (
            Global.dropped_uplink_packets, Global.total_uplink_packets, uplink_pct))
        print("Downlink: %d/%d (%.1f%%)" % (
            Global.dropped_downlink_packets, Global.total_downlink_packets, downlink_pct))
        print_div()

    elif cmd == "e":  # Change password
        Global.password = input("Enter new password: ")
        assert len(Global.password) == 4

    elif cmd == "f":  # Arbitrary command
        opcode = input_int("Enter opcode: ")
        arg1 = input_int("Enter argument 1: ")
        arg2 = input_int("Enter argument 2: ")
        send_and_receive_packet(opcode, arg1, arg2)

    elif cmd == "g":  # Raw UART
        send_raw_uart(string_to_bytes(input("Enter raw hex for UART: ")))
        rx_packet = receive_rx_packet()
        process_rx_packet(rx_packet)

    elif cmd == "h": # Reset Command Id
        Global.command_id = 0
        # TODO - figure out a better way to do this
        opcode = 0
        arg1 = 0
        arg2 = 0
        send_and_receive_packet(opcode, arg1, arg2)
    

def main_loop():
    while True:
        # Print top-level command groups
        print("a. Simulator Data Collection")
        print("b. Simulator Actions")
        print("q. Quit Simulator")
        for (num, desc) in g_command_groups:
            print("%d. %s" % (num, desc))
        
        cmd = input("Enter command group: ") # User input typed through terminal console

        if cmd == "a":
            sim_data_col()
        
        elif cmd == "b":
            sim_actions()
            
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
    parser.add_argument('-ud', '--uplink-drop', required=False, default=0,
            metavar=('uplink'), help='Package drop rate from ground to satellite (0-1)')
    parser.add_argument('-dd', '--downlink-drop', required=False, default=0,
            metavar=('downlink'), help='Package drop rate from satellite to ground (0-1)')

    # Converts strings to objects, which are then assigned to variables below
    args = parser.parse_args()
    uart = args.uart
    baud = args.baud
    Global.uplink_drop = float(args.uplink_drop)
    print("Uplink packet drop rate: %.1f%%" % (Global.uplink_drop * 100.0))
    Global.downlink_drop = float(args.downlink_drop)
    print("Downlink packet drop rate: %.1f%%" % (Global.downlink_drop * 100.0))

    try:
        # TODO - figure out inter_byte_timeout
        Global.serial = serial.Serial(uart, baud, timeout=0.1)
        print("Using port " + uart + " for UART")
    except serial.SerialException as e:
        print("ERROR: Port " + uart + " is in use")
        sys.exit(1)

    for section in g_all_sections:
        section.load_file()
    
    # TODO - refactor checking for out folder?
    # https://stackoverflow.com/questions/2757887/file-mode-for-creatingreadingappendingbinary

    write_path = OUT_FOLDER + "/" + "serial_write.log"
    if os.path.exists(write_path):
        print("Found existing file %s, appending to file" % write_path)
    else:
        print("Did not find existing file %s, creating new file" % write_path)
    Global.serial_write_file = open(write_path, 'a+')
    
    read_path = OUT_FOLDER + "/" + "serial_read.log"
    if os.path.exists(read_path):
        print("Found existing file %s, appending to file" % read_path)
    else:
        print("Did not find existing file %s, creating new file" % read_path)
    Global.serial_read_file = open(read_path, 'a+')

    print("To view these files live, run `tail -f out/serial*.log`")

    main_loop()
    
    for section in g_all_sections:
        section.data_file.close()

    Global.serial.close() # Close serial port when program done
    print("Quit Transceiver Simulator")
