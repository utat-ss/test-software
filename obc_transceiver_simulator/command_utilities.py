
from common import *
from encoding import *
from packets import *
from sections import *

def print_header(header):
    print("Block number = 0x%x (%d)" % (bytes_to_uint24(header[0:3]), bytes_to_uint24(header[0:3])))
    print("Date = %s" % date_time_to_str(header[3:6]))
    print("Time = %s" % date_time_to_str(header[6:9]))
    print("Status = 0x%x (%d)" % (header[9], header[9]))

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
        print("Opcode = 0x%x (%d)" % (opcode, opcode))
        print("Argument 1 = 0x%x (%d)" % (arg1, arg1))
        print("Argument 2 = 0x%x (%d)" % (arg2, arg2))


def process_rx_packet(packet):
    from commands import g_all_commands
    global g_all_commands

    print_div()
    print("RX packet - received %s" % ("ACK" if packet.is_ack else "response"))

    print([command.name for command in g_all_commands if command.opcode == packet.opcode][0])

    print("Encoded (%d bytes):" % len(packet.enc_msg), bytes_to_string(packet.enc_msg))
    print("Decoded (%d bytes):" % len(packet.dec_msg), bytes_to_string(packet.dec_msg))

    print("Opcode = 0x%x (%d)" % (packet.opcode, packet.opcode))
    print("Argument 1 = 0x%x (%d)" % (packet.arg1, packet.arg1))
    print("Argument 2 = 0x%x (%d)" % (packet.arg2, packet.arg2))
    print("Data (%d bytes) = %s" % (len(packet.data), bytes_to_string(packet.data)))

    if packet.is_ack:
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
        # from commands import g_all_commands
        # global g_all_commands
        for command in g_all_commands:
            if command.opcode == packet.opcode:
                command.run_rx(packet)
                break
        else:
            sys.exit(1)

    print_div()


def send_and_receive_eps_can(msg_type, field_num, tx_data=0):
    send_and_receive_packet(CommandOpcode.SEND_EPS_CAN_MSG, (msg_type << 8) | field_num, tx_data)

def send_and_receive_pay_can(msg_type, field_num, tx_data=0):
    send_and_receive_packet(CommandOpcode.SEND_PAY_CAN_MSG, (msg_type << 8) | field_num, tx_data)



def print_sections():
    for section in g_all_sections:
        print(section)

def get_sat_block_nums():
    print("Getting satellite block numbers...")
    for i in range(len(g_all_sections)):
        send_and_receive_packet(19, i, 0)
    print_sections()


def read_all_missing_blocks(ser):
    get_sat_block_nums()
    print_sections()

    print("Reading all missing blocks...")
    for i, section in enumerate(g_all_sections):
        for block_num in range(section.file_block_num, section.sat_block_num):
            print("Reading block #", block_num)
            if not send_and_receive_packet(ser, 8, i, block_num):
                return


def send_and_receive_packet(opcode, arg1=0, arg2=0, attempts=10):
    for i in range(attempts):
        # TODO - receive previous characters and discard before sending?
        send_tx_packet(TXPacket(opcode, arg1, arg2))

        ack_packet = receive_rx_packet()
        if ack_packet is None:
            continue
        process_rx_packet(ack_packet)

        resp_packet = receive_rx_packet()
        if resp_packet is None:
            continue
        process_rx_packet(resp_packet)

        return True
    return False
