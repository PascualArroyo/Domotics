#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import deviceConfig
import time

class Rele:

	#Rele
	valueRele = 0

	def __init__(self):

		GPIO.setup(deviceConfig.pinRele, GPIO.OUT)
		GPIO.setup(deviceConfig.pinReleLed, GPIO.OUT)
		GPIO.setup(deviceConfig.pinReleButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		GPIO.add_event_detect(deviceConfig.pinReleButton, GPIO.FALLING, callback=self.buttonReleCallback, bouncetime=500)

	def getValue(self):
		
		return self.valueRele

	def setValue(self, value):

		self.valueRele = int(value)
		GPIO.output(deviceConfig.pinRele, self.valueRele)
		GPIO.output(deviceConfig.pinReleLed, self.valueRele)
  			
  		return self.valueRele

  	#Button rele
	def buttonReleCallback(self, channel):

		print "Rele"

		time.sleep(0.2)

		if GPIO.input(channel) == GPIO.LOW:

			print "Rele confirmacion"

			if self.valueRele == 0:
				self.valueRele = 1
			else:
				self.valueRele = 0

			GPIO.output(deviceConfig.pinRele, self.valueRele)
			GPIO.output(deviceConfig.pinReleLed, self.valueRele)
        