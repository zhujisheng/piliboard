import machine
from umqtt.simple import MQTTClient
from ubinascii import hexlify

LED = machine.Pin(5, machine.Pin.OUT)
CLIENT_ID = hexlify(machine.unique_id()).decode()
COMMAND_TOPIC = CLIENT_ID + '/command'

def mqtt_cb(topic, msg):
    print("接收到来自MQTT服务器的消息——topic：{t}；message：{m}".format(t=topic,m=msg))

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            LED.value(1)
        elif msg == b"OFF":
            LED.value(0)

def main( mqtt_broker='test.mosquitto.org', mqtt_port=1883, mqtt_user=None, mqtt_password=None, client_id=None, command_topic=None):

    global COMMAND_TOPIC, CLIENT_ID

    if client_id:
        CLIENT_ID = client_id
    if command_topic:
        COMMAND_TOPIC = command_topic

    mqtt = MQTTClient( CLIENT_ID, mqtt_broker, mqtt_port, mqtt_user, mqtt_password )
    mqtt.set_callback(mqtt_cb)
    mqtt.connect()
    mqtt.subscribe(COMMAND_TOPIC)

    print("链接到服务器：{s},端口：{p}".format(s=mqtt_broker,p=mqtt_port))
    print("接受命令topic：开关（{c}）".format(c=COMMAND_TOPIC))

    while True:
        mqtt.check_msg()
