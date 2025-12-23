import logging
import time
from lib.controller import *

_data = None
_active_dsi = None
_active_dso = None
thresh_white_red_defaults = None
thresh_red_blue_defaults = None
thresh_white_red = None
thresh_red_blue = None
_ts_state_dsi = None
_ts_state_dso = None
is_dsi_last = None
is_dso_last = None
state_active_dsi_last = None
state_active_dso_last = None
state_active_dsi = None
state_active_dso = None
_dsi = None
_dso = None
def thread_update_dsi():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE, '-')
    _ts_state_dsi = 0
    is_dsi_last = None
    state_active_dsi_last = None
    while True:
        if (time.time() * 1000) - _ts_state_dsi > 10000 or is_dsi() != is_dsi_last or state_active_dsi != state_active_dsi_last:
            _ts_state_dsi = (time.time() * 1000)
            is_dsi_last = is_dsi()
            state_active_dsi_last = state_active_dsi
        time.sleep(0.5)

def thread_update_dso():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE, '-')
    _ts_state_dso = 0
    is_dso_last = None
    state_active_dso_last = None
    while True:
        if (time.time() * 1000) - _ts_state_dso > 10000 or is_dso() != is_dso_last or state_active_dso != state_active_dso_last:
            _ts_state_dso = (time.time() * 1000)
            is_dso_last = is_dso()
            state_active_dso_last = state_active_dso
        time.sleep(0.5)



def get_calib_data_DPS_defaults():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE, '-')
    return [thresh_white_red_defaults, thresh_red_blue_defaults]


def thread_DPS():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE, '-')
    thresh_white_red_defaults = 1150
    thresh_white_red = thresh_white_red_defaults
    thresh_red_blue_defaults = 1300
    thresh_red_blue = thresh_red_blue_defaults
    state_active_dsi = 0
    state_active_dso = 0
    _dsi = 0
    _dso = 0
    set_state_dsi(0)
    set_state_dso(0)


def get_calib_data_DPS():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE, '-')
    return [thresh_white_red, thresh_red_blue]


def set_calib_data_DPS(_data):
    global _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE, _data)
    thresh_white_red = _data[0]
    thresh_red_blue = _data[1]


def set_state_dsi(_active_dsi):
    global _data, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE0, '-')
    if state_active_dsi != _active_dsi:
        _ts_state_dsi = 0
        state_active_dsi = _active_dsi
    if _dsi != is_dsi():
        _ts_state_dsi = 0
        _dsi = is_dsi()


def set_state_dso(_active_dso):
    global _data, _active_dsi, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE0, '-')
    if state_active_dso != _active_dso:
        _ts_state_dso = 0
        state_active_dso = _active_dso
    if _dso != is_dso():
        _ts_state_dso = 0
        _dso = is_dso()


def is_dsi():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE0, '-')
    return TXT_M_C4_photo_transistor.is_dark()


def is_dso():
    global _data, _active_dsi, _active_dso, thresh_white_red_defaults, thresh_red_blue_defaults, thresh_white_red, thresh_red_blue, _ts_state_dsi, _ts_state_dso, is_dsi_last, is_dso_last, state_active_dsi_last, state_active_dso_last, state_active_dsi, state_active_dso, _dsi, _dso
    logging.log(logging.TRACE0, '-')
    return TXT_M_C4_photo_transistor.is_dark()


