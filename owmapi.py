import ujson as json
import urequests
import gc

gc.collect()

class WeatherStation:
    def __init__(self, city, api_key, api='https://api.openweathermap.org'):
        self.city = 'id=' + city
        self.api_key = '&appid=' + api_key
        self.api = api

    @staticmethod
    def use_wifi(network_name, network_pass):
        import network
        import time
        import machine
        from machine import Pin, I2C, ADC, SPI
        led_wifi=Pin(21, Pin.OUT) #WiFi status info LED
        sta_if = network.WLAN(network.STA_IF)
        ap = network.WLAN(network.AP_IF) #create access-point interface
        ap.active(False) #deactivate interface
        start = time.ticks_ms()
        to = 15000 #retry connection for 15 seconds, you can edit this
        while not sta_if.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) > to:
                led_wifi.value(1) #connection timeout, light up WiFi LED
                break
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(network_name, network_pass)
            while not sta_if.isconnected() and time.ticks_diff(time.ticks_ms(), start) < to:
                print('connecting')
                time.sleep_ms(500)
        else:
            led_wifi.value(0) #when connected turn LED off
            print('network config:', sta_if.ifconfig())
            a = sta_if.config('mac')
            print('MAC {:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(a[0],a[1],a[2],a[3],a[4]))
    
    def post_update(self, network_name, network_pass, a, b, c): #this fn is added for maintenance reasons
        key = 'add your own key' #IFTTT key for webhooks, post to google sheets
        value1 = a
        value2 = b
        value3 = c
        WeatherStation.use_wifi(network_name, network_pass)
        status_update = json.dumps({'value1':value1, 'value2':value2, 'value3':value3}) #dictionary to pass values
        request_headers = {'Content-Type': 'application/json'}
        #create ifttt.com trigger with webhooks and google sheets, add your trigger name to link
        request = urequests.post('http://maker.ifttt.com/trigger/*here is your trigger name*/with/key/' + key, json=status_update, headers=request_headers)
        request.close()
        gc.collect()
        print("post update success")
            
    def get_AQI_info(self, network_name, network_pass):
        WeatherStation.use_wifi(network_name, network_pass)
        request_url = 'http://api.waqi.info/feed/*add your city and station link*/?token=*add your token obtained from aqicn.com*'
        response = urequests.get(request_url)
        print("aqi response received")
        if (response.status_code >=200 and response.status_code <=229):
            print("aqi response OK")
            aqi_index = str(response.json()['data']['aqi']) #you can read any json data provided, here we read AQI index for PM2.5
            response.close()
            print("AQI read success")
        else:
            print("aqi response not good")
            aqi_index = -1
            response.close()
        return(aqi_index)

    def get_current_weather(self, network_name, network_pass):
        WeatherStation.use_wifi(network_name, network_pass)
        request_url = self.api + '/data/2.5/weather?' + self.city + self.api_key + '&units=metric'
        response = urequests.get(request_url)
        print("response received")
        if (response.status_code >=200 and response.status_code <=229):
          print("response OK")
          temp_e = str(response.json()['main']['temp'])
          r_hum_e = str(response.json()['main']['humidity'])
          p_e = str(response.json()['main']['pressure'])
          wind_s = str(response.json()['wind']['speed'])
          wind_d = str(response.json()['wind']['deg'])
          degrees = float(response.json()['wind']['deg'])
          direction = int(round(degrees/22.5,0)+1)
          dict_direction = {1:"N",2:"NNE",3:"NE",4:"ENE",5:"E",6:"ESE",7:"SE",8:"SSE",9:"S",10:"SSW",11:"SW",12:"WSW",13:"W",14:"WNW",15:"NW",16:"NNW"}
          text_direction = dict_direction[direction]
          response.close()
          print("weather read success")
        else:
          print("response not good")
          temp_e = str("NaN")
          r_hum_e = str("NaN")
          p_e = str("NaN")
          wind_s = str("NaN")
          wind_d = str("NaN")
          degrees = str("NaN")
          text_smjer = str("NaN")
          response.close()
        return(temp_e, r_hum_e, p_e, wind_s, wind_d, text_direction)

#optional, you can also read json data for weather forecast - not used in main code







































