from common import *
from conversions import *
from encoding import *
from packets import *
from sections import *


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
    print("Status = 0x%x (%d) - %s" % (packet.status, packet.status, packet_to_status_str(packet)))
    print("Data (%d bytes) = %s" % (len(packet.data), bytes_to_string(packet.data)))

    if not packet.is_ack:
        for command in g_all_commands:
            if command.opcode == packet.opcode:
                command.run_rx(packet)
                break
        else:
            sys.exit(1)

    print_div()

def print_header(header):
    print("Block number = 0x%x (%d)" % (bytes_to_uint24(header[0:3]), bytes_to_uint24(header[0:3])))
    print("Date = %s" % date_time_to_str(header[3:6]))
    print("Time = %s" % date_time_to_str(header[6:9]))
    print("Status = 0x%x (%d)" % (header[9], header[9]))

def process_data_block(packet):
    (header, fields) = parse_data(packet.data)
    block_type = packet.arg1
    block_num = packet.arg2
    print("Expected block number:", block_num)
    print_header(header)

    # TODO - each "converted" value should be allowable as either a float, int, or string
    # If float, log with constant number of decimal places

    if block_type == BlockType.OBC_HK:
        num_fields = len(OBC_HK_MAPPING)
        converted = [0 for i in range(num_fields)]
        converted[0] = fields[0]
        converted[1] = fields[1]
        converted[2] = "0x%.2x (%s)" % (fields[2], restart_reason_to_str(fields[2])) # Represent as string
        converted[3] = date_time_to_str(uint24_to_bytes(fields[3]))
        converted[4] = date_time_to_str(uint24_to_bytes(fields[4]))

        # Print to screen
        obc_hk_section.print_fields(fields, converted)
        # Write to file
        obc_hk_section.write_block_to_file(block_num, header, converted)

    elif block_type == BlockType.EPS_HK:
        num_fields = len(EPS_HK_MAPPING)
        converted = [0 for i in range(num_fields)]
        converted[0]    = adc_raw_data_to_eps_vol(fields[0])
        converted[1]    = adc_raw_data_to_bat_cur(fields[1])
        converted[2]    = adc_raw_data_to_eps_cur(fields[2])
        converted[3]    = adc_raw_data_to_eps_cur(fields[3])
        converted[4]    = adc_raw_data_to_eps_cur(fields[4])
        converted[5]    = adc_raw_data_to_eps_cur(fields[5])
        converted[6]    = adc_raw_data_to_eps_vol(fields[6])
        converted[7]    = adc_raw_data_to_eps_cur(fields[7])
        converted[8]    = adc_raw_data_to_eps_vol(fields[8])
        converted[9]    = adc_raw_data_to_eps_cur(fields[9])
        converted[10]   = adc_raw_data_to_eps_cur(fields[10])
        converted[11]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[11])))
        converted[12]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[12])))
        converted[13]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[13])))
        converted[14]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[14])))
        converted[15]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[15])))
        converted[16]   = enable_states_to_str(fields[16], 4)
        converted[17]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[17])))
        converted[18]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[18])))
        converted[19]   = imu_raw_data_to_gyro(fields[19])
        converted[20]   = imu_raw_data_to_gyro(fields[20])
        converted[21]   = imu_raw_data_to_gyro(fields[21])
        converted[22]   = imu_raw_data_to_gyro(fields[22])
        converted[23]   = imu_raw_data_to_gyro(fields[23])
        converted[24]   = imu_raw_data_to_gyro(fields[24])
        converted[25]   = fields[25]
        converted[26]   = fields[26]
        converted[27]   = "0x%.2x (%s)" % (fields[27], restart_reason_to_str(fields[27])) # Represent as string

        # Print to screen
        eps_hk_section.print_fields(fields, converted)
        # Write to file
        eps_hk_section.write_block_to_file(block_num, header, converted)
        
    elif block_type == BlockType.PAY_HK:
        num_fields = len(PAY_HK_MAPPING)
        converted = [0 for i in range(num_fields)]
        converted[0]    = hum_raw_data_to_humidity(fields[0])
        converted[1]    = pres_raw_data_to_pressure(fields[1])
        converted[2]    = adc_raw_data_to_therm_temp(fields[2])
        converted[3]    = adc_raw_data_to_therm_temp(fields[3])
        converted[4]    = adc_raw_data_to_therm_temp(fields[4])
        converted[5]    = adc_raw_data_to_therm_temp(fields[5])
        converted[6]    = adc_raw_data_to_therm_temp(fields[6])
        converted[7]    = adc_raw_data_to_therm_temp(fields[7])
        converted[8]    = adc_raw_data_to_therm_temp(fields[8])
        converted[9]    = adc_raw_data_to_therm_temp(fields[9])
        converted[10]   = adc_raw_data_to_therm_temp(fields[10])
        converted[11]   = adc_raw_data_to_therm_temp(fields[11])
        converted[12]   = adc_raw_data_to_therm_temp(fields[12])
        converted[13]   = adc_raw_data_to_therm_temp(fields[13])
        converted[14]   = adc_raw_data_to_therm_temp(fields[14])
        converted[15]   = adc_raw_data_to_therm_temp(fields[15])
        converted[16]   = adc_raw_data_to_therm_temp(fields[16])
        converted[17]   = adc_raw_data_to_therm_temp(fields[17])
        converted[18]   = adc_raw_data_to_therm_temp(fields[18])
        converted[19]   = enable_states_to_str(fields[19], 5)
        converted[20]   = enable_states_to_str(fields[20], 4)
        converted[21]   = fields[21]
        converted[22]   = fields[22]
        converted[23]   = "0x%.2x (%s)" % (fields[23], restart_reason_to_str(fields[23])) # Represent as string

        # Print to screen
        pay_hk_section.print_fields(fields, converted)
        # Write to file
        pay_hk_section.write_block_to_file(block_num, header, converted)

    elif block_type == BlockType.PAY_OPT:
        num_fields = len(PAY_OPT_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = opt_adc_raw_data_to_vol(fields[i], 1)
        
        # Print to screen
        pay_opt_section.print_fields(fields, converted)
        # Write to file
        pay_opt_section.write_block_to_file(block_num, header, converted)

def process_cmd_block(packet):
    print("Expected starting block number:", packet.arg1)
    print("Expected block count:", packet.arg2)
    assert len(packet.data) % 19 == 0

    count = len(packet.data) // 19
    print("%d blocks" % count)
    for i in range(count):
        block_data = packet.data[i * 19 : (i + 1) * 19]

        header = block_data[0:10]
        opcode = block_data[10]
        arg1 = bytes_to_uint32(block_data[11:15])
        arg2 = bytes_to_uint32(block_data[15:19])

        # Get command name string for opcode
        matches = [command for command in g_all_commands if command.opcode == opcode]
        if len(matches) > 0:
            opcode_str = matches[0].name
        else:
            opcode_str = "UNKNOWN"
        converted = ["0x%.2x (%s)" % (opcode, opcode_str), arg1, arg2]

        print_div()
        print_header(header)
        print("Opcode = 0x%x (%d)" % (opcode, opcode))
        print("Argument 1 = 0x%x (%d)" % (arg1, arg1))
        print("Argument 2 = 0x%x (%d)" % (arg2, arg2))

        if packet.opcode == CommandOpcode.READ_PRIM_CMD_BLOCKS:
            prim_cmd_log_section.write_block_to_file(packet.arg1 + i, header, converted)
        elif packet.opcode == CommandOpcode.READ_SEC_CMD_BLOCKS:
            sec_cmd_log_section.write_block_to_file(packet.arg1 + i, header, converted)
        else:
            sys.exit(1)

        



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


def read_all_missing_blocks():
    get_sat_block_nums()
    print_sections()

    print("Reading all missing blocks...")
    for i, section in enumerate(g_all_sections):
        for block_num in range(section.file_block_num, section.sat_block_num):
            print("Reading block #", block_num)
            if not send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, i + 1, block_num):
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
