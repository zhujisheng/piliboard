from machine import Timer

def callback_a(tim):
    print("callback a called")

def callback_b(tim):
    print("callback b called")


tim1 = Timer(-1)
tim2 = Timer(-1)
tim1.init(period=5000, mode=Timer.ONE_SHOT, callback=callback_a)
tim2.init(period=3000, mode=Timer.PERIODIC, callback=callback_b)
