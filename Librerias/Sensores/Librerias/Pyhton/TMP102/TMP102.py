from smbus import SMBus
import time

# I2C globals
ADDR1 = 0x48 #temp
ADDR2 = 0x40 #hum
ADDR3 = 0x77 #presion
ADDR4 = 0x39 #luz

bus = SMBus(1)

#Main loop

#while true:
bus.write_byte(ADDR1, 0x00)
ans = bus.read_i2c_block_data(ADDR1, 0x00, 2)
	
print ans

temp = ans[0] + ans[1]/256.0

temp = '{:.01f}'.format(temp)
print temp


msb = ans[0]
lsb = ans[1]

print (((msb << 8) | lsb) >> 4) * 0.0625
	
	 
