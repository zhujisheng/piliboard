from machine import Pin
from apa102 import APA102

clock_pin = 12
data_pin = 14
leds_num = 30

clock = Pin(clock_pin, Pin.OUT)
data = Pin(data_pin, Pin.OUT)
apa = APA102(clock, data, leds_num)

color = [(255,0,0,31),(0,255,0,31),(0,0,255,31),(255,255,255,31)]    #红、绿、蓝、白
for i in range(0,leds_num):
    apa[i] = color[i%4]
apa.write()
