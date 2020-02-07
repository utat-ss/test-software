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

    # Each "converted" value is allowable as either a float, int, or string
    # If float, log with constant number of decimal places

    if block_type == BlockType.OBC_HK:
        num_fields = len(OBC_HK_MAPPING)
        converted = [0 for i in range(num_fields)]

        converted[0x00] = fields[0x00]
        converted[0x01] = fields[0x01]
        converted[0x02] = restart_reason_to_str(fields[0x02]) # Represent as string
        converted[0x03] = date_time_to_str(uint24_to_bytes(fields[0x03]))
        converted[0x04] = date_time_to_str(uint24_to_bytes(fields[0x04]))

        # Print to screen
        obc_hk_section.print_fields(fields, converted)
        # Write to file
        obc_hk_section.write_block_to_file(block_num, header, fields, converted)

    elif block_type == BlockType.EPS_HK:
        num_fields = len(EPS_HK_MAPPING)
        converted = [0 for i in range(num_fields)]

        converted[0x00] = fields[0x00]
        converted[0x01] = fields[0x01]
        converted[0x02] = restart_reason_to_str(fields[0x02]) # Represent as string
        converted[0x03] = adc_raw_to_circ_vol(fields[0x03], EPS_ADC_VOL_SENSE_LOW_RES, EPS_ADC_VOL_SENSE_HIGH_RES)
        converted[0x04] = adc_raw_to_circ_cur(fields[0x04], EPS_ADC_BAT_CUR_SENSE_RES, EPS_ADC_BAT_CUR_SENSE_VREF)
        converted[0x05] = adc_raw_to_circ_cur(fields[0x05], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x06] = adc_raw_to_circ_cur(fields[0x06], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x07] = adc_raw_to_circ_cur(fields[0x07], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x08] = adc_raw_to_circ_cur(fields[0x08], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x09] = adc_raw_to_circ_vol(fields[0x09], EPS_ADC_VOL_SENSE_LOW_RES, EPS_ADC_VOL_SENSE_HIGH_RES)
        converted[0x0A] = adc_raw_to_circ_cur(fields[0x0A], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x0B] = adc_raw_to_circ_vol(fields[0x0B], EPS_ADC_VOL_SENSE_LOW_RES, EPS_ADC_VOL_SENSE_HIGH_RES)
        converted[0x0C] = adc_raw_to_circ_cur(fields[0x0C], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x0D] = adc_raw_to_circ_cur(fields[0x0D], EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        converted[0x0E] = adc_raw_to_therm_temp(fields[0x0E])
        converted[0x0F] = adc_raw_to_therm_temp(fields[0x0F])
        converted[0x10] = adc_raw_to_therm_temp(fields[0x10])
        converted[0x11] = adc_raw_to_therm_temp(fields[0x11])
        converted[0x12] = adc_raw_to_therm_temp(fields[0x12])
        converted[0x13] = dac_raw_data_to_heater_setpoint(fields[0x13])
        converted[0x14] = dac_raw_data_to_heater_setpoint(fields[0x14])
        converted[0x15] = imu_raw_data_to_gyro(fields[0x15])
        converted[0x16] = imu_raw_data_to_gyro(fields[0x16])
        converted[0x17] = imu_raw_data_to_gyro(fields[0x17])
        converted[0x18] = imu_raw_data_to_gyro(fields[0x18])
        converted[0x19] = imu_raw_data_to_gyro(fields[0x19])
        converted[0x1A] = imu_raw_data_to_gyro(fields[0x1A])

        # Print to screen
        eps_hk_section.print_fields(fields, converted)
        # Write to file
        eps_hk_section.write_block_to_file(block_num, header, fields, converted)
        
    elif block_type == BlockType.PAY_HK:
        num_fields = len(PAY_HK_MAPPING)
        converted = [0 for i in range(num_fields)]

        converted[0x00] = fields[0x00]
        converted[0x01] = fields[0x01]
        converted[0x02] = restart_reason_to_str(fields[0x02]) # Represent as string
        converted[0x03] = hum_raw_data_to_humidity(fields[0x03])
        converted[0x04] = pres_raw_data_to_pressure(fields[0x04])
        converted[0x05] = adc_raw_to_therm_temp(fields[0x05])
        converted[0x06] = adc_raw_to_therm_temp(fields[0x06])
        converted[0x07] = adc_raw_to_therm_temp(fields[0x07])
        converted[0x08] = adc_raw_to_therm_temp(fields[0x08])
        converted[0x09] = adc_raw_to_therm_temp(fields[0x09])
        converted[0x0A] = adc_raw_to_therm_temp(fields[0x0A])
        converted[0x0B] = adc_raw_to_therm_temp(fields[0x0B])
        converted[0x0C] = adc_raw_to_therm_temp(fields[0x0C])
        converted[0x0D] = adc_raw_to_therm_temp(fields[0x0D])
        converted[0x0E] = adc_raw_to_therm_temp(fields[0x0E])
        converted[0x0F] = adc_raw_to_therm_temp(fields[0x0F])
        converted[0x10] = adc_raw_to_therm_temp(fields[0x10])
        converted[0x11] = adc_raw_to_therm_temp(fields[0x11])
        converted[0x12] = adc_raw_to_therm_temp(fields[0x12])
        converted[0x13] = adc_raw_to_therm_temp(fields[0x13])
        converted[0x14] = adc_raw_to_therm_temp(fields[0x14])
        converted[0x15] = adc_raw_to_therm_temp(fields[0x15])
        converted[0x16] = dac_raw_data_to_heater_setpoint(fields[0x16])
        converted[0x17] = adc_raw_to_therm_temp(fields[0x17])
        converted[0x18] = enable_states_to_str(fields[0x18], 12)
        converted[0x19] = enable_states_to_str(fields[0x19], 5)
        converted[0x1A] = adc_raw_to_circ_vol(fields[0x1A], PAY_ADC1_BATT_LOW_RES, PAY_ADC1_BATT_HIGH_RES)
        converted[0x1B] = adc_raw_to_circ_vol(fields[0x1B], PAY_ADC1_BOOST6_LOW_RES, PAY_ADC1_BOOST6_HIGH_RES)
        converted[0x1C] = adc_raw_to_circ_cur(fields[0x1C], PAY_ADC1_BOOST6_SENSE_RES, PAY_ADC1_BOOST6_REF_VOL)
        converted[0x1D] = adc_raw_to_circ_vol(fields[0x1D], PAY_ADC1_BOOST10_LOW_RES, PAY_ADC1_BOOST10_HIGH_RES)
        converted[0x1E] = adc_raw_to_circ_cur(fields[0x1E], PAY_ADC1_BOOST10_SENSE_RES, PAY_ADC1_BOOST10_REF_VOL)

        # Print to screen
        pay_hk_section.print_fields(fields, converted)
        # Write to file
        pay_hk_section.write_block_to_file(block_num, header, fields, converted)

    elif block_type == BlockType.PAY_OPT_OD:
        num_fields = len(PAY_OPT_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = opt_raw_to_light_intensity(fields[i])

        # Print to screen
        pay_opt_od_section.print_fields(fields, converted)
        # Write to file
        pay_opt_od_section.write_block_to_file(block_num, header, fields, converted)

        # Keep latest block number consistent
        pay_opt_section.write_block_to_file(block_num, header, fields, converted)

    elif block_type == BlockType.PAY_OPT_FL:
        num_fields = len(PAY_OPT_MAPPING)
        converted = [0 for i in range(num_fields)]
        for i in range(num_fields):
            converted[i] = opt_raw_to_light_intensity(fields[i])

        # Print to screen
        pay_opt_fl_section.print_fields(fields, converted)
        # Write to file
        pay_opt_fl_section.write_block_to_file(block_num, header, fields, converted)

        # Keep latest block number consistent
        pay_opt_section.write_block_to_file(block_num, header, fields, converted)

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
        
        fields = [opcode, arg1, arg2]
        converted = [opcode_str, arg1, arg2]

        print_div()
        print_header(header)
        print("Command ID = 0x%x (%d)" % (cmd_id, cmd_id))
        print("Opcode = 0x%x (%d)" % (opcode, opcode))
        print("Argument 1 = 0x%x (%d)" % (arg1, arg1))
        print("Argument 2 = 0x%x (%d)" % (arg2, arg2))

        if tx_packet.opcode == CommandOpcode.READ_PRIM_CMD_BLOCKS:
            prim_cmd_log_section.write_block_to_file(tx_packet.arg1 + i, header, fields, converted)
        elif tx_packet.opcode == CommandOpcode.READ_SEC_CMD_BLOCKS:
            sec_cmd_log_section.write_block_to_file(tx_packet.arg1 + i, header, fields, converted)
        else:
            sys.exit(1)

        



def send_and_receive_eps_can(opcode, field_num, tx_data=0):
    send_and_receive_packet(CommandOpcode.SEND_EPS_CAN_MSG, (opcode << 24) | (field_num << 16), tx_data)

def send_and_receive_pay_can(opcode, field_num, tx_data=0):
    send_and_receive_packet(CommandOpcode.SEND_PAY_CAN_MSG, (opcode << 24) | (field_num << 16), tx_data)



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
                if not send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, pay_opt_od_section.number, block_num):
                    return
                if not send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, pay_opt_fl_section.number, block_num):
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
        # Read any missed input to flush the buffer
        read_serial()

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
