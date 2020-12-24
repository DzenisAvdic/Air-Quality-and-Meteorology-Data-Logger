from time import sleep_ms, ticks_ms, ticks_diff #,sleep
from utime import sleep, sleep_us
import machine
from machine import Pin, I2C, ADC, SPI
from struct import unpack as unp

#SHT20 default address
SHT20_I2CADDR = 64

#SHT20 command
TRI_T_MEASURE_NO_HOLD = b'\xf3'
TRI_RH_MEASURE_NO_HOLD = b'\xf5'
READ_USER_REG = b'\xe7'
WRITE_USER_REG = b'\xe6'
SOFT_RESET = b'\xfe'



#SHT20 class to read temperature and humidity sensors
class SHT20(object):

    def __init__(self, scl_pin=16, sda_pin=17, clk_freq=115200):
        self._address = SHT20_I2CADDR

        pin_c = Pin(scl_pin)
        pin_d = Pin(sda_pin)
        self._bus = I2C(scl=pin_c, sda=pin_d, freq=clk_freq)

    def get_temperature(self):
        self._bus.writeto(self._address, TRI_T_MEASURE_NO_HOLD)
        sleep_ms(150)
        origin_data = self._bus.readfrom(self._address, 2)
        origin_value = unp('>h', origin_data)[0]
        value = -46.85 + 175.72 * (origin_value / 65536)
        return value

    def get_relative_humidity(self):
        self._bus.writeto(self._address, TRI_RH_MEASURE_NO_HOLD)
        sleep_ms(150)
        origin_data = self._bus.readfrom(self._address, 2)
        origin_value = unp('>H', origin_data)[0]
        value = -6 + 125 * (origin_value / 65536)
        return value



