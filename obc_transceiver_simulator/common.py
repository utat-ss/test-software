import codecs
import sys

from constants import *


# Global Variables
class Global(object):
    serial = None       # UART serial port, one port is used
    password = str.encode("UTAT")   # To send to OBC, store as bytes
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
    return bytes(bytearray(codecs.decode(s.replace(':', ''), 'hex')))

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

def uint16_to_bytes(num):
    return bytes([(num >> 8) & 0xFF, num & 0xFF])

# Only take 2 bytes
def bytes_to_uint16(bytes):
    return ((bytes[0] & 0xFF) << 8) | bytes[1]

def uint15_to_bytes(num):
    return bytes([(num >> 8) & 0x7F, num & 0xFF])
    
# Only take 2 bytes minus 1 bit
def bytes_to_uint15(bytes):
    return ((bytes[0] & 0x7F) << 8) | bytes[1]

# NOTE: this is in decimal, not hex
def date_time_to_str(data):
    return "%02d.%02d.%02d" % (data[0], data[1], data[2])

def conv_value_to_str(value):    
    if type(value) == float:
        return "%.6f" % value
    elif type(value) == int:
        return "%d" % value
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
    return input_int("Enter block type (OBC_HK = %d, EPS_HK = %d, PAY_HK = %d, PAY_OPT = %d, PAY_OPT_OD = %d, PAY_OPT_FL = %d, PRIM_CMD_LOG = %d, SEC_CMD_LOG = %d): " % (
        BlockType.OBC_HK, BlockType.EPS_HK, BlockType.PAY_HK, BlockType.PAY_OPT,
        BlockType.PAY_OPT_OD, BlockType.PAY_OPT_FL,
        BlockType.PRIM_CMD_LOG, BlockType.SEC_CMD_LOG))

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

def eps_ctrl_field_num_to_str(num):
    if num == EPS_CTRL.PING:
        return "Ping"
    elif num == EPS_CTRL.READ_EEPROM:
        return "Read EEPROM"
    elif num == EPS_CTRL.ERASE_EEPROM:
        return "Erase EEPROM"
    elif num == EPS_CTRL.READ_RAM_BYTE:
        return "Read RAM Byte"
    elif num == EPS_CTRL.RESET:
        return "Reset"
    elif num == EPS_CTRL.GET_HEAT_SHAD_SP:
        return "Get heater shadow setpoints"
    elif num == EPS_CTRL.SET_HEAT_1_SHAD_SP:
        return "Set heater 1 shadow setpoint"
    elif num == EPS_CTRL.SET_HEAT_2_SHAD_SP:
        return "Set heater 2 shadow setpoint"
    elif num == EPS_CTRL.GET_HEAT_SUN_SP:
        return "Get heater sun setpoints"
    elif num == EPS_CTRL.SET_HEAT_1_SUN_SP:
        return "Set heater 1 sun setpoint"
    elif num == EPS_CTRL.SET_HEAT_2_SUN_SP:
        return "Set heater 2 sun setpoint"
    elif num == EPS_CTRL.GET_HEAT_CUR_THR:
        return "Get heater current thresholds"
    elif num == EPS_CTRL.SET_HEAT_LOWER_CUR_THR:
        return "Set heater lower current threshold"
    elif num == EPS_CTRL.SET_HEAT_UPPER_CUR_THR:
        return "Set heater upper current threshold"
    else:
        return "UNKNOWN"

