import dht
import machine
import time
from ubinascii import hexlify

# 引入mqtt客户端库
from umqtt.simple import MQTTClient

# 温湿度传感器连接2号GPIO
PIN_NO = 2

# 初始化一个温湿度传感器
DHT = dht.DHT11(machine.Pin(PIN_NO))

# CLIENT_ID: 每个mqtt客户端有自己独立的client_id标识
# 无所谓是什么，但不同客户端不能相同。此处我们使用8266的unique_id
CLIENT_ID = hexlify(machine.unique_id()).decode()

# 温度和湿度在mqtt服务器上的主题位置
TEMPERATURE_TOPIC = "my/test/dht11/temperature"
HUMIDITY_TOPIC = "my/test/dht11/humidity"

mqtt = None

def main( mqtt_broker='test.mosquitto.org', mqtt_port=1883, mqtt_user=None, mqtt_password=None, client_id=CLIENT_ID):

    global mqtt

    # 初始化mqtt，设置一些需要的参量
    mqtt = MQTTClient( client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password )

    # 连接到mqtt服务器
    mqtt.connect()
    print("连接到服务器：{s},端口：{p}".format(s=mqtt_broker,p=mqtt_port))

    while True:
        # 不断循环，每10秒测量一次温度和湿度，发布到mqtt服务器上
        try:
            DHT.measure()
        except:
            print("No dht sensor connected to Pin(%d)"%(PIN_NO))
            return
        print("测量到温度：%d；湿度：%d"%(DHT.temperature(),DHT.humidity()))
        
        # mqtt发布信息
        mqtt.publish( TEMPERATURE_TOPIC, str(DHT.temperature()).encode(), retain=True)
        mqtt.publish( HUMIDITY_TOPIC, str(DHT.humidity()).encode(), retain=True)
        
        time.sleep(10)
        
    


