#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyjsonrpc
import socket, struct, fcntl
import os
import deviceConfig
import urllib2
import json

from utils import Utils
from leds import Leds

from random import randint
import RPi.GPIO as GPIO

from datetime import datetime
from apscheduler.scheduler import Scheduler
from HTU21D import HTU21D
from TSL2561 import TSL2561
import Adafruit_BMP.BMP085 as BMP085

from nrf24 import NRF24
import time

class Device:

	sendOrder = 1
	sendStatus = 1
	valueRele = 0
	radio = 0
	status = 1

	leds = 0
	
	devicesRemote = []
	
	def __init__(self):

		#Configuramos el los pines GPIO
		GPIO.setwarnings(False)

		GPIO.setmode(GPIO.BCM)

		GPIO.setup(deviceConfig.pinReset, GPIO.IN)
		GPIO.setup(deviceConfig.pinSensor, GPIO.IN)

		self.leds = Leds()
		#Cuando se encienda el dispositivo se encenderan todos los leds
		self.leds.setLedsOn()

		#Configuracion del evento para el reset
		GPIO.add_event_detect(deviceConfig.pinReset, GPIO.RISING, callback=self.my_callback_reset, bouncetime=300)

		#Configuracion del evento para el detector de presencia
		GPIO.add_event_detect(deviceConfig.pinSensor, GPIO.RISING, callback=self.my_callback_sensor, bouncetime=300)

		time.sleep(1)
		#Una vez pasa 1 segundo se mantiene encendida solo la luz de error hasta que consiga conectarse a internet y montar el servidor
		
		self.leds.setLedsError()
		
		querry = self.getPort()

		while querry == False:
			#print "No hay conexion a internet, o el servidor central esta caido"
			time.sleep(1)
			querry = self.getPort()

		port = int(querry['port']) #Consultamos del servidor sobre que puerto debemos montar el servicio que presta este dispositivo

		ip = self.getNetworkIp() #Obtenemos la ip

		class RequestHandler(pyjsonrpc.HttpRequestHandler):
			# Register public JSON-RPC methods
			methods = {
    			"switchGetValue": self.switchGetValue,
    			"switchSetValue": self.switchSetValue,
        		"sensorGetValues": self.sensorGetValues,
        		"cameraGetPhoto": self.cameraGetPhoto,
        		"cameraGetPhotoForMail": self.cameraGetPhotoForMail
    		}

		# Threading HTTP-Server
		http_server = pyjsonrpc.ThreadingHttpServer(
    		server_address = (ip, port),
    		RequestHandlerClass = RequestHandler
		)


		# Start the scheduler
		sched = Scheduler()
		sched.start()

		# Schedule sendStatus every one minutes
		sched.add_interval_job(self.sendStatus, minutes=1)

		#Obtenemos del servidor el tipo de dispositivo que es y inicializamos
		querry = self.getTypeDevice()
		typeDevice = int(querry['type'])

		
		#Remote Device
		if typeDevice == 0:

			#Preparamos la configuración de la comunicación por radio
			self.radio = NRF24()
			self.radio.begin(0, 0, 25, 18) #Set CE and IRQ pins
			self.radio.setRetries(15,15)
			self.radio.setPayloadSize(32)
			self.radio.setChannel(0x4c)
			self.radio.setPALevel(NRF24.PA_MAX)
			self.radio.powerUp()

			#Obtenemos todos los dispositivos
			self.devicesRemote = self.getDevicesRemote()

			#Actualizamos el puerto de cada dispositivo remoto
			for deviceRemote in self.devicesRemote:
				self.setRemotePort(deviceRemote['id'], port)
			
		#Rele device
		elif typeDevice == 1:
			GPIO.setup(deviceConfig.pinRele, GPIO.OUT)


		## Actualizamos el estado del dispositivo
		self.sendStatus()

		#print myconfig.urlDb
		print "Starting HTTP server ..."
		print "URL: http://%s:%d" % (ip, port)


		#Encendemos solo el led de estado ok
		self.leds.setLedsOk()

		try:
 			http_server.serve_forever()	
		except KeyboardInterrupt:
		    http_server.shutdown()
		    self.leds.setLedsError()
		print "Stopping HTTP server ..."


	def my_callback_reset(self, channel):

		#print "Reset"

		time.sleep(1)

		if GPIO.input(channel) == GPIO.LOW:
			
			valuePinStatusError = GPIO.input(deviceConfig.pinStatusError);
			valuePinStatusOk = GPIO.input(deviceConfig.pinStatusOk);
			valuePinStatusAdHoc = GPIO.input(deviceConfig.pinStatusAdHoc);

			buttonAlwaysPressed = 1

			for i in range(5):

				if GPIO.input(channel) == GPIO.LOW:
					self.leds.setLedsOn()
					time.sleep(0.5)
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

				os.system('sudo cp /home/pi/Domotics/Default/network/adhoc/interfaces /etc/network/interfacesAUX')

				nameWIFI = "Domotics%d" % (randint(1000,9999))
				#Creamos el fichero de configuración en base a la plantilla y rellenamos el nombre de la red adhoc
				with open("/etc/network/interfaces", "wt") as fout:
					with open("/etc/network/interfacesAUX", "rt") as fin:
						for line in fin:
							fout.write(line.replace('<NAME>', nameWIFI))

				#Eliminamos la planilla
				os.system('sudo rm /etc/network/interfacesAUX')

				time.sleep(2)

				os.system('sudo reboot')

			else:

				self.leds.setLeds(valuePinStatusOk, valuePinStatusError, valuePinStatusAdHoc)


	
	def my_callback_sensor(self, channel):

		if GPIO.input(channel) == GPIO.LOW:

			if self.status == 1:
				self.status = 0

				self.leds.setLedsError()

				ip = self.getIp()
				rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
				rpc_client("deviceOnline", ip, self.status, deviceConfig.deviceId)


	# private IP
	def getNetworkIp(self):
	
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		s.connect(('<broadcast>', 0))
		
		return s.getsockname()[0]
	
	# public IP
	def getIp(self):
	
		response = urllib2.urlopen('http://httpbin.org/ip')
		data = json.load(response)  
	
		return data['origin']

	#### Status
	def sendStatus(self):

		ip = self.getIp()

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)

		for deviceRemote in self.devicesRemote:

			while self.sendStatus == 0:
				time.sleep(0.1)

			self.sendOrder = 0

			i = 0

			utils = Utils()

			pipe1 = utils.convert(deviceRemote['pipeSend'])
			pipe2 = utils.convert(deviceRemote['pipeRecv'])

			self.radio.openWritingPipe(pipe1)
			self.radio.openReadingPipe(1, pipe2) 

			self.radio.stopListening()
			self.radio.write("0")
			self.radio.startListening()


			while not self.radio.available([1]):

				time.sleep(0.250)
				i = i+1

  				if i > 10:
  					break

  			if i <= 10:
  				recv_buffer = []
  				self.radio.read(recv_buffer)
  				out = ''.join(chr(i) for i in recv_buffer)

  				value = str(out.strip('\0'))
  				
  				result = rpc_client("deviceOnline", ip, value, deviceRemote['id'])

		self.sendOrder = 1

		result = rpc_client("deviceOnline", ip, self.status, deviceConfig.deviceId)

		#Si la vez anterior ya se cancelo lo alarma ahora ponemos las luces en ok
		if self.status == 1:
			self.leds.setLedsOk()

		self.status = 1
		
		return result

	def getPort(self):

		try:
			rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
			result = rpc_client("getPort", deviceConfig.deviceId)
			return result

		except:
			pass
			return False

	def setRemotePort(self, idDevice, port):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("setRemotePort", idDevice, port)

		return result

	def getDevicesRemote(self):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("getDevicesRemote", deviceConfig.deviceId)

		return result

	def getTypeDevice(self):

		rpc_client = pyjsonrpc.HttpClient(url = deviceConfig.url)
		result = rpc_client("getTypeDevice", deviceConfig.deviceId)

		return result
	
	
	####### Domotics
	def switchGetValue(self, pipeSend, pipeRecv, idDevice):

		if deviceConfig.deviceId == idDevice:

			if pipeSend == "0":
				value = self.valueRele
			else:

				while self.sendOrder == 0:
					time.sleep(0.1)

				self.sendStatus = 0
			
				i = 0

				utils = Utils()

				pipe1 = utils.convert(pipeSend)
				pipe2 = utils.convert(pipeRecv)

				self.radio.openWritingPipe(pipe1)
				self.radio.openReadingPipe(1, pipe2) 


				while not self.radio.available([1]):

					if i%10==0:
						self.radio.stopListening()
  						self.radio.write("1")
  						self.radio.startListening()

  					time.sleep(0.250)
  					i = i+1


  					if i > 38:
  						break
  				
  				if i <= 38:
					recv_buffer = []
  					self.radio.read(recv_buffer)
  					out = ''.join(chr(i) for i in recv_buffer)
  					value = str(out.strip('\0'))
  				else:
  					value = "-1"

  				self.sendStatus = 1

  		else:
			value = "-1"


		return value
	
	def switchSetValue(self, pipeSend, pipeRecv, value, idDevice):

		if deviceConfig.deviceId == idDevice:

			if pipeSend == "0":
				self.valueRele = value
				GPIO.output(deviceConfig.pinRele, int(value))
		
			else:

				while self.sendOrder == 0:
					time.sleep(0.1)

				self.sendStatus = 0

				i = 0

				if value == "1":
					#ON
					comando = "2"
				else:
					#OFF
					comando = "3"

				utils = Utils()

				pipe1 = utils.convert(pipeSend)
				pipe2 = utils.convert(pipeRecv)

				self.radio.openWritingPipe(pipe1)
				self.radio.openReadingPipe(1, pipe2) 

				while not self.radio.available([1]):

					#Enviamos
					if i%10==0:
						self.radio.stopListening()
						self.radio.write(comando)
						self.radio.startListening()

					time.sleep(0.250)
					i = i+1

					if i > 28:
						break #No hemos recivido nada
  				
				if i <= 28:
					recv_buffer = []
 					self.radio.read(recv_buffer)
 					out = ''.join(chr(i) for i in recv_buffer)
 					value = str(out.strip('\0'))
 				else:
 					value = "-1"

  				self.sendStatus = 1

  		else:
  			value = "-1"


		return value
	
	def sensorGetValues(self, idDevice):
		
		if deviceConfig.deviceId == idDevice:

			htu = HTU21D()
			sensor = BMP085.BMP085()
			tsl=TSL2561()

			temp = htu.read_tmperature()
			hum = htu.read_humidity()
			pres = sensor.read_pressure()
			lux = tsl.readLux()
			
			return {"temp":temp, "hum":hum, "pres": pres, "lux":lux}

		else:
			
			return {"error":"error"}

	def cameraGetPhoto(self, width, height, quality, exposure, brightness, idDevice):

		if deviceConfig.deviceId == idDevice:

			# "Capturamos la imagen de la camara con el comando raspistill"
			os.system('raspistill -vf -hf -w "%s" -h "%s" -t 1000 -q "%s" -ex "%s" -br "%s" -ISO 800 -o capture.jpg' % (width, height, quality, exposure, brightness))
			# "Cargamos la imagen"
			f = open('capture.jpg', 'r+')

			jpgdata = f.read()

			f.close()

			#Base64
			return jpgdata.encode("base64")
		
		else:
			return {"error":"error"}

	def cameraGetPhotoForMail(self):

		# "Capturamos la imagen de la camara con el comando raspistill"
		os.system('raspistill -vf -hf -w 640 -h 480 -t 2000 -q 50 -ex auto -ISO 800 -br 55 -o capture.jpg')
		# "Cargamos la imagen"
		f = open('capture.jpg', 'r+')

		jpgdata = f.read()

		f.close()

		return jpgdata.encode("base64")

Device()