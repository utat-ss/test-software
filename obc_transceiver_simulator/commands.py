import sys

from command_utilities import *
from command_utilities import send_and_receive_packet   # TODO - figure out why this needs to be done separately
from common import *
from constants import *
from packets import *


class Command(object):
    # TODO - better way?
    serial = None

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
        pass

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
        pass

class SendEPSCANMessage(object):
    def __init__(self):
        self.name = "Send EPS CAN Message"
        self.opcode = CommandOpcode.SEND_EPS_CAN_MSG
    
    def run_tx(self):
        print("0. Ping")
        print("14. Read EEPROM")
        print("15. Erase EEPROM")
        cmd = input_int("Enter command number: ")
        
        if cmd == 0:
            send_and_receive_eps_can(CAN.EPS_CTRL, EPS_CTRL.PING)

        elif cmd == 14:
            send_and_receive_eps_can(CAN.EPS_CTRL, EPS_CTRL.READ_EEPROM)

        elif cmd == 15:
            send_and_receive_pay_can(CAN.PAY_CTRL, PAY_CTRL.ERASE_EEPROM)

        # TODO
        # elif opcode == CommandOpcode.PING_OBC: #Heater DAC Setpoints
        #     print("1. Set EPS - Shadow Setpoint 1")
        #     print("2. Set EPS - Shadow Setpoint 2")
        #     print("3. Set EPS - Sun Setpoint 1")
        #     print("4. Set EPS - Sun Setpoint 2")
        #     print("5. Set PAY - Setpoint 1")
        #     print("6. Set PAY - Setpoint 2")
        #     next_cmd = input("Enter command number: ")

        #     setpoint = float(input("Enter setpoint (in C): "))
        #     data = dac_vol_to_raw_data(therm_res_to_vol(therm_temp_to_res(setpoint)))

        #     if next_cmd == ("1"):
        #         send_and_receive_eps_can(1, 1, data)
        #     elif next_cmd == ("2"):
        #         send_and_receive_eps_can(1, 2, data)
        #     elif next_cmd == ("3"):
        #         send_and_receive_eps_can(1, 3, data)
        #     elif next_cmd == ("4"):
        #         send_and_receive_eps_can(1, 4, data)
        #     elif next_cmd == ("5"):
        #         send_and_receive_pay_can(4, 1, data)
        #     elif next_cmd == ("6"):
        #         send_and_receive_pay_can(4, 2, data)
        #     else:
        #         print("Invalid command")

        # TODO
        # elif opcode == CommandOpcode.PING_OBC:
        #     print("1. Lower")
        #     print("2. Upper")
        #     next_cmd = input("Enter command number: ")

        #     threshold = float(input("Enter threshold (in A): "))
        #     data = adc_eps_cur_to_raw_data(threshold)

        #     if next_cmd == ("1"):
        #         send_and_receive_eps_can(1, 5, data)
        #     elif next_cmd == ("2"):
        #         send_and_receive_eps_can(1, 6, data)
        #     else:
        #         print("Invalid command")
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        opcode = packet.data[2]
        field_num = packet.data[3]
        rx_data = packet.data[4:8]
        print("Opcode =", opcode, ", Field =", field_num, ", Data = ", bytes_to_string(rx_data))
        
        # EPS CTRL
        if opcode == 1:
            if field_num == 0:
                print("Ping")
            elif field_num == 1:
                print("Battery heater - shadow setpoint 1")
            elif field_num == 2:
                print("Battery heater - shadow setpoint 2")
            elif field_num == 3:
                print("Battery heater - sun setpoint 1")
            elif field_num == 4:
                print("Battery heater - sun setpoint 2")
            elif field_num == 5:
                print("Battery heater mode - lower current threshold")
            elif field_num == 6:
                print("Battery heater mode - upper current threshold")
            elif field_num == 7:
                print("Reset")
            elif field_num == 8:
                print("Read EEPROM")
            elif field_num == 9:
                print("Erase EEPROM")
            elif field_num == 14:
                print("Get restart count")
            elif field_num == 15:
                print("Get restart reason")
            elif field_num == 12:
                print("Get uptime")
            elif field_num == 13:
                print("Start temporary low-power mode")




