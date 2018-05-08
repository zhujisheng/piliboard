from Config import Config
from StateMQTTClient import StateMQTTClient
from ControlApa102 import ControlApa102
from IrqLongpressReset import IrqLongpressReset
from ubinascii import hexlify
import machine
import network
import utime
import micropython
import sys
import json

irq = IrqLongpressReset()

pili_apa102 = ControlApa102( led_num=300, clock_pin=12, data_pin=14 )

CLIENT_ID = hexlify(machine.unique_id()).decode()


CONFIG_DATA_SCHEMA = """
{"platform": "mqtt_json",
"name": "%s",
"command_topic": "%s",
"state_topic": "%s",
"availability_topic": "%s",
"effect": "true",
"brightness":"true",
"rgb":"true",
"effect_list":%s
}
"""

BASE_TOPIC = 'piliboard/pili_apa102_' + CLIENT_ID
AVAILABILITY_TOPIC = BASE_TOPIC + "/availability"
COMMAND_TOPIC = BASE_TOPIC + "/command"
STATE_TOPIC = BASE_TOPIC + "/state"

CONFIG_TOPIC = 'homeassistant/light/piliboard/pili_apa102_' + CLIENT_ID + '/config'
CONFIG_DATA = CONFIG_DATA_SCHEMA % ('piliboard_apa102_'+CLIENT_ID,
                                    COMMAND_TOPIC,
                                    STATE_TOPIC,
                                    AVAILABILITY_TOPIC,
                                    json.dumps(pili_apa102.effect_list),
                                    )

sta_if = network.WLAN(network.STA_IF)
MqttClient = None
conf = Config()


def mqtt_start():
    MqttClient.connect()
    if MqttClient.connected:
        print("mqtt connected: subto {b}".format(b=COMMAND_TOPIC))
        MqttClient.subscribe(COMMAND_TOPIC)
        MqttClient.publish( CONFIG_TOPIC, CONFIG_DATA.encode(), retain=True)
        MqttClient.publish( AVAILABILITY_TOPIC, b"online", retain=True)
        MqttClient.publish( STATE_TOPIC, json.dumps(pili_apa102.state).encode(), retain=True )
        return True
    else:
        print("Can't connect to MQTT Broker")
        return False


def mqtt_cb(topic, msg):
    print((topic, msg))

    if topic==COMMAND_TOPIC.encode():
        command = json.loads(msg.decode())
        pili_apa102.control( command )

        MqttClient.publish( STATE_TOPIC, json.dumps(pili_apa102.state).encode(), retain=True )


def init(conf):
    global MqttClient

    if conf == None:
        return False
    if not('mqtt_ip' in conf):
        return False

    port=1883
    try:
        port=int(conf.get("mqtt_port"))
    except:
        print("MQTT Input port error, let it be 1883, and continue...")
        
    MqttClient = StateMQTTClient(CLIENT_ID, conf.get("mqtt_ip"), port=port, user=conf.get("mqtt_user"), password=conf.get("mqtt_password"), keepalive=60)
    MqttClient.set_callback(mqtt_cb)
    MqttClient.set_last_will( AVAILABILITY_TOPIC, b"offline", retain=True)

    return True

def start():
    last_try_time1 = 0
    last_try_time2 = 0
    last_resp_time = utime.time()

    if (not init(conf.content)):
        print("init failed")
        return
    utime.sleep(5)

#    try:
    if True:

        while True :
            if not sta_if.isconnected():
                print("Can't connect to WIFI")
                utime.sleep(3)

            elif not MqttClient.connected:
                now = utime.time()
                last_resp_time = now
                delta = now - last_try_time1
                if delta > 10:
                    last_try_time1 = now
                    mqtt_start()
                    micropython.mem_info()

            else:
                if MqttClient.check_msg()==1:
                    last_resp_time = utime.time()
                now = utime.time()
                if now-last_resp_time > 20:
                    print("No mqtt ping response, disconnect it")
                    MqttClient.disconnect()
                    continue

                delta = now - last_try_time2
                if delta > 10:
                    MqttClient.ping()
                    last_try_time2 = now
                    micropython.mem_info()

#    except KeyboardInterrupt:
#        sys.exit()
#    else:
#        machine.reset()
