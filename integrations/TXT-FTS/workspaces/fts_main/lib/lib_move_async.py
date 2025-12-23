import math
import time
from fischertechnik.controller.Motor import Motor
from lib.controller import *
from lib.util import *

v = None
dist = None
rot = None


def move_async_wait():
    global v, dist, rot
    while True:
        if (not TXT_M_M1_encodermotor.is_running()):
            break
        time.sleep(0.010)


def move_asnyc_done():
    global v, dist, rot
    return not TXT_M_M1_encodermotor.is_running()


def move_async_distance_fwd(v, dist):
    global rot
    TXT_M_M1_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M2_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M3_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M4_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M1_encodermotor.set_distance(int(util_mm_to_enc_pulses(dist, v)), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def move_async_distance_backwd(v, dist):
    global rot
    TXT_M_M1_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M2_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M3_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M4_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M1_encodermotor.set_distance(int(util_mm_to_enc_pulses(dist, v)), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def move_async_distance_left(v, dist):
    global rot
    TXT_M_M1_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M2_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M3_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M4_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M1_encodermotor.set_distance(int((util_mm_to_enc_pulses_sideways(dist, v)) * math.sqrt(2)), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def move_async_distance_right(v, dist):
    global rot
    TXT_M_M1_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M2_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M3_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M4_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M1_encodermotor.set_distance(int((util_mm_to_enc_pulses_sideways(dist, v)) * math.sqrt(2)), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def move_async_rotate_left(v, rot):
    global dist
    TXT_M_M1_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M2_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M3_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M4_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M1_encodermotor.set_distance(int(util_deg_to_enc_pulses(rot)), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def move_async_rotate_right(v, rot):
    global dist
    TXT_M_M1_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M2_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M3_encodermotor.set_speed(int(v), Motor.CCW)
    TXT_M_M4_encodermotor.set_speed(int(v), Motor.CW)
    TXT_M_M1_encodermotor.set_distance(int(util_deg_to_enc_pulses(rot)), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


