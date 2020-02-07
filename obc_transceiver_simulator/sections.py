import os

from common import *

OUT_FOLDER = "out"

COMMON_HEADER = [
    "Expected Block Number",
    "Actual Block Number",
    "Date",
    "Time",
    "Status",
]

# Name, unit, mapping for reordering measurements
OBC_HK_MAPPING = [
    ("Uptime",                  "s",        0x00    ),
    ("Restart count",           "",         0x01    ),
    ("Restart reason",          "",         0x02    ),
    ("Restart date",            "",         0x03    ),
    ("Restart time",            "",         0x04    ),
]

EPS_HK_MAPPING = [
    ("Uptime",                  "s",        0x00    ),
    ("Restart count",           "",         0x01    ),
    ("Restart reason",          "",         0x02    ),
    ("Bat Vol",                 "V",        0x03    ),
    ("Bat Cur",                 "A",        0x04    ),
    ("X+ Cur",                  "A",        0x05    ),
    ("X- Cur",                  "A",        0x06    ),
    ("Y+ Cur",                  "A",        0x07    ),
    ("Y- Cur",                  "A",        0x08    ),
    ("3V3 Vol",                 "V",        0x09    ),
    ("3V3 Cur",                 "A",        0x0A    ),
    ("5V Vol",                  "V",        0x0B    ),
    ("5V Cur",                  "A",        0x0C    ),
    ("PAY Cur",                 "A",        0x0D    ),
    ("3V3 Temp",                "C",        0x0E    ),
    ("5V Temp",                 "C",        0x0F    ),
    ("PAY Conn Temp",           "C",        0x10    ),
    ("Bat Temp 1",              "C",        0x11    ),
    ("Bat Temp 2",              "C",        0x12    ),
    ("Heater Setpoint 1",       "C",        0x13    ),
    ("Heater Setpoint 2",       "C",        0x14    ),
    ("Gyroscope (Uncal) X",     "rad/s",    0x15    ),
    ("Gyroscope (Uncal) Y",     "rad/s",    0x16    ),
    ("Gyroscope (Uncal) Z",     "rad/s",    0x17    ),
    ("Gyroscope (Cal) X",       "rad/s",    0x18    ),
    ("Gyroscope (Cal) Y",       "rad/s",    0x19    ),
    ("Gyroscope (Cal) Z",       "rad/s",    0x1A    ),
]

PAY_HK_MAPPING = [
    ("Uptime",                  "s",    0x00    ),
    ("Restart count",           "",     0x01    ),
    ("Restart reason",          "",     0x02    ),
    ("Humidity",                "%RH",  0x03    ),
    ("Pressure",                "kPa",  0x04    ),
    ("Ambient Temp",            "C",    0x05    ),
    ("6V Temp",                 "C",    0x06    ),
    ("10V Temp",                "C",    0x07    ),
    ("Motor Driver 1 Temp",     "C",    0x08    ),
    ("Motor Driver 2 Temp",     "C",    0x09    ),
    ("MF Temp 1",               "C",    0x0A    ),
    ("MF Temp 2",               "C",    0x0B    ),
    ("MF Temp 3",               "C",    0x0C    ),
    ("MF Temp 4",               "C",    0x0D    ),
    ("MF Temp 5",               "C",    0x0E    ),
    ("MF Temp 6",               "C",    0x0F    ),
    ("MF Temp 7",               "C",    0x10    ),
    ("MF Temp 8",               "C",    0x11    ),
    ("MF Temp 9",               "C",    0x12    ),
    ("MF Temp 10",              "C",    0x13    ),
    ("MF Temp 11",              "C",    0x14    ),
    ("MF Temp 12",              "C",    0x15    ),
    ("Heater Setpoint",         "C",    0x16    ),
    ("Def Invalid Therm Temp",  "C",    0x17    ),
    ("Thermistor Enables",      "",     0x18    ),
    ("Heater Enables",          "",     0x19    ),
    ("Batt Vol",                "V",    0x1A    ),
    ("6V Vol",                  "V",    0x1B    ),
    ("6V Cur",                  "A",    0x1C    ),
    ("10V Vol",                 "V",    0x1D    ),
    ("10V Cur",                 "A",    0x1E    ),
]

PAY_OPT_MAPPING = [("Well %d" % i, "counts/ms", i) for i in range(0, 32)]

# The command log mappings have a different format
# Same for primary and secondary
CMD_LOG_MAPPING = [
    ("Opcode",                  "",     0),
    ("Argument 1",              "",     1),
    ("Argument 2",              "",     2),
]


