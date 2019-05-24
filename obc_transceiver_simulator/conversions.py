# Conversion functions (similar to lib-common/src/conversions/conversions.c)

'''
Conversions library

All conversions are based on the data conversion protocol:
https:#utat-ss.readthedocs.io/en/master/our-protocols/data-conversion.html

Conversion functions between raw data (bits represented as `uint` types) and
actual measurements for all software systems in the satellite.

ADC - ADS7952 - PAY/EPS
http:#www.ti.com/lit/ds/slas605c/slas605c.pdf

EPS ADC uses current monitor - INA214
http:#www.ti.com/lit/ds/symlink/ina214.pdf

DAC - DAC7562 - PAY
Datasheet: http:#www.ti.com/lit/ds/symlink/dac8162.pdf

Temperature sensor - LM95071 - PAY
http:#www.ti.com/lit/ds/symlink/lm95071.pdf

Humidity sensor - HIH7131 - PAY
https:#sensing.honeywell.com/honeywell-sensing-humidicon-hih7000-series-product-sheet-009074-6-en.pdf

Pressure sensor - MS5803-05BA - PAY
http:#www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5803-05BA%7FB3%7Fpdf%7FEnglish%7FENG_DS_MS5803-05BA_B3.pdf%7FCAT-BLPS0011

Optical ADC - AD7194 - PAY-Optical, different from main ADC
http:#www.analog.com/media/en/technical-documentation/data-sheets/AD7194.pdf

Thermistor:
NTC Thermistor 10k 0603 (1608 Metric) Part # NCU18XH103F60RB
Digikey link: https:#www.digikey.ca/product-detail/en/murata-electronics-north-america/NCU18XH103F60RB/490-16279-1-ND/7363262
Datasheet (page 13. Part # NCU__XH103):
https:#www.murata.com/~/media/webrenewal/support/library/catalog/products/thermistor/r03e.ashx?la=en-us
Datasheet (NCU18XH103F60RB): https:#www.murata.com/en-us/api/pdfdownloadapi?cate=luNTCforTempeSenso&partno=NCU18XH103F60RB

IMU - BNO080
https://cdn.sparkfun.com/assets/1/3/4/5/9/BNO080_Datasheet_v1.3.pdf
https://cdn.sparkfun.com/assets/4/d/9/3/8/SH-2-Reference-Manual-v1.2.pdf
https://cdn.sparkfun.com/assets/7/6/9/3/c/Sensor-Hub-Transport-Protocol-v1.7.pdf
'''


from ctypes import *


ADC_V_REF = 5.0

ADC_EPS_VOUT_DIV_RATIO = 0.5

ADC_EPS_IOUT_RES        = 0.010
ADC_EPS_IOUT_AMP_GAIN   = 100.0
ADC_EPS_IOUT_VREF       = 3.3


DAC_VREF        = 2.5
DAC_VREF_GAIN   = 2
DAC_NUM_BITS    = 12


OPT_ADC_V_REF       = 2.5
OPT_ADC_NUM_BITS    = 24


THERM_V_REF = 2.5
THERM_R_REF = 10.0

THERM_LUT_COUNT = 34


# Resistances (in kilo-ohms)
THERM_RES = [
    195.652,    148.171,    113.347,    87.559,     68.237,
    53.650,     42.506,     33.892,     27.219,     22.021,
    17.926,     14.674,     12.081,     10.000,     8.315,
    6.948,      5.834,      4.917,      4.161,      3.535,
    3.014,      2.586,      2.228,      1.925,      1.669,
    1.452,      1.268,      1.110,      0.974,      0.858,
    0.758,      0.672,      0.596,      0.531
]

# Temperatures (in C)
THERM_TEMP = [
    -40,        -35,        -30,        -25,        -20,
    -15,        -10,        -5,         0,          5,
    10,         15,         20,         25,         30,
    35,         40,         45,         50,         55,
    60,         65,         70,         75,         80,
    85,         90,         95,         100,        105,
    110,        115,        120,        125
]


