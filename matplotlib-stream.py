"""
matplotlib-stream.py

Display ADXL345 I2C data to the Raspberry Pi using Python (matplotlib)

Author: Diego Aulet-Leon
"""
import new;print(new.__file__)
import time
from collections import deque
import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import dates
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import datetime

import ADXL345

# Variables
MAX_LENGTH = 25
ACC_RANGE = 16
  
# plot class
class AnalogPlot:
	# constr
	def __init__(self, Gs, maxLen):
		
		# open i2c port
		self.ser = ADXL345.ADXL345(Gs, ADXL345.BW_RATE_1600HZ, ADXL345.MEASURE)

		self.ax = deque([0.0]*maxLen)
		self.ay = deque([0.0]*maxLen)
		self.az = deque([0.0]*maxLen)
		self.amag = deque([0.0]*maxLen)
		self.maxLen = maxLen

	# add to buffer
	def addToBuf(self, buf, val):
		if len(buf) < self.maxLen:
			buf.append(val)
		else:
			buf.pop()
			buf.appendleft(val)

	# add data
	def add(self, data):
		assert(len(data) == 4)
		self.addToBuf(self.ax, data[0])
		self.addToBuf(self.ay, data[1])
		self.addToBuf(self.az, data[2])
		self.addToBuf(self.amag, data[3])

	# update plot
	def update(self, frameNum, a0, a1, a2, a3):
		try:
			data = self.ser.read_accel()
			mag = round(np.linalg.norm(data),4)
			data.append(mag)
			#print data
			if(len(data) == 4):
				self.add(data)
				a0.set_data(range(self.maxLen), self.ax)
				a1.set_data(range(self.maxLen), self.ay)
				a2.set_data(range(self.maxLen), self.az)
				a3.set_data(range(self.maxLen), self.amag)
		except KeyboardInterrupt:
			print('exiting')

		return a0, 

# main() function
def main():
	# plot parameters
	analogPlot = AnalogPlot(ACC_RANGE, MAX_LENGTH)

	print('plotting data...')

	# set up animation
	fig = plt.figure()
	ax = plt.axes(xlim=(0, MAX_LENGTH), ylim=(-1*ACC_RANGE, ACC_RANGE))
	a0, = ax.plot([], [], label="x-axis")
	a1, = ax.plot([], [], label="y-axis")
	a2, = ax.plot([], [], label="z-axis")
	a3, = ax.plot([], [], label="Magnitude")
	
	ax.xaxis.set_major_locator(MultipleLocator(5))
	ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
	ax.xaxis.set_minor_locator(MultipleLocator(1))

	ax.yaxis.set_major_locator(MultipleLocator(ACC_RANGE*0.25))
	ax.yaxis.set_minor_locator(MultipleLocator(ACC_RANGE))

	ax.xaxis.grid(True,'minor')
	ax.yaxis.grid(True,'minor')
	ax.xaxis.grid(True,'major',linewidth=2)
	ax.yaxis.grid(True,'major',linewidth=2)
	
	fontP = FontProperties()
	fontP.set_size('small')
	plt.legend(prop = fontP)
	
	anim = animation.FuncAnimation(fig, analogPlot.update,
									fargs=(a0, a1, a2, a3),
									interval=1)

	plt.grid()
	# show plot
	plt.show()

	print('exiting.')
  

# call main
if __name__ == '__main__':
	main()
