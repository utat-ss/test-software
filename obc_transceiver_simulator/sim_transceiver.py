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
        val = ser.readLine()
        #Print given hex value
        #hex_val = hex(int.from_bytes(in_bin, byteorder='little'))
        print(ser.readline().decode("utf-8", errors='ignore'))

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

    # It is necessary for the user to specify the programming port and appropriate directory
    # In most cases, this should be the tests directory
    # The uart port only needs to be specified when it is not able to be inferred from the
    # uart_offset() method
    parser = argparse.ArgumentParser(description=harness_description)
    # Method arguments include (in order), expected shell text, name of that argument (used below),
    # nargs specifies the number of arguments, with '+' inserting arguments of that type into a list
    # required is self-explanatory, metavar assigns a displayed name to each argument when using the help argument
    parser.add_argument('-p', '--prog', nargs='+', required=True,
            metavar=('port1', 'port2'),
            help='list of programming ports')
    parser.add_argument('-u', '--uart', nargs='+', required=False,
            metavar=('uart1', 'uart2'), default=[],
            help='list of UART ports')
    parser.add_argument('-d', '--test-dir', required=True,
            metavar='test_dir',
            help='directory in which to search for tests') #I DON"T THINK THIS IS NEEDED?

    # Converts strings to objects, which are then assigned to variables below
    args = parser.parse_args()
    test_path = args.test_dir
    port = args.prog
    uart = args.uart

    # If there is no uart argument, add port using uart offset
    # This is done by removing the last digit and adding uart_offset()
    # Then, it adds it to the uart variable (list)
    # However, this will not work for cases when port ends in 8 or 9
    if len(uart) == 0:
        for p in port:
            (head, tail) = os.path.split(p)
            tail = tail[:-1] + str(int(tail[-1]) + uart_offset())
            uart.append(os.path.join(head, tail))

    #Find ports
    baud_rate = 9600

    print("Transceiver simulation starting...")

    i = 0
    for p in port:
        ser[i] = serial.Serial(p, baud_rate, timeout = None)

    proc = Process(target = read_board, args=(ser[0]))
    proc.start() #Start reading from board

    cmd = None #Command to board
    while cmd != ("quit"):
        cmd = input()
        if cmd == ("quit"):
            proc.terminate()
        else:
            cmd.split(":")
            for i in range (len(cmd)):
                cmd[i] = int(cmd[i], 16) #Convert to hex number
                #cmd = "".join(cmd) #Made cmd one string
                #bytes.fromhex(cmd) Gives \xAA\x0A\x0B etc
                ser[1].to_bytes(cmd[i]) #Send hex command
                #ser[1].write(b"%s" % cmd[i])
                #ser[1].write(bytes(cmd[i]))

for i in range len(port):
    ser[i].close()
print("Quit Transceiver Simulator")
