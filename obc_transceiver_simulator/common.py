import codecs

def string_to_bytes(s):
    return bytearray(codecs.decode(s.replace(':', ''), 'hex'))

def bytes_to_string(b):
    return ":".join(map(lambda x: "%02x" % x, list(b)))

def uint32_to_bytes(num):
    return bytes([(num >> 24) & 0xFF, (num >> 16) & 0xFF, (num >> 8) & 0xFF, num & 0xFF])

# Take 4 bytes
def bytes_to_uint32(bytes):
    return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

# Only take 3 bytes
def bytes_to_uint24(bytes):
    return (bytes[0] << 16) | (bytes[1] << 8) | bytes[2]

# NOTE: this is in decimal, not hex
def date_time_to_str(data):
    return "%02d:%02d:%02d" % (data[0], data[1], data[2])

def file_value_to_str(value):
    if type(value) == float:
        return "%.6f" % value
    else:
        return str(value)

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

# prompt is the send_message information
# Sends data back as an int
def input_int(prompt):
    return str_to_int(input(prompt))
