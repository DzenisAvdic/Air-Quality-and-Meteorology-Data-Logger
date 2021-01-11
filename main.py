import machine
import network
import time
from time import sleep_ms, ticks_ms, ticks_diff
from utime import sleep, sleep_us
from machine import Pin, I2C, ADC, SPI
import sys
from struct import unpack as unp
import uSGP30
import ujson
import utime
import sdcard
import uos
import DS1302
import owmapi
import urequests
import SHT20
import gc

gc.collect()
gc.enable()

#RTC module
ds = DS1302.DS1302(clk=Pin(4), dio=Pin(32), cs=Pin(5))

#use this code block for setting time on RTC, and start tracking time
#and dont forget to comment it afterwards, since RTC has its own power to keep track of time
#ds.DateTime()
#ds.DateTime([2020, 12, 18, 5, 21, 09, 0, 0])
#ds.start()

led_success=Pin(26, Pin.OUT) #yellow, info LED (blinking loop)
led_wifi=Pin(21, Pin.OUT) #red, WiFi connection LED (on if connection lost)
led_int_aq=Pin(22, Pin.OUT) #yellow, indoors PM2.5 level LED (on if air inside is bad)
led_ext_aq=Pin(23, Pin.OUT) #green, outdoors PM2.5 AQI index LED (on if air outside is good for ventilation)

#set all LEDs to off
led_success.value(0)
led_wifi.value(0)
led_int_aq.value(0)
led_ext_aq.value(0)

