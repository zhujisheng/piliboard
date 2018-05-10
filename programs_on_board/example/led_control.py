import machine
import time

def flash(time_step=1000):
    print("初始化……")
    # PiliBoard的LED灯在5号GPIO上
    p5 = machine.Pin(5, machine.Pin.OUT)

    print("开始运行……")
    while True:
        print("明……")
        p5.value(1)
        time.sleep_ms(time_step)

        print("灭……")
        p5.value(0)
        time.sleep_ms(time_step)
