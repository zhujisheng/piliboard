from WebConfig import WebConfig
from Config import Config
from StateMQTTClient import StateMQTTClient
from ubinascii import hexlify
import network
import machine
import utime
import micropython
import sys


LED = machine.PWM(machine.Pin(5),freq=500)

CLIENT_ID = hexlify(machine.unique_id()).decode()
DEVICE_NAME = 'pilight_' + CLIENT_ID

CONFIG_DATA_SCHEMA = """
{"name": "%s",
"command_topic": "%s",
"state_topic": "%s",
"availability_topic": "%s",
"brightness_command_topic": "%s",
"brightness_state_topic": "%s",
"brightness_scale": 100}
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


ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

MqttClient = None
mqtt_conf = Config()
webconfig = WebConfig(mqtt_conf=mqtt_conf, change_main=False,device_name=DEVICE_NAME)

brightness = 100
is_on = False


def mqtt_start():
    MqttClient.connect()
    if MqttClient.connected:
        print("mqtt connected: subto {b}".format(b=COMMAND_TOPIC))
        MqttClient.subscribe(COMMAND_TOPIC)
        MqttClient.subscribe(BRIGHTNESS_COMMAND_TOPIC)
        MqttClient.publish( CONFIG_TOPIC, CONFIG_DATA.encode(), retain=True)
        MqttClient.publish( AVAILABILITY_TOPIC, b"online", retain=True)
        MqttClient.publish( STATE_TOPIC, b"ON" if is_on else b"OFF", retain=True )
        MqttClient.publish( BRIGHTNESS_STATE_TOPIC, str(brightness).encode(), retain=True )
        return True
    else:
        print("Can't connect to MQTT Broker")
        return False


def mqtt_cb(topic, msg):
    global brightness, is_on
    print((topic, msg))

    if webconfig.started:
        webconfig.stop()

    if topic==COMMAND_TOPIC.encode():
        if msg == b"ON":
            is_on = True
            LED.duty(int(brightness/100*1024))
            MqttClient.publish( STATE_TOPIC, msg, retain=True )
        elif msg == b"OFF":
            is_on = False
            LED.duty(0)
            MqttClient.publish( STATE_TOPIC, msg, retain=True )

    elif topic==BRIGHTNESS_COMMAND_TOPIC.encode():
        try:
            brightness=int(msg.decode())
        except:
            return
        if brightness < 0:
            brightness = 0
        elif brightness > 100:
            brightness = 100

        is_on = True
        LED.duty(int(brightness/100*1024))
        MqttClient.publish( BRIGHTNESS_STATE_TOPIC, str(brightness).encode(), retain = True )


def mqtt_init(conf):
    global MqttClient

    if conf == None:
        MqttClient = StateMQTTClient(CLIENT_ID, None)
        return False
    if not('mqtt_ip' in conf):
        MqttClient = StateMQTTClient(CLIENT_ID, None)
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

    ap_if.active(False)
    sta_if.active(True)
    mqtt_init(mqtt_conf.content)
    utime.sleep(5)
    mqtt_start()


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
