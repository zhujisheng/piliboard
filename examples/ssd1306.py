from machine import I2C
import machine
from ssd1306 import SSD1306_I2C

WIDTH = const(128)
HEIGHT = const(64)

pscl = machine.Pin(12, machine.Pin.OUT)
psda = machine.Pin(13, machine.Pin.OUT)
i2c = machine.I2C(scl=pscl, sda=psda)
ssd = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def textshow():
    ssd.text("Welcome to",0,0)
    ssd.text("PiliBoard!",0,10)
    ssd.show()

def drawshow():
    rhs = WIDTH -1
    ssd.line(rhs - 20, 0, rhs, 20, 1)
    square_side = 10
    ssd.fill_rect(rhs - square_side, 0, square_side, square_side, 1)
    ssd.show()

def clear():
    ssd.fill(0)
    ssd.show()
