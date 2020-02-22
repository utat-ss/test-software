from enum import IntEnum

class CommandOpcode(IntEnum):
    PING_OBC                    = 0x00
    GET_RTC                     = 0x01
    SET_RTC                     = 0x02
    READ_OBC_EEPROM             = 0x03
    ERASE_OBC_EEPROM            = 0x04
    READ_OBC_RAM_BYTE           = 0x05
    SET_INDEF_BEACON_ENABLE     = 0x06
    READ_DATA_BLOCK             = 0x10
    READ_PRIM_CMD_BLOCKS        = 0x11
    READ_SEC_CMD_BLOCKS         = 0x12
    READ_REC_STATUS_INFO        = 0x13
    READ_REC_LOC_DATA_BLOCK     = 0x14
    READ_RAW_MEM_BYTES          = 0x15
    COL_DATA_BLOCK              = 0x20
    GET_AUTO_DATA_COL_SETTINGS  = 0x21
    SET_AUTO_DATA_COL_ENABLE    = 0x22
    SET_AUTO_DATA_COL_PERIOD    = 0x23
    RESYNC_AUTO_DATA_COL_TIMERS = 0x24
    GET_CUR_BLOCK_NUMS          = 0x30
    SET_CUR_BLOCK_NUM           = 0x31
    GET_MEM_SEC_ADDRS           = 0x32
    SET_MEM_SEC_START_ADDR      = 0x33
    SET_MEM_SEC_END_ADDR        = 0x34
    ERASE_MEM_PHY_SECTOR        = 0x35
    ERASE_MEM_PHY_BLOCK         = 0x36
    ERASE_ALL_MEM               = 0x37
    SEND_EPS_CAN_MSG            = 0x40
    SEND_PAY_CAN_MSG            = 0x41
    RESET_SUBSYS                = 0x42

class Subsystem(IntEnum):
    OBC = 1
    EPS = 2
    PAY = 3

class BlockType(IntEnum):
    OBC_HK          = 1
    EPS_HK          = 2
    PAY_HK          = 3
    PAY_OPT         = 4
    PAY_OPT_OD      = 5
    PAY_OPT_FL      = 6
    PRIM_CMD_LOG    = 7
    SEC_CMD_LOG     = 8

class CAN(IntEnum):
    EPS_CTRL = 0x02
    PAY_CTRL = 0x05

class EPS_CTRL(IntEnum):
    PING                    = 0
    READ_EEPROM             = 1
    ERASE_EEPROM            = 2
    READ_RAM_BYTE           = 3
    RESET                   = 4
    GET_HEAT_SHAD_SP        = 5
    SET_HEAT_1_SHAD_SP      = 6
    SET_HEAT_2_SHAD_SP      = 7
    GET_HEAT_SUN_SP         = 8
    SET_HEAT_1_SUN_SP       = 9
    SET_HEAT_2_SUN_SP       = 10
    GET_HEAT_CUR_THR        = 11
    SET_HEAT_LOWER_CUR_THR  = 12
    SET_HEAT_UPPER_CUR_THR  = 13

class PAY_CTRL(IntEnum):
    PING                    = 0
    READ_EEPROM             = 1
    ERASE_EEPROM            = 2
    READ_RAM_BYTE           = 3
    RESET_SSM               = 4
    RESET_OPT               = 5
    ENABLE_6V               = 6
    DISABLE_6V              = 7
    ENABLE_10V              = 8
    DISABLE_10V             = 9
    GET_HEAT_PARAMS         = 10
    SET_HEAT_SP             = 11
    SET_INV_THERM_READING   = 12
    GET_THERM_READING       = 13
    GET_THERM_ERR_CODE      = 14
    SET_THERM_ERR_CODE      = 15
    GET_MOTOR_STATUS        = 16
    MOTOR_DEP_ROUTINE       = 17
    MOTOR_UP                = 18
    MOTOR_DOWN              = 19
    SEND_OPT_SPI            = 20

class PAYThermErrCode(IntEnum):
    NORMAL          = 0x00
    BELOW_ULL       = 0x01
    ABOVE_UHL       = 0x02
    BELOW_MIU       = 0x03
    ABOVE_MIU       = 0x04
    MANUAL_INVALID  = 0x05
    MANUAL_VALID    = 0x06

class PAYOptSPIOpcode(IntEnum):
    GET_READING         = 0x01
    GET_POWER           = 0x02
    ENTER_SLEEP_MODE    = 0x03
    ENTER_NORMAL_MODE   = 0x04

class PacketACKStatus(IntEnum):
    OK                  = 0x00
    RESET_CMD_ID        = 0x01
    INVALID_ENC_FMT     = 0x02
    INVALID_LEN         = 0x03
    INVALID_CSUM        = 0x04
    INVALID_DEC_FMT     = 0x05
    INVALID_CMD_ID      = 0x06
    DECREMENTED_CMD_ID  = 0x07
    REPEATED_CMD_ID     = 0x08
    INVALID_OPCODE      = 0x09
    INVALID_PWD         = 0x0A
    FULL_CMD_QUEUE      = 0x0B

class PacketRespStatus(IntEnum):
    OK                      = 0x00
    INVALID_ARGS            = 0x01
    TIMED_OUT               = 0x02
    INVALID_CAN_OPCODE      = 0x11
    INVALID_CAN_FIELD_NUM   = 0x12
    INVALID_CAN_DATA        = 0x13
