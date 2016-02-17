#Es necesario cambiar estos datos por los parametros de nuestro servidor, usuarios, password

userDb = "userDb"
passDb = "passDb"
mail = "*********@gmail.com"
passMail = "passMail"
nameDb = "domotics_db"
urlDb = "urlDb"
serverPort = 8080


#Security Code Device
updateCode = "UPDATE device SET code = '%s' WHERE id = '%s' AND (code = '%s' OR connectionStatus = 0)"
updateCodeRemote = "UPDATE device SET code = '%s' WHERE idDevice = '%s'"

#manage Port
selectGetPort = "SELECT port FROM device WHERE id = '%s' AND code ='%s'"

#Remotes
selectGetDevicesRemote = "SELECT deviceRemote.id AS id, deviceRemote.pipeSend AS pipeSend, deviceRemote.pipeRecv AS pipeRecv, deviceRemote.type AS type FROM device deviceRemote, device deviceCentral WHERE deviceRemote.idDevice = deviceCentral.id AND deviceCentral.id = '%s' AND deviceCentral.code = '%s'"

#Type device
selectGetTypeDevice = "SELECT type FROM device WHERE id = '%s' AND code ='%s'"

#Get User id
selectUserId = "SELECT id FROM user WHERE login = '%s' AND password = '%s'"

#Check users and mails
selectUserExists = "SELECT login FROM user WHERE login = '%s'"
selectMailExists = "SELECT login FROM user WHERE mail = '%s'"
selectUserExistsCheck = "SELECT login FROM user WHERE login = '%s' AND active = '1'"
selectMailExistsWithoutCheck = "SELECT login FROM user WHERE mail = '%s' AND active != '1'"

#SignIn user
insertSignIn = "INSERT INTO user (login, name, mail, password, active) VALUES ('%s', '%s', '%s', '%s', '%d')"
updateSignIn = "UPDATE user SET login = '%s', name = '%s', password = '%s', active = '%d' WHERE mail = '%s'"

#Check SignIn
updateCheckSignIn = "UPDATE user SET active = 1 WHERE login = '%s' AND password = '%s' AND active = '%s'"

#LogIn
selectLogIn = "SELECT id, name, active FROM user WHERE login = '%s' AND password = '%s' AND active = '1'"

#List locations of user
selectLocationsUser = "SELECT location.id AS id, location.name AS name, location.security AS security FROM user, location, userLocation WHERE userLocation.idUser = user.id AND userLocation.idLocation = location.id AND user.id = '%s'"

#Check Device User
checkDeviceUser = "SELECT device.id AS idDevice FROM user, device, userLocation, locationDevice WHERE device.id = locationDevice.idDevice AND locationDevice.idLocation = userLocation.idLocation AND userLocation.idUser = user.id AND user.id = '%s' AND device.id = '%s'"
#Check Location User
checkLocationUser = "SELECT userLocation.idLocation AS idLocation FROM userLocation WHERE userLocation.idUser = '%s' AND userLocation.idLocation = '%s'"
#list devices of locations and user
selectDevicesLocation = "SELECT device.id AS id, device.name AS name, device.publicIp AS publicIp, device.privateIp AS privateIp, device.port AS port, DATE_FORMAT(device.timeStamp,'%%d/%%m/%%Y %%H:%%i:%%s') AS timeStamp, device.connectionStatus AS connectionStatus, device.RIPMotion AS RIPMotion, device.alarm AS alarm, device.type AS type, device.idDevice AS idDevice, device.pipeSend AS pipeSend, device.pipeRecv AS pipeRecv, device.code AS code, device.connectionMode AS connectionMode, device.version AS version FROM user, location, device, userLocation, locationDevice WHERE device.id = locationDevice.idDevice AND locationDevice.idLocation = location.id AND location.id = '%s' AND location.id = userLocation.idLocation AND userLocation.idUser = user.id AND user.id = '%s'"


#create new location
selectCheckLocationUser = "SELECT location.name AS name FROM user, location, userLocation WHERE userLocation.idUser = user.id AND userLocation.idLocation = location.id AND user.id = '%s' AND location.name = '%s'"
insertLocation = "INSERT INTO location (name, security) VALUES ('%s','1')"
insertLocationUser = "INSERT INTO userLocation (idUser, idLocation) VALUES ('%s','%s')"

#edit location
selectCheckUpdateLocationUser = "SELECT location.name AS name FROM user, location, userLocation WHERE userLocation.idUser = user.id AND userLocation.idLocation = location.id AND user.id = '%s' AND location.name = '%s' AND location.id != '%s'"
updateLocation = "UPDATE location SET name = '%s' WHERE id = '%s'"
updateLocationSecurity = "UPDATE location SET security = '%s' WHERE id = '%s'"

#delete location
deleteUserLocation = "DELETE FROM userLocation WHERE idLocation = '%s'"
deleteLocation = "DELETE FROM location WHERE id = '%s'"


#insert device
insertDeviceServer = "INSERT INTO device (name, port, timeStamp, type, idDevice) VALUES ('%s', '%s', NOW(), '%s', '%s')"
insertLocationDevice = "INSERT INTO locationDevice (idLocation, idDevice) VALUES ('%s', '%s')"


#Update Devices
updateDevice = "UPDATE device SET name = '%s', port = '%s', connectionMode = '%s', RIPMotion = '%s' WHERE id = '%s'"
updateDevicePipes = "UPDATE device SET pipeSend = '%s', pipeRecv = '%s' WHERE id = '%s'"
updateIpDevice = "UPDATE device SET publicIp = '%s', privateIp = '%s' WHERE id = '%s' AND code = '%s'"
updateNotOnline = "UPDATE device SET connectionStatus = '0' WHERE connectionStatus != '0' AND TIMEDIFF(NOW(), device.timeStamp) > TIME('00:01:00')"
updateOnline = "UPDATE device SET connectionStatus = '%s', device.timeStamp = NOW() WHERE id = '%s' AND code = '%s'"


