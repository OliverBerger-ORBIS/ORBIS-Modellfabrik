import json
import math
import os
import subprocess
import threading
import time
from fischertechnik.controller.Motor import Motor
from lib.charger import *
from lib.controller import *
from lib.display import *

new_volt_upper_limit = None
battery_config_file = None
volt = None
volt_percentage_value = None
upper_limit = None
lower_limit = None
battery_config = None


def battery_start_thread():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    battery_config_file = open(os.path.join(os.path.dirname(__file__), '../data/config.json'), 'r', encoding='utf8')
    battery_config = (json.loads(battery_config_file.read()))['battery']
    volt = 0
    lower_limit = battery_config['minVolt'] / 1000
    upper_limit = battery_config['maxVolt'] / 1000
    volt_percentage_value = 0
    threading.Thread(target=update_battery_gauge, daemon=True).start()


def return_volt_voltage():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    return volt


def return_volt_percentage_value():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    volt_percentage_value = int(volt_percentage_value)
    return volt_percentage_value


def return_volt_upper_limit():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    return upper_limit


def update_battery_gauge():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    while True:
        time.sleep(2)
        # Running motors drag down the battery, only read the state when idle
        while battery_is_driving():
            time.sleep(1)
        volt = round((charger_get_battery_voltage()) / 1000, 1)
        if not volt:
            volt = battery_read_local()
        if volt < 0:
            continue
        # Calculation in percent
        volt_percentage_value = round(((volt - lower_limit) / (upper_limit - lower_limit)) *100,1)
        volt = round(volt, 1)
        display.set_attr("txt_Volt_label.text", str(volt))
        display.set_attr("txt_Volt_Header.text", str('V {}'.format('~CHR' if (charger_is_charging()) else '◼▊▊▊')))
        display.set_attr("txt_gauge.value", str(volt_percentage_value))


def return_volt_lower_limit():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    return lower_limit


def update_volt_upper_limit(new_volt_upper_limit):
    global battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    upper_limit = new_volt_upper_limit


def battery_read_local():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    # use usr/bin/battery.sh to get the current Battery Voltage
    output_bytes = subprocess.check_output('/usr/bin/battery.sh')

    # should return something like this
    # 8.9064
    # It's OK

    # convert and parse according to volt specification
    output_str = output_bytes.decode("utf-8")
    output_lines = output_str.split("\n")
    volt_str = output_lines[0].split()[0]
    return float(volt_str)


def battery_is_driving():
    global new_volt_upper_limit, battery_config_file, volt, volt_percentage_value, upper_limit, lower_limit, battery_config
    return (TXT_M_M1_encodermotor.is_running()) or (TXT_M_M2_encodermotor.is_running()) or (TXT_M_M3_encodermotor.is_running()) or (TXT_M_M4_encodermotor.is_running())


