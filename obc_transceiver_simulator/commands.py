import sys

from command_utilities import *
from command_utilities import send_and_receive_packet   # TODO - figure out why this needs to be done separately
from common import *
from constants import *
from conversions import *
from packets import *


class Command(object):
    def __init__(self):
        self.name = "UNKNOWN"
        self.opcode = 0xFF
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)


class PingOBC(Command):
    def __init__(self):
        super().__init__()
        self.name = "Ping OBC"
        self.opcode = CommandOpcode.PING_OBC

    def run_tx(self):
        send_and_receive_packet(self.opcode, 0, 0)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class GetRTC(Command):
    def __init__(self):
        self.name = "Get RTC"
        self.opcode = CommandOpcode.GET_RTC

    def run_tx(self):
        send_and_receive_packet(self.opcode, 0, 0)
    
    def run_rx(self, packet):
        print("Date =", date_time_to_str(packet.data[0:3]))
        print("Time =", date_time_to_str(packet.data[3:6]))


class SetRTC(object):
    def __init__(self):
        self.name = "Set RTC"
        self.opcode = CommandOpcode.SET_RTC
    
    def run_tx(self):
        year = input_int("Enter year: ")
        month = input_int("Enter month: ")
        day = input_int("Enter day: ")
        arg1 = bytes_to_uint24([year, month, day])

        hour = input_int("Enter hours: ")
        minute = input_int("Enter minutes: ")
        second = input_int("Enter seconds: ")
        arg2 = bytes_to_uint24([hour, minute, second])

        send_and_receive_packet(CommandOpcode.SET_RTC, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class ReadOBCEEPROM(object):
    def __init__(self):
        self.name = "Read OBC EEPROM"
        self.opcode = CommandOpcode.READ_OBC_EEPROM
    
    def run_tx(self):
        addr = input_int("Enter address: ")
        send_and_receive_packet(CommandOpcode.READ_OBC_EEPROM, addr, 0)

    # packet must be an RXPacket
    def run_rx(self, packet):
        print("Value: 0x%.8x" % bytes_to_uint32(packet.data[0:4]))


class EraseOBCEEPROM(object):
    def __init__(self):
        self.name = "Erase OBC EEPROM"
        self.opcode = CommandOpcode.ERASE_OBC_EEPROM
    
    def run_tx(self):
        addr = input_int("Enter address: ")
        send_and_receive_packet(CommandOpcode.ERASE_OBC_EEPROM, addr, 0)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class ReadOBCRAMByte(object):
    def __init__(self):
        self.name = "Read OBC RAM Byte"
        self.opcode = CommandOpcode.READ_OBC_RAM_BYTE
    
    def run_tx(self):
        addr = input_int("Enter address: ")
        send_and_receive_packet(CommandOpcode.READ_OBC_RAM_BYTE, addr, 0)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        print("Value is 0x%.2x" % packet.data[0])


class SetIndefBeaconEnable(object):
    def __init__(self):
        self.name = "Set Indefinite Beacon Enable"
        self.opcode = CommandOpcode.SET_INDEF_BEACON_ENABLE
    
    def run_tx(self):
        number = input_int("Enter enable number (1 or 2): ")
        setting = input_int("Enter setting (0 = disable, 1 = enable): ")
        send_and_receive_packet(self.opcode, number, setting)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        tx_packet = tx_packet_for_rx_packet(packet)
        if tx_packet is not None:
            print("Set indefinite beacon enable %d to %s" % (tx_packet.arg1, "Enabled" if tx_packet.arg2 else "Disabled"))


class ReadDataBlock(object):
    def __init__(self):
        self.name = "Read Data Block"
        self.opcode = CommandOpcode.READ_DATA_BLOCK
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Enter block number: ")
        send_and_receive_packet(self.opcode, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        process_data_block(packet)


class ReadPrimaryCommandBlocks(object):
    def __init__(self):
        self.name = "Read Primary Command Blocks"
        self.opcode = CommandOpcode.READ_PRIM_CMD_BLOCKS
    
    def run_tx(self):
        arg1 = input_int("Enter starting block number: ")
        arg2 = input_int("Enter number of blocks: ")
        send_and_receive_packet(CommandOpcode.READ_PRIM_CMD_BLOCKS, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        process_cmd_block(packet)


class ReadSecondaryCommandBlocks(object):
    def __init__(self):
        self.name = "Read Secondary Command Blocks"
        self.opcode = CommandOpcode.READ_SEC_CMD_BLOCKS
    
    def run_tx(self):
        arg1 = input_int("Enter starting block number: ")
        arg2 = input_int("Enter number of blocks: ")
        send_and_receive_packet(CommandOpcode.READ_SEC_CMD_BLOCKS, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        process_cmd_block(packet)


class ReadRecentStatusInfo(object):
    def __init__(self):
        self.name = "Read Recent Status Info"
        self.opcode = CommandOpcode.READ_REC_STATUS_INFO
    
    def run_tx(self):
        send_and_receive_packet(CommandOpcode.READ_REC_STATUS_INFO)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        print("OBC data: ", bytes_to_string(packet.data[0:15]))
        print("EPS data: ", bytes_to_string(packet.data[15:24]))
        print("PAY data: ", bytes_to_string(packet.data[24:33]))


class ReadRecentLocalDataBlock(object):
    def __init__(self):
        self.name = "Read Recent Local Data Block"
        self.opcode = CommandOpcode.READ_REC_LOC_DATA_BLOCK
    
    def run_tx(self):
        arg1 = input_block_type()
        send_and_receive_packet(CommandOpcode.READ_REC_LOC_DATA_BLOCK, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        process_data_block(packet)


class ReadRawMemoryBytes(object):
    def __init__(self):
        self.name = "Read Raw Memory Bytes"
        self.opcode = CommandOpcode.READ_RAW_MEM_BYTES
    
    def run_tx(self):
        arg1 = input_int("Enter starting address: ")
        arg2 = input_int("Enter number of bytes: ")
        send_and_receive_packet(CommandOpcode.READ_RAW_MEM_BYTES, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        print("Data = %s" % bytes_to_string(packet.data))


class CollectDataBlock(object):
    def __init__(self):
        self.name = "Collect Data Block"
        self.opcode = CommandOpcode.COL_DATA_BLOCK
    
    def run_tx(self):
        arg1 = input_block_type()
        # Needs longer wait time for CAN messages to be sent back and forth
        send_and_receive_packet(CommandOpcode.COL_DATA_BLOCK, arg1, wait_time=45)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        # TODO - subtract one somewhere? probably on OBC?
        # Only check data if we received any (OK status)
        if len(packet.data) > 0:
            print("Collected block number %d" % bytes_to_uint32(packet.data[0:4]))


class GetAutoDataCollectionSettings(object):
    def __init__(self):
        self.name = "Get Auto Data Collection Settings"
        self.opcode = CommandOpcode.GET_AUTO_DATA_COL_SETTINGS
    
    def run_tx(self):
        send_and_receive_packet(self.opcode)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        assert len(packet.data) == 40

        print("Current uptime = %ds" % (bytes_to_uint32(packet.data[0:4])))

        for i, section in enumerate(g_all_col_data_sections):
            data = packet.data[4 + (i * 9) : 4 + ((i+1) * 9)]
            enabled_str = "enabled" if data[0] else "disabled"
            period = bytes_to_uint32(data[1:5])
            count = bytes_to_uint32(data[5:9])
            print("%s: %s, period = %ds, last_uptime = %ds" % (section.name, enabled_str, period, count))


class SetAutoDataCollectionEnable(object):
    def __init__(self):
        self.name = "Set Auto Data Collection Enable"
        self.opcode = CommandOpcode.SET_AUTO_DATA_COL_ENABLE
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Disable (0) or Enable (1): ")
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_ENABLE, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        tx_packet = tx_packet_for_rx_packet(packet)
        if tx_packet is not None:
            print("%s - %s" % (section_num_to_str(tx_packet.arg1), "enabled" if tx_packet.arg2 else "disabled"))


class SetAutoDataCollectionPeriod(object):
    def __init__(self):
        self.name = "Set Auto Data Collection Period"
        self.opcode = CommandOpcode.SET_AUTO_DATA_COL_PERIOD
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Enter period in seconds: ")
        send_and_receive_packet(CommandOpcode.SET_AUTO_DATA_COL_PERIOD, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        tx_packet = tx_packet_for_rx_packet(packet)
        if tx_packet is not None:
            print("%s - %d seconds" % (section_num_to_str(tx_packet.arg1), tx_packet.arg2))


class ResyncAutoDataCollectionTimers(object):
    def __init__(self):
        self.name = "Resync Auto Data Collection Timers"
        self.opcode = CommandOpcode.RESYNC_AUTO_DATA_COL_TIMERS
    
    def run_tx(self):
        send_and_receive_packet(CommandOpcode.RESYNC_AUTO_DATA_COL_TIMERS)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class GetCurrentBlockNumbers(object):
    def __init__(self):
        self.name = "Get Current Block Numbers"
        self.opcode = CommandOpcode.GET_CUR_BLOCK_NUMS
    
    def run_tx(self):
        send_and_receive_packet(self.opcode)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        obc_hk   = bytes_to_uint32(packet.data[0:4])
        eps_hk   = bytes_to_uint32(packet.data[4:8])
        pay_hk   = bytes_to_uint32(packet.data[8:12])
        pay_opt  = bytes_to_uint32(packet.data[12:16])
        prim_cmd = bytes_to_uint32(packet.data[16:20])
        sec_cmd  = bytes_to_uint32(packet.data[20:24])

        print("Current block numbers:")
        print("OBC_HK: 0x%x (%d)" % (obc_hk, obc_hk))
        print("EPS_HK: 0x%x (%d)" % (eps_hk, eps_hk))
        print("PAY_HK: 0x%x (%d)" % (pay_hk, pay_hk))
        print("PAY_OPT: 0x%x (%d)" % (pay_opt, pay_opt))
        print("PRIM_CMD_LOG: 0x%x (%d)" % (prim_cmd, prim_cmd))
        print("SEC_CMD_LOG: 0x%x (%d)" % (sec_cmd, sec_cmd))

        obc_hk_section.sat_block_num = obc_hk
        eps_hk_section.sat_block_num = eps_hk
        pay_hk_section.sat_block_num = pay_hk
        pay_opt_section.sat_block_num = pay_opt
        prim_cmd_log_section.sat_block_num = prim_cmd
        sec_cmd_log_section.sat_block_num = sec_cmd


class SetCurrentBlockNumber(object):
    def __init__(self):
        self.name = "Set Current Block Number"
        self.opcode = CommandOpcode.SET_CUR_BLOCK_NUM
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Enter block number: ")
        send_and_receive_packet(CommandOpcode.SET_CUR_BLOCK_NUM, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class GetMemorySectionAddrs(object):
    def __init__(self):
        self.name = "Get Memory Section Addresses"
        self.opcode = CommandOpcode.GET_MEM_SEC_ADDRS
    
    def run_tx(self):
        send_and_receive_packet(self.opcode)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        for i, section in enumerate(g_all_col_sections):
            data = packet.data[i * 8 : (i+1) * 8]
            start = bytes_to_uint32(data[0:4])
            end = bytes_to_uint32(data[4:8])
            print("%s: start = 0x%x, end = 0x%x" % (section.name, start, end))


class SetMemorySectionStartAddr(object):
    def __init__(self):
        self.name = "Set Memory Section Start Address"
        self.opcode = CommandOpcode.SET_MEM_SEC_START_ADDR
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Enter start address: ")
        send_and_receive_packet(CommandOpcode.SET_MEM_SEC_START_ADDR, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class SetMemorySectionEndAddr(object):
    def __init__(self):
        self.name = "Set Memory Section End Address"
        self.opcode = CommandOpcode.SET_MEM_SEC_END_ADDR
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Enter end address: ")
        send_and_receive_packet(CommandOpcode.SET_MEM_SEC_END_ADDR, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class EraseMemoryPhysicalSector(object):
    def __init__(self):
        self.name = "Erase Memory Physical Sector"
        self.opcode = CommandOpcode.ERASE_MEM_PHY_SECTOR
    
    def run_tx(self):
        arg1 = input_int("Enter address: ")
        send_and_receive_packet(CommandOpcode.ERASE_MEM_PHY_SECTOR, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class EraseMemoryPhysicalBlock(object):
    def __init__(self):
        self.name = "Erase Memory Physical Block"
        self.opcode = CommandOpcode.ERASE_MEM_PHY_BLOCK
    
    def run_tx(self):
        arg1 = input_int("Enter address: ")
        send_and_receive_packet(CommandOpcode.ERASE_MEM_PHY_BLOCK, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class EraseAllMemory(object):
    def __init__(self):
        self.name = "Erase All Memory"
        self.opcode = CommandOpcode.ERASE_ALL_MEM
    
    def run_tx(self):
        resp = input("ARE YOU SURE? Type 'yes' to confirm, or Enter to cancel: ")
        if resp == "yes":
            send_and_receive_packet(CommandOpcode.ERASE_ALL_MEM)
            print("Confirmed")
        else:
            print("Cancelled")
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass


class SendEPSCANMessage(object):
    def __init__(self):
        self.name = "Send EPS CAN Message"
        self.opcode = CommandOpcode.SEND_EPS_CAN_MSG
    
    def run_tx(self):
        print("a. Arbitrary values")
        print("b. Arbitrary bytes")

        # Enum to all ints: https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class/29503414
        for field in list(map(int, EPS_CTRL)):
            print("%d. %s" % (field, eps_ctrl_field_num_to_str(field)))

        cmd = input("Enter command number: ")

        if cmd == "a":
            opcode = input_int("Enter opcode: ")
            field_num = input_int("Enter field number: ")
            tx_data = input_int("Enter data: ")
            send_and_receive_eps_can(opcode, field_num, tx_data)
            return

        if cmd == "b":
            b = string_to_bytes(input("Enter 8 bytes: "))
            send_and_receive_packet(CommandOpcode.SEND_EPS_CAN_MSG, bytes_to_uint32(b[0:4]), bytes_to_uint32(b[4:8]))
            return

        field_num = str_to_int(cmd)
        # Can be overriden depending on the command
        tx_data = 0

        if field_num == EPS_CTRL.READ_EEPROM:
            tx_data = input_int("Enter address: ")
        
        elif field_num == EPS_CTRL.ERASE_EEPROM:
            tx_data = input_int("Enter address: ")
        
        elif field_num == EPS_CTRL.READ_RAM_BYTE:
            tx_data = input_int("Enter address: ")

        elif field_num == EPS_CTRL.SET_HEAT_1_SHAD_SP:
            tx_data = heater_setpoint_to_dac_raw_data(
                input("Enter temperature in C:"))
        
        elif field_num == EPS_CTRL.SET_HEAT_2_SHAD_SP:
            tx_data = heater_setpoint_to_dac_raw_data(
                input("Enter temperature in C:"))
        
        elif field_num == EPS_CTRL.SET_HEAT_1_SUN_SP:
            tx_data = heater_setpoint_to_dac_raw_data(
                input("Enter temperature in C:"))
        
        elif field_num == EPS_CTRL.SET_HEAT_2_SUN_SP:
            tx_data = heater_setpoint_to_dac_raw_data(
                input("Enter temperature in C:"))
        
        elif field_num == EPS_CTRL.SET_HEAT_LOWER_CUR_THR:
            tx_data = adc_circ_cur_to_raw(input("Enter current in A:"), EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        
        elif field_num == EPS_CTRL.SET_HEAT_UPPER_CUR_THR:
            tx_data = adc_circ_cur_to_raw(input("Enter current in A:"), EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF)
        
        send_and_receive_eps_can(CAN.EPS_CTRL, field_num, tx_data)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        opcode = packet.data[0]
        field_num = packet.data[1]
        status = packet.data[2]
        rx_data = bytes_to_uint32(packet.data[4:8])
        print("Opcode =", opcode, ", Field =", field_num, ", Status =", status, "(", packet_resp_status_to_str(status), "), Data = ", bytes_to_string(uint32_to_bytes(rx_data)))

        if opcode == CAN.EPS_CTRL:
            if field_num == EPS_CTRL.READ_EEPROM:
                print("Value is 0x%x" % rx_data)
            
            elif field_num == EPS_CTRL.READ_RAM_BYTE:
                print("Value is 0x%x" % rx_data)

            elif field_num == EPS_CTRL.GET_HEAT_SHAD_SP:
                sp1 = (rx_data >> 16) & 0xFFFF
                sp2 = rx_data & 0xFFFF
                print("Heater 1 setpoint: %f C" % dac_raw_data_to_heater_setpoint(sp1))
                print("Heater 2 setpoint: %f C" % dac_raw_data_to_heater_setpoint(sp2))
            
            elif field_num == EPS_CTRL.GET_HEAT_SUN_SP:
                sp1 = (rx_data >> 16) & 0xFFFF
                sp2 = rx_data & 0xFFFF
                print("Heater 1 setpoint: %f C" % dac_raw_data_to_heater_setpoint(sp1))
                print("Heater 2 setpoint: %f C" % dac_raw_data_to_heater_setpoint(sp2))
            
            elif field_num == EPS_CTRL.GET_HEAT_CUR_THR:
                lower = (rx_data >> 16) & 0xFFFF
                upper = rx_data & 0xFFFF
                print("Lower threshold: %f A" % adc_raw_to_circ_cur(lower,
                    EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF))
                print("Upper threshold: %f A" % adc_raw_to_circ_cur(upper,
                    EPS_ADC_DEF_CUR_SENSE_RES, EPS_ADC_DEF_CUR_SENSE_VREF))


class SendPAYCANMessage(object):
    def __init__(self):
        self.name = "Send PAY CAN Message"
        self.opcode = CommandOpcode.SEND_PAY_CAN_MSG
    
    def run_tx(self):
        print("a. Arbitrary values")
        print("b. Arbitrary bytes")

        # Enum to all ints: https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class/29503414
        for field in list(map(int, PAY_CTRL)):
            print("%d. %s" % (field, pay_ctrl_field_num_to_str(field)))

        cmd = input("Enter command number: ")

        if cmd == "a":
            opcode = input_int("Enter opcode: ")
            field_num = input_int("Enter field number: ")
            tx_data = input_int("Enter data: ")
            send_and_receive_pay_can(opcode, field_num, tx_data)
            return

        if cmd == "b":
            b = string_to_bytes(input("Enter 8 bytes: "))
            send_and_receive_packet(CommandOpcode.SEND_PAY_CAN_MSG, bytes_to_uint32(b[0:4]), bytes_to_uint32(b[4:8]))
            return

        field_num = str_to_int(cmd)
        tx_data = 0

        if field_num == PAY_CTRL.READ_EEPROM:
            tx_data = input_int("Enter address: ")
        
        elif field_num == PAY_CTRL.ERASE_EEPROM:
            tx_data = input_int("Enter address: ")
        
        elif field_num == PAY_CTRL.READ_RAM_BYTE:
            tx_data = input_int("Enter address: ")
        
        elif field_num == PAY_CTRL.SET_HEAT_SP:
            tx_data = input_int("Enter address: ")

        elif field_num == PAY_CTRL.SET_INV_THERM_READING:
            tx_data = input_int("Enter address: ")

        elif field_num == PAY_CTRL.SET_THERM_ERR_CODE:
            tx_data = input_int("Enter address: ")

        elif field_num == PAY_CTRL.SEND_OPT_SPI:
            tx_data = input_int("Enter address: ")

        send_and_receive_pay_can(CAN.PAY_CTRL, field_num, tx_data)

    # packet must be an RXPacket
    def run_rx(self, packet):
        tx_packet = tx_packet_for_rx_packet(packet)

        opcode = packet.data[0]
        field_num = packet.data[1]
        status = packet.data[2]
        rx_data = packet.data[4:8]
        print("Opcode =", opcode, ", Field =", field_num, ", Status =", status, ", Data = ", bytes_to_string(rx_data))
        print(pay_ctrl_field_num_to_str(field_num))

        if opcode == CAN.PAY_CTRL:
            if field_num == PAY_CTRL.READ_EEPROM:
                print("Value is 0x%x" % rx_data)
            
            elif field_num == PAY_CTRL.READ_RAM_BYTE:
                print("Value is 0x%x" % rx_data)

            elif field_num == PAY_CTRL.GET_HEAT_PARAMS:
                setpoint = (rx_data >> 16) & 0xFFFF
                inv_therm_reading = rx_data & 0xFFFF
                print("Heater setpoint: %f C" % dac_raw_data_to_heater_setpoint(setpoint))
                print("Invalid thermistor reading: %f C" % adc_raw_to_therm_temp(inv_therm_reading))

            elif field_num == PAY_CTRL.GET_THERM_READING:
                zero = (rx_data >> 16) & 0xFFFF
                one = rx_data & 0xFFFF
                print("(n+0) reading: %f C" % adc_raw_to_therm_temp(zero))
                print("(n+1) reading: %f C" % adc_raw_to_therm_temp(one))

            elif field_num == PAY_CTRL.GET_THERM_ERR_CODE:
                zero = (rx_data >> 24) & 0xFFFF
                one = (rx_data >> 16) & 0xFFFF
                two = (rx_data >> 8) & 0xFFFF
                three = rx_data & 0xFFFF

                print("(n+0) code: 0x%x (%s) C" % (zero, pay_therm_err_code_to_str(zero)))
                print("(n+1) code: 0x%x (%s) C" % (one, pay_therm_err_code_to_str(one)))
                print("(n+2) code: 0x%x (%s) C" % (two, pay_therm_err_code_to_str(two)))
                print("(n+3) code: 0x%x (%s) C" % (three, pay_therm_err_code_to_str(three)))

            elif field_num == PAY_CTRL.GET_MOTOR_STATUS:
                fault2 = (rx_data >> 31) & 0x01
                fault1 = (rx_data >> 30) & 0x01
                lim2 = (rx_data >> 29) & 0x01
                lim1 = (rx_data >> 28) & 0x01
                last_exec_time = (rx_data >> 8) & 0xFFFFF
                motor_status = rx_data & 0xFF

                # TODO
            
            elif field_num == PAY_CTRL.SEND_OPT_SPI:
                spi_opcode = (tx_packet.arg2 >> 8) & 0xFF
                spi_field = tx_packet.arg2 & 0xFF
                print("Opcode:", spi_opcode)
                print("Field:", spi_field)
                print(pay_opt_spi_opcode_to_str(spi_opcode))

                print("Response data: 0x%x" % rx_data)

                # Print power data
                if spi_opcode == PAYOptSPIOpcode.GET_POWER:
                    (voltage, current, power) = opt_power_raw_to_conv(rx_data)
                    print("%f V, %f A, %f W" % (voltage, current, power))


class ResetSubsystem(object):
    def __init__(self):
        self.name = "Reset Subsystem"
        self.opcode = CommandOpcode.RESET_SUBSYS
    
    def run_tx(self):
        arg1 = input_subsys()
        if arg1 == Subsystem.OBC:
            # don't wait for response if it's OBC
            send_tx_packet(TXPacket(Global.cmd_id, self.opcode, arg1, 0))
        else:
            send_and_receive_packet(self.opcode, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass




g_all_commands = [
    PingOBC(),
    GetRTC(),
    SetRTC(),
    ReadOBCEEPROM(),
    EraseOBCEEPROM(),
    ReadOBCRAMByte(),
    SetIndefBeaconEnable(),

    ReadDataBlock(),
    ReadPrimaryCommandBlocks(),
    ReadSecondaryCommandBlocks(),
    ReadRecentStatusInfo(),
    ReadRecentLocalDataBlock(),
    ReadRawMemoryBytes(),

    CollectDataBlock(),
    GetAutoDataCollectionSettings(),
    SetAutoDataCollectionEnable(),
    SetAutoDataCollectionPeriod(),
    ResyncAutoDataCollectionTimers(),

    GetCurrentBlockNumbers(),
    SetCurrentBlockNumber(),
    GetMemorySectionAddrs(),
    SetMemorySectionStartAddr(),
    SetMemorySectionEndAddr(),
    EraseMemoryPhysicalSector(),
    EraseMemoryPhysicalBlock(),
    EraseAllMemory(),

    SendEPSCANMessage(),
    SendPAYCANMessage(),
    ResetSubsystem(),
]

g_command_groups = [
    (0, "General OBC Functions"),
    (1, "Read Data"),
    (2, "Data Collection"),
    (3, "Memory Management"),
    (4, "Inter-Subsystem Commands"),
]
