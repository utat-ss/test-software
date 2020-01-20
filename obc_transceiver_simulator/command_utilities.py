from common import *
from conversions import *
from encoding import *
from packets import *
from sections import *


def process_rx_packet(rx_packet):
    print_div()
    print("RX packet - received %s" % ("ACK" if not rx_packet.is_resp else "response"))

    print("Encoded (%d bytes):" % len(rx_packet.enc_msg), bytes_to_string(rx_packet.enc_msg))
    print("Decoded (%d bytes):" % len(rx_packet.dec_msg), bytes_to_string(rx_packet.dec_msg))

    print("Command ID = 0x%x (%d)" % (rx_packet.command_id, rx_packet.command_id))
    print("Status = 0x%x (%d) - %s" % (rx_packet.status, rx_packet.status, packet_to_status_str(rx_packet)))
    if (len(rx_packet.data) > 0):
        print("Data (%d bytes) = %s" % (len(rx_packet.data), bytes_to_string(rx_packet.data)))
    
    # Look in our history of sent packets to get the TXPacket we had previously
    # sent corresponding to this RXPacket we got back
    tx_packet = tx_packet_for_rx_packet(rx_packet)
    if tx_packet is not None:
        opcode = tx_packet.opcode
        arg1 = tx_packet.arg1
        arg2 = tx_packet.arg2

        # The RXPacket doesn't contain opcode information, so we can only
        # retrieve it by inspecting the previously send packet for that command ID

        # TODO
        from commands import g_all_commands
        global g_all_commands
        matched_cmds = [command for command in g_all_commands if command.opcode == tx_packet.opcode]
        assert len(matched_cmds) <= 1

        if len(matched_cmds) > 0:
            print(matched_cmds[0].name)
        else:		
            print("UNKNOWN OPCODE")

        print("Opcode = 0x%x (%d)" % (opcode, opcode))
        print("Argument 1 = 0x%x (%d)" % (arg1, arg1))		
        print("Argument 2 = 0x%x (%d)" % (arg2, arg2))

        if rx_packet.is_resp and len(matched_cmds) > 0:
            matched_cmds[0].run_rx(rx_packet)

    else:
        print("UNRECOGNIZED COMMAND ID")    

    print_div()

def print_header(header):
    print("Block number = 0x%x (%d)" % (bytes_to_uint24(header[0:3]), bytes_to_uint24(header[0:3])))
    print("Date = %s" % date_time_to_str(header[3:6]))
    print("Time = %s" % date_time_to_str(header[6:9]))
    print("Status = 0x%x (%d)" % (header[9], header[9]))

