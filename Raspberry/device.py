#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyjsonrpc
import socket, struct, fcntl
import os
import deviceConfig
import urllib2
import json

from remote import Remote
from rele import Rele
from camera import Camera
from sensors import Sensors
from leds import Leds
from sounds import Sounds

from random import randint
import RPi.GPIO as GPIO

from datetime import datetime
from apscheduler.scheduler import Scheduler

import time
import threading

class Device:

	#Sensors
	sensors = 0

	#Remote
	NRF24 = 0 #Remoto
	devicesRemote = [] #Dispositivos remotos

	#Rele
	rele = 0

	#Rele
	camera = 0
	
	#Status
	connectionStatus = 0 #0 offline, 1 online, 2 portNotOpen
	alarmMode = 0 #0 No, 1 Yes

	#Leds
	leds = 0

	#Sounds
	sounds = 0

	#Port and IPs
	port = 0
	publicIp = 0
	privateIp = 0

	#Code security
	currentCode = str(randint(10000,99999999))
	previousCode = currentCode
	numberOfPetitions = 0

	#Type Device
	typeDevice = 0
	

#################################################################################################################################################
#################################################################################################################################################
#####################################################      SECTION DOMOTICS SERVER      #########################################################
#################################################################################################################################################
#################################################################################################################################################

	
	def __init__(self):

		print "Arranca Domotics"

		#Configuramos el los pines GPIO
		GPIO.setwarnings(False)

		GPIO.setmode(GPIO.BCM)

		GPIO.setup(deviceConfig.pinResetButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
		GPIO.setup(deviceConfig.pinIRSensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

		self.leds = Leds()
		#Cuando se encienda el dispositivo se encenderan todos los leds
		self.leds.setLedsOn()

		self.sounds = Sounds()

		#Configuracion del evento para el reset
		GPIO.add_event_detect(deviceConfig.pinResetButton, GPIO.FALLING, callback=self.buttonResetCallback, bouncetime=500)

		time.sleep(1)
		#Una vez pasa 1 segundo se mantiene encendida solo la luz de error hasta que consiga conectarse a internet y montar el servidor
		
		self.leds.setLedsError()

		print "Solicitamos codigo se seguridad"

		self.updateSecurityCode()

		print "¡¡¡Tenemos codigo!!!"

		self.updateVersionDevice(deviceConfig.deviceId)

		self.updateSoftware()

		self.port = int(self.getPort()) #obtenemos el puerto
		print self.port

		self.privateIp = self.getPrivateIp() #Obtenemos la ip privada
		print self.privateIp

		class RequestHandler(pyjsonrpc.HttpRequestHandler):
			# Register public JSON-RPC methods
			methods = {
    			"switchGetValue": self.switchGetValue,
    			"switchSetValue": self.switchSetValue,
        		"sensorGetValues": self.sensorGetValues,
        		"cameraGetPhoto": self.cameraGetPhoto,
        		"cameraGetPhotoForMail": self.cameraGetPhotoForMail,
        		"installRemoteDevice": self.installRemoteDevice,
        		"setDeviceAlarmMode": self.setDeviceAlarmMode,
        		"quitDeviceAlarmMode": self.quitDeviceAlarmMode
    		}

		# Threading HTTP-Server
		http_server = pyjsonrpc.ThreadingHttpServer(
    		server_address = (self.privateIp, self.port),
    		RequestHandlerClass = RequestHandler
		)
		
		print "Creado servidor"

		# Start the scheduler
		sched = Scheduler()
		sched.start()

		# Schedule sendStatus every 1 minutes
		sched.add_interval_job(self.sendStatus, minutes=1)

		# Schedule updateSecurityCode every 1 hours
		sched.add_interval_job(self.updateSecurityCode, hours=1)

		# Schedule updateSoftware every 24 hours
		sched.add_interval_job(self.updateSoftware, hours=24)

		#Obtenemos del servidor el tipo de dispositivo que es y inicializamos
		self.typeDevice = int(self.getTypeDevice())

		print self.typeDevice

		#Remote Device
		if self.typeDevice == 0:

			self.NRF24 = Remote()
			sched.add_interval_job(self.newReadingSensors, hours=1)
			
		#Rele device
		elif self.typeDevice == 1:
			self.rele = Rele()

		#Camera device
		elif self.typeDevice == 2:
			self.camera = Camera()

		#Sensors device
		elif self.typeDevice == 4:

			self.sensors = Sensors()
			sched.add_interval_job(self.newReadingSensors, hours=1)

		print "Actualizamos estado dispositivo"

		## Actualizamos el estado del dispositivo
		self.sendStatus()

		#Temporizador para guadar datos de sensores
		if self.typeDevice == 0 or self.typeDevice == 4:

			self.newReadingSensors()

		#Configuracion del evento para el detector de presencia
		GPIO.add_event_detect(deviceConfig.pinIRSensor, GPIO.RISING, callback=self.IRSensorDetectCallback, bouncetime=10000)
		
		print "Listo para arracar el servidor"

		self.sounds.start()

		#print myconfig.urlDb
		print "Starting HTTP server ..."
		print "URL: http://%s:%d" % (self.privateIp, self.port)

		try:
 			http_server.serve_forever()

		except KeyboardInterrupt:
		    http_server.shutdown()
		    self.leds.setLedsError()

		except:
			self.leds.setLedsError()
			time.sleep(10)
			os.system('sudo reboot')

		print "Stopping HTTP server ..."


#################################################################################################################################################
#################################################################################################################################################
#####################################################       SECTION INSTALL DEVICE      #########################################################
#################################################################################################################################################
#################################################################################################################################################

	def buttonResetCallback(self, channel):

		print "Reset"

		time.sleep(1)

		if GPIO.input(channel) == GPIO.LOW:

			buttonAlwaysPressed = 1

			for i in range(10):

				if GPIO.input(channel) == GPIO.LOW:
					self.leds.setLedsOn()
					
					time.sleep(0.2)
					self.sounds.on()
					time.sleep(0.1)
					self.sounds.off()
					time.sleep(0.2)
					
					self.leds.setLedsOff()
					
					time.sleep(0.5)

				else:

					buttonAlwaysPressed = 0
			
					
			if GPIO.input(channel) == GPIO.LOW and buttonAlwaysPressed == 1:
						
				self.leds.setLedsAdhoc()

				os.system('sudo cp /home/pi/Domotics/Default/bootInstall.py /home/pi/Domotics/bootConfig.py')
						
				os.system('sudo cp /home/pi/Domotics/Default/network/adhoc/dhcpd.conf /etc/dhcp/dhcpd.conf')
				os.system('sudo cp /home/pi/Domotics/Default/network/adhoc/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')


				#Eliminamos fichero de configuracion
				os.system('sudo rm /etc/network/interfaces')
				

				nameWIFI = "Domotics%d" % (randint(1000,9999))
				#Creamos el fichero de configuración en base a la plantilla y rellenamos el nombre de la red adhoc
				with open("/etc/network/interfaces", "wt") as fout:
					with open("/home/pi/Domotics/Default/network/adhoc/interfaces", "rt") as fin:
						for line in fin:
							fout.write(line.replace('<NAME>', nameWIFI))


				self.sounds.reset()

				time.sleep(2)

				os.system('sudo reboot')

			else:

				self.leds.updateLeds(self.connectionStatus, self.alarmMode)



	def installRemoteDevice(self, idDevice, pipeSend, pipeRecv, code):


		if (self.currentCode == code or self.previousCode == code) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:


			#Eliminamos el software anterior
			os.system('sudo rm /home/pi/Domotics/Arduino/src/domotics.ino')
			
			#Configuramos el nuevo software con el valor del pipeSend y el pipeRecv
			with open("/home/pi/Domotics/Arduino/src/domotics.ino", "wt") as fout:
				with open("/home/pi/Domotics/Default/domoticsAux.ino", "rt") as fin:
					for line in fin:
						fout.write(line.replace('<PIPE_SEND>', pipeSend).replace('<PIPE_RECV>', pipeRecv))

			#Cambiamos la ruta en la que esta el Software Arduino
			os.chdir('/home/pi/Domotics/Arduino')

			#Limpiamos el proyecto
			#os.system('sudo ino clean')

			#Compilamos
			os.system('sudo ino build -m leonardo')

			#Subimos el binario al ardino
			os.system('sudo ino upload -m leonardo')

			self.updateVersionDevice(idDevice)

			self.sendStatus()

			return 1

		else:

			self.numberOfPetitions += 1
			
			return -1

#################################################################################################################################################
#################################################################################################################################################
#####################################################       SECTION SECURITY CODE       #########################################################
#################################################################################################################################################
#################################################################################################################################################

	def updateSecurityCode(self):
		
		self.previousCode = self.currentCode
		self.currentCode = str(randint(10000,99999999))

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("updateSecurityCode", deviceConfig.deviceId, self.currentCode, self.previousCode)
 
		while result == 0:

			time.sleep(5)
			result = rpc_client("updateSecurityCode", deviceConfig.deviceId, self.currentCode, self.previousCode)
			print "Intentamos enviar el codigo de seguridad"


		return result


#################################################################################################################################################
#################################################################################################################################################
################################################       SECTION GET DEVICE IP & PORT       #######################################################
#################################################################################################################################################
#################################################################################################################################################

	# private IP
	def getPrivateIp(self):

		success = False
		privateIp = 0

		while success == False:

			try:

				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
				s.connect_ex(('<broadcast>', 0))

				privateIp = s.getsockname()[0]
			
				success = True

			except:

				success = False

				self.connectionStatus = 0
				self.leds.setLedsError()
				time.sleep(1)


		return privateIp
	
	# public IP
	def getPublicIp(self):

		success = False
		publicIp = 0
 
		while success == False:

			try:

				publicIp = json.load(urllib2.urlopen('http://httpbin.org/ip'))['origin']
				success = True

			except:

				self.connectionStatus = 0
				self.leds.setLedsError()
				time.sleep(1)

				try:

					publicIp = json.load(urllib2.urlopen('http://jsonip.com'))['ip']
					success = True

				except:

					self.connectionStatus = 0
					self.leds.setLedsError()
					time.sleep(1)

					try:

						publicIp = json.load(urllib2.urlopen('https://api.ipify.org/?format=json'))['ip']
						success = True

					except:

						success = False
						self.connectionStatus = 0
						self.leds.setLedsError()
						time.sleep(1)


		return publicIp


	# Port
	def getPort(self):

		success = False
		port = 0

		while success == False:

			try:
				rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
				port = rpc_client("getPort", deviceConfig.deviceId, self.currentCode)['port']
			
				success = True

			except:
				success = False

				self.connectionStatus = 0
				self.leds.setLedsError()
				time.sleep(1)

		return port


	def checkPortConnection(self, port, publicIp):

		# Setup socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(1)

		connectionStatus = 2
		
		try:
			sock.connect((publicIp, port))
		
		except Exception,e:
			
			rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
			result = rpc_client("checkPort", publicIp, port)

			if result:
				#print "Port is open"
				connectionStatus = 1
   			
			else:
				#print "Port is not open"
				connectionStatus = 2
		
		else:
			#print "Port is open"
			connectionStatus = 1

		sock.close()

		self.leds.updateLeds(connectionStatus, self.alarmMode)

		return connectionStatus

	

#################################################################################################################################################
#################################################################################################################################################
#######################################################      SECTION SEND STATUS     ############################################################
#################################################################################################################################################
#################################################################################################################################################

	def getDevicesRemote(self):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		devicesRemote = rpc_client("getDevicesRemote", deviceConfig.deviceId, self.currentCode)
		
		return devicesRemote

	def getTypeDevice(self):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("getTypeDevice", deviceConfig.deviceId, self.currentCode)

		return result['type']

	def updateDeviceIp(self):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("updateIp",self.publicIp, self.privateIp, deviceConfig.deviceId, self.currentCode)

		return result

	def deviceOnline(self, idDevice):
		
		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("deviceOnline", self.connectionStatus, idDevice, self.currentCode)

		return result


	def sendStatus(self):
	
		#Actualizamos el contador de peticiones
		self.numberOfPetitions = 0

		#optenemos los parametros de la red
		publicIp = self.getPublicIp()
		privateIp = self.getPrivateIp()
		port = int(self.getPort()) 

		#Si cambian la dirección pridava o el puerto reiniamos el Software
		if (self.privateIp != privateIp or self.port != port):
			#Reiniciamos el Software para que se adapte al cambio de ips o puertos
			os.system('sudo /etc/init.d/domotics_device restart')


		#Si cambia la IP publica lo comunicamos al servidor
		if self.publicIp != publicIp:
			
			self.publicIp = publicIp

			self.updateDeviceIp()


		#Comprobamos el estado de los puertos
		self.connectionStatus = self.checkPortConnection(port, publicIp)

		#Comprobamos el estado de los dipositivos remotos
		if self.typeDevice == 0:

			self.devicesRemote = self.getDevicesRemote()

			for deviceRemote in self.devicesRemote:

				print deviceRemote['id']

				while self.NRF24.transmit == 1:
					time.sleep(0.1)

				self.NRF24.transmit = 1
				
				value = self.NRF24.transmitInt(deviceRemote['pipeSend'], deviceRemote['pipeRecv'], "0") #Pide estado del dispositivo remoto

				self.NRF24.transmit = 0

				print value

				#Si value es 1 se ha detectado movimiento
  				if value == 1:
  					self.deviceOnline(deviceRemote['id'])
  					self.motionDetected(deviceRemote['id'])

  				#Si value es 0 el dispositivo se encuentra conectado
  				elif value == 0:
  					self.deviceOnline(deviceRemote['id'])

  				#Si value es -1 no hacemos nada por que el dispositivo no se encuentra en el alcance de la centralita


  				#Si el dispositivo remoto esta en alcance y es rele comprobamos si tiene algun temporizador que activar
  				if value != -1 and deviceRemote['type'] == 1:

  					action = self.automation(deviceRemote['id'])

  					print "Temporizador"
  					print action

  					if action != -1:
  						print "Ahora Siiiiiiii"
 
  						self.setRele(deviceRemote['pipeSend'], deviceRemote['pipeRecv'], action) 


  		#Si el dispositivo es Rele comprobamos si tiene temporizadores que activar
  		elif self.typeDevice == 1:

			action = self.automation(deviceConfig.deviceId)

			if action != -1:

				self.setRele("0","0", action)


		#Enviamos el estado del dispositivo
		result = self.deviceOnline(deviceConfig.deviceId)
			
		return result
	

#################################################################################################################################################
#################################################################################################################################################
###########################################################       SECTION RELE      #############################################################
#################################################################################################################################################
#################################################################################################################################################

	#Get status rele
	def getRele(self, pipeSend, pipeRecv):

		if pipeSend == "0":
			value = self.rele.getValue()
			
		else:
			comand = "1" #Leer valor Rele remoto

			while self.NRF24.transmit == 1:
				time.sleep(0.1)

			self.NRF24.transmit = 1

			value = self.NRF24.transmitInt(pipeSend, pipeRecv, comand)

			self.NRF24.transmit = 0

		return value

	def switchGetValue(self, pipeSend, pipeRecv, code):

		if (self.currentCode == code or self.previousCode == code) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:

			value = self.getRele(pipeSend, pipeRecv)

  		else:

  			self.numberOfPetitions += 1
			value = -1

		return value


	#Set status rele
	def setRele(self, pipeSend, pipeRecv, value):

		if pipeSend == "0":
			value = self.rele.setValue(value)
		
		else:

			if str(value) == "1":
				#ON
				comando = "2"
			else:
				#OFF
				comando = "3"

			while self.NRF24.transmit == 1:
				time.sleep(0.1)

			self.NRF24.transmit = 1
				
			value = self.NRF24.transmitInt(pipeSend, pipeRecv, comando)

			self.NRF24.transmit = 0

		return value

	
	def switchSetValue(self, pipeSend, pipeRecv, value, code):

		if (self.currentCode == code or self.previousCode == code) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:

			value = self.setRele(pipeSend, pipeRecv, value)

  		else:

  			self.numberOfPetitions += 1
			value = -1

		return value


	#Automation rele
	def automation(self, idDevice):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("automation", idDevice, self.currentCode)

		return result



#################################################################################################################################################
#################################################################################################################################################
##########################################################       SECTION SENSORS      ###########################################################
#################################################################################################################################################
#################################################################################################################################################


	def getSensors(self, pipeSend, pipeRecv):

		if pipeSend == "0":
			
			values = self.sensors.getSensorsValues()
		
		else:

			comando = "4"
	
			while self.NRF24.transmit == 1:
				time.sleep(0.1)

			self.NRF24.transmit = 1
				
			values = self.NRF24.transmitStringJSON(pipeSend, pipeRecv, comando)

			self.NRF24.transmit = 0

		return values

	
	def sensorGetValues(self, pipeSend, pipeRecv, code):

		if (self.currentCode == code or self.previousCode == code) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:
			
			valueSensors = self.getSensors(pipeSend, pipeRecv)

			print valueSensors
			
			return valueSensors

		else:

			self.numberOfPetitions += 1
			
			return {"error":"error"}


	def newReadingSensors(self):

		print "newReadingSensors"

		if self.typeDevice == 4:

			valueSensors = self.getSensors("0", "0")

			rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
			rpc_client("newReadingSensors", valueSensors['temp'], valueSensors['hum'], valueSensors['pres'], valueSensors['lux'], deviceConfig.deviceId)

		elif self.typeDevice == 0:

			for deviceRemote in self.devicesRemote:

				print deviceRemote['id']

				if deviceRemote['type'] == 4:
					
					valueSensors = self.getSensors(deviceRemote['pipeSend'], deviceRemote['pipeRecv'])

					print valueSensors

    				if 'error' not in valueSensors:
						rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
						rpc_client("newReadingSensors", valueSensors['temp'], valueSensors['hum'], valueSensors['pres'], valueSensors['lux'], deviceRemote['id'])



#################################################################################################################################################
#################################################################################################################################################
##########################################################       SECTION CAMERA      ############################################################
#################################################################################################################################################
#################################################################################################################################################

	def cameraGetPhoto(self, width, height, time, quality, exposure, brightness, code):

		if (self.currentCode == code or self.previousCode == code) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:
		
			return self.camera.getCameraImg(width, height, time, quality, exposure, brightness)
			
		else:

			self.numberOfPetitions += 1

			return -1

	def cameraGetPhotoForMail(self, code):

		return self.cameraGetPhoto("640", "480", "2000", "50", "auto", "55", str(code))



#################################################################################################################################################
#################################################################################################################################################
#######################################################      SECTION MOTION DETECT     ##########################################################
#################################################################################################################################################
#################################################################################################################################################


	def IRSensorDetectCallback(self, channel):

		print "IRSensor"

		t = threading.Thread(target=self.motion, args=(channel,))
		t.start()


	def motion(self, channel):

		print "Sensor"
		time.sleep(2)

		if GPIO.input(channel) == GPIO.HIGH:

			print "Sensor confirmacion"

			self.motionDetected(deviceConfig.deviceId)

	def motionDetected (self, idDevice):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("motionDetected", idDevice, self.currentCode)

		if result == 1:

			if self.alarmMode != 1:
				
				self.alarmMode = 1
				
				t = threading.Thread(target=self.soundAlarm)
				t.start()

				self.leds.updateLeds(self.connectionStatus, self.alarmMode)





#################################################################################################################################################
#################################################################################################################################################
###########################################################       SECTION ALARM      ############################################################
#################################################################################################################################################
#################################################################################################################################################


	def setDeviceAlarmMode(self, code):

		print code

		print "Alarm mode"

		if (self.currentCode == str(code) or self.previousCode == str(code)) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:

			print "Alarm mode confirmado"

			print self.alarmMode

			if self.alarmMode != 1:
				
				self.alarmMode = 1
				
				t = threading.Thread(target=self.soundAlarm)
				t.start()

				self.leds.updateLeds(self.connectionStatus, self.alarmMode)

			return 1

		else:

			self.numberOfPetitions += 1

			return -1


	def setDeviceOtherLocationNotification(self, code):

		if (self.currentCode == str(code) or self.previousCode == str(code)) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:

			if self.alarmMode != 1:

				for i in range(3):
					self.sounds.on()
					time.sleep(0.5)
					self.sounds.off()

			return 1

		else:

			self.numberOfPetitions += 1

			return -1


	def quitDeviceAlarmMode(self, code):

		print code

		print "Quitar alarma" 

		if (self.currentCode == str(code) or self.previousCode == str(code)) and self.numberOfPetitions < deviceConfig.maxNumberOfPetitions:

			print "Quitar alarma confirmado" 

			print self.alarmMode

			self.alarmMode = 0

			self.leds.updateLeds(self.connectionStatus, self.alarmMode)

			return 1

		else:

			self.numberOfPetitions += 1

			return -1



	def soundAlarm(self):

		i = 0
		
		while self.alarmMode == 1:

			if i == 0:

				rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
				self.alarmMode = rpc_client("deviceStatusSecurity", deviceConfig.deviceId, self.currentCode)
				self.leds.updateLeds(self.connectionStatus, self.alarmMode)

				print self.alarmMode

			else:
		 	
		 		self.sounds.on()
				time.sleep(0.5)
				self.sounds.off()
				time.sleep(0.5)

				if i >= 10:
					
					i = 0
					time.sleep(5)

			i = i + 1




#################################################################################################################################################
#################################################################################################################################################
#####################################################       SECTION UPDATE SOFTWARE      ########################################################
#################################################################################################################################################
#################################################################################################################################################


	def updateSoftware(self):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("updateSoftwareDevice", deviceConfig.deviceId, self.currentCode)

		if result != 0:

			idDevice = deviceConfig.deviceId
			
			keylist = result.keys()

			#Guardamos todos los ficheros que vienen en el json
			for key in keylist:
				f = open(key, 'w+')
				f.write(result[key].decode("base64"))
				f.close()

			#Eliminamos el fichero actual de configuracion
			os.system('sudo rm /home/pi/Domotics/deviceConfig.py')

			#Configuramos el fichero plantilla de configuracion con el valor del id del dispositivo
			with open("/home/pi/Domotics/deviceConfig.py", "wt") as fout:
				with open("/home/pi/Domotics/Default/deviceConfigAux.py", "rt") as fin:
					for line in fin:
						fout.write(line.replace('<DEVICE_ID>', idDevice))

			#Reiniciamos el Software que acabamos de instalar
			os.system('sudo /etc/init.d/domotics_device restart')



	def updateVersionDevice(self,idDevice):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("updateVersionDevice", deviceConfig.version, idDevice, self.currentCode)

		return result


Device()