# Represents one section in flash memory
# Mostly used to track and update the data output files
class Section(object):
    def __init__(self, number, name, mapping):
        self.number = number
        self.name = name
        self.file_name = "%d_%s.csv" % (self.number, self.name.lower())
        self.mapping = mapping
        self.data_file = None
        self.file_block_num = 0
        self.sat_block_num = 0
    
    def __str__(self):
        return "%s: file_name = %s, file_block_num = %d, sat_block_num = %d" \
            % (self.name, self.file_name, self.file_block_num, self.sat_block_num)

    # Create or append to file
    # Adapted from https://stackoverflow.com/questions/20432912/writing-to-a-new-file-if-it-doesnt-exist-and-appending-to-a-file-if-it-does
    def load_file(self):
        if os.path.isdir(OUT_FOLDER):
            print("Found existing folder", OUT_FOLDER)
        else:
            os.mkdir(OUT_FOLDER)
            print("Created new folder", OUT_FOLDER)

        file_path = OUT_FOLDER + "/" + self.file_name

        if os.path.exists(file_path):
            print("Found existing file %s, appending to file" % file_path)

            # https://stackoverflow.com/questions/2757887/file-mode-for-creatingreadingappendingbinary
            self.data_file = open(file_path, 'a+')

            # Read last block number stored in file
            # Change pointer to beginning of file
            self.data_file.seek(0, 0)
            all_lines = self.data_file.readlines()
            #print("all_lines =", all_lines)
            if len(all_lines) > 1:
                last_line = all_lines[-1]
                if len(last_line) > 0:
                    self.file_block_num = int(last_line.split(",")[0].strip()) + 1
            # Change pointer back to end of file
            self.data_file.seek(0, 2)

        else:
            print("Did not find existing file %s, creating new file" % file_path)

            print("Writing header")
            self.data_file = open(file_path, 'a+')
            # Write header
            values = []
            values.extend(COMMON_HEADER)
            values.extend(map(lambda x : x[0] + (" (" + x[1] + ")" if len(x[1]) > 0 else ""), self.mapping))
            self.data_file.write(", ".join(values) + "\n")
            self.data_file.flush()
        
        print(self)
    
    def print_fields(self, fields, converted):
        print(self.name)
        # Each value in converted can be float, int, or str
        for i in range(len(self.mapping)):
            conv_str = conv_value_to_str(converted[i])
            out_str = "Field #%d (%s): 0x%.6x = %s" % (self.mapping[i][2], self.mapping[i][0], fields[i], conv_str)
            # Add unit if it has one
            if len(self.mapping[i][1]) > 0:
                out_str += " " + self.mapping[i][1]
            print(out_str)
    
    def write_block_to_file(self, expected_block_num, header, fields, converted):
        # Write row
        values = []
        # Add header
        values.extend(map(str, [expected_block_num, bytes_to_uint24(header[0:3]),  date_time_to_str(header[3:6]), date_time_to_str(header[6:9]), "0x%.2x (%s)" % (header[9], packet_resp_status_to_str(header[9]))]))

        # Add fields (raw and converted)
        assert len(fields) == len(converted)
        for i in range(len(fields)):
            values.append("0x%.6x (%s)" % (fields[i], conv_value_to_str(converted[i])))

        self.data_file.write(", ".join(values) + "\n")
        self.data_file.flush()
        print("Added block row to file", self.file_name)

        # Update file_block_num
        self.file_block_num = expected_block_num + 1
        print(self)
    
    # Just writes a single number to keep track of manually changing the expected block number in the file
    def set_file_block_num(self, block_num):
        self.file_block_num = block_num
        self.data_file.write("%d\n" % (self.file_block_num - 1))
        self.data_file.flush()
        print("Wrote block number to file:", self.file_block_num - 1)
        print(self)


# Data sections
obc_hk_section          = Section(BlockType.OBC_HK,         "OBC_HK",       OBC_HK_MAPPING)
eps_hk_section          = Section(BlockType.EPS_HK,         "EPS_HK",       EPS_HK_MAPPING)
pay_hk_section          = Section(BlockType.PAY_HK,         "PAY_HK",       PAY_HK_MAPPING)
pay_opt_section         = Section(BlockType.PAY_OPT,        "PAY_OPT",      PAY_OPT_MAPPING)  # won't be used for reading data blocks
pay_opt_od_section      = Section(BlockType.PAY_OPT_OD,     "PAY_OPT_OD",   PAY_OPT_MAPPING)
pay_opt_fl_section      = Section(BlockType.PAY_OPT_FL,     "PAY_OPT_FL",   PAY_OPT_MAPPING)
# Command log sections
prim_cmd_log_section    = Section(BlockType.PRIM_CMD_LOG,   "PRIM_CMD_LOG", CMD_LOG_MAPPING)
sec_cmd_log_section     = Section(BlockType.SEC_CMD_LOG,    "SEC_CMD_LOG",  CMD_LOG_MAPPING)

g_all_col_data_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_section,
]
g_all_read_data_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_od_section,
    pay_opt_fl_section,
]

g_all_cmd_log_sections = [
    prim_cmd_log_section,
    sec_cmd_log_section,
]

g_all_col_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_section,
    prim_cmd_log_section,
    sec_cmd_log_section,
]
g_all_read_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_od_section,
    pay_opt_fl_section,
    prim_cmd_log_section,
    sec_cmd_log_section,
]
g_all_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_section,
    pay_opt_od_section,
    pay_opt_fl_section,
    prim_cmd_log_section,
    sec_cmd_log_section,
]
