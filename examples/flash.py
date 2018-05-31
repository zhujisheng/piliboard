# led_flash.py
import machine
import time

print("载入flash.py ")
n = 0

def flash(time_step=1000):
    global n
    print("初始化……")
    # PiliBoard的LED灯在5号GPIO上
    p5 = machine.Pin(5, machine.Pin.OUT)

    print("开始循环运行……")
    while True:
        n = n + 1
        print("第%d次"%n)
        print("明……")
        p5.value(1)
        time.sleep_ms(time_step)

        print("灭……")
        p5.value(0)
        time.sleep_ms(time_step)
