# ADXL345.py

import RPi.GPIO as GPIO
import time
import sys
import os
import smbus


addr_ADXL345 = 0x53

# ADXL345 Registers
EARTH_GRAVITY_MS2 = 9.80665
SCALE_MULTIPLIER = 0.004
DATA_FORMAT = 0x31
BW_RATE = 0x2C
POWER_CTL = 0x2D
AXES_DATA = 0x32

# ADXL345 Ranges
RANGE_2G = 0x00
RANGE_4G = 0x01
RANGE_8G = 0x02
RANGE_16G = 0x03

MEASURE = 0x08

# ADXL345 Bandwidths
BW_RATE_1600HZ = 0x0F
BW_RATE_800HZ = 0x0E
BW_RATE_400HZ = 0x0D
BW_RATE_200HZ = 0x0C
BW_RATE_100HZ = 0x0B
BW_RATE_50HZ = 0x0A
BW_RATE_25HZ = 0x09


# plot class
class ADXL345:
	def __init__(self, rnge, bw, pwr):
		# Define accelerometer location in smbus I2C
		if GPIO.RPI_REVISION == 2:
			self.i2cBus = smbus.SMBus(1)
		else:
			self.i2cBus = smbus.SMBus(0)
		
		if rnge == 2:
			G = RANGE_2G
		elif rnge == 4:
			G = RANGE_4G
		elif rnge == 8:
			G = RANGE_8G
		elif rnge == 16:
			G = RANGE_16G
		else:
			print str(rnge) +"is not a correct range"
			quit()
		
		# Set Range
		current = self.i2cBus.read_byte_data(addr_ADXL345, DATA_FORMAT)
		temp = G
		current = current & int('11111100',2)
		temp = current | temp
		self.i2cBus.write_byte_data(addr_ADXL345, DATA_FORMAT, temp)
		self.Range = rnge
		
		# Set Bandwidth
		current = self.i2cBus.read_byte_data(addr_ADXL345, BW_RATE)
		temp = bw
		current = current & int('11110000',2)
		temp = current | temp
		self.i2cBus.write_byte_data(addr_ADXL345, BW_RATE, temp)
		self.BW = bw
		
		# Set Power Mode
		current = self.i2cBus.read_byte_data(addr_ADXL345, POWER_CTL)
		current = current & int('11110111',2)
		temp = current | pwr
		self.i2cBus.write_byte_data(addr_ADXL345, POWER_CTL, temp)
		self.Power = pwr
		
	def read_accel(self):
		d = [0,0]
		acceleration = [0,0,0]
		self.i2cBus.write_quick(addr_ADXL345)
		#time.sleep(0.010)
		d = self.i2cBus.read_i2c_block_data(addr_ADXL345, AXES_DATA,6)
		
		for i in range(3):
			temp = (d[2*i+1] << 8) | d[2*i]
			if(temp & (1 << 16 - 1)):
				temp = temp - (1<<16)
			temp2 = temp * SCALE_MULTIPLIER * self.Range * 0.5
			acceleration[i] = round(temp2, 4)

		return acceleration 
