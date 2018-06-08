import uasyncio as asyncio
import machine

async def counter(ms=1000):
    count = 0
    while True:
        count += 1
        print("counter：", count)
        await asyncio.sleep_ms(ms)

async def flash(ms=1000):
    n=0
    print("flash:初始化……")
    p5 = machine.Pin(5, machine.Pin.OUT)

    print("flash:开始循环运行……")
    while True:
        n = n + 1
        print("flash:第%d次"%n)
        print("flash:明……")
        p5.value(1)
        await asyncio.sleep_ms(ms)

        print("flash:灭……")
        p5.value(0)
        await asyncio.sleep_ms(ms)

loop = asyncio.get_event_loop()
loop.create_task(counter(1500))
loop.create_task(flash(2000))
loop.run_forever()

print("这句话永远不会被执行")
