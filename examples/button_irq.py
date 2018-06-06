from machine import Pin

button = Pin(4, Pin.IN)
is_pressed = False

def callback1(p):
    global is_pressed
    button.irq(trigger=Pin.IRQ_RISING, handler=callback2)
    if not is_pressed:
        is_pressed = True
        print("button pressed")


def callback2(p):
    global is_pressed
    button.irq(trigger=Pin.IRQ_FALLING, handler=callback1)
    if is_pressed:
        is_pressed = False
        print("button released")

button.irq(trigger=Pin.IRQ_FALLING, handler=callback1)
