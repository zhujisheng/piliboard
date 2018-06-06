import machine

pin_no = 2
duty_angle0 = 40
duty_angle180 = 115

servo = machine.PWM(machine.Pin(pin_no), freq=50)

def turn(angle=90):
    assert angle>=0 and angle <=180
    d = duty_angle0 + angle*(duty_angle180-duty_angle0)/180
    servo.duty(int(d))

