import time
import machine
import onewire, ds18x20

# 设备数据线连接在GPIO2
dat = machine.Pin(2)

# 基于1-wire创建ds18x20温度传感器
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# 寻找设备
roms = ds.scan()
print('找到设备：', roms)

# 循环10次，每次打印所有设备测量的温度
for i in range(10):
    print('温度：', end=' ')
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(ds.read_temp(rom), end=' ')
    print()
