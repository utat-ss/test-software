from common import *
from encoding import *


class TXPacket(object):
    def __init__(self, opcode, arg1, arg2):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.password = Global.password

        self.dec_pkt = b''
        self.dec_pkt += bytes([self.opcode])
        self.dec_pkt += uint32_to_bytes(self.arg1)
        self.dec_pkt += uint32_to_bytes(self.arg2)
        self.dec_pkt += bytes(self.password, 'utf-8')

        self.enc_pkt = encode_packet(self.dec_pkt)


class RXPacket(object):
    def __init__(self, enc_msg):
        self.enc_msg = enc_msg
        self.dec_msg = decode_packet(self.enc_msg)
        self.is_ack = bool((self.dec_msg[0] >> 7) & 0x1)
        self.opcode = self.dec_msg[0] & 0x7F
        self.arg1 = bytes_to_uint32(self.dec_msg[1:5])
        self.arg2 = bytes_to_uint32(self.dec_msg[5:9])
        self.status = int(self.dec_msg[9])
        self.data = self.dec_msg[10:]
        # TODO - status bytes, 10 bytes minimum


def receive_rx_packet():
    print("Waiting for RX packet...")

    uart_rx_buf = bytes(0)

    # Read from serial to bytes
    # DO NOT DECODE IT WITH UTF-8, IT DISCARDS ANY CHARACTERS > 127
    # See https://www.avrfreaks.net/forum/serial-port-data-corrupted-when-sending-specific-pattern-bytes
    # See https://stackoverflow.com/questions/14454957/pyserial-formatting-bytes-over-127-return-as-2-bytes-rather-then-one
    
    enc_msg = bytes(0)

    # Make sure to delay for longer than 2 seconds
    # (OBC needs to clear its UART RX buffer after 2 seconds)
    for i in range(50):
        new = Global.serial.read(2 ** 16)
        # print("%d new bytes" % len(new))
        uart_rx_buf += new

        # Get indices of all '\r' (<CR>) bytes
        cr_indices = [i for i in range(len(uart_rx_buf)) if uart_rx_buf[i] == ord('\r')]
        # print("cr_indices =", cr_indices)

        # Need 2 <CR> bytes to start/end message
        if len(cr_indices) >= 2:
            # Get first 2 CR characters
            start_index = cr_indices[0]
            end_index = cr_indices[1]
            # print("Detected two <CR> characters")
            # print("Received UART (raw):", bytes_to_string(uart_rx_buf))

            enc_msg = uart_rx_buf[start_index + 1 : end_index]
            uart_rx_buf = uart_rx_buf[end_index + 1 : ]

            # print("Received encoded packet (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))

            # TODO - rename packet
            if len(enc_msg) >= 5 and \
                    enc_msg[0] == 0x00 and \
                    enc_msg[1] - 0x10 == len(enc_msg) - 4 and \
                    enc_msg[2] == 0x00 and \
                    enc_msg[len(enc_msg) - 1] == 0x00:
                print("Successfully received RX packet")
                return RXPacket(enc_msg)
            else:
                print("Invalid RX packet")
                return None

    # print("Received UART (raw):", bytes_to_string(uart_rx_buf))
    print("No RX packet found")
    return None

# string should look something like "00:ff:a3:49:de"
# Use `bytearray` instead of `bytes`
def send_raw_uart(uart_bytes):
    print("Sending UART (%d bytes):" % len(uart_bytes), bytes_to_string(uart_bytes))
    Global.serial.write(uart_bytes)


#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def send_tx_packet(packet):
    from commands import g_all_commands
    global g_all_commands

    #change length and type to binary
    print_div()

    print("TX packet - sending request")

    print([command.name for command in g_all_commands if command.opcode == packet.opcode][0])

    print("Opcode = 0x%x (%d)" % (packet.opcode, packet.opcode))
    print("Argument 1 = 0x%x (%d)" % (packet.arg1, packet.arg1))
    print("Argument 2 = 0x%x (%d)" % (packet.arg2, packet.arg2))
    print("Password = %s" % packet.password)

    print("Decoded (%d bytes):" % len(packet.dec_pkt), bytes_to_string(packet.dec_pkt))
    print("Encoded (%d bytes):" % len(packet.enc_pkt), bytes_to_string(packet.enc_pkt))

    send_raw_uart(packet.enc_pkt)

    print_div()
