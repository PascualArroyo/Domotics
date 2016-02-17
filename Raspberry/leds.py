import deviceConfig

import RPi.GPIO as GPIO

class Leds:

	def __init__(self):

		GPIO.setup(deviceConfig.pinStatusError, GPIO.OUT)
		GPIO.setup(deviceConfig.pinStatusOk, GPIO.OUT)
		GPIO.setup(deviceConfig.pinStatusAdHoc, GPIO.OUT)


	def setLeds(self, valuePinStatusError, valuePinStatusOk, valuePinStatusAdHoc):

		GPIO.output(deviceConfig.pinStatusError, valuePinStatusError)
		GPIO.output(deviceConfig.pinStatusOk, valuePinStatusOk)
		GPIO.output(deviceConfig.pinStatusAdHoc, valuePinStatusAdHoc)
		
	#Leds Funtions status
	def setLedsOn(self):

		self.setLeds(True,True,True)

	def setLedsOff(self):

		self.setLeds(False,False,False)

	def setLedsOnLine(self):

		self.setLeds(False,True,False)

	def setLedsNotOpenPort(self):

		self.setLeds(False,True,True)

	def setLedsError(self):

		self.setLeds(True,False,False)

	def setLedsAdhoc(self):

		self.setLeds(False,False,True)


	def setLedsAlarm(self):

		GPIO.output(deviceConfig.pinStatusError, True)

	def setLedsNotAlarm(self):

		GPIO.output(deviceConfig.pinStatusError, False)


	def updateLeds(self, statusConnection, motionDetected):

		if statusConnection == 0:

			self.setLedsError()

		elif statusConnection == 1:

			self.setLedsOnLine()

		elif statusConnection == 2:

			self.setLedsNotOpenPort()


		if motionDetected == 0 and statusConnection != 0:

			self.setLedsNotAlarm()

		elif motionDetected == 1:
			
			self.setLedsAlarm()




        