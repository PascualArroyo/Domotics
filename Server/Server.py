#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyjsonrpc
import myconfig
import deviceConfigAux
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
				"checkPort":self.checkPort,
				"getDevicesRemote":self.getDevicesRemote,
				"getTypeDevice":self.getTypeDevice,
				"signIn": self.signIn,
				"checkSignIn": self.checkSignIn,
				"logIn": self.logIn,
				"locationsUser": self.locationsUser,
				"devicesLocationUser": self.devicesLocationUser,
				"addNewLocation": self.addNewLocation,
				"editLocation": self.editLocation,
				"editLocationSecurity": self.editLocationSecurity,
				"deleteLocation": self.deleteLocation,
				"installDeviceServer": self.installDeviceServer,
				"editDevice": self.editDevice,
				"deleteDevice": self.deleteDevice,
				"updateIp": self.updateIp,
				"deviceOnline": self.deviceOnline,
				"motionDetected": self.motionDetected,
				"quitAlarm": self.quitAlarm,
				"newReadingSensors": self.newReadingSensors,
				"sensorsHistory": self.sensorsHistory,
				"alertHistory": self.alertHistory,
				"updateSoftwareDevice": self.updateSoftwareDevice,
				"updateSecurityCode": self.updateSecurityCode,
				"updateVersionDevice": self.updateVersionDevice,
				"deviceStatusSecurity": self.deviceStatusSecurity,
				"createTimer": self.createTimer,
				"updateTimer": self.updateTimer,
				"deviceTimers": self.deviceTimers,
				"deleteTimer": self.deleteTimer,
				"automation": self.automation

        	}


		# Threading HTTP-Server
		http_server = pyjsonrpc.ThreadingHttpServer(
			server_address = (socket.gethostbyname(socket.gethostname()), myconfig.serverPort),
			RequestHandlerClass = RequestHandler
		)

		# Start the scheduler
		sched = Scheduler()
		sched.start()

		# Schedule checkOnline 5 seconds
		sched.add_interval_job(self.checkOnline, seconds=5)

		#print myconfig.urlDb
		print "Starting HTTP server ..."
		print "URL: http://%s:%d" % (socket.gethostbyname(socket.gethostname()), myconfig.serverPort)

		try:
 			http_server.serve_forever()
		except KeyboardInterrupt:
			http_server.shutdown()

		print "Stopping HTTP server ..."



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
			#print "Error %d: %s" % (e.args[0],e.args[1])

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
			#print "Error %d: %s" % (e.args[0],e.args[1])

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
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

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
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()


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
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	#Edit location
	def editLocation(self, login, password, idLocation, nameOfLocation):

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

					consulta = myconfig.updateLocation % (nameOfLocation, idLocation)
					cur.execute(consulta)

					con.commit()
					result = 1

					#Name already register
				else:
					result = 2
			else:
				result = 3

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result

	
	#Edit location security
	def editLocationSecurity(self, login, password, idLocation, security):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.updateLocationSecurity % (security, idLocation)
				cur.execute(consulta)

				con.commit()

				if security == '0':
					self.quitAlarm(login, password, idLocation)

					result = 2
			
				else:
					result = 1

			else:
				result = 3

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

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

			#Hacemos Login
			consulta = myconfig.selectUserId % (login, password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				userId = row['id']

				#Comprobamos que la localizacion es del Usuario logueado
				consulta = myconfig.checkLocationUser % (userId, idLocation)
				cur.execute(consulta)
				row = cur.fetchone()

				if row:

					idLocation = row['idLocation']

					#Comprobamos que la localizacion no tiene dispositivos
					consulta = myconfig.selectDevicesLocation % (idLocation, userId)
					cur.execute(consulta)
					row = cur.fetchone()

					if row is None:

						#Eliminamos a la localizacion y su relacion con el usuario
						consulta = myconfig.deleteUserLocation % (idLocation)
						cur.execute(consulta)
						consulta = myconfig.deleteLocation % (idLocation)
						cur.execute(consulta)
				
						#Todo correcto
						con.commit()
						result = 1

					else:

						#Error, la localizacion tiene dispositivos
						result = 2

				else:
					#Error login localizacion
					result = 0

			else:
				#Error login
				result = 0

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

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
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()


		finally:

			if con:
				con.close()

		return result



	#Install device server
	def installDeviceServer(self, login, password, name, port, typeDevice, idLocation, idDevice, code):

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

						consulta = myconfig.updateCodeRemote % (code, idDevice)
						cur.execute(consulta)


					consulta = myconfig.insertLocationDevice % (idLocation, deviceIdentifier)
					cur.execute(consulta)

					con.commit()

					result = deviceIdentifier

				else:
					result = 0


			except mdb.Error, e:
				#print "Error %d: %s" % (e.args[0],e.args[1])

				if con:
					con.rollback()


			finally:

				if con:
					con.close()

			return result



	#Edit device
	def editDevice(self, login, password, idDevice, name, port, connectionMode, RIPMotion):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.updateDevice % (name, port, connectionMode, RIPMotion, idDevice)
				cur.execute(consulta)

				con.commit()
				result = 1
			
			else:
				result = 2

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

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

			#Hacemos login
			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				#Comprobamos que el dispositivo es del usuario logueado
				consulta = myconfig.checkDeviceUser % (row['id'], idDevice)
				cur.execute(consulta)
				row = cur.fetchone()

				if row:

					idDevice = row['idDevice']

					#Comprobamos que el dispositivo no tiene dispositivos remotos asociados
					consulta = myconfig.checkDeviceRemote % (idDevice)
					cur.execute(consulta)
					row = cur.fetchone()

					if row is None:
						
						#Borramos timer, alertas, sensores, relacion localizacion dispositivo y dispositivo
						consulta = myconfig.deleteTimerDevice % (idDevice)
						cur.execute(consulta)
						consulta = myconfig.deleteAlertDevice % (idDevice)
						cur.execute(consulta)
						consulta = myconfig.deleteSensorsData % (idDevice)
						cur.execute(consulta)
						consulta = myconfig.deleteLocationDevice % (idDevice)
						cur.execute(consulta)
						consulta = myconfig.deleteDevice % (idDevice)
						cur.execute(consulta)
				
						con.commit()

						#Todo correcto
						result = 1

					else:
						#No se puede eliminar hay dispositivos remotos
						result = 2
			
				else:

					#Error login dispositivo
					result = 0

			else:
				#Error login
				result = 0

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result



	def getPort(self, idDevice, code):

		con = ""
		result = 0

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectGetPort % (idDevice, code)
			cur.execute(consulta)
			result = cur.fetchone()


		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:

			if con:
				con.close()

		return result


	def checkPort(self, publicIp, port):

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(1)
		
		try:
			sock.connect((publicIp, port))

		except Exception,e:
			result = False

		else:
			result = True

		sock.close()
	
		return result


	def getDevicesRemote(self, idDevice, code):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectGetDevicesRemote % (idDevice, code)
			cur.execute(consulta)
			result = cur.fetchall()

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:

			if con:
				con.close()

		return result


	def getTypeDevice(self, idDevice, code):

		con = ""
		result = {"error":"error"}

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectGetTypeDevice % (idDevice, code)
			cur.execute(consulta)
			result = cur.fetchone()

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:

			if con:
				con.close()

		return result



	def updateSecurityCode(self, idDevice, currentCode, previousCode):

		con = ""
		result = 0

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)
			
			consulta = myconfig.updateCode % (currentCode, idDevice, previousCode)
			cur.execute(consulta)
			
			result = cur.rowcount

			if result == 1:
				consulta = myconfig.updateCodeRemote % (currentCode, idDevice)
				cur.execute(consulta)

			con.commit()
			
		
		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close() 
			
		return result


	## Actualizar ip de un dispositivo
	def updateIp(self, publicIp, privateIp, idDevice, code):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)
			consulta = myconfig.updateIpDevice % (publicIp, privateIp, idDevice, code)
			cur.execute(consulta)
			
			result = cur.rowcount

			con.commit()
		
		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close() 
			
		return result


	## Actualizar estado de la conexion
	def deviceOnline(self, connectionStatus, idDevice, code):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)
			consulta = myconfig.updateOnline % (connectionStatus, idDevice, code)
			cur.execute(consulta)
			con.commit()
					
			result = 1
		
		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close() 
			
		return result



	## Detectado movimiento en un dispositivo
	def motionDetected(self, idDevice, code):

		con = ""

		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)
			consulta = myconfig.selectLocationSecurity % (idDevice, code)
			cur.execute(consulta)
			row = cur.fetchone()

			if int(row['RIPMotion']) == 1: #Detector de movimiento activado

				if int(row['security']) == 1: #Seguridad activada

					if int(row['alarm']) == 0: #Alarma aun no activada
 
						#Actualizamos el estado del dispositivo a alarma
						consulta = myconfig.updateAlarm % ("1", idDevice)
						cur.execute(consulta)
						con.commit()

						#Introducimos la alerta en el registro de alertas
						consulta = myconfig.insertAlert % ("2", idDevice)
						cur.execute(consulta)
						con.commit()

						#Obtenemos los dispositivos camara de esa ubicacion
						consulta = myconfig.selectDevicesLocationOpenPortCameras % (row['idLocation'])
						cur.execute(consulta)
						cameras = cur.fetchall()


						subject = u"Domotics Alerta seguridad %s" % (row['nameLocation'])
						message = u"Hola %s.\n\nTu dispositivo %s ha dectado movimiento en su %s.\n\n" % (row['nameUser'], row['nameDevice'], row['nameLocation'])
					
						photos = []

						if len(cameras) > 0:

							message +=u"Adjuntamos imágenes de sus cámaras de seguridad:\n"

							for camera in cameras:

								try:
									resultPhoto = self.getImageForDeviceCamera(camera['publicIp'], camera['port'], camera['code'])
									photos.append(resultPhoto)
									message+=u"%s\n"%(camera['name'])

								except:
									pass

						message+=u"\nAtentamente Domotics.\n\n"

						m = Mail()

						m.send(row['email'], subject, message, photos)

						#Notificamos a los dispositivos la alerta
						consulta = myconfig.selectDevicesLocationOpenPort % (row['idLocation'])
						cur.execute(consulta)
						devices = cur.fetchall()

						for device in devices:

							try:

								#Actualizamos el estado del dispositivo a alarma
								consulta = myconfig.updateAlarm % ("1", device['id'])
								cur.execute(consulta)
								con.commit()

								self.setDeviceAlarmMode(device['publicIp'], device['port'], device['code'])
								
							except:
								pass

						#Notificamos a los dispositivos de otras ubicaciones la alerta
						consulta = myconfig.selectDevicesOtherLocationOpenPort % (row['idLocation'])
						cur.execute(consulta)
						devicesOtherLocation = cur.fetchall()


						for device in devicesOtherLocation:

							try:
								self.setDeviceOtherLocationNotification(device['publicIp'], device['port'], device['code'])
							except:
								pass

						result = 1
		

					else:

						#Comprobamos duplicados
						consulta = myconfig.checkInsertAlert % ("1", idDevice)
						cur.execute(consulta)
						row = cur.fetchone()

						if not row: #Si no existe duplicado insertamos en BBDD

							consulta = myconfig.insertAlert % ("1", idDevice)
							cur.execute(consulta)
							con.commit()

						#print "Seguridad ya activada"
				
				else:

					#Comprobamos duplicados
					consulta = myconfig.checkInsertAlert % ("0", idDevice)
					cur.execute(consulta)
					row = cur.fetchone()

					if not row: #Si no existe duplicado insertamos en BBDD
						consulta = myconfig.insertAlert % ("0", idDevice)
						cur.execute(consulta)
						con.commit()
					
					#print "Seguridad desactivada"


		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close()

				 
			
		return result


	## Desactivar alarma en todos los dispositivos de una ubicacion
	def quitAlarm(self, login, password, idLocation):

		con = ""
		result = 0

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.selectDevicesLocation % (idLocation, row['id'])
				cur.execute(consulta)
				devices = cur.fetchall()

				for device in devices:

					try:
						consulta = myconfig.updateAlarm % ("0", device['id'])
						cur.execute(consulta)
						con.commit()

					except:
						pass

				#Notificamos a los dispositivos la anulacion de la alerta
				consulta = myconfig.selectDevicesLocationUserOpenPort % (idLocation, row['id'])
				cur.execute(consulta)
				devices = cur.fetchall()

				for device in devices:

					try:
						self.quitDeviceAlarmMode(device['publicIp'], device['port'], device['code'])
					except:
						pass
					
				result = 1

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close() 
			
		return result


	## Estado de seguridad de un dispositivo
	def deviceStatusSecurity(self, idDevice, code):

		con = ""
		result = 0

		try:

			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.checkDeviceAlarmStatus % (idDevice,code)
			cur.execute(consulta)
			row = cur.fetchone()
			result = row['alarm']


		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
		
			if con:    
				con.rollback()
        	
		finally:
			if con:    
				con.close() 
			
		return result
		

	## Evento que se dispara cada 5 segundos para establecer a offline a los dispositivos que esten mas de minuto sin enviar su estado
	def checkOnline(self):

		con = ""

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.updateNotOnline

			cur.execute(consulta)
			con.commit()

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

	def getImageForDeviceCamera(self, publicIp, port, code):

		rpc_client = pyjsonrpc.HttpClient(url = "http://%s:%s" % (publicIp, port))
		result = rpc_client("cameraGetPhotoForMail", code)

		return result

	def setDeviceAlarmMode(self, publicIp, port, code):

		rpc_client = pyjsonrpc.HttpClient(url = "http://%s:%s" % (publicIp, port))
		result = rpc_client("setDeviceAlarmMode", code)

		return result

	def quitDeviceAlarmMode(self, publicIp, port, code):

		rpc_client = pyjsonrpc.HttpClient(url = "http://%s:%s" % (publicIp, port))
		result = rpc_client("quitDeviceAlarmMode", code)

		return result
		

	def newReadingSensors(self, temperature, humidity, pressure, brightness, idDevice):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.insertSensors % (temperature, humidity, pressure, brightness, idDevice)
			cur.execute(consulta)
			con.commit()
			result = 1

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result

	def sensorsHistory(self, login, password, idDevice, period):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:
				
				consulta = myconfig.selectSensors % (idDevice, period, row['id'])
				cur.execute(consulta)
				result = cur.fetchall()

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	def alertHistory(self, login, password, idDevice, period):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:
				
				consulta = myconfig.selectAlert % (idDevice, period, row['id'])	
				cur.execute(consulta)
				result = cur.fetchall()

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result



	def createTimer(self, login, password, name, time, action, idDevice):

		con = ""
		result = 0

		print "createTimer"

		try:
			
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login, password)
			cur.execute(consulta)
			row = cur.fetchone()

			print row['id']

			if row:

				consulta = myconfig.checkDeviceUser % (row['id'], idDevice)
				cur.execute(consulta)
				row = cur.fetchone()

				print row['idDevice']

				if row:

					consulta = myconfig.insertTimer % (name, time, action, row['idDevice'])
					print consulta
					cur.execute(consulta)

					con.commit()
					result = 1
			
				else:
					result = 0

			else:
				result = 0

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result




	def updateTimer(self, login, password, identifier, name, time, active, action, idDevice):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.checkDeviceUser % (row['id'], idDevice)
				cur.execute(consulta)
				row = cur.fetchone()

				if row:
					consulta = myconfig.updateTimer % (name, active, time, action, identifier, row['idDevice'])
					cur.execute(consulta)

					con.commit()
					result = 1
			
				else:
					result = 0

			else:
				result = 0

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result



	def deleteTimer(self, login, password, identifier, idDevice):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.checkDeviceUser % (row['id'], idDevice)
				cur.execute(consulta)
				row = cur.fetchone()

				if row:
					consulta = myconfig.deleteTimer % (identifier, row['idDevice'])
					cur.execute(consulta)

					con.commit()
					result = 1
			
				else:
					result = 0

			else:
				result = 0

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	def deviceTimers(self, login, password, idDevice):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectUserId % (login,password)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				consulta = myconfig.checkDeviceUser % (row['id'], idDevice)
				cur.execute(consulta)
				row = cur.fetchone()

				if row:

					consulta = myconfig.selectTimer % (row['idDevice'])
					cur.execute(consulta)
					result = cur.fetchall()
			

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	def automation(self, idDevice, code):

		con = ""
		result = -1

		try:
			
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectTimerAutomation % (idDevice, code)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				result = row['action']
			

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result


	## Metodo que actualiza el software de los dispositivos remotamente
	def updateSoftwareDevice(self, idDevice, code):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.selectDeviceVersion % (idDevice, code)
			cur.execute(consulta)
			row = cur.fetchone()

			if row:

				if row['version'] < deviceConfigAux.version:

					#Open software files
					file_device = open('/home/Domotics/device.py', 'r+')
					file_deviceConfig = open('/home/Domotics/deviceConfigAux.py', 'r+')
					file_bootConfig = open('/home/Domotics/bootConfig.py', 'r+')
					file_bootInstall = open('/home/Domotics/bootInstall.py', 'r+')
					file_bootNormal = open('/home/Domotics/bootNormal.py', 'r+')
					file_init = open('/home/Domotics/init.py', 'r+')
					file_install = open('/home/Domotics/install.py', 'r+')
					file_leds = open('/home/Domotics/leds.py', 'r+')
					file_sounds = open('/home/Domotics/sounds.py', 'r+')
					file_rele = open('/home/Domotics/rele.py', 'r+')
					file_sensors = open('/home/Domotics/sensors.py', 'r+')
					file_camera = open('/home/Domotics/camera.py', 'r+')
					file_remote = open('/home/Domotics/remote.py', 'r+')
					
					file_arduino = open('/home/Domotics/domoticsAux.ino', 'r+')

					#Read software files
					device = file_device.read()
					deviceConfig = file_deviceConfig.read()
					bootConfig = file_bootConfig.read()
					bootInstall = file_bootInstall.read()
					bootNormal = file_bootNormal.read()
					init = file_init.read()
					install = file_install.read()
					leds = file_leds.read()
					sounds = file_sounds.read()
					rele = file_rele.read()
					sensors = file_sensors.read()
					camera = file_camera.read()
					remote = file_remote.read()

					arduino = file_arduino.read()

					#Close software files
					file_device.close()
					file_deviceConfig.close()
					file_bootConfig.close()
					file_bootInstall.close()
					file_bootNormal.close()
					file_init.close()
					file_install.close()
					file_leds.close()
					file_sounds.close()
					file_rele.close()
					file_sensors.close()
					file_camera.close()
					file_remote.close()

					file_arduino.close()



					result = {"/home/pi/Domotics/bootConfig.py":bootConfig.encode("base64"),
						"/home/pi/Domotics/init.py":init.encode("base64"),
						"/home/pi/Domotics/install.py":install.encode("base64"),
						"/home/pi/Domotics/device.py":device.encode("base64"),
						"/home/pi/Domotics/leds.py":leds.encode("base64"),
						"/home/pi/Domotics/sounds.py":sounds.encode("base64"),
						"/home/pi/Domotics/rele.py":rele.encode("base64"),
						"/home/pi/Domotics/sensors.py":sensors.encode("base64"),
						"/home/pi/Domotics/camera.py":camera.encode("base64"),
						"/home/pi/Domotics/remote.py":remote.encode("base64"),
						"/home/pi/Domotics/Default/deviceConfigAux.py":deviceConfig.encode("base64"),
						"/home/pi/Domotics/Default/bootInstall.py":bootInstall.encode("base64"),
						"/home/pi/Domotics/Default/bootNormal.py":bootNormal.encode("base64"),
						"/home/pi/Domotics/Default/domoticsAux.ino":arduino.encode("base64")} 



		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])
			
			if con:
				con.close()

		finally:
			if con:
				con.close()

		return result


	##Actualiza la version de software en la base de datos
	def updateVersionDevice(self, version, idDevice, code):

		con = ""
		result = 0

		try:
			con = mdb.connect(myconfig.urlDb, myconfig.userDb, myconfig.passDb, myconfig.nameDb, charset = "utf8")
			cur = con.cursor(mdb.cursors.DictCursor)

			consulta = myconfig.updateVersionDevice % (version, idDevice, code)
			cur.execute(consulta)
			con.commit()
			result = 1

		except mdb.Error, e:
			#print "Error %d: %s" % (e.args[0],e.args[1])

			if con:
				con.rollback()

		finally:
			if con:
				con.close()

		return result
			
			



Server()
