#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTU21D import HTU21D
from TSL2561 import TSL2561
from BMP085 import BMP085


class Sensors:

	#Sensors
	tsl = 0
	htu = 0
	bmp = 0

	def __init__(self):

		self.tsl = TSL2561()
		self.htu = HTU21D()
		self.bmp = BMP085()

	def getSensorsValues(self):

		temp = "%.2f" % self.htu.read_tmperature()
		hum = "%.2f" % self.htu.read_humidity()
		pres = "%.2f" % (self.bmp.read_pressure()/100.0)
		lux = "%.2f" % self.tsl.readLux()
			
		return {"temp":temp, "hum":hum, "pres": pres, "lux":lux}