import os
from fischertechnik.controller.Motor import Motor
from lib.controller import *

mm = None
speed = None
degrees = None
range2 = None
util_controller_id = None
us_left = None
us_right = None


def util_get_controller_id():
    global mm, speed, degrees, range2, util_controller_id, us_left, us_right
    if not util_controller_id:
        with open("/etc/deviceid") as file:
            print("OK")
            util_controller_id = file.readline().strip()
    return util_controller_id


def util_stop_driving():
    global mm, speed, degrees, range2, util_controller_id, us_left, us_right
    TXT_M_M1_encodermotor.stop_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


# calculate required encoder pulses to move a distance in millimeter.
# Factor contains pulses per motor revolution, internal gearbox ratio, external gearing, wheel diameter.
# Values determined experimentally
def util_mm_to_enc_pulses(mm, speed):
    global degrees, range2, util_controller_id, us_left, us_right
    return 0.625 * mm


# calculate required encoder pulses to move a distance in millimeter.
# Factor contains pulses per motor revolution, internal gearbox ratio, external gearing, wheel diameter.
# Values determined experimentally
def util_mm_to_enc_pulses_sideways(mm, speed):
    global degrees, range2, util_controller_id, us_left, us_right
    return 0.672 * mm


# calculate required encoder pulses to rotate an angle in degrees.
# Factor contains pulses per motor revolution, internal gearbox ratio, external gearing, wheel diameter.
# Values determined experimentaller_
def util_deg_to_enc_pulses(degrees):
    global mm, speed, range2, util_controller_id, us_left, us_right
    return 1.5333333333 * degrees


def util_module_in_range(range2):
    global mm, speed, degrees, util_controller_id, us_left, us_right
    us_left = TXT_M_I7_ultrasonic_distance_meter.get_distance()
    us_right = TXT_M_I8_ultrasonic_distance_meter.get_distance()
    return us_left < range2 and us_right < range2


