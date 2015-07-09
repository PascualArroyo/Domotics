#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#akirasan.net

from nrf24 import NRF24
import time

pipes = [[0x65, 0x64, 0x6f, 0x4e, 0x32], [0x65, 0x64, 0x6f, 0x4e, 0x31]]

radio = NRF24()
radio.begin(0, 0, 25, 18) #Set CE and IRQ pins
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x4c)
radio.setPALevel(NRF24.PA_MAX)

radio.openReadingPipe(1, pipes[1])
radio.openWritingPipe(pipes[0])

radio.startListening()
radio.printDetails()
radio.powerUp()
cont=0

while True:
  pipe = [0]

  while not radio.available(pipe):
    time.sleep(0.250)

  recv_buffer = []
  radio.read(recv_buffer)
  out = ''.join(chr(i) for i in recv_buffer)
  print out

  cont=cont+1
  print cont

  if cont==5:
    comando = "ON"
    radio.stopListening()
    print "Envio comando --- ON"
    radio.write(comando)
    radio.startListening()

  if cont==10:
    comando = "OFF"
    radio.stopListening()
    print "Envio comando --- OFF"
    radio.write(comando)
    radio.startListening()
    cont=0