class SendPAYCANMessage(object):
    def __init__(self):
        self.name = "Send PAY CAN Message"
        self.opcode = CommandOpcode.SEND_PAY_CAN_MSG
    
    def run_tx(self):
        print("0. Ping")
        cmd = input_int("Enter command number: ")

        if cmd == 0:
            send_and_receive_pay_can(CAN.PAY_CTRL, PAY_CTRL.PING)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        opcode = packet.data[2]
        field_num = packet.data[3]
        rx_data = packet.data[4:8]
        print("Opcode =", opcode, ", Field =", field_num, "Data = ", bytes_to_string(rx_data))
        
        # PAY CTRL
        if opcode == 4:
            if field_num == 0:
                print("Ping")
            elif field_num == 1:
                print("MF heater - setpoint 1")
            elif field_num == 2:
                print("MF heater - setpoint 2")
            elif field_num == 3:
                print("Move act plate up")
            elif field_num == 4:
                print("Move act plate down")
            elif field_num == 5:
                print("Reset")
            elif field_num == 6:
                print("Read EEPROM")
            elif field_num == 7:
                print("Erase EEPROM")
            elif field_num == 8:
                print("Get restart count")
            elif field_num == 9:
                print("Get restart reason")
            elif field_num == 10:
                print("Get uptime")
            elif field_num == 11:
                print("Start temporary low-power mode")




class ActuatePAYMotors(object):
    def __init__(self):
        self.name = "Actuate PAY Motors"
        self.opcode = CommandOpcode.ACT_PAY_MOTORS
    
    def run_tx(self):
        print("15. Move plate up")
        print("16. Move plate down")
        print("17. Run deployment sequence")
        arg1 = input_int("Enter command number: ")
        send_and_receive_packet(CommandOpcode.ACT_PAY_MOTORS, arg1, 0)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        pass

class ResetSubsystem(object):
    def __init__(self):
        self.name = "Reset Subsystem"
        self.opcode = CommandOpcode.RESET_SUBSYS
    
    def run_tx(self):
        arg1 = input_subsys()
        if arg1 == Subsystem.OBC:
            # don't wait for response if it's OBC
            send_tx_packet(TXPacket(CommandOpcode.RESET_SUBSYS, arg1, 0))
        else:
            send_and_receive_packet(15, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)

class SetIndefiniteLPMEnable(object):
    def __init__(self):
        self.name = "Set Indefinite LPM Enable"
        self.opcode = CommandOpcode.SET_INDEF_LPM_ENABLE
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)

class ReadRecentStatusInfo(object):
    def __init__(self):
        self.name = "Read Recent Status Info"
        self.opcode = CommandOpcode.READ_REC_STATUS_INFO
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)

class ReadDataBlock(object):
    def __init__(self):
        self.name = "Read Data Block"
        self.opcode = CommandOpcode.READ_DATA_BLOCK
    
    def run_tx(self):
        arg1 = input_block_type()
        arg2 = input_int("Enter block number: ")
        send_and_receive_packet(CommandOpcode.READ_DATA_BLOCK, arg1, arg2)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        process_rx_block(packet.arg1, packet.arg2, packet.data)

        # if type == 0x01:
    #     print("Subsystem status (OBC)")
    #     print("Restart count =", bytes_to_uint32(data[0:4]))
    #     print("Restart date =", date_time_to_str(data[4:7]))
    #     print("Restart time =", date_time_to_str(data[7:10]))
    #     print("Uptime =", bytes_to_uint32(data[10:14]))


