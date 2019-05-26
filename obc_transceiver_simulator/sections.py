import os

from common import *


COMMON_HEADER = [
    "Expected Block Number"
    "Block Number",
    "Error",
    "Date",
    "Time"
]

# Name, unit, mapping for reordering measurements
EPS_HK_MAPPING = [
    ("BB Vol",                  "V",        6   ),
    ("BB Cur",                  "A",        7   ),
    ("-Y Cur",                  "A",        5   ),
    ("+X Cur",                  "A",        2   ),
    ("+Y Cur",                  "A",        3   ),
    ("-X Cur",                  "A",        4   ),
    ("Bat Temp 1",              "C",        10  ),
    ("Bat Temp 2",              "C",        11  ),
    ("Bat Vol",                 "V",        0   ),
    ("Bat Cur",                 "A",        1   ),
    ("BT Cur",                  "A",        8   ),
    ("BT Vol",                  "V",        9   ),
    ("Heater Setpoint 1",       "C",        12  ),
    ("Heater Setpoint 2",       "C",        13  ),
    ("IMU Gyroscope (Uncal) X", "rad/s",    14  ),
    ("IMU Gyroscope (Uncal) Y", "rad/s",    15  ),
    ("IMU Gyroscope (Uncal) Z", "rad/s",    16  ),
    ("IMU Gyroscope (Cal) X",   "rad/s",    17  ),
    ("IMU Gyroscope (Cal) Y",   "rad/s",    18  ),
    ("IMU Gyroscope (Cal) Z",   "rad/s",    19  )
]

PAY_HK_MAPPING = [
    ("Temperature",          "C",   0   ),
    ("Humidity",             "%RH", 1   ),
    ("Pressure",             "kPa", 2   ),
    ("MF Temp 0",            "C",   3   ),
    ("MF Temp 1",            "C",   4   ),
    ("MF Temp 2",            "C",   5   ),
    ("MF Temp 3",            "C",   6   ),
    ("MF Temp 4",            "C",   7   ),
    ("MF Temp 5",            "C",   8   ),
    ("MF Temp 6",            "C",   9   ),
    ("MF Temp 7",            "C",   10  ),
    ("MF Temp 8",            "C",   11  ),
    ("MF Temp 9",            "C",   12  ),
    ("Heater Setpoint 1",    "C",   13  ),
    ("Heater Setpoint 2",    "C",   14  ),
    ("Left Proximity",       "",    15  ),
    ("Right Proximity",      "",    16  )
]

PAY_OPT_MAPPING = [("Well #%d" % (i + 1), "V", i) for i in range(32)]


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
        return "%d: file_name = %d, file_block_num = %d, sat_block_num = %d" \
            % (self.name, self.file_name, self.file_block_num, self.sat_block_num)

    # Create or append to file
    # Adapted from https://stackoverflow.com/questions/20432912/writing-to-a-new-file-if-it-doesnt-exist-and-appending-to-a-file-if-it-does
    def load_file(self):
        if os.path.exists(self.file_name):
            print("Found existing file", self.file_name)
            print("Appending to file")

            # https://stackoverflow.com/questions/2757887/file-mode-for-creatingreadingappendingbinary
            self.data_file = open(self.file_name, 'a+')

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
            print("Did not find existing file", self.file_name)
            print("Creating new file")

            print("Writing header")
            self.data_file = open(self.file_name, 'a+')
            # Write header
            values = []
            values.extend(COMMON_HEADER)
            values.extend(map(lambda x : x[0] + " (" + x[1] + ")", mapping))
            self.data_file.write(", ".join(values) + "\n")
            self.data_file.flush()
        
        print(self)
    
    def print_fields(self, fields, converted):
        print(self.name)
        for i in range(len(self.mapping)):
            print("Field #%d (%s): 0x%.6x = %.6f %s" % (i, self.mapping[i], fields[i], converted[i], self.mapping[i][1]))
    
    def write_block_to_file(self, expected_block_num, header, converted):
        # Write row
        values = []
        values.extend([expected_block_num, bytes_to_uint24(header[0:3]), header[3], date_time_to_str(header[4:7]), date_time_to_str(header[7:10])])
        values.extend(map(str, converted))
        self.data_file.write(", ".join(map(file_value_to_str, values)) + "\n")
        self.data_file.flush()
        print("Added block row to file", self.file_name)

        # Update file_block_num
        if bytes_to_uint24(header[0:3]) == self.file_block_num:
            self.file_block_num += 1
        print(self)


# Memory sections
eps_hk_section = Section("EPS_HK", "eps_hk.csv", EPS_HK_MAPPING)
pay_hk_section = Section("PAY_HK", "pay_hk.csv", PAY_HK_MAPPING)
pay_opt_section = Section("PAY_OPT", "pay_opt.csv", PAY_OPT_MAPPING)

all_sections = [eps_hk_section, pay_hk_section, pay_opt_section]
