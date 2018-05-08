from machine import Pin
from machine import Timer
from apa102 import APA102
import urandom

class ControlApa102:
    def __init__(self, led_num, clock_pin, data_pin, transition=100):
        self._led_num = led_num
        clock = Pin( clock_pin, Pin.OUT )
        data = Pin( data_pin, Pin.OUT )

        self._apa = APA102( clock, data, self._led_num )
        self._timer = Timer(-1)

        self._state = "OFF"
        self._transition = transition
        self._color = (255,255,255)
        self._brightness = 0
        self._effect = "plain"

        self._effect_list = [ "plain",
                              "run",
                              "run_fast",
                              "move",
                              "worm"
                              ]

        self._point = 0
        self._cell_state = self._color + (round(self._brightness/255*31),)

        self._shutdown()

    def _shutdown(self):
        for i in range(0,self._led_num):
            self._apa[i] = (0,0,0,0)
        self._apa.write()

    def _plainshow(self):
        self._cell_state = self._color + (round(self._brightness/255*31),)
        for i in range(0,self._led_num):
            self._apa[i] = self._cell_state
        self._apa.write()

    def _show(self):
        for i in range(0,self._led_num):
            self._apa[i] = (0,0,0,0)
        self._cell_state = self._color + (round(self._brightness/255*31),)

        if self._effect == 'run':
            self._apa[self._point]=self._cell_state
            self._apa[(self._point+1)%self._led_num]=self._cell_state
            self._apa[(self._point+2)%self._led_num]=self._cell_state
            self._apa[(self._point+3)%self._led_num]=self._cell_state
            cb_fun = self._move_show
        elif self._effect == 'run_fast':
            for i in range(0,90):
                self._apa[(self._point+i)%self._led_num]=self._cell_state
            cb_fun = self._run_fast_show
        elif self._effect == 'move':
            self._apa[self._point]=(255,0,0,round(self._brightness/255*31))
            self._apa[(self._point+1)%self._led_num]=(0,255,0,round(self._brightness/255*31))
            self._apa[(self._point+2)%self._led_num]=(0,0,255,round(self._brightness/255*31))
            self._apa[(self._point+3)%self._led_num]=(255,255,255,round(self._brightness/255*31))
            cb_fun = self._move_show
        elif self._effect == 'worm':
            self._worm_phrase=0
            cb_fun = self._worm_show

        self._timer.init(period=self._transition, mode=Timer.PERIODIC, callback=cb_fun)


    def _move2(self, i_len, i_mpt):
        "后端到前段"
        for i in range(0, i_mpt):
            self._apa[(self._point+i+i_len)%self._led_num] = self._apa[(self._point+i)%self._led_num]
            self._apa[(self._point+i)%self._led_num] = (0,0,0,0)
        self._apa.write()
        self._point = (self._point + i_mpt)%self._led_num


    def _move_show(self, tim):
        self._move2(4,1)

    def _run_fast_show(self, tim):
        self._move2(90,15)

    def _worm_show(self, tim):

        c0 = (128,255,0,round(self._brightness/255*31))
        c_black = (0,0,0,0)
        c_head = (255,255,255,round(self._brightness/255*31))
        c_tail = (0,255,0,round(self._brightness/255*31/2))
        c_dark = (0,255,0,round(self._brightness/255*31))

        if self._worm_phrase == 0:
            self._apa[self._point] = c_tail
            self._apa[(self._point + 29)%self._led_num] = c_head
            for i in range(1,29):
                self._apa[(self._point + i)%self._led_num] = c0
        elif self._worm_phrase == 4:
            self._apa[(self._point + 4)%self._led_num] = c_tail
            self._apa[(self._point +0)%self._led_num] = c_black
            self._apa[(self._point +1)%self._led_num] = c_black
            self._apa[(self._point +2)%self._led_num] = c_black
            self._apa[(self._point +3)%self._led_num] = c_black
        elif self._worm_phrase == 5:
            self._apa[(self._point + 8)%self._led_num] = c_tail
            self._apa[(self._point +4)%self._led_num] = c_black
            self._apa[(self._point +5)%self._led_num] = c_black
            self._apa[(self._point +6)%self._led_num] = c_black
            self._apa[(self._point +7)%self._led_num] = c_black
        elif self._worm_phrase == 6:
            self._apa[(self._point + 12)%self._led_num] = c_tail
            self._apa[(self._point +8)%self._led_num] = c_black
            self._apa[(self._point +9)%self._led_num] = c_black
            self._apa[(self._point +10)%self._led_num] = c_black
            self._apa[(self._point +11)%self._led_num] = c_black
            for i in range(12,29):
                self._apa[(self._point + i)%self._led_num] = c_dark
        elif self._worm_phrase == 10:
            self._apa[(self._point + 33)%self._led_num] = c_head
            self._apa[(self._point +29)%self._led_num] = c0
            self._apa[(self._point +30)%self._led_num] = c0
            self._apa[(self._point +31)%self._led_num] = c_black
            self._apa[(self._point +32)%self._led_num] = c_black
        elif self._worm_phrase == 11:
            self._apa[(self._point + 37)%self._led_num] = c_head
            self._apa[(self._point +33)%self._led_num] = c0
            self._apa[(self._point +34)%self._led_num] = c0
            self._apa[(self._point +35)%self._led_num] = c_black
            self._apa[(self._point +36)%self._led_num] = c_black


        self._apa.write()
        if self._worm_phrase == 11:
            self._point = (self._point + 12)%self._led_num
        self._worm_phrase = (self._worm_phrase+1)%12


    def control(self, command ):

        if command.get('state') == "OFF":
            self._state = "OFF"
        elif command.get('state') == "ON":
            self._state = "ON"
        if command.get('transition'):
            self._transition = command.get('transition')
        if command.get('color'):
            self._color = (command["color"]["r"],
                           command["color"]["g"],
                           command["color"]["b"],
                           )
        if command.get('brightness'):
            self._brightness = command["brightness"]

        if command.get('effect') in self._effect_list:
            self._effect = command['effect']

        self._timer.deinit()

        if self._state == 'OFF':
            self._shutdown()
        elif self._effect == 'plain':
            self._plainshow()
        else:
            self._show()

    @property
    def state(self):
        c_state = { 'state': self._state,
                    'brightness': self._brightness,
                    'effect': self._effect,
                    'transition': self._transition,
                    'color': { "r":self._color[0],
                               "g":self._color[1],
                               "b":self._color[2],
                               }
                    }
        return c_state

    @property
    def effect_list(self):
        return self._effect_list

