import json
from lib.calibration_data import *
from lib.vda5050 import *

name = None
value = None
listToExtend = None
listB = None
INSTANT_ACTION_START = None
temp = None
INSTANT_ACTION_STOP = None
INSTANT_ACTION_SELECT = None
INSTANT_ACTION_RESET = None
INSTANT_ACTION_SET = None
INSTANT_ACTION_STORE = None
INSTANT_ACTION_TEST = None
status_values = None
_combined_status_values = None


def calibration_mode_init():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    INSTANT_ACTION_START = 'startCalibration'
    INSTANT_ACTION_STOP = 'stopCalibration'
    INSTANT_ACTION_SELECT = 'selectCalibrationPosition'
    INSTANT_ACTION_RESET = 'resetCalibration'
    INSTANT_ACTION_SET = 'setCalibrationValues'
    INSTANT_ACTION_STORE = 'storeCalibrationValues'
    INSTANT_ACTION_TEST = 'testCalibrationPosition'


def calibration_mode_enable():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    vda_set_teachin(True)
    status_values = json.loads('{}')
    calibration_mode_update_status()


def calibration_mode_disable():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    vda_set_teachin(False)
    vda_delete_information('calibration_data')
    vda_delete_information('calibration_status')
    status_values = json.loads('{}')


def calibration_mode_update_status():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    temp = calibration_get_flattened()
    _combined_status_values = []
    for key,value in temp.items():
        _combined_status_values.append({
            "referenceKey": key,
            "referenceValue": value
            })
    vda_set_information('calibration_data', 'DEBUG', _combined_status_values)
    _combined_status_values = []
    for key,value in status_values.items():
        _combined_status_values.append({
            "referenceKey": key,
            "referenceValue": value
            })
    vda_set_information('calibration_status', 'DEBUG', _combined_status_values)


def calibration_mode_set_status_value(name, value):
    global listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    status_values[name] = value


def calibration_mode_get_instant_actions():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return [INSTANT_ACTION_START, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST]


def calibration_mode_get_instant_action_start():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_START


def calibration_mode_get_instant_action_stop():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_STOP


def calibration_mode_get_instant_action_select():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_SELECT


def calibration_mode_get_instant_action_reset():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_RESET


def calibration_mode_get_instant_action_set():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_SET


def calibration_mode_get_instant_action_store():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_STORE


def calibration_mode_get_instant_action_test():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return INSTANT_ACTION_TEST


def calibration_mode_extend_list(listToExtend, listB):
    global name, value, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    # this function modifies the list given in the first parameter

    listToExtend.extend(listB)
    return listToExtend


def calibration_mode_get_key_available_positions():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return 'POSITIONS.AVAILABLE'


def calibration_mode_get_key_current_position():
    global name, value, listToExtend, listB, INSTANT_ACTION_START, temp, INSTANT_ACTION_STOP, INSTANT_ACTION_SELECT, INSTANT_ACTION_RESET, INSTANT_ACTION_SET, INSTANT_ACTION_STORE, INSTANT_ACTION_TEST, status_values, _combined_status_values
    return 'POSITIONS.CURRENT'