#define pins for SD card
spisd = SPI(2, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
sd = sdcard.SDCard(spisd, machine.Pin(15,mode=Pin.OUT))

#mount SD card
try:
  uos.mount(sd,'/sd') #clayton
except OSError:
  led_success.value(1)
  sleep_ms(500)
  led_success.value(0)
finally:
  pass

#SGP30 sensor needs calibration, so here we define txt file to write baseline values
BASELINE_FILE = "sd/sgp30_iaq_baseline.txt"
#after reset stored data is used to turn on/off the LEDs
LAST_READ_DATA_FILE = "sd/web_api_data.txt"

#instantiate SGP30 sensor (carbon dioxide equivalent and total volatile organic compounds)
I2C_SCL_GPIO = const(18) #SCL on pin 18
I2C_SDA_GPIO = const(19) #SDA on pin 19
I2C_FREQ = const(115200)
MEASURE_INTERVAL_MS = const(1000)       # Minutely measurements
BASELINE_INTERVAL_MS = const(3600000)   # Hourly baseline commits
SGP30_INIT_TIME_MS = const(15000)

i2c = machine.I2C(
    scl=machine.Pin(I2C_SCL_GPIO, machine.Pin.OUT),
    sda=machine.Pin(I2C_SDA_GPIO, machine.Pin.OUT),
    freq=I2C_FREQ
)
sgp30 = uSGP30.SGP30(i2c) #use module to instantiate sensor

#instantiate SHT20 sensor (temperature and relative humidity)
sht_sensor = SHT20.SHT20()
t = sht_sensor.get_temperature()
rh = sht_sensor.get_relative_humidity()
#SGP30 sensor initialisation time
utime.sleep_ms(SGP30_INIT_TIME_MS)

#check if there's valid baseline for SGP30
#(for values older than 7 days manually delete
#baseline file and calibrate for 12 hours)
try:
    with open(BASELINE_FILE, "r") as file:
        current_baseline = ujson.loads(file.read())
except OSError as exception:
    print(exception)
    print("No valid baseline found. You should wait 12 hours for calibration before use.")
else:
    print("Baseline found:", current_baseline)
    sgp30.set_iaq_baseline(current_baseline[0], current_baseline[1])
finally:
    #set absolute humidity
    ah = uSGP30.convert_r_to_a_humidity(t, rh)
    sgp30.set_absolute_humidity(ah)

#load data stored on file to turn LEDs on/off
try:
    with open(LAST_READ_DATA_FILE, "r") as file:
        current_data = ujson.loads(file.read())
except OSError as exception:
    print(exception)
    print("No valid past found. Reset values")
    with open(LAST_READ_DATA_FILE, "w") as file:
      file.write(str("[%s, %s]" % (0, 0)))
      file.close() #new line
else:
    print("Past data found:", current_data)
    dust=current_data[0]
    AQI_index=current_data[1]
finally:
    pass

#dust sensor define pins
measurePIN = ADC(Pin(33)) #analog sensor
measurePIN.atten(ADC.ATTN_11DB) #range 0-4095 -> 5 V
LedPower = Pin(25, Pin.OUT)
samplingTime = 280 #original 280
deltaTime = 40
sleepTime = 9680
voMeasured = 0
calcVoltage = 0
dustDensity = 0

#dust sensor fn
def readDust():
    LedPower.value(0)
    sleep_us(samplingTime)
    voMeasured = measurePIN.read() #read dust value
    sleep_us(deltaTime)
    LedPower.value(1)
    sleep_us(sleepTime)
    #0 – 5 V mapped to 0 – 4095
    calcVoltage = voMeasured * (5.0 / 4096)
    dustDensity = 0.17 * calcVoltage - 0.01 #miligrams per cubic meter
    if dustDensity < 0:
      dustDensity = 0
    return(dustDensity*1000) #micrograms per cubic meter

#set values for looping and calculating averages    
counter = 0
sumTI=0
t=0
sumRH=0
rh=0
sumCO=0
co2=0
sumTV=0
tvoc=0
sumPM=0
pm=0

#set API values as unknown (when there's no WiFi connection,
#still measure and write sensor values)
t_e = str("NaN")
r_hum_e = str("NaN")
p_e = str("NaN")
wind_s = str("NaN")
wind_d = str("NaN")
direction = str("NaN")
AQI_index = -1

#blink all LEDs to signal first loop start
led_success.value(1) #start loop blink
sleep_ms(1000)
led_success.value(0)
sleep_ms(500)
led_success.value(1)
sleep_ms(250)
led_wifi.value(1)
sleep_ms(250)
led_int_aq.value(1)
sleep_ms(250)
led_ext_aq.value(1)
sleep_ms(250)
led_success.value(0)
led_wifi.value(0)
led_int_aq.value(0)
led_ext_aq.value(0)
sleep_ms(500)
led_ext_aq.value(1)
sleep_ms(1000)
led_ext_aq.value(0)

#check LED values from stored data
if int(AQI_index) <=50 and int(AQI_index) >= 0: led_ext_aq.value(1)
else: led_ext_aq.value(0)
gc.collect()
#check LED values from stored data
if int(dust) >=35: led_int_aq.value(1)
else: led_int_aq.value(0)
gc.collect()

#start measuring time for next reset LED data
last_write_commit_ms = utime.ticks_ms()
#start measuring time for next baseline check
last_baseline_commit_ms = utime.ticks_ms()

while True:
  #last measurement from SGP30
  last_iaq_check_ms = utime.ticks_ms()

  if utime.ticks_ms() - last_write_commit_ms > WRITE_INTERVAL_MS: #900 seconds for 15 minutes, you can also use time delta with utime.ticks_ms()
    try:
      #get weather and AQI values from web APIs
        Test = owmapi.WeatherStation('enter your city ID from openweathermap', 'enter your API key from openweathermap')  #City ID, API key
        t_e, r_hum_e, p_e, wind_s, wind_d, direction = Test.get_current_weather('enter your WiFi SSID', 'enter you WiFi password')  #WiFi credentials
        AQI_index = Test.get_AQI_info('enter your WiFi SSID', 'enter you WiFi password')
    except Exception as eks:
        print(eks)
        t_e = str("NaN")
        r_hum_e = str("NaN")
        p_e = str("NaN")
        wind_s = str("NaN")
        wind_d = str("NaN")
        smjer = str("NaN")
        AQI_index = -1

    #check if AQI index is less than 50, and light up the green LED   
    if int(AQI_index) <=50 and int(AQI_index) >= 0: led_ext_aq.value(1)
    else: led_ext_aq.value(0)
    gc.collect()
    
    #average 15 minutes readings append to file on SD card
    t=sumTI/counter
    rh=sumRH/counter
    co2=sumCO/counter
    tvoc=sumTV/counter
    dust=sumPM/counter
    counter=0
    sumTI=0
    sumRH=0
    sumCO=0
    sumTV=0
    sumPM=0
    
    #check if PM2.5 level indoors is bad
    #light up yellow LED for fine dust over 35 ug/m3
    if int(dust) >=35: led_int_aq.value(1)
    else: led_int_aq.value(0)
    gc.collect()
    
    try: #update google sheets with values obtained from APIs for maintenance
        Test = owmapi.WeatherStation('enter your city ID from openweathermap', 'enter your API key from openweathermap')
        Test.post_update('enter your WiFi SSID', 'enter you WiFi password', AQI_index, wind_s, direction)
        print("posted")
    except Exception as e:
        print(e)
        gc.collect()
        print('Failed to publish status data.')
    
    #open file on SD card and append values in one row, comma separated values
    DATA_FILE = open("sd/log_data_avdic_apartment.txt","a+")
    DATA_FILE.write("%s.%s.%s,%s,%s:%s:%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (ds.DateTime()[2],ds.DateTime()[1],ds.DateTime()[0],ds.DateTime()[3],ds.DateTime()[4],ds.DateTime()[5],ds.DateTime()[6],t,rh,co2,tvoc,dust,t_e,r_hum_e,p_e,wind_s,wind_d,direction,AQI_index))
    gc.collect()
    #signal successful append
    led_success.value(1)
    sleep_ms(500)
    led_success.value(0)
    DATA_FILE.close()
    last_write_commit_ms = utime.ticks_ms()

  #read values from dust PM2.5 sensor
  pm = readDust()
  #read values from SHT20 sensor
  t = sht_sensor.get_temperature()
  rh = sht_sensor.get_relative_humidity()
  #read eCO2 and tVOC values from SGP30 sensor
  co2, tvoc = sgp30.measure_iaq()
  ah = uSGP30.convert_r_to_a_humidity(t, rh) #humidity compensation
  sgp30.set_absolute_humidity(ah) #humidity compensation

  #add values to a sum, and increase counter by 1 for every loop
  sumTI = sumTI + t
  sumRH = sumRH + rh
  sumCO = sumCO + co2
  sumTV = sumTV + tvoc
  sumPM = sumPM + pm
  counter = counter + 1
    
  led_success.value(1) #loop check
  sleep_ms(100)
  led_success.value(0)
  
  if utime.ticks_ms() - last_baseline_commit_ms > BASELINE_INTERVAL_MS:
    #get current baseline and store on SD card
    current_baseline = sgp30.get_iaq_baseline()
    with open(BASELINE_FILE, "w") as file:
      file.write(str(current_baseline))
      file.close()
    #get current data for LEDs and store on SD card
    with open(LAST_READ_DATA_FILE, "w") as file:
      file.write(str("[%s, %s]" % (dust, AQI_index)))
      file.close()
    print("Baseline commited:", str(current_baseline))
    machine.reset()
    last_baseline_commit_ms = utime.ticks_ms()

  gc.collect()
  
  utime.sleep_ms(MEASURE_INTERVAL_MS - (utime.ticks_ms() - last_iaq_check_ms))






























































































