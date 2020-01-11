import random

from common import *
from encoding import *


class TXPacket(object):
    def __init__(self, cmd_id, opcode, arg1, arg2, password=Global.password):
        self.cmd_id = cmd_id
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.password = password

        self.dec_pkt = b''
        self.dec_pkt += uint15_to_bytes(self.cmd_id)
        self.dec_pkt += bytes([self.opcode])
        self.dec_pkt += uint32_to_bytes(self.arg1)
        self.dec_pkt += uint32_to_bytes(self.arg2)
        self.dec_pkt += bytes(self.password, 'utf-8')

        self.enc_pkt = encode_packet(self.dec_pkt)


class RXPacket(object):
    def __init__(self, enc_msg):
        self.enc_msg = enc_msg
        self.dec_msg = decode_packet(self.enc_msg)
        self.command_id = bytes_to_uint15(self.dec_msg[0:2])
        self.status = int(self.dec_msg[2])
        # False for ACK, True for response
        self.is_resp = bool((self.dec_msg[0] >> 7) & 0x1)
        self.data = self.dec_msg[3:]


# wait_time is in seconds
def receive_rx_packet(wait_time=5):
    print("Waiting for RX packet...")

    uart_rx_buf = bytes(0)

    # Read from serial to bytes
    # DO NOT DECODE IT WITH UTF-8, IT DISCARDS ANY CHARACTERS > 127
    # See https://www.avrfreaks.net/forum/serial-port-data-corrupted-when-sending-specific-pattern-bytes
    # See https://stackoverflow.com/questions/14454957/pyserial-formatting-bytes-over-127-return-as-2-bytes-rather-then-one
    
    # Make sure to delay for longer than 2 seconds
    # (OBC needs to clear its UART RX buffer after 2 seconds)
    for i in range(int(wait_time / Global.serial.timeout)):
        new = read_serial()
        # print("%d new bytes" % len(new))
        uart_rx_buf += new

        # Get indices of all delimiter (0x55) bytes
        delim_indices = [i for i in range(len(uart_rx_buf)) if uart_rx_buf[i] == 0x55]
        # print("cr_indices =", cr_indices)

        # Note that there might be 0x55 bytes in the decoded message data, so this can be tricky to detect

        # Need at least 4 delimiter bytes to form packet, but note this might include 0x55 data bytes
        if len(delim_indices) >= 4:
            # print("Detected 4 delim characters")
            # print("Received UART (raw):", bytes_to_string(uart_rx_buf))

            start = delim_indices[0]
            dec_len = uart_rx_buf[start + 1]
            end = start + dec_len + 9 - 1   # should be index of ending 0x55 if it's a valid packet

            # If the delimiters are in the right places and the length byte
            # matches the number of bytes in the decoded section
            # Also need to have enough bytes in the buffer
            if uart_rx_buf[start] == 0x55 and \
                    uart_rx_buf[start + 2] == 0x55 and \
                    end < len(uart_rx_buf):

                if uart_rx_buf[end + 1 - 6] == 0x55 and \
                        uart_rx_buf[end + 1 - 1] == 0x55:
                    
                    enc_pkt = uart_rx_buf[start : end + 1]
                    enc_len = len(enc_pkt)

                    # print("Received encoded packet (%d bytes):" % len(enc_pkt), bytes_to_string(enc_pkt))

                    # Bytes to calculate the checksum on
                    csum_bytes = bytes([enc_pkt[1]]) + enc_pkt[3 : enc_len - 6]
                    # Calculate expected checksum
                    calc_csum = crc32(csum_bytes, len(csum_bytes))
                    # print("Calculated checksum is 0x%x" % calc_csum)

                    rcvd_csum = bytes_to_uint32(enc_pkt[enc_len - 5 : enc_len - 1])
                    # print("Received checksum is 0x%x" % rcvd_csum)

                    # See if checksum is correct
                    if rcvd_csum == calc_csum:
                        print("Correct checksum")
                    else:
                        print("WRONG CHECKSUM")
                        sys.exit(1)

                    # Drop packet?
                    if (random.uniform(0,1) < Global.downlink_drop):
                        print_div()
                        print("Downlink Packet Dropped")
                        Global.dropped_downlink_packets += 1
                        Global.total_downlink_packets += 1
                        return None

                    # If did not drop packet
                    print("Successfully received RX packet")
                    Global.total_downlink_packets += 1
                    return RXPacket(enc_pkt)

                # If we received enough bytes but it is not in packet format,
                # discard some bytes so it will check again on the next loop iteration
                else:
                    uart_rx_buf = uart_rx_buf[delim_indices[1] : ]

    # print("Received UART (raw):", bytes_to_string(uart_rx_buf))
    print("No RX packet found")
    return None

# string should look something like "00:ff:a3:49:de"
# Use `bytearray` instead of `bytes`
def send_raw_uart(uart_bytes):
    print("Sending UART (%d bytes):" % len(uart_bytes), bytes_to_string(uart_bytes))
    write_serial(uart_bytes)


#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def send_tx_packet(packet):
    from commands import g_all_commands
    global g_all_commands

    #change length and type to binary
    print_div()

    print("TX packet - sending request")

    matched_cmds = [command.name for command in g_all_commands if command.opcode == packet.opcode]
    if len(matched_cmds) > 0:
        print(matched_cmds[0])
    else:
        print("UNKNOWN OPCODE")

    print("Command Id = 0x%x (%d)" % (packet.cmd_id, packet.cmd_id))
    print("Opcode = 0x%x (%d)" % (packet.opcode, packet.opcode))
    print("Argument 1 = 0x%x (%d)" % (packet.arg1, packet.arg1))
    print("Argument 2 = 0x%x (%d)" % (packet.arg2, packet.arg2))
    print("Password = %s" % packet.password)

    print("Decoded (%d bytes):" % len(packet.dec_pkt), bytes_to_string(packet.dec_pkt))
    print("Encoded (%d bytes):" % len(packet.enc_pkt), bytes_to_string(packet.enc_pkt))

    # Drop packets?
    if (random.uniform(0,1) < Global.uplink_drop):
        print_div()
        print("Uplink Packet Dropped")
        Global.dropped_uplink_packets += 1
    else:
        send_raw_uart(packet.enc_pkt)
    
    # Whether the send actually worked or dropped, we still think we sent it so
    # add it to our dictionary mapping command IDs to send packets
    Global.sent_packets[packet.cmd_id] = packet
    
    Global.total_uplink_packets += 1

    print_div()
