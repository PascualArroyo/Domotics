#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

class Camera:

	def getCameraImg(self, width, height, time, quality, exposure, brightness):

		# "Capturamos la imagen de la camara con el comando raspistill"
		os.system('raspistill -vf -hf -w "%s" -h "%s" -t "%s" -q "%s" -ex "%s" -br "%s" -o capture.jpg' % (width, height, time, quality, exposure, brightness))
		# "Cargamos la imagen"
		f = open('capture.jpg', 'r+')

		jpgdata = f.read()

		f.close()			
		os.system('sudo rm /home/pi/capture.jpg')

		#Base64
		return jpgdata.encode("base64")
        