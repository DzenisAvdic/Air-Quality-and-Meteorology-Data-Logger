# Air-Quality-and-Meteorology-Data-Logger

![data logger](https://github.com/DzenisAvdic/Air-Quality-and-Meteorology-Data-Logger/blob/master/images/data_logger_small.jpg)

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

![requirements](https://github.com/DzenisAvdic/Air-Quality-and-Meteorology-Data-Logger/blob/master/images/requirements_small.jpg)
