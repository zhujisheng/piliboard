from SimpleDevice import PWMLight
from WebConfig import WebConfig
from Config import Config
from StateMQTTClient import StateMQTTClient
from ubinascii import hexlify
import network
import machine
import utime
import micropython
import sys

ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

LIGHT_PIN = 5
DEVICE_NAME = 'pilight_pwm_' + hexlify(ap_if.config("mac")[-3:]).decode()

CONFIG_DATA_SCHEMA = """
{"name": "%s",
"command_topic": "%s",
"state_topic": "%s",
"availability_topic": "%s",
"brightness_command_topic": "%s",
"brightness_state_topic": "%s"}
"""

BASE_TOPIC = 'piliboard/' + DEVICE_NAME
AVAILABILITY_TOPIC = BASE_TOPIC + "/availability"
COMMAND_TOPIC = BASE_TOPIC + "/command"
STATE_TOPIC = BASE_TOPIC + "/state"
BRIGHTNESS_COMMAND_TOPIC = BASE_TOPIC + "/brightness/command"
BRIGHTNESS_STATE_TOPIC = BASE_TOPIC + "/brightness/state"

CONFIG_TOPIC = 'homeassistant/light/piliboard/' + DEVICE_NAME + '/config'
CONFIG_DATA = CONFIG_DATA_SCHEMA % (DEVICE_NAME,
                                    COMMAND_TOPIC,
                                    STATE_TOPIC,
                                    AVAILABILITY_TOPIC,
                                    BRIGHTNESS_COMMAND_TOPIC,
                                    BRIGHTNESS_STATE_TOPIC,
                                    )

MqttClient = None
mqtt_conf = Config()

webconfig = WebConfig(mqtt_conf=mqtt_conf, main_module=None, device_name=DEVICE_NAME)

pilight = PWMLight( led_num=LIGHT_PIN )


def mqtt_start():
    MqttClient.connect()
    if MqttClient.connected:
        print("mqtt connected: subto {b}".format(b=COMMAND_TOPIC))
        MqttClient.subscribe(COMMAND_TOPIC)
        MqttClient.subscribe(BRIGHTNESS_COMMAND_TOPIC)
        MqttClient.publish( CONFIG_TOPIC, CONFIG_DATA.encode(), retain=True)
        MqttClient.publish( AVAILABILITY_TOPIC, b"online", retain=True)
        MqttClient.publish( STATE_TOPIC, pilight._state.encode(), retain=True )
        MqttClient.publish( BRIGHTNESS_STATE_TOPIC, str(pilight._brightness).encode(), retain=True )
        return True
    else:
        print("Can't connect to MQTT Broker")
        return False


def mqtt_cb(topic, msg):
    print((topic, msg))

    if webconfig.started:
        webconfig.stop()

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            pilight.turn_on()
        elif msg == b"OFF":
            pilight.turn_off()
        MqttClient.publish( STATE_TOPIC, pilight._state.encode(), retain=True )

    elif topic==BRIGHTNESS_COMMAND_TOPIC.encode():
        try:
            brightness=int(msg.decode())
        except:
            return
        ret = pilight.turn_brightness(brightness)
        MqttClient.publish( BRIGHTNESS_STATE_TOPIC, str(ret).encode(), retain=True )


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


#    try:
    while True :
        if webconfig.started:
            client, cliAddr = webconfig._HttpServer.accept()
            if client:
                webconfig._HttpServer.handle_client(client, cliAddr)
                continue

        if not MqttClient.connected:
            now = utime.time()
            last_resp_time = now
            delta = now - last_try_time1
            if delta > 30:
                last_try_time1 = now
                if (not sta_if.isconnected()) or (not mqtt_start()):
                    if not webconfig.started:
                        webconfig.start()
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

            if webconfig.started and webconfig.data_changed==False:
                webconfig.stop()

#    except KeyboardInterrupt:
#        sys.exit()
#    else:
#        machine.reset()
