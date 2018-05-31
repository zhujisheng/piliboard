import machine
from umqtt.simple import MQTTClient
from ubinascii import hexlify

LED = machine.Pin(5, machine.Pin.OUT)
CLIENT_ID = hexlify(machine.unique_id()).decode()
COMMAND_TOPIC = 'my/test/command'

# 回调函数，当收到订阅的mqtt消息时，调用此函数
# 传入参数为消息的主题，以及消息的内容（bytes格式）
def mqtt_cb(topic, msg):
    print("接收到来自MQTT服务器的消息——topic：{t}；message：{m}".format(t=topic,m=msg))

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            LED.value(1)
        elif msg == b"OFF":
            LED.value(0)

def main( mqtt_broker='test.mosquitto.org', mqtt_port=1883, mqtt_user=None, mqtt_password=None, client_id=CLIENT_ID ):

    mqtt = MQTTClient( client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password )

    # 设置回调函数（当收到订阅的mqtt消息时调用的函数）
    mqtt.set_callback(mqtt_cb)

    mqtt.connect()

    # 在服务器上注册接收哪些mqtt消息
    mqtt.subscribe(COMMAND_TOPIC)

    print("连接到服务器：{s},端口：{p}".format(s=mqtt_broker,p=mqtt_port))
    print("接受命令topic：开关（{c}）".format(c=COMMAND_TOPIC))

    while True:
        # 检查是否有新消息
        mqtt.check_msg()
