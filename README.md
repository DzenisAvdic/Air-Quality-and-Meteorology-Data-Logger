# Air Quality and Meteorology Data Logger

![data logger](https://github.com/DzenisAvdic/Air-Quality-and-Meteorology-Data-Logger/blob/main/images/data_logger_small.jpg)

Collecting good set of data for academic research is always a challenging task. For me, assembling and making this data logger run flawlessly was quite a challenge, since I'm self-taught in this filed. My profession is architecture, and architectural research of interior comfort and indoor air quality needs tools to monitor data related to these topics.

Data logger is based on a ESP32 microcontroller (Croduino NOVA32 made by e-r.io) and programmed in micropython. Data is colleted and stored to microSD card in a .txt file format with comma separeted values for later conversion in .csv and pandas analysis. Sensors included are SHT20 for temperature and relative humidity readings, SGP30-2.5k for eCO2 and tVOC readings and PM2.5 dust analog sensor for indoors AQI evaluation. Since this data should be compared to outdoors meteorology, additional requests are made to collect data from OpenWeatherMAap API and aqicn.org API. Data logger is going to be introduced inside architectural space to be monitored, and for maintenance purposes, IFTTT trigger is added to post data to Google Sheet document. Data logger has basic air quality monitor UI, just to make it less "boring" inside room, and yellow LED light up when air inside is more than 100 AQI index (cca. 35ug/m3) and green LED light up when air outside is good enough (less than 50 AQI index) for ventilating (opening window).

Requirements (thanks to https://e-radionica.com/en/):

- ESP32 board (Croduino NOVA32 from e-r.io used)
- SHT20 breakout board (e-r.io breakout board used)
- SGP30 breakout board (e-r.io breakout board used)
- RTC module (DS1302 used, for different RTC use different micropython module) + CR2032 3V battery
- Sharp PM2.5 dust sensor GP2Y1010AU0F, 220 Ohm resistor and 220 uF capacitor (usually provided with sensor)
- microSD card module (also from e-radionica) + microSD card (32GB used, can be smaller)
- few LEDs and 220 Ohm resistors
- more than few wires, and some patience to connect them and solder everything together
- 5V power supply (5V, 950mA used)


![requirements](https://github.com/DzenisAvdic/Air-Quality-and-Meteorology-Data-Logger/blob/main/images/requirements_small.jpg)

Pins for individual components can be read from source code, and also edited to adapt to your ESP32 board, and here is the list of pins used:

microSD card module:
- SPI -> 2
- SCK -> 14
- MOSI -> 13
- MISO -> 12
- CS -> 15

SHT20 sensor:
- SCL -> 16
- SDA ->17

SGP30 sensor:
- SCL -> 18
- SDA -> 19

PM2.5 dust sensor:
- analog read -> 33
- LED inside sensor -> 25
- wiring diagram: https://hacksterio.s3.amazonaws.com/uploads/attachments/1042324/untitled_sketch_bb_ByIh5u0VXi.jpg

RTC module:
- CLK -> 4
- DIO -> 32
- CS -> 5

LEDs:
- info LED -> 26
- WiFi LED -> 21
- AQI indoors -> 22
- AQI outside -> 23

ESP32 has micropython firmware version: esp32-idf3-20200902-v1.13.bin, that can be downloaded here: https://micropython.org/download/esp32/

Everything is done using uPyCraft V1.1 for micropython coding.

Finally, it's all assembled and packed inside designed and handmade enclosure.

Thanks to my fellow architects at https://www.instagram.com/osa_lamps/ for providing it for free. Check out their Instagram page, they're designing and making some pretty good lamps.

![enclosure](https://github.com/DzenisAvdic/Air-Quality-and-Meteorology-Data-Logger/blob/main/images/enclosure_small.jpg)



I tried to fix as many bugs as I could find, and there should still be need for some tweaks and fixes.
In the end, here is the final output inside one line of .txt file. Updated every ~15 minutes:

23.12.2020,3,11:52:12,25.13388,45.58258,404.9233,0.0,100.9003,2,100,1023,1,0,N,169

general data (timestamp):

date, day of week, time

indoors air parameters:

temperature, relative humidity, CO2 levels, tVOC levels, PM2.5 levels

outdoors meteorology data:

temperature, realtive humidity, atmospheric pressure, wind speed, wind direction (polar angle), wind direction (cardinal), AQI index


![final assembly](https://github.com/DzenisAvdic/Air-Quality-and-Meteorology-Data-Logger/blob/main/images/final_assembly_small.jpg)

For providing useful resources, thanks to:

https://github.com/fantasticdonkey/uSGP30

https://github.com/nenadfilipovic/esp8266-micropython-weather-station/

https://github.com/micropython/micropython/tree/master/drivers/sdcard

https://github.com/omarbenhamid/micropython-ds1302-rtc





