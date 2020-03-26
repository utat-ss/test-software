import time
import sys
import os
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

OUT_FOLDER = "out"

class Global(object):
    serial = None       # UART serial port, one port is used
    password = "UTAT"   # To send to OBC, store as a string
    uplink_drop = 0     # Ratio of packets to drop from ground to satellite
    downlink_drop = 0   # Ratio of packets to drop from satellite to ground

    dropped_uplink_packets = 0
    total_uplink_packets = 0
    
    dropped_downlink_packets = 0
    total_downlink_packets = 0

    serial_write_file = None
    serial_read_file = None

    cmd_id = 1 # Note that id will be incremented after it is sent

    # Maps command ID to TXPacket
    sent_packets = {}

def write_serial(data):
    Global.serial.write(data)

    # Calling str(data) will give a string like: "b'U\\x0fU\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00UTATUB\\xbd\\xf2\\x1cU'"
    # Want to remove b' at the beginning and ' at the end so they don't appear in the output
    # Can't decode to utf-8 because bytes > 127 will give an error
    data_str = str(data)[2:-1]
    Global.serial_write_file.write(data_str)
    Global.serial_write_file.flush()

def read_serial():
    data = Global.serial.read(2 ** 16)

    data_str = str(data)[2:-1]
    Global.serial_read_file.write(data_str)
    Global.serial_read_file.flush()
    return data

def string_to_bytes(s):
    return bytes(bytearray(codecs.decode(s.replace(':', ''), 'hex')))

def print_div():
    print("-" * 80)


def main_loop():
    last_time = time.time()

    while True:
        write_serial(string_to_bytes("Help"))
        data = read_serial()
        time.sleep(1)



if __name__ == "__main__":
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

    Global.serial = serial.Serial(uart, baud, timeout=0.1)
    print("Using port " + uart + " for UART")

    write_path = OUT_FOLDER + "/" + "serial_write.log"

    if os.path.exists(write_path):
        print("Found existing file %s, appending to file" % write_path)
    else:
        print("Did not find existing file %s, creating new file" % write_path)
    Global.serial_write_file = open(write_path, 'a+')

    # try:
    main_loop()

    # except KeyboardInterrupt:
    #     print("Closing the program")

    Global.serial.close() # Close serial port when program done