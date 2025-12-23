import logging
import time
from lib.VGR import *

_mode = None
bits = None
lights_mode = None
lights_mode_last = None


def set_lights_mode(_mode):
    global bits, lights_mode, lights_mode_last
    logging.log(logging.TRACE, _mode)
    lights_mode = _mode


def thread_lights():
    global _mode, bits, lights_mode, lights_mode_last
    logging.log(logging.TRACE, '-')
    lights_mode = 3
    lights_mode_last = 0
    while True:
        if (get_state_code_VGR()) == 4:
            lights_mode = 4
        elif (get_state_code_VGR()) == 2:
            lights_mode = 2
        elif (get_state_code_VGR()) == 1:
            lights_mode = 1
        else:
            lights_mode = 3
        if lights_mode == 7:
            set_LEDs(7)
            time.sleep(0.2)
            set_LEDs(0)
        else:
            if lights_mode != lights_mode_last:
                logging.log(logging.DEBUG, lights_mode)
                set_LEDs(lights_mode)
                lights_mode_last = lights_mode
        time.sleep(0.2)


def set_LEDs(bits):
    global _mode, lights_mode, lights_mode_last
    logging.log(logging.TRACE, bits)
    b1 = bits & (1<<2)
    b2 = bits & (1<<1)
    b3 = bits & (1<<0)
    # TODO remove all code calling this


