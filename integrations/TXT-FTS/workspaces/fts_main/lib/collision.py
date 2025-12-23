import time
from lib.controller import *
from lib.display import *
from lib.vda5050 import *

distance = None
collisionsFound = None


def collision_check(distance):
    global collisionsFound
    if collision_in_range(distance):
        display.set_attr("label_status.text", str('COLLISION WARNING'))
        time.sleep(1)
        vda_set_warning('COLLISION')
        vda_publish_status()
        while TXT_M_I7_ultrasonic_distance_meter.get_distance() <= distance and TXT_M_I8_ultrasonic_distance_meter.get_distance() <= distance:
            time.sleep(0.1)
        vda_remove_warning('COLLISION')
        vda_publish_status()
        time.sleep(1)


def collision_in_range(distance):
    global collisionsFound
    print('collision_in_range?')
    collisionsFound = 0
    for count in range(10):
        if TXT_M_I7_ultrasonic_distance_meter.get_distance() <= distance:
            collisionsFound = (collisionsFound if isinstance(collisionsFound, (int, float)) else 0) + 1
        if TXT_M_I8_ultrasonic_distance_meter.get_distance() <= distance:
            collisionsFound = (collisionsFound if isinstance(collisionsFound, (int, float)) else 0) + 1
        time.sleep(0.1)
    return collisionsFound >= 8
