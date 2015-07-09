#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#akirasan.net

from nrf24 import NRF24
import time

pipes = [[0x65, 0x64, 0x6f, 0x4e, 0x32], [0x65, 0x64, 0x6f, 0x4e, 0x31], [0x75, 0x64, 0x6f, 0x4e, 0x32], [0x75, 0x64, 0x6f, 0x4e, 0x31]]

radio = NRF24()
radio.begin(0, 0, 25, 18) #Set CE and IRQ pins
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x4c)
radio.setPALevel(NRF24.PA_MAX)

radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.printDetails()
radio.powerUp()
cont=0

while True:

  time.sleep(3)
  print "Llamamos a la 1"
  radio.stopListening()
  radio.openWritingPipe(pipes[0])
  radio.write("Debes de ser la 1")
  radio.openReadingPipe(1, pipes[1])
  radio.startListening()
  print "Enviado 1"

  i = 0
  while not radio.available([1]):
    i = i+1
    print "NO 1"
    time.sleep(0.250)

    if i >= 10:
      i = 0
      radio.stopListening()
      radio.openWritingPipe(pipes[0])
      radio.write("Debes de ser la 1")
      radio.openReadingPipe(1, pipes[1])
      radio.startListening()
      


  recv_buffer = []
  radio.read(recv_buffer)
  out = ''.join(chr(i) for i in recv_buffer)
  print "Respuesta 1" + out

  time.sleep(3)
  print "Llamamos a la 2"
  radio.stopListening()
  radio.openWritingPipe(pipes[2])
  radio.write("Debes de ser la 2")
  radio.openReadingPipe(1, pipes[3])
  radio.startListening()
  print "Enviado 2"

  i = 0
  while not radio.available([1]):
    i = i+1
    print "NO 2"
    time.sleep(0.250)

    if i >= 10:
      i = 0
      radio.stopListening()
      radio.openWritingPipe(pipes[2])
      radio.write("Debes de ser la 2")
      radio.openReadingPipe(1, pipes[3])
      radio.startListening()


  recv_buffer = []
  radio.read(recv_buffer)
  out = ''.join(chr(i) for i in recv_buffer)
  print "Respuesta 2" + out



