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
import time
import serial
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import traceback

# check what this needs to be
SERIAL_PORT = 'ttyS0'
BAUD_RATE = 9600
TEST_NAME = 'Pressure_Test_02'
LOG_DIR = './logs'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'
CONNECTION_TIMEOUT = 15
LENGTH_GRAPH = 100
RST_GPIO = 18

global incoming_data

# Initializes the output file for the pressure test, returns file object for
# the output csv
#
def init_script():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RST_GPIO, GPIO.OUT)
    GPIO.output(RST_GPIO, GPIO.LOW)
    time.sleep(1)
    GPIO.output(RST_GPIO, GPIO.HIGH)

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
            if data == b'A\n':
                s.write(b'A')
                handshake = True
        except:
            print()
            raise SystemExit

    data = s.readline()
    while (data == b'A\n'):
        print(data)
        continue;

    print('Completed handshake')

# Generator function to read the serial port
#
def read_serial(s, outfile):
    while True:
        line = str(s.readline())
        nums = line.split(',')
        # TODO: Check these
        nums[0] = float(nums[0].replace("b'", ""))
        nums[1] = float(nums[1].replace("", ""))
        nums[2] = float(nums[2].replace("\\n'",""))
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
    

def animate(i, x, read_next):
    global incoming_data

    # pressures
    data = next(read_next)
    incoming_data = np.vstack((incoming_data, data))
    num_readings = incoming_data.shape[0]

    if num_readings > LENGTH_GRAPH:
        xvals = x
        incoming_data = incoming_data[-LENGTH_GRAPH:]
    else:
        xvals = x[0:num_readings]

    line[0].set_data(xvals, incoming_data[:,0])
    line[1].set_data(xvals, incoming_data[:,1])
    line[2].set_data(xvals, incoming_data[:,2])
    
    return line

def exit_script(file, s_port):
    file.close()
    s_port.close()

if __name__ == "__main__":
    global incoming_data
    s = serial.Serial(
        port = SERIAL_PORT,
        baudrate = BAUD_RATE,
        timeout = CONNECTION_TIMEOUT
        )
    outfile = init_script()

    GPIO18
    
    handshake(s)
    print('Setting up the generator')
    read_next = read_serial(s, outfile)
    # read_next = test_animate(10)
    incoming_data = next(read_next)
    x = np.arange(0, LENGTH_GRAPH, 1)
    print('Starting main loop')
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True)
    
    # pressure
    line1, = ax1.plot([], [], 'b')
    line2, = ax2.plot([], [], 'r')
    line3, = ax3.plot([], [], 'g')

    # Pressure
    ax1.set_xlim(0, LENGTH_GRAPH)
    ax1.set_ylim(0,250)
    ax1.set_ylabel('Pressure (kPa)')
    # Temperature
    ax2.set_ylim(0,100)
    ax2.set_ylabel('Temperature (C)')

    # Humidity
    ax3.set_ylim(0,100)
    ax3.set_ylabel('Humidity (%RH)')

    for ax in [ax1, ax2, ax3]:
        ax.minorticks_on()
        ax.grid(b=True, which='major', linestyle='--')
        ax.grid(b=True, which='minor', linestyle=':')
    
    line = [line1, line2, line3]

    print('Starting animation')
    ani = animation.FuncAnimation(fig, animate, fargs=(x, read_next), blit=False)
    plt.show()
