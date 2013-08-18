# -*- coding: utf-8 -*-
import socket
import smbus
import time
import httplib, urllib

bus=smbus.SMBus(1)
address=0x48
counter=1

def tmp102Read():
        tmp = (bus.read_word_data(address, 0))
        return tmp

def TemperatureConversion():
        '''
        #the received tmp102 data must be reordered
        e.g. received data=0x2011 (LSB=0x11, MSB=0x20)
        must be translated to 0x1120. 
        LSB<<8 gives additional 2 nulls 0x1100 now one may combine it with MSB
        reverseddata=LSBtoWord|MSB the returned value is 0x1120
        next reversed data must be shifted by 4 (according to tmp102 documentation)
        finally the result must be multiplied by 0.0625 convertedtemp = reverseddata*0.0625
        '''
        LSBtoWord = (LSB<<8)
        reverseddata = LSBtoWord|MSB
        reverseddata = reverseddata>>4
        convertedtemp = reverseddata*0.0625
        return convertedtemp

while 1:
    iTmp102 = tmp102Read()
    LSB = iTmp102 % 256
    MSB = iTmp102 / 256
    tempInC = str("%.4f" % TemperatureConversion())
    print(str(counter) + ": " + tempInC)
    params = urllib.urlencode({'key': '5SR4JLCOJXRO0IRD','field1': tempInC})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    conn.close()
    counter += 1
    time.sleep(60)
