import deviceConfig

import RPi.GPIO as GPIO

class Leds:

	def __init__(self):

		GPIO.setup(deviceConfig.pinStatusError, GPIO.OUT)
		GPIO.setup(deviceConfig.pinStatusOk, GPIO.OUT)
		GPIO.setup(deviceConfig.pinStatusAdHoc, GPIO.OUT)
		
	#Leds Funtions
	def setLedsOn(self):

		self.setLeds(True,True,True)

	def setLedsOff(self):

		self.setLeds(False,False,False)

	def setLedsOk(self):

		self.setLeds(False,True,False)

	def setLedsError(self):

		self.setLeds(True,False,False)

	def setLedsAdhoc(self):

		self.setLeds(False,False,True)

	def setLeds(self, valuePinStatusError, valuePinStatusOk, valuePinStatusAdHoc):

		GPIO.output(deviceConfig.pinStatusError, valuePinStatusError)
		GPIO.output(deviceConfig.pinStatusOk, valuePinStatusOk)
		GPIO.output(deviceConfig.pinStatusAdHoc, valuePinStatusAdHoc)
        