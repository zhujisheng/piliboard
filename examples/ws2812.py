from machine import Pin
from neopixel import NeoPixel
import time

def init(data_pin, leds_num):
    global np

    dp = Pin(data_pin, Pin.OUT)
    np = NeoPixel(dp, leds_num)
    clear()

# 按红、绿、蓝、白显示灯带
def demo0():
    color = [(255,0,0),(0,255,0),(0,0,255),(255,255,255)]    #红、绿、蓝、白
    for i in range(0,np.n):
        np[i] = color[i%4]
    np.write()

# 白色循环2圈
def demo1():
    n = np.n
    for i in range(2 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(25)
    clear()

# 反射
def demo2():
    n = np.n
    for i in range(2 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)

# 褪色
def demo3():
    n = np.n
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()

def clear():
    n = np.n
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()
