import machine
from umqtt.simple import MQTTClient
from ubinascii import hexlify

LED = machine.Pin(5, machine.Pin.OUT)
CLIENT_ID = hexlify(machine.unique_id()).decode()
COMMAND_TOPIC = 'my/test/command'
STATE_TOPIC = "my/test/state"
AVAILABILITY_TOPIC = "my/test/availability"

mqtt = None

def mqtt_cb(topic, msg):
    print("接收到来自MQTT服务器的消息——topic：{t}；message：{m}".format(t=topic,m=msg))

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            LED.value(1)
        elif msg == b"OFF":
            LED.value(0)

        state = b"ON" if LED.value()==1 else b"OFF"
        mqtt.publish( STATE_TOPIC, state, retain=True )


def main( mqtt_broker='test.mosquitto.org', mqtt_port=1883, mqtt_user=None, mqtt_password=None, client_id=CLIENT_ID):

    global mqtt

    # 此处增加keepalive=60，表示60秒以上未通讯，客户端为断开
    mqtt = MQTTClient( client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, keepalive=60 )
    mqtt.set_callback(mqtt_cb)
    # 设置lastwill，相应消息会在断开mqtt连接后自动在服务器端发布
    # 注：在connect之前设置lastwill
    mqtt.set_last_will( AVAILABILITY_TOPIC, b"offline", retain=True)

    mqtt.connect()
    mqtt.subscribe(COMMAND_TOPIC)
    mqtt.publish( AVAILABILITY_TOPIC, b"online", retain=True)
    state = b"ON" if LED.value()==1 else b"OFF"
    mqtt.publish( STATE_TOPIC, state, retain=True )

    print("链接到服务器：{s},端口：{p}".format(s=mqtt_broker,p=mqtt_port))
    print("接受命令topic：开关（{c}）".format(c=COMMAND_TOPIC))

    while True:
        mqtt.check_msg()
