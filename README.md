# piliboard


## 写入固件
1.将开发板上模式开关置于“write flash”状态
2.按开发板上reset按钮重启piliboard
3.在pc上运行命令：`esptool.py --port COMx erase_flash`，擦除flash中内容
4.按开发板上reset按钮重启piliboard
5.在pc上运行命令：`esptool.py --port COMx --baud 115200 write_flash 0 firmware-on-pili.bin`，写入固件
6.将开发板上模式开关置于“run”状态
7.按开发板上reset按钮重启piliboard

注：
- 命令`COMx`为连接的串口，在Windows下可以使用`mode`命令查看，在linux下形式为`/dev/ttyUSB0`
- esptool工具通过`pip3 install esptool`命令安装

## 固件的一些基本信息
- 网络
	- 初始AP网卡为打开，AP的名称为`MicroPython-xxxxxx`，密码为`micropythoN`（注意最后一个`N`为大写）
	- 初始工作网卡为关闭
- WebREPL
	- 初始启动WebREPL
    - 连接密码为`piliboard`
    - 可通过命令`import webrepl_setup`进行设置（关闭/开启、密码）
- 固件内集成以下micropython库
	- `Config.py`（json格式配置文件读写、配置内容）
	- `ControlApa102.py`(apa102灯带控制程序)
	- `IrqLongpressReset.py`(通过按钮调用中断程序)
	- `MiniWebSrv.py`（一个小型的Web服务器）
	- `SimpleDevice.py`(简单的开关与pwm调值设备)
	- `StateMQTTClient.py`（一个基于`umqtt.simple`的mqtt库）