#Check Device Remote for Delete
checkDeviceRemote = "SELECT id FROM device WHERE idDevice = '%s'"

#Delete devices
deleteTimerDevice = "DELETE FROM timer WHERE idDevice = '%s'"
deleteAlertDevice = "DELETE FROM alert WHERE idDevice = '%s'"
deleteSensorsData = "DELETE FROM sensors WHERE idDevice = '%s'"
deleteLocationDevice = "DELETE FROM locationDevice WHERE idDevice = '%s'"
deleteDevice = "DELETE FROM device WHERE id = '%s'"


#Security
selectLocationSecurity = "SELECT user.mail AS email, user.name AS nameUser, location.id AS idLocation, location.security AS security, location.name AS nameLocation, device.name AS nameDevice, device.RIPMotion AS RIPMotion, device.alarm AS alarm FROM location, device, locationDevice, userLocation, user WHERE device.id = locationDevice.idDevice AND locationDevice.idLocation = location.id AND device.id ='%s' AND device.code = '%s' AND userLocation.idLocation = location.id AND userLocation.idUser = user.id"
updateAlarm = "UPDATE device SET alarm = '%s' WHERE id = '%s'"
selectDevicesLocationOpenPort = "SELECT device.id AS id, device.publicIp AS publicIp, device.port AS port, device.name AS name, device.code AS code FROM device, locationDevice WHERE locationDevice.idLocation = '%s' AND locationDevice.idDevice = device.id AND device.connectionStatus = '1' AND device.RIPMotion = '1'"
selectDevicesLocationUserOpenPort = "SELECT device.publicIp AS publicIp, device.port AS port, device.name AS name, device.code AS code FROM device, locationDevice, userLocation WHERE locationDevice.idLocation = '%s' AND locationDevice.idDevice = device.id AND device.connectionStatus = '1' AND userLocation.idLocation = locationDevice.idLocation AND userLocation.idUser = '%s'"
selectDevicesOtherLocationOpenPort = "SELECT device.publicIp AS publicIp, device.port AS port, device.name AS name, device.code AS code FROM device, locationDevice WHERE locationDevice.idLocation <> '%s' AND locationDevice.idDevice = device.id AND device.connectionStatus = '1'"
selectDevicesLocationOpenPortCameras = "SELECT device.publicIp AS publicIp, device.port AS port, device.name AS name, device.code AS code FROM device, locationDevice WHERE locationDevice.idLocation = '%s' AND locationDevice.idDevice = device.id AND device.connectionStatus = '1' AND device.type = '2'"
checkDeviceAlarmStatus = "SELECT alarm FROM device WHERE id = '%s' AND code ='%s'"

#Alert
insertAlert = "INSERT INTO alert (date, time, type, idDevice) VALUES (CURRENT_DATE(), CURRENT_TIME(), '%s', '%s')"
checkInsertAlert = "SELECT id FROM alert WHERE alert.type = '%s' AND alert.idDevice = '%s' AND alert.date = CURRENT_DATE() AND CURRENT_TIME()-alert.time < TIME('00:02:00')"
selectAlert = "SELECT DATE_FORMAT(alert.date,'%%d/%%m/%%Y') AS date, DATE_FORMAT(alert.time,'%%H:%%i') AS time, alert.type AS type FROM device, alert, locationDevice, userLocation WHERE device.id = alert.idDevice AND device.id = '%s' AND alert.date = STR_TO_DATE('%s','%%d/%%m/%%Y') AND locationDevice.idDevice = device.id AND locationDevice.idLocation = userLocation.idLocation AND userLocation.idUser = '%s' ORDER BY alert.id DESC"

#Sensors
insertSensors = "INSERT INTO sensors (temperature, humidity, pressure, brightness, date, time, idDevice) VALUES ('%s', '%s', '%s', '%s', CURRENT_DATE(), CURRENT_TIME(), '%s')"
selectSensors = "SELECT temperature, humidity, pressure, brightness, DATE_FORMAT(sensors.time,'%%H:%%i') AS time FROM device, sensors, locationDevice, userLocation WHERE device.id = sensors.idDevice AND device.id = '%s' AND sensors.date = STR_TO_DATE('%s','%%d/%%m/%%Y') AND locationDevice.idDevice = device.id AND locationDevice.idLocation = userLocation.idLocation AND userLocation.idUser = '%s' ORDER BY sensors.id DESC"

#Timer
selectTimer = "SELECT id, name, active, DATE_FORMAT(time,'%%H:%%i') AS time, action FROM timer WHERE idDevice = '%s' ORDER BY time"
insertTimer = "INSERT INTO timer (name, active, time, action, idDevice) VALUES ('%s', '1', '%s', '%s', '%s')"
updateTimer = "UPDATE timer SET name = '%s', active = '%s', time = '%s', action = '%s' WHERE id = '%s' and idDevice = '%s'"
deleteTimer = "DELETE FROM timer WHERE id = '%s' and idDevice = '%s'"

selectTimerAutomation = "SELECT timer.action AS action, CURRENT_TIME()-timer.time AS diff FROM timer, device WHERE timer.idDevice = '%s' AND timer.idDevice = device.id AND device.code = '%s' AND timer.active = '1' AND CURRENT_TIME()-timer.time < TIME('00:01:00') AND CURRENT_TIME > timer.time ORDER BY 1"


#SoftwareUpdate
selectDeviceVersion = "SELECT version FROM device WHERE id = '%s' AND code ='%s'"
updateVersionDevice = "UPDATE device SET version = '%s' WHERE id = '%s' AND code = '%s'"



