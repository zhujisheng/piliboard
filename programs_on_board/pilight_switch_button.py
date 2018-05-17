from SimpleDevice import SwitchLight
from Config import Config
from StateMQTTClient import StateMQTTClient
from IrqLongpressReset import IrqLongpressReset
from ubinascii import hexlify
import network
import machine
import utime
import micropython

ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

RESET_PIN = 4
LED_PIN = 5
LIGHT_PIN = 12
PROGRAM_NAME = 'pilight_switch_button'
DEVICE_NAME = 'pilight_switch_' + hexlify(ap_if.config("mac")[-3:]).decode()

CONFIG_DATA_SCHEMA = """
{"name": "%s",
"command_topic": "%s",
"state_topic": "%s",
"availability_topic": "%s"}
"""

BASE_TOPIC = 'piliboard/' + DEVICE_NAME
AVAILABILITY_TOPIC = BASE_TOPIC + "/availability"
COMMAND_TOPIC = BASE_TOPIC + "/command"
STATE_TOPIC = BASE_TOPIC + "/state"

CONFIG_TOPIC = 'homeassistant/light/piliboard/' + DEVICE_NAME + '/config'
CONFIG_DATA = CONFIG_DATA_SCHEMA % (DEVICE_NAME,
                                    COMMAND_TOPIC,
                                    STATE_TOPIC,
                                    AVAILABILITY_TOPIC,
                                    )

MqttClient = None
mqtt_conf = Config()

pilight = SwitchLight( led_num=LIGHT_PIN )


def mqtt_start():
    MqttClient.connect()
    if MqttClient.connected:
        print("mqtt connected: subto {b}".format(b=COMMAND_TOPIC))
        MqttClient.subscribe(COMMAND_TOPIC)
        MqttClient.publish( CONFIG_TOPIC, CONFIG_DATA.encode(), retain=True)
        MqttClient.publish( AVAILABILITY_TOPIC, b"online", retain=True)
        MqttClient.publish( STATE_TOPIC, pilight._state.encode(), retain=True )
        return True
    else:
        print("Can't connect to MQTT Broker")
        return False


def mqtt_cb(topic, msg):
    print((topic, msg))

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            pilight.turn_on()
        elif msg == b"OFF":
            pilight.turn_off()
        MqttClient.publish( STATE_TOPIC, pilight._state.encode(), retain=True )

def toggle():
    pilight.toggle()
    if MqttClient:
        MqttClient.publish( STATE_TOPIC, pilight._state.encode(), retain=True )

def mqtt_init(conf):
    global MqttClient

    if (conf == None) or not('mqtt_ip' in conf):
        MqttClient = StateMQTTClient(DEVICE_NAME, None)
        return False

    port=1883
    try:
        port=int(conf.get("mqtt_port"))
    except:
        print("MQTT Input port error, let it be 1883, and continue...")
        
    MqttClient = StateMQTTClient(DEVICE_NAME, conf.get("mqtt_ip"), port=port, user=conf.get("mqtt_user"), password=conf.get("mqtt_password"), keepalive=60)
    MqttClient.set_callback(mqtt_cb)
    MqttClient.set_last_will( AVAILABILITY_TOPIC, b"offline", retain=True)

    return True


def start():
    irq = IrqLongpressReset(pin_no=RESET_PIN, led_pin_no=LED_PIN, main_module=PROGRAM_NAME, press_action=toggle, device_name=DEVICE_NAME)

    last_try_time1 = 0
    last_try_time2 = 0
    last_resp_time = utime.time()

    ap_if.active(False)
    sta_if.active(True)
    if mqtt_init(mqtt_conf.content):
        utime.sleep(5)
        mqtt_start()
    else:
        print("mqtt_init failed")
        return


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
