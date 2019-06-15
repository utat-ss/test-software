#################################################################################
#
# Pressure Vessel Test Code
# Written by: Dylan Vogel
#
# Python script for collecting UART sensor readings from PAY-SSM. Creates a nice
# little live graph and log file. Intended to be used with the corresponding 
# PAY-SSM test in: 
# https://github.com/HeronMkII/pay/tree/master/manual_tests/pressure_vessel_test/
#
# Please check that the code version matches the one for PAY-SSM or else I give
# no guarantees for code functionality.
#
# Code Version:       v1.0
# 
# HOOKUP:
# RPi Zero
# 
#################################################################################

#import RPi.GPIO as GPIO
import serial
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import traceback

# check what this needs to be
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
TEST_NAME = 'Pressure_Test_02'
LOG_DIR = './logs'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'
CONNECTION_TIMEOUT = 15
LENGTH_GRAPH = 100

global incoming_data, x_axis_data
incoming_data = np.array([0,0,0])
x_axis_data = np.arange(0, LENGTH_GRAPH-1, 1)

# Initializes the output file for the pressure test, returns file object for
# the output csv
#
def init_script():
    # Check if logging directory exists
    logPath = os.path.abspath(LOG_DIR)
    if not os.path.exists(logPath):
        os.mkdir(logPath)
    # Format a timestamp for the log
    timestamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    # Open up the output file
    filename = os.path.join(logPath, TEST_NAME + '_' + timestamp + '.csv')
    outFile = open(filename, 'w')
    return outFile

# Perform a handshake with the arduino. If handshake doesn't work out, terminates after CONNECTION_TIMEOUT
def handshake(s):
    handshake = False
    while not handshake:
        try:
            data = s.readline()
            print(data)
            if data == b'AA\n':
                s.write(b'AA')
                handshake = True
        except:
            print()
            raise SystemExit

    print('Completed handshake')

# Generator function to read the serial port
#
def read_serial(s, outfile):
    while True:
        line = str(s.readline())
        nums = line.split(',')
        # TODO: Check these
        nums[0] = int(nums[0].replace("b'", ""))
        nums[1] = int(nums[1].replace("\\r\\n'", ""))
        nums[2] = int(nums[2].replace("",""))
        print(nums)
        write_output(nums, outfile)
        nums = np.array(nums)
        yield nums
    
# Function exists in case I want to do any fancy formatting or processing before
# writing the output
#
def write_output(values, file):
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    time = datetime.datetime.now().strftime('%H:%M:%S')
    file.write(date + ',' + time + ',')
    for value in values:
        file.write(str(value) + ',')
    file.write('\n')
        

def test_animate(mu):
    while True:
        p = 101.3 + mu * np.random.randn()
        t = 23.5 + mu * np.random.randn()
        h = 57 + mu * np.random.randn()
        yield np.array([p, t, h])
    

def animate(i, read_next):
    global incoming_data, x_axis_data

    # pressures
    data = next(read_next)
    incoming_data = np.vstack((incoming_data, data))
    num_readings = len(incoming_data[0])

    if num_readings > LENGTH_GRAPH:
        # check that this is correct
        incoming_data = incoming_data[-LENGTH_GRAPH:]

    line[0].set_data(x_axis_data[:num_readings - 1], incoming_data[:,0])
    line[1].set_data(x_axis_data[:num_readings - 1], incoming_data[:,1])
    line[2].set_data(x_axis_data[:num_readings - 1], incoming_data[:,2])
    
    return line

def exit_script(file, s_port):
    file.close()
    s_port.close()

if __name__ == "__main__":
    # s = serial.Serial(
    #     port = SERIAL_PORT,
    #     baudrate = BAUD_RATE,
    #     timeout = CONNECTION_TIMEOUT
    #     )
    outfile = init_script()
    
    # handshake(s)
    print('Setting up the generator')
    # read_next = read_serial(s, outfile)
    read_next = test_animate(10)
    print('Starting main loop')
    fig, axes = plt.subplots(nrows=3, ncols=1, squeeze=False)
    # pressure
    ln1, = axes[0,0].plot([],[])
    axes[0,0].set_xlim(0, 100)
    axes[0,0].set_ylim(50,250)
    axes[0,0].set_ylabel('Pressure (kPa)')
    # temp
    ln2, = axes[1,0].plot([],[])
    axes[1,0].set_ylim(0, 50)
    axes[1,0].set_ylabel('Temperature (C)')
    # humidity
    ln3, = axes[2,0].plot([],[])
    axes[2,0].set_ylim(0,100)
    axes[2,0].set_ylabel('Humidity (%RH)')
    
    line = [ln1, ln2, ln3]

    print('Starting animation')
    ani = animation.FuncAnimation(fig, animate, fargs=read_next, blit=True, interval=1000)
    plt.show()
