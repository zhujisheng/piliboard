import dht
import machine

d = dht.DHT11(machine.Pin(2))
d.measure()

def measure():
    d.measure()
    print("当前温度：%d摄制度"%d.temperature())
    print("当前湿度度：%d%%"%d.humidity())
