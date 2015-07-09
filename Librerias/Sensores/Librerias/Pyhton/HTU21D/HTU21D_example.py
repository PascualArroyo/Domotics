#!/usr/bin/python
import time
import smbus

msleep = lambda x: time.sleep(x/1000.0)

ADDR = 0x40

i2c = smbus.SMBus(1)

CMD_READ_TEMP_HOLD = 0xe3
CMD_READ_HUM_HOLD = 0xe5
CMD_READ_TEMP_NOHOLD = 0xf3
CMD_READ_HUM_NOHOLD = 0xf5
CMD_WRITE_USER_REG = 0xe6
CMD_READ_USER_REG = 0xe7
CMD_SOFT_RESET= 0xfe

i2c.write_byte(ADDR, CMD_SOFT_RESET)
msleep(100)

i2c.write_byte(ADDR, CMD_READ_TEMP_NOHOLD)
msleep(100)

data = i2c.read_i2c_block_data(ADDR, CMD_READ_TEMP_NOHOLD, 3)
msleep(100)