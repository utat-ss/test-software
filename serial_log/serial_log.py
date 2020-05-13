# Serial read to timestamped output

import argparse
import os
import sys

from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: This program requires the pyserial module. To install " +
        "pyserial,\nvisit https://pypi.org/project/pyserial/ or run\n" +
        "    $ pip install pyserial\n" +
        "in the command line.")
    sys.exit(1)


if __name__ == "__main__":    
    print("Starting serial log...")

    # It is necessary for the user to specify the UART port
    parser = argparse.ArgumentParser(description=("Serial log"))
    # Method arguments include (in order), expected shell text, name of that argument (used below),
    # nargs specifies the number of arguments, with '+' inserting arguments of that type into a list
    # required is self-explanatory, metavar assigns a displayed name to each argument when using the help argument
    parser.add_argument('-u', '--uart', required=True,
            metavar=('uart'), help='UART port on programmer')
    parser.add_argument('-b', '--baud', required=False, default=9600,
            metavar=('baud'), help='Baud rate (e.g. 1200, 9600, 19200, 115200')
    parser.add_argument('-o', '--output', required=True,
            metavar=('output'), help='File for timestamped serial output')

    # Converts strings to objects, which are then assigned to variables below
    args = parser.parse_args()
    uart = args.uart
    baud = args.baud
    read_path = args.output

    try:
        ser = serial.Serial(uart, baud, timeout=0.1)
        print("Using port " + uart + " for UART")
    except serial.SerialException as e:
        print("ERROR: Port " + uart + " is in use")
        sys.exit(1)

    if os.path.exists(read_path):
        print("Found existing file %s, appending to file" % read_path)
    else:
        print("Did not find existing file %s, creating new file" % read_path)
    read_file = open(read_path, 'a+')

    while True:
        line = ser.readline().strip().decode('utf-8',errors='ignore')
        if len(line) > 0:
            # print("Received", line)

            # From https://www.programiz.com/python-programming/datetime/current-datetime
            # datetime object containing current date and time
            now = datetime.now()
            # YY/mm/dd H:M:S
            dt_string = now.strftime("%Y-%m-%d, %H:%M:%S")
            # print("Date and time:", dt_string)	

            line = dt_string + ": " + line + "\n"

            print(line)
            read_file.write(line)
            read_file.flush()
