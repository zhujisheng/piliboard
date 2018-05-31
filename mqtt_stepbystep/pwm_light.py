import machine
from umqtt.simple import MQTTClient
from ubinascii import hexlify

# 一盏PWM调制的灯
LED = machine.PWM(machine.Pin(5))

CLIENT_ID = hexlify(machine.unique_id()).decode()
COMMAND_TOPIC = 'my/test/command'
STATE_TOPIC = "my/test/state"
AVAILABILITY_TOPIC = "my/test/availability"
BRIGHTNESS_COMMAND_TOPIC = "my/test/brightness/command"
BRIGHTNESS_STATE_TOPIC = "my/test/brightness/state"

CONFIG_TOPIC = 'homeassistant/light/piliboard_pwm/' + CLIENT_ID + '/config'

# 此处增加了亮度命令主题与亮度状态反馈主题
CONFIG_DATA = """
{"name": "%s",
"command_topic": "%s",
"state_topic": "%s",
"availability_topic": "%s",
"brightness_command_topic": "%s",
"brightness_state_topic": "%s"}
"""%("PWM light auto discovered",
     COMMAND_TOPIC,
     STATE_TOPIC,
     AVAILABILITY_TOPIC,
     BRIGHTNESS_COMMAND_TOPIC,
     BRIGHTNESS_STATE_TOPIC
     )

mqtt = None
LED.duty(0)
light_state = 'OFF'
light_brightness = 255


def mqtt_cb(topic, msg):
    # 此处增加对于亮度命令的接收处理，以及亮度状态的反馈
    global light_state, light_brightness
    print("接收到来自MQTT服务器的消息——topic：{t}；message：{m}".format(t=topic,m=msg))

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            LED.duty(int(light_brightness/255*1023))
            light_state = 'ON'
            
        elif msg == b"OFF":
            LED.duty(0)
            light_state = 'OFF'
        mqtt.publish( STATE_TOPIC, light_state.encode(), retain=True )

    # 接收到亮度指令
    elif topic==BRIGHTNESS_COMMAND_TOPIC.encode():
        try:
            light_brightness=int(msg.decode())
            assert light_brightness > 0 and light_brightness <= 255
        except:
            print('received error brightness command')
            return
        LED.duty(int(light_brightness/255*1023))
        mqtt.publish( BRIGHTNESS_STATE_TOPIC, str(light_brightness).encode(), retain=True )



def main( mqtt_broker='test.mosquitto.org', mqtt_port=1883, mqtt_user=None, mqtt_password=None, client_id=CLIENT_ID):

    global mqtt

    mqtt = MQTTClient( client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password, keepalive=60 )
    mqtt.set_callback(mqtt_cb)
    mqtt.set_last_will( AVAILABILITY_TOPIC, b"offline", retain=True)

    mqtt.connect()
    mqtt.subscribe(COMMAND_TOPIC)

    #此处增加对亮度命令的订阅
    mqtt.subscribe(BRIGHTNESS_COMMAND_TOPIC)

    mqtt.publish( CONFIG_TOPIC, CONFIG_DATA.encode(), retain=True)
    mqtt.publish( AVAILABILITY_TOPIC, b"online", retain=True)

    mqtt.publish( STATE_TOPIC, light_state.encode(), retain=True )
    mqtt.publish( BRIGHTNESS_STATE_TOPIC, str(light_brightness).encode(), retain=True )

    print("链接到服务器：{s},端口：{p}".format(s=mqtt_broker,p=mqtt_port))
    print("接受开关命令topic：开关（{c}）".format(c=COMMAND_TOPIC))
    print("接受亮度命令topic：开关（{c}）".format(c=BRIGHTNESS_COMMAND_TOPIC))

    while True:
        mqtt.check_msg()
