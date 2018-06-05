def do_connect(essid, password):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('连接WIFI...')
        wlan.connect(essid, password)
        while not wlan.isconnected():
            pass
    print('网络配置信息：', wlan.ifconfig())
