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
    ("Uptime",                  "s",        0   ),
    ("Restart count",           "",         1   ),
    ("Restart reason",          "",         2   ),
    ("Restart date",            "",         3   ),
    ("Restart time",            "",         4   )
]

EPS_HK_MAPPING = [
    ("Bat Vol",                 "V",        0   ),
    ("Bat Cur",                 "A",        1   ),
    ("X+ Cur",                  "A",        2   ),
    ("X- Cur",                  "A",        3   ),
    ("Y+ Cur",                  "A",        4   ),
    ("Y- Cur",                  "A",        5   ),
    ("3V3 Vol",                 "V",        6   ),
    ("3V3 Cur",                 "A",        7   ),
    ("5V Vol",                  "V",        8   ),
    ("5V Cur",                  "A",        9   ),
    ("PAY Cur",                 "A",        10  ),
    ("Bat Temp 1",              "C",        11  ),
    ("Bat Temp 2",              "C",        12  ),
    ("3V3 Temp",                "C",        13  ),
    ("5V Temp",                 "C",        14  ),
    ("PAY Conn Temp",           "C",        15  ),
    ("Solar shunt states",      "",         16  ),
    ("Heater Setpoint 1",       "C",        17  ),
    ("Heater Setpoint 2",       "C",        18  ),
    ("Gyroscope (Uncal) X",     "rad/s",    19  ),
    ("Gyroscope (Uncal) Y",     "rad/s",    20  ),
    ("Gyroscope (Uncal) Z",     "rad/s",    21  ),
    ("Gyroscope (Cal) X",       "rad/s",    22  ),
    ("Gyroscope (Cal) Y",       "rad/s",    23  ),
    ("Gyroscope (Cal) Z",       "rad/s",    24  ),
    ("Uptime",                  "s",        25  ),
    ("Restart count",           "",         26  ),
    ("Restart reason",          "",         27  ),
]

PAY_HK_MAPPING = [
    ("Humidity",                "%RH",  0   ),
    ("Pressure",                "kPa",  1   ),
    ("Ambient Temp",            "C",    2   ),
    ("Motor Driver 1 Temp",     "C",    3   ),
    ("Motor Driver 2 Temp",     "C",    4   ),
    ("10V Temp",                "C",    5   ),
    ("6V Temp",                 "C",    6   ),
    ("MF Temp 1",               "C",    7   ),
    ("MF Temp 2",               "C",    8   ),
    ("MF Temp 3",               "C",    9   ),
    ("MF Temp 4",               "C",    10   ),
    ("MF Temp 5",               "C",    11  ),
    ("MF Temp 6",               "C",    12   ),
    ("MF Temp 7",               "C",    13  ),
    ("MF Temp 8",               "C",    14  ),
    ("MF Temp 9",               "C",    15  ),
    ("MF Temp 10",              "C",    16  ),
    ("MF Temp 11",              "C",    17  ),
    ("MF Temp 12",              "C",    18  ),
    ("Heater Enabled States",   "",     19  ),
    ("Limit Switch States",     "",     20  ),
    ("Uptime",                  "s",    21  ),
    ("Restart count",           "",     22  ),
    ("Restart reason",          "",     23  ),
]

PAY_OPT_MAPPING = [("Well #%d" % (i + 1), "V", i) for i in range(32)]

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
    def __init__(self, name, file_name, mapping):
        self.name = name
        self.file_name = file_name
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
    
    def write_block_to_file(self, expected_block_num, header, converted):
        # Write row
        values = []
        values.extend(map(str, [expected_block_num, bytes_to_uint24(header[0:3]),  date_time_to_str(header[3:6]), date_time_to_str(header[6:9]), "0x%.2x (%s)" % (header[9], packet_resp_status_to_str(header[9]))]))
        values.extend(map(conv_value_to_str, converted))
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
# TODO - number sections
obc_hk_section = Section("OBC_HK", "obc_hk.csv", OBC_HK_MAPPING)
eps_hk_section = Section("EPS_HK", "eps_hk.csv", EPS_HK_MAPPING)
pay_hk_section = Section("PAY_HK", "pay_hk.csv", PAY_HK_MAPPING)
pay_opt_section = Section("PAY_OPT", "pay_opt.csv", PAY_OPT_MAPPING)

# Command log sections
# TODO - fix issues with file writing?
prim_cmd_log_section = Section("PRIM_CMD_LOG", "prim_cmd_log.csv", CMD_LOG_MAPPING)
sec_cmd_log_section = Section("SEC_CMD_LOG", "sec_cmd_log.csv", CMD_LOG_MAPPING)

g_all_data_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_section,
]
g_all_cmd_log_sections = [
    prim_cmd_log_section,
    sec_cmd_log_section,
]
g_all_sections = [
    obc_hk_section,
    eps_hk_section,
    pay_hk_section,
    pay_opt_section,
    prim_cmd_log_section,
    sec_cmd_log_section,
]
