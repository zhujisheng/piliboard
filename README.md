# piliboard

## 写入固件
`esptool.py --port COMx erase_flash`

`esptool.py --port COMx --baud 115200 write_flash 0 firmware-on-pili.bin`

注：`COMx`为连接的串口，在linux下形式为`/dev/ttyUSB0`

## 固件的一些基本信息
- 默认开放AP，AP的名称为`MicroPython-xxxxxx`，密码为`micropythoN`（注意最后一个`N`为大写）
- 默认启动WebREPL，连接密码为`piliboard`
- 集成了MiniWebSrv（一个小型的Web服务器）
- 集成了Config（json格式配置文件读写、配置内容）
- 集成了StateMQTTClient（一个基于umqtt.simple的mqtt库）
