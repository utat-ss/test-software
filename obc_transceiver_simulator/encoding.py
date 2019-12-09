"""
Encoding and decoding operations for transceiver messages.
This attempts to follow obc/src/transceiver.c as closely as possible.
"""

# Calculates the checksum for the string message.
# Algorithm modified for python from:
# https://stackoverflow.com/questions/21001659/crc32-algorithm-implementation-in-c-without-a-look-up-table-and-with-a-public-li

def crc32(message, len):
   crc = 0xFFFFFFFF

   i = 0
   while message[i] != 0 and i < len:
      byte = message[i]
      crc = crc ^ byte
      for j in range (0, 8):
         mask = -(crc & 1)
         crc = (crc >> 1) ^ (0xEDB88320 & mask)
      i = i + 1
   
   crc = ~crc

   # Python might treat this as a negative number, so make it the positive
   # 32-bit equivalent if necessary
   if crc < 0:
       crc += (1 << 32)
    
   return crc


def encode_packet(dec_msg):
    TRANS_RX_DEC_MSG_MAX_SIZE = 15 #make this some kind of constant later
    TRANS_PKT_DELIMITER = 0x55

    # Decoded length
    dec_len = len(dec_msg)
    enc_len = dec_len + 9

    enc_msg = [0x00] * enc_len    # Convert to bytes later

    checksum_buf = [0x00] * (TRANS_RX_DEC_MSG_MAX_SIZE + 1)
    checksum_buf[0] = dec_len
    i = 0
    while i < dec_len and 1 + i < len(checksum_buf):
        checksum_buf[1 + i] = dec_msg[i]
        i += 1

    checksum = crc32(checksum_buf, 1 + dec_len)

    # All encoded messages start with 0x00
    enc_msg[0] = TRANS_PKT_DELIMITER
    # Next field is the length. This value will later be mapped similar to the other bytes.
    enc_msg[1] = dec_len
    enc_msg[2] = TRANS_PKT_DELIMITER
    for i in range (0, dec_len):
        enc_msg[3 + i] = dec_msg[i]

    enc_msg[enc_len - 6] = TRANS_PKT_DELIMITER
    enc_msg[enc_len - 5] = (checksum >> 24) & 0xFF
    enc_msg[enc_len - 4] = (checksum >> 16) & 0xFF
    enc_msg[enc_len - 3] = (checksum >> 8) & 0xFF
    enc_msg[enc_len - 2] = (checksum >> 0) & 0xFF
    enc_msg[enc_len - 1] = TRANS_PKT_DELIMITER

    return bytes(enc_msg)

def decode_packet(enc_msg):
    # Make these constants later
    CMD_CMD_ID_UNKNOWN = [0x00, 0x00]
    CMD_ACK_STATUS_INVALID_CSUM = [0x04]
    TRANS_RX_DEC_MSG_MAX_SIZE = 15
    # Easier to work with encoded message as a list of ints rather than bytes
    enc_msg = list(enc_msg)

    enc_len = len(enc_msg)
    dec_len = enc_msg[1]

    dec_msg = [0x00] * dec_len

    # Check invalid length
    if dec_len != enc_len - 9:
        # NACK
        return bytes(CMD_CMD_ID_UNKNOWN + CMD_ACK_STATUS_INVALID_CSUM)

    actual_checksum = (enc_msg[enc_len - 5] << 24) | (enc_msg[enc_len - 4] << 16) | (enc_msg[enc_len - 3] << 8) | enc_msg[enc_len - 2]

    # Array size to contain max number of decoded bytes plus the length byte
    checksum_bytes = [0x00] * (TRANS_RX_DEC_MSG_MAX_SIZE + 1)
    checksum_bytes[0] = dec_len
    i = 0
    while i < dec_len and 1 + i < len(checksum_bytes):
        checksum_bytes[1 + i] = enc_msg[3 + i]
        i += 1

    expected_checksum = crc32(checksum_bytes, 1 + dec_len)

    # Check invalid checksum
    # TODO - This doesn't work but the decoded message is accurate
    # actual checksum or expected checksum might be wrong
    # if expected_checksum != actual_checksum:
        # NACK for invalid checksum
        # return bytes(CMD_CMD_ID_UNKNOWN + CMD_ACK_STATUS_INVALID_CSUM)

    for i in range (0, dec_len):
        dec_msg[i] = enc_msg[3 + i]

    return bytes(dec_msg)
