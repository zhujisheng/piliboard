from machine import ADC

adc = ADC(0)

def measure():
    d = adc.read()
    print("测量到输入电压为：%f V"%(d/1024) )
