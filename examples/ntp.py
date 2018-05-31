import ntptime
import time
ntptime.settime()

t = time.localtime()
print("当前国际标准时间：%d年%d月%d日 %d:%d:%d"%
      (t[0],t[1],t[2],t[3],t[4],t[5]))

print("sleep 8 秒钟")
time.sleep(8)

t = time.localtime()
print("当前国际标准时间：%d年%d月%d日 %d:%d:%d"%
      (t[0],t[1],t[2],t[3],t[4],t[5]))
