import machine

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

# RTC.ALARM0 10 秒后触发
rtc.alarm(rtc.ALARM0, 10000)

# 进入深度睡眠模式
machine.deepsleep()
