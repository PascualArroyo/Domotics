import deviceConfig
import time

import RPi.GPIO as GPIO

class Sounds:

	def __init__(self):

		GPIO.setup(deviceConfig.pinSound, GPIO.OUT)

	#Sound Funtions status
	def on(self):
		GPIO.output(deviceConfig.pinSound, 1)

	def off(self):
		GPIO.output(deviceConfig.pinSound, 0)


	def start(self):
		self.on()
		time.sleep(0.2)
		self.off()
		time.sleep(0.2)
		self.on()
		time.sleep(0.2)
		self.off()
		time.sleep(0.2)
		self.on()
		time.sleep(0.2)
		self.off()


	def reset(self):
		self.on()
		time.sleep(1)
		self.off()
