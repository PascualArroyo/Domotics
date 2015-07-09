from HTU21D import HTU21D
from TSL2561 import TSL2561
import Adafruit_BMP.BMP085 as BMP085

htu = HTU21D()
print htu.read_tmperature()
print htu.read_humidity()

sensor = BMP085.BMP085()
print sensor.read_pressure()

tsl=TSL2561()
print tsl.readLux()