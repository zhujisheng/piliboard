from MiniWebSrv import MiniWebSrv
import json
import utime
import machine
import network


HTTP_RES_HEAD = b"""HTTP/1.1 200 OK
Content-Type: application/json;charset=utf-8
Connection: close

"""
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)


class WebConfig:
    def __init__(self, mqtt_conf, change_main=False, main_module=None, device_name='unknown'):
        self._change_main = change_main
        self._main_module = main_module
        self._device_name = device_name
        self._mqtt_conf = mqtt_conf

        routeHandlers = [( "/set_wifi", "POST", self._http_set_wifi ),
                         ( "/set_mqtt", "POST", self._http_set_mqtt ),
                         ( "/set_ap", "POST", self._http_set_ap ),
                         ( "/reboot", "POST", self._http_reboot ),
                         ( "/get_wifi", "GET", self._http_get_wifi ),
                         ( "/get_mqtt", "GET", self._http_get_mqtt ),
                         ( "/get_ap", "GET", self._http_get_ap ),
                         ( "/get_name", "GET", self._http_get_name ),
                         ]
        self._HttpServer = MiniWebSrv(routeHandlers=routeHandlers)
        self._data_changed=False

    def start(self):
        if not self._HttpServer._started:
            ap_if.active(True)
            self._HttpServer.start()
            self._data_changed=False
    def stop(self):
        self._HttpServer.stop()
        ap_if.active(False)
        sta_if.active(True)

    @property
    def started(self):
        return self._HttpServer._started
    @property
    def data_changed(self):
        return self._data_changed

    def _http_set_wifi(self, c_socket, request_data):
        ssid = request_data.get("ssid")
        pwd = request_data.get("pwd")
        c = {}

        sta_if.active(True)
        sta_if.connect(ssid,pwd)

        i=0
        while not sta_if.isconnected():
            utime.sleep(1)
            i += 1
            if i>15:
                sta_if.active(False)
                break

        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()
        self._data_changed=True


    def _http_set_mqtt(self, c_socket, request_data):
        c = {}

        try:
            from StateMQTTClient import StateMQTTClient
            port=1883
            try:
                port=int(request_data.get("mqtt_port"))
            except:
                print("MQTT Input port error, let it be 1883, and continue...")
            MqttClient = StateMQTTClient("testtest", request_data.get("mqtt_ip"), port=port, user=request_data.get("mqtt_user"), password=request_data.get("mqtt_password"), keepalive=60)
            MqttClient.connect()
            if MqttClient.connected:
                self._mqtt_conf.save( request_data )
                c['working']=True
                c['state_info']= [{'测试连接':'成功'},
                                  {'配置文件':'已保存'},
                                  ]
            else:
                c['working']=False
                c['state_info']= [{'测试连接':'失败'},
                                  {'配置文件':'未保存'},
                                  ]
                
            MqttClient.disconnect()
        except:
            c['working']=False
            c['state_info']= [{'测试连接':'异常'},
                              {'配置文件':'未保存'},
                              ]

        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()
        self._data_changed=True
    
    def _http_set_ap(self, c_socket, request_data):
        c = {}

        ap_pwd = request_data.get("ap_pwd")
        ap_if.config( password = ap_pwd )

        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()
        self._data_changed=True

    def _http_reboot(self, c_socket, request_data):
        c = {}

        if self._change_main:
            content = "import %s\n%s.start()\n"%(self._main_module,self._main_module)
            f = open('/main.py', 'w')
            f.write(content)
            f.close()

        c['working']=False
        c['state_info']= [{'当前状态':'重启……'}]

        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()
        ap_if.active(False)

        utime.sleep(3)
        machine.reset()


    def _http_get_wifi(self, c_socket, request_data):
        c = {}
        
        isconnected = sta_if.isconnected()

        if isconnected:
            ifconfig = sta_if.ifconfig()
            c['working']=True
            c['state_info']= [{'当前状态':'已连接'},
                              {'IP':ifconfig[0]},
                              {'网络掩码':ifconfig[1]},
                              {'网关':ifconfig[2]},
                              {'域名服务器':ifconfig[3]},
                              ]
        else:
            sta_if.active(False)
            c['working']=False
            c['state_info']= [{'当前状态':'未连接'},
                              ]
        
        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()

    def _http_get_mqtt(self, c_socket, request_data):
        c = {}

        if self._mqtt_conf.content:
            c = self._mqtt_conf.content

        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()
        
    def _http_get_ap(self, c_socket, request_data):
        c = {}

        if ap_if.active():
            c['working']=True
            c['state_info']= [{'当前状态':'已打开'},
                              {'名称':ap_if.config('essid')},
                              ]
        else:
            c['working']=False
            c['state_info']= [{'当前状态':'AP未打开'},
                              ]
        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()

    def _http_get_name(self, c_socket, request_data):
        c = {}

        c['name'] = self._device_name

        c_socket.sendall(HTTP_RES_HEAD)
        c_socket.sendall( json.dumps(c).encode())
        c_socket.close()



def start():
    from IrqLongpressReset import IrqLongpressReset
    from ubinascii import hexlify
    from Config import Config

    irq = IrqLongpressReset()
    device_name = 'pili_apa102_' + hexlify(machine.unique_id()).decode()
    main_module="pili_apa102"
    mqtt_conf = Config()

    webconfig = WebConfig(mqtt_conf=mqtt_conf, change_main=True, main_module=main_module, device_name=device_name)

    utime.sleep(10)
    webconfig.start()

    while True:
        client, cliAddr = webconfig._HttpServer.accept()
        if client:
            webconfig._HttpServer.handle_client(client, cliAddr)
