#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyjsonrpc
import myconfig
import os
import socket
import MySQLdb as mdb

from datetime import datetime
from apscheduler.scheduler import Scheduler
from random import randint
from mail import Mail


class Server:

	def __init__(self):

		#Metodos RPC
		class RequestHandler(pyjsonrpc.HttpRequestHandler):
			# Register public JSON-RPC methods
			methods = {
				"getPort":self.getPort,
				"setRemotePort":self.setRemotePort,
				"getDevicesRemote":self.getDevicesRemote,
				"getTypeDevice":self.getTypeDevice,
				"signIn": self.signIn,
				"checkSignIn": self.checkSignIn,
				"logIn": self.logIn,
				"locationsUser": self.locationsUser,
				"devicesLocationUser": self.devicesLocationUser,
				"addNewLocation": self.addNewLocation,
				"editLocation": self.editLocation,
				"deleteLocation": self.deleteLocation,
				"installDeviceServer": self.installDeviceServer,
				"editDevice": self.editDevice,
				"deleteDevice": self.deleteDevice,
				"deviceOnline": self.deviceOnline
        	}


		# Threading HTTP-Server
		http_server = pyjsonrpc.ThreadingHttpServer(
			server_address = (socket.gethostbyname(socket.gethostname()), myconfig.serverPort),
			RequestHandlerClass = RequestHandler
		)

		# Start the scheduler
		sched = Scheduler()
		sched.start()

		# Schedule checkOnline 1 minute
		sched.add_interval_job(self.checkOnline, minutes=1)

		#print myconfig.urlDb
		print "Starting HTTP server ..."
		print "URL: http://%s:%d" % (socket.gethostbyname(socket.gethostname()), myconfig.serverPort)

		try:
 			http_server.serve_forever()
		except KeyboardInterrupt:
			http_server.shutdown()

		print "Stopping HTTP server ..."



	def getPort(self, idDevice):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectGetPort % (idDevice)
			cur.execute(consulta)
			result = cur.fetchone()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

		finally:

			if con:
				con.close()

		return result

	def setRemotePort(self, idDevice, port):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.updateRemotePort % (port, idDevice)
			
			cur.execute(consulta)
			result = cur.rowcount
			con.commit()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

		finally:

			if con:
				con.close()

		return result


	def getDevicesRemote(self, idDevice):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectGetDevicesRemote % (idDevice)
			cur.execute(consulta)
			result = cur.fetchall()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

		finally:

			if con:
				con.close()

		return result


	def getTypeDevice(self, idDevice):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectGetTypeDevice % (idDevice)
			cur.execute(consulta)
			result = cur.fetchone()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

		finally:

			if con:
				con.close()

		return result


	# Sign In
	def signIn(self, login, name, email, password):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)
			consulta = myconfig.selectMailExists % (email)
			cur.execute(consulta)
			response = cur.fetchone()

			if response == None:

				consulta = myconfig.selectUserExists % (login)
				cur.execute(consulta)
				response = cur.fetchone()

				if response == None:

					code = randint(100000,999999)
					text = "Ya casi estas registrado en Domotics.\nPara completar el codigo de verificacion de tu registro es %s.\n\nEquipo de Domotics" % (code)

					m = Mail()

					m.send(email, "Registro Domotics", text, [])

					consulta = myconfig.insertSignIn % (login, name, email, password, code)
					cur.execute(consulta)
					con.commit()

					result = 1

				else:
					result = 2


    		#Re-Send Code and update
			else:

				consulta = myconfig.selectMailExistsWithoutCheck % (email)
				cur.execute(consulta)
				response = cur.fetchone()

				if response == None:
					result = 3


				else:

					consulta = myconfig.selectUserExistsCheck % (login)
					cur.execute(consulta)
					response = cur.fetchone()

					if response == None:

						code = randint(100000,999999)
						text = "Ya casi estas registrado en Domotics.\nPara completar el codigo de verificacion de tu registro es %s.\n\nEquipo de Domotics" % (code)

						m = Mail()

						m.send(email, "Registro Domotics", text, [])

						consulta = myconfig.updateSignIn % (login, name, password, code, email)

						cur.execute(consulta)
						con.commit()

						result = 1


					else:
						result = 2



		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	## Check Sign In
	def checkSignIn(self, login, password, code):

		con = ""
		result = 0

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.updateCheckSignIn % (login,password,code)

			cur.execute(consulta)
			result = cur.rowcount
			con.commit()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:

			if con:
				con.close()

		return result


	# Autenticar usuario
	def logIn(self, login, password):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectLogIn % (login,password)

			cur.execute(consulta)
			result = cur.fetchall()


		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

		finally:

			if con:
				con.close()

		return result





	## List locations of user
	def locationsUser(self, login, password):

		con = ""
		result = {"error":"error"}


		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:
				consulta = myconfig.selectLocationsUser % (row['id'])

				cur.execute(consulta)
				result = cur.fetchall()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])


		finally:

			if con:
				con.close()

		return result



	# Add New Location
	def addNewLocation(self, login, password, nameOfLocation):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.selectCheckLocationUser % (row['id'], nameOfLocation)
				cur.execute(consulta)
				response = cur.fetchone()

				if response == None:

					consulta = myconfig.insertLocation % (nameOfLocation)
					cur.execute(consulta)

					consulta = myconfig.insertLocationUser % (row['id'], cur.lastrowid)
					cur.execute(consulta)
					con.commit()
					result = 1

					#Name already register
				else:
					result = 2
			else:
				result = 3

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	#Edit location
	def editLocation(self, login, password, nameOfLocation, idLocation, security):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.selectCheckUpdateLocationUser % (row['id'], nameOfLocation, idLocation)
				cur.execute(consulta)
				response = cur.fetchone()

				if response == None:

					consulta = myconfig.updateLocation % (nameOfLocation, security, idLocation)
					cur.execute(consulta)

					con.commit()
					result = 1

					#Name already register
				else:
					result = 2
			else:
				result = 3

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	#Delete location
	def deleteLocation(self, login, password, idLocation):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:
				consulta = myconfig.deleteDevices % (idLocation)
				cur.execute(consulta)
				consulta = myconfig.deleteUserLocation % (idLocation)
				cur.execute(consulta)
				consulta = myconfig.deleteLocation % (idLocation)
				cur.execute(consulta)
				
				con.commit()
				result = 1

			else:
				result = 2

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result




	## List devices of location and user
	def devicesLocationUser(self, login, password, idLocation):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:
		
				consulta = myconfig.selectDevicesLocation % (idLocation, row['id'])
				cur.execute(consulta)
				result = cur.fetchall()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])


		finally:

			if con:
				con.close()

		return result



	#Install device server
	def installDeviceServer(self, login, password, name, port, typeDevice, idLocation, idDevice):

			con = ""
			result = 0

			try:

				con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
				cur = con.cursor(mdb.cursors.DictCursor)

				consulta = myconfig.selectUserId % (login,password)
				cur.execute(consulta)
				row = cur.fetchone()

				if row:

					consulta = myconfig.insertDeviceServer % (name, port, typeDevice, idDevice)
					cur.execute(consulta)

					deviceIdentifier = cur.lastrowid

					aux = str(deviceIdentifier)

					if idDevice != "0":

						tam = 9 - len(aux)

						for x in range(0, tam):
							aux += "0"

						pipeSend = aux + "1"
						pipeRecv = aux + "2"

						consulta = myconfig.updateDevicePipes % (pipeSend, pipeRecv, deviceIdentifier)
						cur.execute(consulta)

						
					print "ok"
					consulta = myconfig.insertLocationDevice % (idLocation, deviceIdentifier)
					cur.execute(consulta)

					con.commit()

					result = deviceIdentifier

				else:
					result = 0


			except mdb.Error, e:
				print "Error %d: %s" % (e.args[0],e.args[1])


			finally:

				if con:
					con.close()

			return result



	#Edit device
	def editDevice(self, login, password, idDevice, name, port):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.updateDevice % (name, port, idDevice)
				cur.execute(consulta)

				con.commit()
				result = 1
			
			else:
				result = 2

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result



	#Delete device
	def deleteDevice(self, login, password, idDevice):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:
				
				consulta = myconfig.deleteLocationDevice % (idDevice)
				cur.execute(consulta)
				consulta = myconfig.deleteLocationDeviceRemote % (idDevice)
				cur.execute(consulta)
				consulta = myconfig.deleteDeviceRemote % (idDevice)
				cur.execute(consulta)
				consulta = myconfig.deleteDevice % (idDevice)
				cur.execute(consulta)
				
				con.commit()
				result = 1

			else:
				result = 2

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result





	## Actualizar estado e ip de un dispositivo
	def deviceOnline(self, ipDevice, status, idDevice):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)
			consulta = myconfig.updateOnline % (ipDevice, status, idDevice)
			cur.execute(consulta)
			con.commit()

			#Alarm
			if int(status) == 0:

				consulta = myconfig.selectLocationSecurity % (idDevice)
				cur.execute(consulta)
				row = cur.fetchone()
				

				#Active Security AND no mail already
				if (int(row['security']) == 1 and int(row['alreadyMail']) == 0):

					consulta = myconfig.updateAlreadyMail % ("1", idDevice)
					cur.execute(consulta)
					con.commit()

					consulta = myconfig.selectCamerasLocation % (row['idLocation'])
					cur.execute(consulta)
					cameras = cur.fetchall()

					subject = "Domotics Alerta seguridad %s" % (row['nameLocation'])
					message = "Hola %s.\n\nTu dispositivo %s ha dectado movimiento en su %s.\n\n" % (row['nameUser'], row['nameDevice'], row['nameLocation'])
					
					if (len(cameras) > 0):
						message+="Adjuntamos imágenes de sus cámaras de seguridad:\n"

					photos = []

					for camera in cameras:
						resultPhoto = self.getImageForDeviceCamera(camera['ip'], camera['port'])
						photos.append(resultPhoto)
						message+="%s\n"%(camera['name'])

					message+="\nAtentamente Domotics.\n\n"

					m = Mail()

					m.send(row['email'], subject, message, photos)

			else:
				consulta = myconfig.updateAlreadyMail % ("0", idDevice)
				cur.execute(consulta)
				con.commit()

					
			result = 1
		
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close() 
			
		return result
		

	## Evento que se dispara cada 2 minutos para establecer a offline a los dispositivos que esten mas de tres mininutos sin enviar su estado
	def checkOnline(self):

		con = ""

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.updateNotOnline

			cur.execute(consulta)
			con.commit()

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

	def getImageForDeviceCamera(self, ip, port):

		rpc_client = pyjsonrpc.HttpClient(url = "http://%s:%s" % (ip, port))
		result = rpc_client("cameraGetPhotoForMail")

		return result


Server()
