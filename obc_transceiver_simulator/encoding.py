"""
Encoding and decoding operations for transceiver messages.
This attempts to follow obc/src/transceiver.c as closely as possible.
"""



def encode_packet(dec_msg):
    enc_msg = []    # Convert to bytes later

    # 64 bit integer that will hold the 56 bit values from the byte groups
    base_conversion_buff = 0
    # Number of 7 byte groups in the decoded message
    num_byte_groups = len(dec_msg) // 7
    # Number of bytes leftover
    num_remainder_bytes = len(dec_msg) % 7
    # Encoded length
    enc_len = (num_byte_groups * 8 + num_remainder_bytes + 1) if (num_remainder_bytes > 0) else (num_byte_groups * 8)

    # All encoded messages start with 0x00
    enc_msg.append(0)
    # Next field is the length. This value will later be mapped similar to the other bytes.
    enc_msg.append(enc_len + 0x10)
    enc_msg.append(0)

    # Set up array of powers of 254
    # [0] = 254^0, [7] = 254^7
    pow_254 = [0 for i in range(8)]
    pow_254[0] = 1
    for i in range(1, 8):
        pow_254[i] = pow_254[i - 1] * 254

    # Convert each of the 7 base-256 digits to 8 base-254 digits
    for i_group in range(0, num_byte_groups):
        base_conversion_buff = 0

        for i_byte in range(0, 7):
            base_conversion_buff += dec_msg[ (7 * i_group) + i_byte] * (1 << ((6 - i_byte) * 8))  
        
        for i_byte in range(0, 8):
            enc_msg.append((base_conversion_buff // pow_254[7 - i_byte]) % 254)
    

    # encode the remainining bytes
    if(num_remainder_bytes > 0):
        base_conversion_buff = 0
        for i_byte in range(0, num_remainder_bytes):
            base_conversion_buff += dec_msg[num_byte_groups*7 + i_byte] * (1 << ((num_remainder_bytes - 1 - i_byte) * 8))
        
        for i_byte in range(0, num_remainder_bytes + 1):
            enc_msg.append((base_conversion_buff // pow_254[num_remainder_bytes - i_byte]) % 254)
    

    # Perform the mapping to avoid values 0 and 13. 0-11 -> 1-12, 12-253 -> 14-255
    # Note that the length of the message is not put through this mapping. The other digit that doesn't get mapped is the 0x00.
    for i in range(3, 3 + enc_len):
        if( enc_msg[i] >= 0 and enc_msg[i] <= 11 ):
            enc_msg[i] += 1
        
        elif( enc_msg[i] >= 12 and enc_msg[i] <= 253 ):
            enc_msg[i] += 2
        
    enc_msg.append(0x00)

    return bytes(enc_msg)


def decode_packet(enc_msg):
    # Easier to work with encoded message as a list of ints rather than bytes
    enc_msg = list(enc_msg)
    dec_msg = []

    # length of base-254 encoded message can be extracted from the first field, the mapping is undone
    enc_len = enc_msg[1] - 0x10
    # 64 bit integer that will hold the 56 bit values from the byte group
    base_conversion_buff = 0
    # concatenate the message into 8 byte groups and leftovers, then calculate length
    num_byte_groups = enc_len // 8
    num_remainder_bytes = enc_len % 8

    # TODO - what if 1 remainder byte?
    if (num_remainder_bytes == 0):
        dec_len = num_byte_groups * 7
    else:
        dec_len = (num_byte_groups * 7) + (num_remainder_bytes - 1)

    # unmap the values in the buffer
    for i in range(0, enc_len):
        if(enc_msg[3 + i] >= 1 and enc_msg[3 + i] <= 12):
            enc_msg[3 + i] -= 1
        elif(enc_msg[3 + i] >= 14 and enc_msg[3 + i] <= 255):
            enc_msg[3 + i] -= 2
    

    # Set up array of powers of 254
    # [0] = 254^0, [7] = 254^7
    pow_254 = [0x00 for i in range(8)]
    pow_254[0] = 1
    for i in range(1, 8):
        pow_254[i] = pow_254[i - 1] * 254
    
    for i_group in range(0, num_byte_groups):
        base_conversion_buff = 0

        for i_byte in range(0, 8):
            base_conversion_buff += enc_msg[ 3 + (8 * i_group) + i_byte ] * pow_254[7 - i_byte]
        
        for i_byte in range(0, 7):
            dec_msg.append((base_conversion_buff // (1 << ((6 - i_byte) * 8))) % 256)
        
    if (num_remainder_bytes > 1):
        base_conversion_buff = 0
        for i_byte in range(0, num_remainder_bytes):
            base_conversion_buff += enc_msg[ 3 + (num_byte_groups * 8) + i_byte ] * pow_254[num_remainder_bytes - 1 - i_byte]

        for i_byte in range(0, num_remainder_bytes - 1):
            dec_msg.append((base_conversion_buff // (1 << ((num_remainder_bytes - 2 - i_byte) * 8))) % 256)

    return bytes(dec_msg)
