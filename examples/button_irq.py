from machine import Pin

button = Pin(4, Pin.IN)

def callback1(p):
    button.irq(trigger=Pin.IRQ_RISING, handler=callback2)
    print("button pressed")


def callback2(p):
    button.irq(trigger=Pin.IRQ_FALLING, handler=callback1)
    print("button released")


button.irq(trigger=Pin.IRQ_FALLING, handler=callback1)

