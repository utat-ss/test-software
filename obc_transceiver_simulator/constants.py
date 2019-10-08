from enum import IntEnum

class CommandOpcode(IntEnum):
    PING_OBC                    = 0x00
    GET_RTC                     = 0x01
    SET_RTC                     = 0x02
    READ_OBC_EEPROM             = 0x03
    ERASE_OBC_EEPROM            = 0x04
    READ_OBC_RAM_BYTE           = 0x05
    SEND_EPS_CAN_MSG            = 0x06
    SEND_PAY_CAN_MSG            = 0x07
    ACT_PAY_MOTORS              = 0x08
    RESET_SUBSYS                = 0x09
    SET_INDEF_LPM_ENABLE        = 0x0A
    READ_REC_STATUS_INFO        = 0x10
    READ_DATA_BLOCK             = 0x11
    READ_REC_LOC_DATA_BLOCK     = 0x12
    READ_PRIM_CMD_BLOCKS        = 0x13
    READ_SEC_CMD_BLOCKS         = 0x14
    READ_RAW_MEM_BYTES          = 0x15
    ERASE_MEM_PHY_SECTOR        = 0x16
    ERASE_MEM_PHY_BLOCK         = 0x17
    ERASE_ALL_MEM               = 0x18
    COL_DATA_BLOCK              = 0x20
    GET_CUR_BLOCK_NUM           = 0x21
    SET_CUR_BLOCK_NUM           = 0x22
    GET_MEM_SEC_START_ADDR      = 0x23
    SET_MEM_SEC_START_ADDR      = 0x24
    GET_MEM_SEC_END_ADDR        = 0x25
    SET_MEM_SEC_END_ADDR        = 0x26
    GET_AUTO_DATA_COL_ENABLE    = 0x27
    SET_AUTO_DATA_COL_ENABLE    = 0x28
    GET_AUTO_DATA_COL_PERIOD    = 0x29
    SET_AUTO_DATA_COL_PERIOD    = 0x2A
    GET_AUTO_DATA_COL_TIMERS    = 0x2B
    RESYNC_AUTO_DATA_COL_TIMERS = 0x2C

class Subsystem(IntEnum):
    OBC = 1
    EPS = 2
    PAY = 3

class BlockType(IntEnum):
    OBC_HK          = 1
    EPS_HK          = 2
    PAY_HK          = 3
    PAY_OPT         = 4
    PRIM_CMD_LOG    = 5
    SEC_CMD_LOG     = 6

class CAN(IntEnum):
    EPS_CTRL = 0x02
    PAY_CTRL = 0x05

class EPS_CTRL(IntEnum):
    PING            = 0
    RESET           = 13
    READ_EEPROM     = 14
    ERASE_EEPROM    = 15
    READ_RAM_BYTE   = 16

class PAY_CTRL(IntEnum):
    PING            = 0
    RESET           = 18
    READ_EEPROM     = 19
    ERASE_EEPROM    = 20
    READ_RAM_BYTE   = 21
