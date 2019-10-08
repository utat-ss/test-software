from commands import *
from common import *
from encoding import *
from sections import *

def print_header(header):
    print("Block number = %d" % bytes_to_uint24(header[0:3]))
    print("Date = %s" % date_time_to_str(header[3:6]))
    print("Time = %s" % date_time_to_str(header[6:9]))
    print("Success = %d" % header[9])

def process_cmd_block(arg1, arg2, data):
    print("Expected starting block number:", arg1)
    print("Expected block count:", arg2)
    assert len(data) % 19 == 0

    count = len(data) // 19
    print("%d blocks" % count)
    for i in range(count):
        block_data = data[i * 19 : (i + 1) * 19]

        header = block_data[0:10]
        opcode = block_data[10]
        arg1 = bytes_to_uint32(block_data[11:15])
        arg2 = bytes_to_uint32(block_data[15:19])

        print_div()
        print_header(header)
        print("Opcode = %d" % opcode)
        print("Argument 1 = %d" % arg1)
        print("Argument 2 = %d" % arg2)


def process_rx_packet(packet):
    print_div()
    print("Received encoded message (%d bytes):" % len(packet.enc_msg), bytes_to_string(packet.enc_msg))
    print("Received decoded message (%d bytes):" % len(packet.dec_msg), bytes_to_string(packet.dec_msg))

    print("Opcode = 0x%x (%d)" % (packet.opcode, packet.opcode))
    print("Argument 1 = 0x%x (%d)" % (packet.arg1, packet.arg1))
    print("Argument 2 = 0x%x (%d)" % (packet.arg2, packet.arg2))
    print("Data (%d bytes) = %s" % (len(packet.data), bytes_to_string(packet.data)))

    if packet.is_ack:
        print("Received ACK/NACK")

        # TODO - status variable/byte?
        if packet.data[0] == 0:
            print("OK")
        elif packet.data[0] == 1:
            print("Invalid packet")
        elif packet.data[0] == 2:
            print("Invalid decoded format")
        elif packet.data[0] == 3:
            print("Invalid opcode")
        elif packet.data[0] == 4:
            print("Invalid password")
        else:
            sys.exit(1)

    else:
        print("Got command response")

        global g_all_commands
        for command in g_all_commands:
            if command.opcode == packet.opcode:
                command.run_rx()
                break
        else:
            sys.exit(1)

    print_div()


def send_and_receive_eps_can(msg_type, field_num, tx_data=0):
    send_and_receive_packet(0x10, (msg_type << 8) | field_num, tx_data)

def send_and_receive_pay_can(msg_type, field_num, tx_data=0):
    send_and_receive_packet(0x11, (msg_type << 8) | field_num, tx_data)



def print_sections():
    for section in g_all_sections:
        print(section)

def get_sat_block_nums():
    print("Getting satellite block numbers...")
    for i in range(len(g_all_sections)):
        send_and_receive_packet(19, i)
    print_sections()


def read_all_missing_blocks():
    get_sat_block_nums()
    print_sections()

    print("Reading all missing blocks...")
    for i, section in enumerate(g_all_sections):
        for block_num in range(section.file_block_num, section.sat_block_num):
            print("Reading block #", block_num)
            if not send_and_receive_packet(8, i, block_num):
                return


def send_and_receive_packet(type, arg1=0, arg2=0, data=bytes(0), attempts=10):
    for i in range(attempts):
        # TODO - receive previous characters and discard before sending?
        send_tx_packet(type, arg1, arg2, data)
        got_ack = receive_rx_packet()
        got_resp = receive_rx_packet()
        if got_ack and got_resp:
            return True
    return False

class TXPacket(object):
    def __init__(self, opcode, arg1, arg2, data):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.data = data

        global g_password
        assert len(g_password) == 4

        self.dec_pkt = b''
        self.dec_pkt += bytes([self.opcode])
        self.dec_pkt += uint32_to_bytes(self.arg1)
        self.dec_pkt += uint32_to_bytes(self.arg2)
        self.dec_pkt += bytes(g_password, 'utf-8')
        self.dec_pkt += bytes(data)

        self.enc_pkt = encode_packet(self.dec_pkt)



class RXPacket(object):
    def __init__(self, enc_msg):
        self.enc_msg = enc_msg
        self.dec_msg = decode_packet(self.enc_msg)
        self.is_ack = bool((dec_msg[0] >> 7) & 0x1)
        self.opcode = dec_msg[0] & 0x7F
        self.arg1 = bytes_to_uint32(dec_msg[1:5])
        self.arg2 = bytes_to_uint32(dec_msg[5:9])
        self.data = dec_msg[9:]