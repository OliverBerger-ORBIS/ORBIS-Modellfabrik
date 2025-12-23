import atexit
import logging
import smbus
import time
from lib.display import *

charger_bus = None
CHARGE_STOP_COUNTER = None
stop_charging = None
voltage_bat = None
V_T0 = None
charging_requested = None
voltage_ext = None
V_T1 = None
CHARGER_ADDRESS = None
REG_READ_V_BAT = None
REG_READ_V_EXT = None
REG_WRITE_MODE = None
MODE_BATTERY = None
MODE_CHARGE = None


def charger_init():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    # Prevent Robo Pro from deleting the variable
    charger_bus = charger_bus
    V_T0 = 0
    V_T1 = 0
    CHARGE_STOP_COUNTER = 0
    CHARGER_ADDRESS = 38
    REG_READ_V_BAT = 0
    REG_READ_V_EXT = 2
    REG_WRITE_MODE = 0
    MODE_BATTERY = 1
    MODE_CHARGE = 0
    # charger is connected to SMBus 3
    # address for charger is 0x26
    # register 0 READ is current battery voltage in mV
    # register 2 READ is current external/charger voltage in mV
    # register 0 WRITE enables / disables charging.
    #    value 0x0001 - stop charging, switch TXT ouput to battery
    #    value 0x0000 - start charging as soon as external power available, then switch TXT to external power supply

    charger_bus = smbus.SMBus(3)
    atexit.register(_charger_stop_on_exit)


def charger_get_battery_voltage():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    if not charger_bus:
        return 0
    return charger_bus.read_word_data(CHARGER_ADDRESS, REG_READ_V_BAT)


def charger_get_charger_voltage():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    if not charger_bus:
        return 0
    return charger_bus.read_word_data(CHARGER_ADDRESS, REG_READ_V_EXT)


def charger_is_available():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    return charger_get_charger_voltage() > 5000


def charger_connect():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    CHARGE_STOP_COUNTER = 0
    V_T0 = 0
    charger_bus.write_word_data(CHARGER_ADDRESS, REG_WRITE_MODE, MODE_CHARGE)   # Schreibe auf Register 0 den Wert "0" = Laden ist möglich, sobald externe Spannungsversorgung gesichert
    display.set_attr("txt_status_loading.active", str(True).lower())
    charging_requested = True


def charger_disconnect():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    if charging_requested:
        charger_bus.write_word_data(CHARGER_ADDRESS, REG_WRITE_MODE, MODE_BATTERY)      # Schreibe auf Register 0 den Wert "1" = Laden beenden, TXT auf Akku schalten
        time.sleep(1)
        display.set_attr("txt_status_loading.active", str(False).lower())
        charging_requested = False


def charger_is_charging():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    return charging_requested and charger_is_available()


def charger_is_done():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    if not charger_is_charging():
        return True
    voltage_ext = charger_get_charger_voltage()
    voltage_bat = charger_get_battery_voltage()
    # define battery as full when the voltage
    #  has not increased  for 5 consecutive tests
    # (function is called once every minute during charging)
    logging.debug("CHARGE: Current battery: %d mV, Previous battery: %d mV, Plateau: %d/5,  external: %d mV", voltage_bat, V_T0, CHARGE_STOP_COUNTER, voltage_ext)
    V_T1 = voltage_bat
    if V_T0 >= V_T1:
        # if old charge is equal or greater,
        # then it is not charging anymore, start timeout
        logging.debug("CHARGE: Plateau now: %d/5", CHARGE_STOP_COUNTER)
        CHARGE_STOP_COUNTER = (CHARGE_STOP_COUNTER if isinstance(CHARGE_STOP_COUNTER, (int, float)) else 0) + 1
    elif V_T0 < V_T1:
        # if new charge is greater, the charge continues
        # reset timer with rising voltage.
        logging.debug("CHARGE: Plateau reset: 0/5")
        CHARGE_STOP_COUNTER = 0
    stop_charging = CHARGE_STOP_COUNTER >= 5
    if stop_charging == False:
        logging.debug("CHARGE: continue")
        if V_T0 <= V_T1 or V_T0 - V_T1 < 50:
            # only save new voltage if it is larger
            # or differs more than 50mV
            # this prevents infinite charge when the value is unstable
            # but is not rising anymore.
            V_T0 = V_T1
    elif stop_charging != False:
        V_T1 = 0
        V_T0 = 0
        CHARGE_STOP_COUNTER = 0
        logging.debug("CHARGE: stop")
    return stop_charging


def _charger_stop_on_exit():
    global charger_bus, CHARGE_STOP_COUNTER, stop_charging, voltage_bat, V_T0, charging_requested, voltage_ext, V_T1, CHARGER_ADDRESS, REG_READ_V_BAT, REG_READ_V_EXT, REG_WRITE_MODE, MODE_BATTERY, MODE_CHARGE
    charger_disconnect()


