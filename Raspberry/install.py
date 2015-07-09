#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyjsonrpc
import socket, struct, fcntl
import os
import deviceConfig

from leds import Leds

import time

import RPi.GPIO as GPIO

class Install:

	leds = 0

	def __init__(self):

		class RequestHandler(pyjsonrpc.HttpRequestHandler):
			# Register public JSON-RPC methods
			methods = {
    			"installDevice": self.installDevice
    		}

		# Threading HTTP-Server
		http_server = pyjsonrpc.ThreadingHttpServer(
    		server_address = (deviceConfig.ipAdhoc, deviceConfig.portAdhoc),
    		RequestHandlerClass = RequestHandler
		)

		#print myconfig.urlDb
		print "Starting HTTP server ..."
		print "URL: http://%s:%d" % (deviceConfig.ipAdhoc, deviceConfig.portAdhoc)

		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		GPIO.setup(deviceConfig.pinReset, GPIO.IN)

		#Configuracion del evento para el reset
		GPIO.add_event_detect(deviceConfig.pinReset, GPIO.RISING, callback=self.exitAdhocMode, bouncetime=500)

		self.leds = Leds()

		#Cuando se encienda el dispositivo se encenderan todos los leds
		self.leds.setLedsOn()

		time.sleep(5)

		self.leds.setLedsAdhoc()

		try:
 			http_server.serve_forever()	
		except KeyboardInterrupt:
		    http_server.shutdown()
		    self.leds.setLedsError()

		print "Stopping HTTP server ..."


	#Metodo para configurar un dispositivo
	def installDevice(self, network, nameWIFI, passwordWIFI, deviceId):

		#Configuracion de conexion a intenet
		print network

		if network == "0": #Ethernet
						
			os.system('sudo cp /home/pi/Domotics/Default/network/ethernet/dhcpd.conf /etc/dhcp/dhcpd.conf')
			os.system('sudo cp /home/pi/Domotics/Default/network/ethernet/interfaces /etc/network/interfaces')
			os.system('sudo cp /home/pi/Domotics/Default/network/ethernet/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
						
		else:

			os.system('sudo cp /home/pi/Domotics/Default/network/wifi/dhcpd.conf /etc/dhcp/dhcpd.conf')
			os.system('sudo cp /home/pi/Domotics/Default/network/wifi/interfaces /etc/network/interfaces')

			#Segun el tipo de seguridad seleccionamos una plantilla distinta para el archivo de configuracion wpa_supplicant.conf
			if network == "1": #Wifi no password
				os.system('sudo cp /home/pi/Domotics/Default/network/wifi/none/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicantAux.conf')

			elif network == "2": #Wifi WEP
				os.system('sudo cp /home/pi/Domotics/Default/network/wifi/wep/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicantAux.conf')

			elif network == "3": #Wifi WPA
				os.system('sudo cp /home/pi/Domotics/Default/network/wifi/wpa/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicantAux.conf')

			elif network == "4": #Wifi WPA2
				os.system('sudo cp /home/pi/Domotics/Default/network/wifi/wpa2/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicantAux.conf')

			#Borramos el fichero de configuracion WIFI antes de volverlo a crear para evitar conflictos
			os.system('sudo rm /etc/wpa_supplicant/wpa_supplicant.conf')

			#Creamos el fichero de configuración en base a la plantilla y rellenamos los campos
			with open("/etc/wpa_supplicant/wpa_supplicant.conf", "wt") as fout:
				with open("/etc/wpa_supplicant/wpa_supplicantAux.conf", "rt") as fin:
					for line in fin:
						fout.write(line.replace('<NAME>', nameWIFI).replace('<PASS>', passwordWIFI))

			#Eliminamos la planilla
			os.system('sudo rm /etc/wpa_supplicant/wpa_supplicantAux.conf')
		

		#Eliminamos el fichero de configuracion
		os.system('sudo rm /home/pi/Domotics/deviceConfig.py')

		#Copiamos el fichero de configuracion en el directorio Domotics
		os.system('sudo cp /home/pi/Domotics/Default/deviceConfig.py /home/pi/Domotics/deviceConfigAux.py')

		#Configuramos el fichero con el valor del id del dispositivo
		with open("/home/pi/Domotics/deviceConfig.py", "wt") as fout:
			with open("/home/pi/Domotics/deviceConfigAux.py", "rt") as fin:
				for line in fin:
					fout.write(line.replace('<DEVICE_ID>', deviceId))

		#Eliminamos la plantilla
		os.system('sudo rm /home/pi/Domotics/deviceConfigAux.py')

		#Sustituimos el fichero de arranque por la plantilla de arranque normal
		os.system('sudo cp /home/pi/Domotics/Default/bootNormal.py /home/pi/Domotics/bootConfig.py')


		for i in range(3):
			self.leds.setLedsOn()
			time.sleep(0.5)
			
			self.leds.setLedsOff()
			time.sleep(0.5)

		os.system('sudo reboot')
		
		return 1

	def exitAdhocMode(self, channel):
		
		print "Reset"

		time.sleep(1)

		if GPIO.input(channel) == GPIO.LOW:

			os.system('./Domotics/ExitAdhocMode/exitAdhocMode.sh')
		
			for i in range(3):
				self.leds.setLedsOn()
				time.sleep(0.5)

				self.leds.setLedsOff()
				time.sleep(0.5)

			os.system('sudo reboot')
		
		return 1


Install()