def pay_ctrl_field_num_to_str(num):
    if num == PAY_CTRL.PING:
        return "Ping"
    elif num == PAY_CTRL.READ_EEPROM:
        return "Read EEPROM"
    elif num == PAY_CTRL.ERASE_EEPROM:
        return "Erase EEPROM"
    elif num == PAY_CTRL.READ_RAM_BYTE:
        return "Read RAM Byte"
    elif num == PAY_CTRL.RESET_SSM:
        return "Reset SSM"
    elif num == PAY_CTRL.RESET_OPT:
        return "Reset OPT"
    elif num == PAY_CTRL.ENABLE_6V:
        return "Enable 6V"
    elif num == PAY_CTRL.DISABLE_6V:
        return "Disable 6V"
    elif num == PAY_CTRL.ENABLE_10V:
        return "Enable 10V"
    elif num == PAY_CTRL.DISABLE_10V:
        return "Disable 10V"
    elif num == PAY_CTRL.GET_HEAT_PARAMS:
        return "Get Heater Parameters"
    elif num == PAY_CTRL.SET_HEAT_SP:
        return "Set Heater Setpoint"
    elif num == PAY_CTRL.SET_INV_THERM_READING:
        return "Set Invalid Thermistor Reading"
    elif num == PAY_CTRL.GET_THERM_READING:
        return "Get Thermistor Reading"
    elif num == PAY_CTRL.GET_THERM_ERR_CODE:
        return "Get Thermistor Error Code"
    elif num == PAY_CTRL.SET_THERM_ERR_CODE:
        return "Set Thermistor Error Code"
    elif num == PAY_CTRL.GET_MOTOR_STATUS:
        return "Get Motor Status"
    elif num == PAY_CTRL.MOTOR_DEP_ROUTINE:
        return "Run Motor Deployment Routine"
    elif num == PAY_CTRL.MOTOR_UP:
        return "Move Motors Up"
    elif num == PAY_CTRL.MOTOR_DOWN:
        return "Move Motors Down"
    elif num == PAY_CTRL.SEND_OPT_SPI:
        return "Send Optical SPI"
    else:
        return "UNKNOWN"

def pay_therm_err_code_to_str(code):
    if code == PAYThermErrCode.NORMAL:
        return "Normal"
    elif code == PAYThermErrCode.BELOW_ULL:
        return "Below ULL"
    elif code == PAYThermErrCode.ABOVE_UHL:
        return "Above ULL"
    elif code == PAYThermErrCode.BELOW_MIU:
        return "Below miu"
    elif code == PAYThermErrCode.ABOVE_MIU:
        return "Above miu"
    elif code == PAYThermErrCode.MANUAL_INVALID:
        return "Manual invalid"
    elif code == PAYThermErrCode.MANUAL_VALID:
        return "Manual valid"
    else:
        return "UNKNOWN"

def pay_opt_spi_opcode_to_str(code):
    if code == PAYOptSPIOpcode.GET_READING:
        return "Get Reading"
    elif code == PAYOptSPIOpcode.GET_POWER:
        return "Get Power"
    elif code == PAYOptSPIOpcode.ENTER_SLEEP_MODE:
        return "Enter Sleep Mode"
    elif code == PAYOptSPIOpcode.ENTER_NORMAL_MODE:
        return "Enter Normal Mode"
    else:
        return "UNKNOWN"

def packet_ack_status_to_str(status):
    if status == PacketACKStatus.OK:
        return "OK"
    elif status == PacketACKStatus.RESET_CMD_ID:
        return "Successfully Reset Command ID"
    elif status == PacketACKStatus.INVALID_ENC_FMT:
        return "Invalid Encoded Format"
    elif status == PacketACKStatus.INVALID_LEN:
        return "Invalid Length"
    elif status == PacketACKStatus.INVALID_CSUM:
        return "Invalid Checksum"
    elif status == PacketACKStatus.INVALID_DEC_FMT:
        return "Invalid Decoded Format"
    elif status == PacketACKStatus.INVALID_CMD_ID:
        return "Invalid Command ID"
    elif status == PacketACKStatus.DECREMENTED_CMD_ID:
        return "Decremented Command ID"
    elif status == PacketACKStatus.REPEATED_CMD_ID:
        return "Repeated Command ID"
    elif status == PacketACKStatus.INVALID_OPCODE:
        return "Invalid Opcode"
    elif status == PacketACKStatus.INVALID_PWD:
        return "Invalid Password"
    elif status == PacketACKStatus.FULL_CMD_QUEUE:
        return "Full Command Queue"
    else:
        return "UNKNOWN"

def packet_resp_status_to_str(status):
    if status == PacketRespStatus.OK:
        return "OK"
    elif status == PacketRespStatus.INVALID_ARGS:
        return "Invalid Arguments"
    elif status == PacketRespStatus.TIMED_OUT:
        return "Timed Out"
    elif status == PacketRespStatus.INVALID_CAN_OPCODE:
        return "Invalid CAN Opcode"
    elif status == PacketRespStatus.INVALID_CAN_FIELD_NUM:
        return "Invalid CAN Field Number"
    elif status == PacketRespStatus.INVALID_CAN_DATA:
        return "Invalid CAN Data"
    else:
        return "UNKNOWN"

def packet_to_status_str(packet):
    if not packet.is_resp:
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


def tx_packet_for_rx_packet(rx_packet):
    if rx_packet.command_id in Global.sent_packets.keys():
        return Global.sent_packets[rx_packet.command_id]
    else:
        return None