def process_rx_block(arg1, arg2, data):
    (header, fields) = parse_data(data)
    print("Expected block number:", arg2)
    print_header(header)

    # if arg1 == 0:
    #     num_fields = len(EPS_HK_MAPPING)
    #     converted = [0 for i in range(num_fields)]
    #     converted[0]    = adc_raw_data_to_eps_vol(fields[0])
    #     converted[1]    = adc_raw_data_to_eps_cur(fields[1])
    #     converted[2]    = adc_raw_data_to_eps_cur(fields[2])
    #     converted[3]    = adc_raw_data_to_eps_cur(fields[3])
    #     converted[4]    = adc_raw_data_to_eps_cur(fields[4])
    #     converted[5]    = adc_raw_data_to_eps_cur(fields[5])
    #     converted[6]    = adc_raw_data_to_therm_temp(fields[6])
    #     converted[7]    = adc_raw_data_to_therm_temp(fields[7])
    #     converted[8]    = adc_raw_data_to_eps_vol(fields[8])
    #     converted[9]    = adc_raw_data_to_bat_cur(fields[9])
    #     converted[10]   = adc_raw_data_to_eps_cur(fields[10])
    #     converted[11]   = adc_raw_data_to_eps_vol(fields[11])
    #     converted[12]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[12])))
    #     converted[13]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[13])))
    #     converted[14]   = imu_raw_data_to_gyro(fields[14])
    #     converted[15]   = imu_raw_data_to_gyro(fields[15])
    #     converted[16]   = imu_raw_data_to_gyro(fields[16])
    #     converted[17]   = imu_raw_data_to_gyro(fields[17])
    #     converted[18]   = imu_raw_data_to_gyro(fields[18])
    #     converted[19]   = imu_raw_data_to_gyro(fields[19])

    #     # Print to screen
    #     eps_hk_section.print_fields(fields, converted)
    #     # Write to file
    #     eps_hk_section.write_block_to_file(arg2, header, converted)
        

    # if arg1 == 1:
    #     num_fields = len(PAY_HK_MAPPING)
    #     converted = [0 for i in range(num_fields)]
    #     converted[0]    = temp_raw_data_to_temperature(fields[0])
    #     converted[1]    = hum_raw_data_to_humidity(fields[1])
    #     converted[2]    = pres_raw_data_to_pressure(fields[2])
    #     converted[3]    = adc_raw_data_to_therm_temp(fields[3])
    #     converted[4]    = adc_raw_data_to_therm_temp(fields[4])
    #     converted[5]    = adc_raw_data_to_therm_temp(fields[5])
    #     converted[6]    = adc_raw_data_to_therm_temp(fields[6])
    #     converted[7]    = adc_raw_data_to_therm_temp(fields[7])
    #     converted[8]    = adc_raw_data_to_therm_temp(fields[8])
    #     converted[9]    = adc_raw_data_to_therm_temp(fields[9])
    #     converted[10]   = adc_raw_data_to_therm_temp(fields[10])
    #     converted[11]   = adc_raw_data_to_therm_temp(fields[11])
    #     converted[12]   = adc_raw_data_to_therm_temp(fields[12])
    #     converted[13]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[13])))
    #     converted[14]   = therm_res_to_temp(therm_vol_to_res(dac_raw_data_to_vol(fields[14])))
    #     converted[15]   = 0
    #     converted[16]   = 0

    #     # Print to screen
    #     pay_hk_section.print_fields(fields, converted)
    #     # Write to file
    #     pay_hk_section.write_block_to_file(arg2, header, converted)

    # if arg1 == 2:
    #     num_fields = len(PAY_OPT_MAPPING)
    #     converted = [0 for i in range(num_fields)]
    #     for i in range(num_fields):
    #         converted[i] = opt_adc_raw_data_to_vol(fields[i], 1)
        
    #     # Print to screen
    #     pay_opt_section.print_fields(fields, converted)
    #     # Write to file
    #     pay_opt_section.write_block_to_file(arg2, header, converted)


    





class ReadRecentLocalDataBlock(object):
    def __init__(self):
        self.name = "Read Recent Local Data Block"
        self.opcode = CommandOpcode.READ_REC_LOC_DATA_BLOCK
    
    def run_tx(self):
        arg1 = input_block_type()
        send_and_receive_packet(CommandOpcode.READ_REC_LOC_DATA_BLOCK, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)
        process_rx_block(packet.arg1, packet.arg2, packet.data)

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
        process_cmd_block(packet.arg1, packet.arg2, packet.data)

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
        process_cmd_block(packet.arg1, packet.arg2, packet.data)

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
        sys.exit(1)


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
        sys.exit(1)