# IMU Q points
IMU_ACCEL_Q = 8
IMU_GYRO_Q  = 9




def adc_raw_data_to_raw_vol(raw_data):
    ratio = raw_data / 0x0FFF
    voltage = ratio * ADC_V_REF
    return voltage



def adc_raw_vol_to_eps_vol(raw_voltage):
    # Use voltage divider circuit ratio to recover original voltage before division
    return raw_voltage / ADC_EPS_VOUT_DIV_RATIO


def adc_raw_vol_to_eps_cur(raw_voltage):
    # Get the voltage across the resistor before amplifier gain
    before_gain_voltage = raw_voltage / ADC_EPS_IOUT_AMP_GAIN
    # Ohm's law (I = V / R)
    current = before_gain_voltage / ADC_EPS_IOUT_RES

    return current


'''
Converts raw 12 bit data from an ADC channel to a voltage in the EPS circuit.
raw_data - 12 bits
returns - in V
'''
def adc_raw_data_to_eps_vol(raw_data):
    return adc_raw_vol_to_eps_vol(adc_raw_data_to_raw_vol(raw_data))


'''
Converts raw 12 bit data from an ADC channel to a current in the EPS circuit.
raw_data - 12 bits
returns - in A
'''
def adc_raw_data_to_eps_cur(raw_data):
    return adc_raw_vol_to_eps_cur(adc_raw_data_to_raw_vol(raw_data))


'''
Converts raw 12 bit data from an ADC channel to the temperature measured by a
    thermistor.
raw_data - 12 bits
returns - in C
'''
def adc_raw_data_to_therm_temp(raw_data):
    return therm_res_to_temp(therm_vol_to_res(adc_raw_data_to_raw_vol(raw_data)))



'''
Converts DAC raw data to an output voltage.
raw_data - 12 bit raw data (Din)
returns - output voltage (in V)
'''
def dac_raw_data_to_vol(raw_data):
    # p.28 - 8.3.1
    # Vout = (Din / 2^n) x Vref x Gain
    ratio = raw_data / (1 << DAC_NUM_BITS)
    result = ratio * DAC_VREF * DAC_VREF_GAIN

    return result


'''
Converts a DAC output voltage value to the raw data (12 bit) value.
voltage - output voltage (in V)
returns - 12 bit raw data
'''
def dac_vol_to_raw_data(voltage):
    # p.28 - 8.3.1
    # Vout = (Din / 2^n) x Vref x Gain
    # Din = (Vout x 2^n) / (Vref x Gain)
    num = voltage * (1 << DAC_NUM_BITS)
    denom = DAC_VREF * DAC_VREF_GAIN
    result = int(num / denom)

    return result



'''
Converts raw data to a temperature from the temperature sensor
raw_data - 16 bits (INCLUDING the 0b11 on the right that is always there)
returns - temperature in degrees C (p. 9).
'''
def temp_raw_data_to_temperature(raw_data):
    signed_temp_data = raw_data / 4
    # LSB is 0.03125 C
    return signed_temp_data * 0.03125


'''
Converts raw data to a humidity measurement (p.6).
raw_data - 14 bits
returns - humidity (in %RH, relative humidity)
'''
def hum_raw_data_to_humidity(raw_data):
    return raw_data / ((1 << 14) - 2.0) * 100.0


'''
Converts raw pressure data to the pressure.
raw_data - 24 bits, 0-6000 mbar with 0.01mbar resolution per bit
    datasheet says 0.03mbar resolution, but should be 0.01mbar
returns - pressure (in kPa)

1 bar = 100,000 Pa
1 mbar = 100 Pa
1 kPa = 10 mbar
'''
def pres_raw_data_to_pressure(raw_data):
    mbar = raw_data * 0.01
    kpa = mbar / 10.0
    return kpa



'''
Converts a raw measurement to the input voltage on the ADC pin.
raw_data - 24 bits
gain - gain scaling factor to multiply the voltage by
returns - voltage (in V)
Unipolar operation (only positive)
'''
def opt_adc_raw_data_to_vol(raw_data, gain):
    # p.31
    # Code = (2^N * AIN * Gain) / (V_REF)
    # => AIN = (Code * V_REF) / (2^N * Gain)
    num = raw_data *  OPT_ADC_V_REF
    denom = (1 << OPT_ADC_NUM_BITS) * gain
    return num / denom


