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

import RPi.GPIO as GPIO
import serial
import time
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# check what this needs to be
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
TEST_NAME = 'Pressure_Test_02'
LOG_DIR = './logs'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'
CONNECTION_TIMEOUT = 15
LENGTH_GRAPH = 100

global incoming_data
pressures = []
temps = []
hums = []

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

# Perform a handshake with the arduino
def handshake(s):
    handshake = False
    t0 = time.clock()
    while not handshake and ((time.clock() - t0) < CONNECTION_TIMEOUT):
        data = s.readline()
        print(data)
        if data == b'AA\n':
            s.write(b'AA')
            handshake = True
        time.sleep(1);
    if ((time.clock() - t0 >= 15)):
        print('Timeout occurred')
        raise SystemExit
    print('Completed handshake')

# Generator function to read the serial port
#
def read_serial(s, outfile):
    while True:
        line = str(s.readline())
        nums = line.split(',')
        # check the processing I need
        nums[0] = int(nums[0].replace("b'", ""))
        nums[1] = int(nums[1].replace("\\r\\n'", ""))
        print(nums)
        write_output(nums, outfile)
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
        

def test_animation(mu):
    while True:
        p = 101.3 + mu * np.random.randn()
        yield p
    

def animate(i, x, read_next):
    global incoming_data
    
    incoming_data.append(next(read_next))
    if len()
    numReadings = len(pressures)
    
    if numReadings > 100:
        xvals = x
        yvals = pressures[-100:]
    else:
        xvals = x[0:numReadings]
        yvals = pressures

    ax1.clear()
    ax1.plot()

    ax2.clear()
    ax2.plot()

    ax3.clear()
    ax3.plot()
    return 

if __name__ == "__main__":
    try:
        s = serial.Serial(
            port = SERIAL_PORT,
            baudrate = BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
           )

        outfile = init_script()
        handshake(s)
        print('Setting up the generator')
        read_next = read_serial(s, outfile)
        time.sleep(1);
        print('Starting main loop')
        x = np.arange(0, LENGTH_GRAPH, 1)
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True, squeeze=False)
        line, = ax1.plot([],[])
        ax1.set_xlim(0, 100)
        # pressure
        ax1.set_ylim(50,250)
        ax1.set_ylabel('Pressure (kPa)')
        # temp
        ax2.set_ylim(0, 50)
        ax2.set_ylabel('Temperature (C)')
        # humidity
        ax3.set_ylim(0,100)
        ax3.set_ylabel('Humidity (%RH)')

        
        print('Starting animation')
        ani = animation.FuncAnimation(fig, animate, fargs=(x, read_next), blit=False)
        plt.show()
        
    except:
        print('Closing the serial port')
        outfile.close()
        s.close()