class CollectDataBlock(object):
    def __init__(self):
        self.name = "Collect Data Block"
        self.opcode = CommandOpcode.COL_DATA_BLOCK
    
    def run_tx(self):
        arg1 = input_block_type()
        send_and_receive_packet(CommandOpcode.COL_DATA_BLOCK, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        # TODO - subtract one somewhere? probably on OBC?
        print("Collected block number %d" % bytes_to_uint32(packet.data[0:4]))


class GetCurrentBlockNumber(object):
    def __init__(self):
        self.name = "Get Current Block Number"
        self.opcode = CommandOpcode.GET_CUR_BLOCK_NUM
    
    def run_tx(self):
        arg1 = input_block_type()
        send_and_receive_packet(CommandOpcode.GET_CUR_BLOCK_NUM, arg1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        print(section_num_to_str(packet.arg1))
        block_num = bytes_to_uint32(packet.data[0:4])
        print("Block number = %d" % block_num)

        if packet.arg1 == 0:
            #global eps_hk_sat_block_num
            eps_hk_section.sat_block_num = block_num
        if packet.arg1 == 1:
            #global pay_hk_sat_block_num
            pay_hk_section.sat_block_num = block_num
        if packet.arg1 == 2:
            #global pay_opt_sat_block_num
            pay_opt_section.sat_block_num = block_num


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
        sys.exit(1)


class GetMemorySectionStartAddr(object):
    def __init__(self):
        self.name = "Get Memory Section Start Address"
        self.opcode = CommandOpcode.GET_MEM_SEC_START_ADDR
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)


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
        sys.exit(1)


class GetMemorySectionEndAddr(object):
    def __init__(self):
        self.name = "Get Memory Section End Address"
        self.opcode = CommandOpcode.GET_MEM_SEC_END_ADDR
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)


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
        sys.exit(1)


class GetAutoDataCollectionEnable(object):
    def __init__(self):
        self.name = "Get Auto Data Collection Enable"
        self.opcode = CommandOpcode.GET_AUTO_DATA_COL_ENABLE
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)



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
        print("%s - %s" % (section_num_to_str(packet.arg1), "enabled" if packet.arg2 else "disabled"))



class GetAutoDataCollectionPeriod(object):
    def __init__(self):
        self.name = "Get Auto Data Collection Period"
        self.opcode = CommandOpcode.GET_AUTO_DATA_COL_PERIOD
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)



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
        print("%s - %d seconds" % (section_num_to_str(packet.arg1), packet.arg2))



class GetAutoDataCollectionTimers(object):
    def __init__(self):
        self.name = "Get Auto Data Collection Timers"
        self.opcode = CommandOpcode.GET_AUTO_DATA_COL_TIMERS
    
    def run_tx(self):
        sys.exit(1)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)



class ResyncAutoDataCollectionTimers(object):
    def __init__(self):
        self.name = "Resync Auto Data Collection Timers"
        self.opcode = CommandOpcode.RESYNC_AUTO_DATA_COL_TIMERS
    
    def run_tx(self):
        send_and_receive_packet(CommandOpcode.RESYNC_AUTO_DATA_COL_TIMERS)
    
    # packet must be an RXPacket
    def run_rx(self, packet):
        sys.exit(1)




g_all_commands = [
    PingOBC(),
    GetRTC(),
    SetRTC(),
    ReadOBCEEPROM(),
    EraseOBCEEPROM(),
    ReadOBCRAMByte(),
    SendEPSCANMessage(),
    SendPAYCANMessage(),
    ActuatePAYMotors(),
    ResetSubsystem(),
    SetIndefiniteLPMEnable(),
    ReadRecentStatusInfo(),
    ReadDataBlock(),
    ReadRecentLocalDataBlock(),
    ReadPrimaryCommandBlocks(),
    ReadSecondaryCommandBlocks(),
    ReadRawMemoryBytes(),
    EraseMemoryPhysicalSector(),
    EraseMemoryPhysicalBlock(),
    EraseAllMemory(),
    CollectDataBlock(),
    GetCurrentBlockNumber(),
    SetCurrentBlockNumber(),
    GetMemorySectionStartAddr(),
    SetMemorySectionStartAddr(),
    GetMemorySectionEndAddr(),
    SetMemorySectionEndAddr(),
    GetAutoDataCollectionEnable(),
    SetAutoDataCollectionEnable(),
    GetAutoDataCollectionPeriod(),
    SetAutoDataCollectionPeriod(),
    GetAutoDataCollectionTimers(),
    ResyncAutoDataCollectionTimers(),
]

g_command_groups = [
    (0, "General"),
    (1, "Read Data"),
    (2, "Memory and Data Collection"),
]