def opt_adc_raw_data_to_diff_vol(raw_data, gain):
  # p.31
  # Code = 2^(n-1) x [(AIN * Gain / V_REF) + 1]
  # => AIN = (Code/2^(n-1) - 1) * V_REF/Gain
  volt = raw_data / (1 << (OPT_ADC_NUM_BITS - 1))
  volt -= 1
  volt *= OPT_ADC_V_REF /  gain

  return volt





'''
Converts the measured thermistor resistance to temperature.
resistance - thermistor resistance (in kilo-ohms)
Returns - temperature (in C)
'''
def therm_res_to_temp(resistance):
    for i in range(THERM_LUT_COUNT - 1):
        # Next value should be smaller than previous value
        resistance_next = THERM_RES[i + 1]

        if (resistance >= resistance_next):
            resistance_prev = THERM_RES[i]
            temp_next = THERM_TEMP[i + 1]
            temp_prev = THERM_TEMP[i]

            temp_diff = (temp_next - temp_prev)
            resistance_diff = (resistance_next - resistance_prev)
            slope = temp_diff / resistance_diff

            diff = resistance - resistance_prev  #should be negative
            return temp_prev + (diff * slope)

    # This shouldn't happen
    return 0.0


'''
Converts the thermistor temperature to resistance.
temp - temperature (in C)
Returns - thermistor resistance (in kilo-ohms)
'''
def therm_temp_to_res(temp):
    for i in range(THERM_LUT_COUNT - 1):
        # Next value should be bigger than previous value
        temp_next = THERM_TEMP[i + 1]

        if (temp <= temp_next):
            temp_prev = THERM_TEMP[i]
            resistance_next = THERM_RES[i + 1]
            resistance_prev = THERM_RES[i]

            resistance_diff = (resistance_next - resistance_prev)
            temp_diff = (temp_next - temp_prev)
            slope = resistance_diff / temp_diff

            diff = temp - temp_prev  #should be positive
            return resistance_prev + (diff * slope)

    # This shouldn't happen
    return 0.0


'''
Using the thermistor resistance, get the voltage at the point between the
    thermistor and the constant 10k resistor (10k connected to ground)
See: https:#www.allaboutcircuits.com/projects/measuring-temperature-with-an-ntc-thermistor/
resistance - in kilo-ohms
returns - voltage (in V)
'''
def therm_res_to_vol(resistance):
    return THERM_V_REF * THERM_R_REF / (resistance + THERM_R_REF)


'''
Gets the resistance of the thermistor given the voltage.
For equation, see: https:#www.allaboutcircuits.com/projects/measuring-temperature-with-an-ntc-thermistor/
voltage - in V
returns - resistance (in kilo-ohms)
'''
def therm_vol_to_res(voltage):
    try:
        return THERM_R_REF * (THERM_V_REF / voltage - 1)
    except ZeroDivisionError:
        return 0


'''
IMU Q-point
Converts the raw 16-bit signed fixed-point value from the input report to the actual floating-point measurement using the Q point.
Q point - number of fractional digits after (to the right of) the decimal point, i.e. higher Q point means smaller/more precise number (#1 p.22)
https://en.wikipedia.org/wiki/Q_(number_format)
Similar to reference library qToFloat()
raw_data - 16 bit raw value
q_point - number of binary digits to shift
'''
def imu_raw_data_to_double(raw_data, q_point):
    # Need to use c_int16 to force signed 16-bit number
    # Implement power of 2 with a bitshift
    return float(c_int16(raw_data).value) / float(1 << q_point)


'''
Converts the raw 16-bit value to a gyroscope measurement (in rad/s).
'''
def imu_raw_data_to_gyro(raw_data):
    return imu_raw_data_to_double(raw_data, IMU_GYRO_Q)
