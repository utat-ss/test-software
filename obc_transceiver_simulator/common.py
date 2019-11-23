import codecs
import sys

from constants import *


# Global Variables
class Global(object):
    serial = None       # UART serial port, one port is used
    password = "UTAT"   # To send to OBC, store as a string
    uplink_drop = 0     # Ratio of packets to drop from ground to satellite
    downlink_drop = 0   # Ratio of packets to drop from satellite to ground

    dropped_uplink_packets = 0
    total_uplink_packets = 0
    
    dropped_downlink_packets = 0
    total_downlink_packets = 0


def check_python3():
    # Detects if correct python version is being run
    if sys.version_info[0] == 2:
        print("You are using Python 2. Please update to Python 3 and try again.")
        sys.exit(1)
    elif sys.version_info[0] == 3:
        print("You are running Python 3.")
    else:
        print("Unknown error. Exiting....")
        sys.exit(1)

def string_to_bytes(s):
    return bytearray(codecs.decode(s.replace(':', ''), 'hex'))

def bytes_to_string(b):
    return ":".join(map(lambda x: "%02x" % x, list(b)))

def uint32_to_bytes(num):
    return bytes([(num >> 24) & 0xFF, (num >> 16) & 0xFF, (num >> 8) & 0xFF, num & 0xFF])

# Take 4 bytes
def bytes_to_uint32(bytes):
    return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

def uint24_to_bytes(num):
    return bytes([(num >> 16) & 0xFF, (num >> 8) & 0xFF, num & 0xFF])

# Only take 3 bytes
def bytes_to_uint24(bytes):
    return (bytes[0] << 16) | (bytes[1] << 8) | bytes[2]

# NOTE: this is in decimal, not hex
def date_time_to_str(data):
    return "%02d.%02d.%02d" % (data[0], data[1], data[2])

def conv_value_to_str(value):    
    if type(value) == float:
        return "%.6f" % value
    elif type(value) == int:
        return "0x%x (%d)" % (value, value)
    elif type(value) == str:
        return value
    else:
        sys.exit(1)

def str_to_int(string):
    try: #Check to see if input is an integer
        # See if the user tried to type in hex
        if string.startswith("0x"):
            ret = int(string.lstrip("0x"), 16)
        else:
            ret = int(string)
        return ret
    except Exception as e:
        print(e)
        print("Error! Input must be an integer or in hex")
        raise e

# prompt is the send_tx_packet information
# Sends data back as an int
def input_int(prompt):
    return str_to_int(input(prompt))

def input_subsys():
    return input_int("Enter subsystem (OBC = %d, EPS = %d, PAY = %d): " % (Subsystem.OBC, Subsystem.EPS, Subsystem.PAY))

def input_block_type():
    return input_int("Enter block type (OBC_HK = %d, EPS_HK = %d, PAY_HK = %d, PAY_OPT = %d, PRIM_CMD_LOG = %d, SEC_CMD_LOG = %d): " % (BlockType.OBC_HK, BlockType.EPS_HK, BlockType.PAY_HK, BlockType.PAY_OPT, BlockType.PRIM_CMD_LOG, BlockType.SEC_CMD_LOG))

def subsys_num_to_str(num):
    if num == Subsystem.OBC:
        return "OBC"
    elif num == Subsystem.EPS:
        return "EPS"
    elif num == Subsystem.PAY:
        return "PAY"
    else:
        sys.exit(1)

def section_num_to_str(num):
    if num == BlockType.OBC_HK:
        return "OBC_HK"
    elif num == BlockType.EPS_HK:
        return "EPS_HK"
    elif num == BlockType.PAY_HK:
        return "PAY_HK"
    elif num == BlockType.PAY_OPT:
        return "PAY_OPT"
    elif num == BlockType.PRIM_CMD_LOG:
        return "PRIM_CMD_LOG"
    elif num == BlockType.SEC_CMD_LOG:
        return "SEC_CMD_LOG"
    else:
        sys.exit(1)

def packet_ack_status_to_str(status):
    if status == 0:
        return "OK"
    elif status == 1:
        return "Invalid packet"
    elif status == 2:
        return "Invalid decoded format"
    elif status == 3:
        return "Invalid opcode"
    elif status == 4:
        return "Invalid password"
    else:
        return "UNKNOWN"

def packet_resp_status_to_str(status):
    if status == 0:
        return "OK"
    elif status == 1:
        return "Invalid arguments"
    elif status == 2:
        return "Timed out"
    else:
        return "UNKNOWN"

def packet_to_status_str(packet):
    if packet.is_ack:
        return packet_ack_status_to_str(packet.status)
    else:
        return packet_resp_status_to_str(packet.status)

def restart_reason_to_str(reason):
    if reason == 0x01:
        return "Unintentional watchdog timeout (hang)"
    elif reason == 0x02:
        return "Intentional reset command"
    elif reason == 0x03:
        return "Communication timeout"
    elif reason == 0x04:
        return "Watchdog system reset"
    elif reason == 0x05:
        return "Brown-out reset"
    elif reason == 0x06:
        return "External reset"
    elif reason == 0x07:
        return "Power-on reset"
    else:
        return "UNKNOWN"

def enable_states_to_str(states, num_bits):
    str_list = []
    for i in range(num_bits - 1, -1, -1):
        if (states >> i) & 0x01:
            str_list.append("%d ON" % i)
        else:
            str_list.append("%d OFF" % i)
    # Can't use comma separators for CSV
    return " ".join(str_list)

def parse_data(data):
    header = data[0:10]
    
    fields = []
    for i in range(10, len(data), 3):
        fields.append(bytes_to_uint24(data[i : i+3]))

    return (header, fields)


def print_div():
    print("-" * 80)