#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nrf24 import NRF24
#import RPi.GPIO as GPIO

import time

class Remote:

	radio = 0
	transmit = 0 #transmit = 0 remoto libre, transmit = 1 remoto ocupado

	TIMETOSLEEP = 0.05
	NUMBEROFATTEMPTSRESEND = 3
	NUMBEROFATTEMPTS = 30

	def __init__(self):

		#Preparamos la configuración de la comunicación por radio
		self.radio = NRF24()
		self.radio.begin(0, 0, 25, 18) #Set CE and IRQ pins
		self.radio.setRetries(15,15)
		self.radio.setPayloadSize(32)
		self.radio.setChannel(0x4c)
		self.radio.setPALevel(NRF24.PA_MAX)
		self.radio.powerUp()

	def convert(self, pipe):
		
		vector = []
		vector.append(int("0x"+pipe[0:2], 16))
		vector.append(int("0x"+pipe[2:4], 16))
		vector.append(int("0x"+pipe[4:6], 16))
		vector.append(int("0x"+pipe[6:8], 16))
		vector.append(int("0x"+pipe[8:10], 16))

		return vector

	def transmitInt(self, pipeSend, pipeRecv, comand):

		i = 0
		value = -1

		#Transformamos los pipes a Exadecimal
		pipe1 = self.convert(pipeSend)
		pipe2 = self.convert(pipeRecv)

		#Configuramos el NRF24 con los pipes de lectura y escritura
		self.radio.openWritingPipe(pipe1)
		self.radio.openReadingPipe(1, pipe2) 

		#Si no obtenemos respuesta o el numero de intentos es menor de NUMBEROFATTEMPTS (16)
		while not self.radio.available([1]) and i < self.NUMBEROFATTEMPTS:

			print i

			#Cada numberOfAttemptsReSend (4 veces) enviamos
			if i % self.NUMBEROFATTEMPTSRESEND == 0: 
				
				#Dejamos de escuchar, enviamos el comando y volvemos a escuchar
				self.radio.stopListening()
				self.radio.write(comand)
  				self.radio.startListening()

  			i = i+1

  			time.sleep(self.TIMETOSLEEP)
  			
  				
  		#Si el numero de intentos es menor al tope, tenemos exito en la comunicacion y podemos leer la salida
  		if i < self.NUMBEROFATTEMPTS:
			
			recv_buffer = []
  			self.radio.read(recv_buffer)
  			out = ''.join(chr(i) for i in recv_buffer)

  			try:

				values = out.split('|')
				value = int(values[0])
			
			except:

				value = -1
  			

  		return value


  	def transmitStringJSON(self, pipeSend, pipeRecv, comand):

		i = 0
		stringJson = {"error":"error"}

		#Transformamos los pipes a Exadecimal
		pipe1 = self.convert(pipeSend)
		pipe2 = self.convert(pipeRecv)

		#Configuramos el NRF24 con los pipes de lectura y escritura
		self.radio.openWritingPipe(pipe1)
		self.radio.openReadingPipe(1, pipe2) 

		#Si no obtenemos respuesta o el numero de intentos es menor de NUMBEROFATTEMPTS (16)
		while not self.radio.available([1]) and i < self.NUMBEROFATTEMPTS:

			print i

			#Cada numberOfAttemptsReSend (4 veces) enviamos
			if i % self.NUMBEROFATTEMPTSRESEND == 0: 
				
				#Dejamos de escuchar, enviamos el comando y volvemos a escuchar
				self.radio.stopListening()
				self.radio.write(comand)
  				self.radio.startListening()

  			i = i+1

  			time.sleep(self.TIMETOSLEEP)
  			
  				
  		#Si el numero de intentos es menor al tope, tenemos exito en la comunicacion y podemos leer la salida
  		if i < self.NUMBEROFATTEMPTS:
			
			recv_buffer = []
  			self.radio.read(recv_buffer)
  			out = ''.join(chr(i) for i in recv_buffer)

  			try:

  				values = out.split('|')
			
				while len(values) < 4:
					values.append('0')

				stringJson = {"temp":values[0], "hum":values[1], "pres": values[2], "lux":values[3]}

			except:

				stringJson = {"error":"error"}
  			

  		return stringJson
        