def process_data_block(rx_packet):
    tx_packet = tx_packet_for_rx_packet(rx_packet)

    # If the status was an error, don't parse
    if len(rx_packet.data) == 0:
        return

    (header, fields) = parse_data(rx_packet.data)

    block_type = tx_packet.arg1
    block_num = tx_packet.arg2
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

    elif block_type == BlockType.PAY_OPT_1:
        num_fields = len(PAY_OPT_1_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = "0x%.6x (%f)" % (fields[i], opt_adc_raw_data_to_vol(fields[i], 1))

        # Print to screen
        pay_opt_1_section.print_fields(fields, converted)
        # Write to file
        pay_opt_1_section.write_block_to_file(block_num, header, converted)

        # Keep latest block number consistent
        pay_opt_section.write_block_to_file(block_num, header, converted)

    elif block_type == BlockType.PAY_OPT_2:
        num_fields = len(PAY_OPT_2_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = "0x%.6x (%f)" % (fields[i], opt_adc_raw_data_to_vol(fields[i], 1))
        
        # Print to screen
        pay_opt_2_section.print_fields(fields, converted)
        # Write to file
        pay_opt_2_section.write_block_to_file(block_num, header, converted)

        # Keep latest block number consistent
        pay_opt_section.write_block_to_file(block_num, header, converted)

def process_cmd_block(rx_packet):
    tx_packet = tx_packet_for_rx_packet(rx_packet)

    print("Expected starting block number:", tx_packet.arg1)
    print("Expected block count:", tx_packet.arg2)

    CMD_BLOCK_LEN = 21  # 10 byte header + 11 byte data
    assert len(rx_packet.data) % CMD_BLOCK_LEN == 0

    count = len(rx_packet.data) // CMD_BLOCK_LEN
    print("%d blocks" % count)
    for i in range(count):
        block_data = rx_packet.data[i * CMD_BLOCK_LEN : (i + 1) * CMD_BLOCK_LEN]

        header = block_data[0:10]
        cmd_id = bytes_to_uint16(block_data[10:12])
        opcode = block_data[12]
        arg1 = bytes_to_uint32(block_data[13:17])
        arg2 = bytes_to_uint32(block_data[17:21])

        # Get command name string for opcode
        matches = [command for command in g_all_commands if command.opcode == opcode]
        if len(matches) > 0:
            opcode_str = matches[0].name
        else:
            opcode_str = "UNKNOWN"
        converted = ["0x%.2x (%s)" % (opcode, opcode_str), arg1, arg2]

        print_div()
        print_header(header)
        print("Command ID = 0x%x (%d)" % (cmd_id, cmd_id))
        print("Opcode = 0x%x (%d)" % (opcode, opcode))
        print("Argument 1 = 0x%x (%d)" % (arg1, arg1))
        print("Argument 2 = 0x%x (%d)" % (arg2, arg2))

        if tx_packet.opcode == CommandOpcode.READ_PRIM_CMD_BLOCKS:
            prim_cmd_log_section.write_block_to_file(tx_packet.arg1 + i, header, converted)
        elif tx_packet.opcode == CommandOpcode.READ_SEC_CMD_BLOCKS:
            sec_cmd_log_section.write_block_to_file(tx_packet.arg1 + i, header, converted)
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
    send_and_receive_packet(CommandOpcode.GET_CUR_BLOCK_NUMS)
    print_sections()


def read_missing_blocks():
    get_sat_block_nums()

    print("Reading all missing blocks...")
    
    for i, section in enumerate(g_all_col_data_sections):
        for block_num in range(section.file_block_num, section.sat_block_num):
            if section == pay_opt_section:
                if not send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, pay_opt_1_section.number, block_num):
                    return
                if not send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, pay_opt_2_section.number, block_num):
                    return
            else:
                if not send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, section.number, block_num):
                    return

    # Can read up to 5 at a time
    for block_num in range(prim_cmd_log_section.file_block_num, prim_cmd_log_section.sat_block_num, 5):
        if not send_and_receive_packet(CommandOpcode.READ_PRIM_CMD_BLOCKS, block_num,
                min(prim_cmd_log_section.sat_block_num - prim_cmd_log_section.file_block_num, 5)):
            return
    

def read_missing_sec_cmd_log_blocks():
    get_sat_block_nums()
    print_sections()

    # Can read up to 5 at a time
    for block_num in range(sec_cmd_log_section.file_block_num, sec_cmd_log_section.sat_block_num, 5):
        if not send_and_receive_packet(CommandOpcode.READ_SEC_CMD_BLOCKS, block_num,
                min(sec_cmd_log_section.sat_block_num - sec_cmd_log_section.file_block_num, 5)):
            return

# Can't use cmd_id=Global.cmd_id directly in the function signature, because the
# default value is bound when the method is created
# https://stackoverflow.com/questions/6689652/using-global-variable-as-default-parameter
# wait_time is in seconds
def send_and_receive_packet(opcode, arg1=0, arg2=0, cmd_id=None, wait_time=5, attempts=3):
    if cmd_id is None:
        cmd_id = Global.cmd_id
    for i in range(attempts):
        # TODO - receive previous characters and discard before sending?
        send_tx_packet(TXPacket(cmd_id, opcode, arg1, arg2))

        ack_packet = receive_rx_packet(wait_time)
    
        # If we didn't receive an ACK packet, send the request again
        if ack_packet is None:
            continue
        
        # Still make sure to process/print it first to see the result
        process_rx_packet(ack_packet)
        # If the ACK packet has a failed status code, it's an invalid packet and
        # sending it again would produce the same result, so stop attempting
        # TODO constants
        # TODO - maybe an exception for full command queue?
        if ack_packet.status > 0x01:
            break
        
        # If we are not requesting OBC to reset its command ID, check for a
        # response packet
        if cmd_id > 0:
            # Try to receive the response packet if we can, but this might fail
            resp_packet = receive_rx_packet(wait_time)
            if resp_packet is not None:
                process_rx_packet(resp_packet)

        # At least got a successful ACK, so consider that a success
        Global.cmd_id += 1

        # When viewing the serial files with `tail`, it doesn't show the most
        # recent block from serial_read.log unless something is added to the
        # serial_write.log file
        # Write dummy data to force it to display the rest of serial_read.log
        Global.serial_write_file.write("\n")
        Global.serial_write_file.flush()

        return True

    Global.cmd_id += 1

    # Write dummy data to force it to display the rest of serial_read.log
    Global.serial_write_file.write("\n")
    Global.serial_write_file.flush()

    return False
