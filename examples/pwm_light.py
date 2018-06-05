import machine
import time

def start(time_step=1, brightness_step=1):
    print("初始化……")
    # LED灯在5号GPIO上
    pin = machine.Pin(5, machine.Pin.OUT)
    # 用PWM方式调制输出，以控制灯光亮度
    led = machine.PWM(pin,freq=500)


    print("每{t}毫秒，亮度提高{b}（在亮度为1024处循环）"
          .format( t=time_step, b=brightness_step )
          )

    print("开始运行……")
    i=0
    while True:
        led.duty(i)
        i = (i+brightness_step)%1024
        time.sleep_ms(time_step)
