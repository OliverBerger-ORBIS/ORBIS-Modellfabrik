import time
from lib.vda5050 import *

last_voltage = None


def battery_monitor_update_thread():
    global last_voltage
    # publish new state when 3 minutes without a state update have passed and the battery charge has changed
    while True:
        if (vda_last_state_update_ts()) and time.time() - (vda_last_state_update_ts()) > 180:
            vda_publish_status()
        time.sleep(10)
