import bootConfig
import os

class Init:

	def __init__(self):

		if bootConfig.Mode == 1:
			os.system('sudo python /home/pi/Domotics/install.py &')
		else:
			os.system('sudo python /home/pi/Domotics/device.py &')

Init()