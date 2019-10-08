from command_utilities import *
from common import *

def receive_enc_msg():
    uart_rx_buf = bytes(0)

    # Read from serial to bytes
    # DO NOT DECODE IT WITH UTF-8, IT DISCARDS ANY CHARACTERS > 127
    # See https://www.avrfreaks.net/forum/serial-port-data-corrupted-when-sending-specific-pattern-bytes
    # See https://stackoverflow.com/questions/14454957/pyserial-formatting-bytes-over-127-return-as-2-bytes-rather-then-one
    
    enc_msg = bytes(0)

    # Make sure to delay for longer than 2 seconds
    # (OBC needs to clear its UART RX buffer after 2 seconds)
    for i in range(30):
        new = g_serial.read(2 ** 16)
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

            print("Received encoded message (%d bytes):" % len(enc_msg), bytes_to_string(enc_msg))

            # TODO - rename packet
            if len(enc_msg) >= 5 and \
                    enc_msg[0] == 0x00 and \
                    enc_msg[1] - 0x10 == len(enc_msg) - 4 and \
                    enc_msg[2] == 0x00 and \
                    enc_msg[len(enc_msg) - 1] == 0x00:
                return RXPacket(enc_msg)
            else:
                print("Invalid message")
                return None

    # print("Received UART (raw):", bytes_to_string(uart_rx_buf))
    print("No RX encoded message found")
    return None

# string should look something like "00:ff:a3:49:de"
# Use `bytearray` instead of `bytes`
def send_raw_uart(uart_bytes):
    print("Sending UART (%d bytes):" % len(uart_bytes), bytes_to_string(uart_bytes))
    g_serial.write(uart_bytes)


#Type and num_chars must be an integer
#if string is true, s are string hexadecimal values
def send_tx_packet(packet):
    #change length and type to binary
    print_div()

    print("Sending command request packet")

    print("Opcode = 0x%x (%d)" % (packet.opcode, packet.opcode))
    print("Argument 1 = 0x%x (%d)" % (packet.arg1, packet.arg1))
    print("Argument 2 = 0x%x (%d)" % (packet.arg2, packet.arg2))
    print("Data (%d bytes) = %s" % (len(packet.data), bytes_to_string(packet.data)))
    print("Password = %s" % bytes_to_string(g_password))

    print("Decoded message (%d bytes):" % len(packet.dec_msg), bytes_to_string(packet.dec_msg))
    print("Encoded message (%d bytes):" % len(packet.enc_msg), bytes_to_string(packet.enc_msg))

    send_raw_uart(packet.enc_msg)

    print_div()


def receive_rx_packet():
    print("Waiting for received message...")
    enc_msg = receive_enc_msg()
    if enc_msg is not None:
        print("Successfully received message")
        process_rx_packet(enc_msg)
        return True
    else:
        print("Failed to receive message")
        return False
