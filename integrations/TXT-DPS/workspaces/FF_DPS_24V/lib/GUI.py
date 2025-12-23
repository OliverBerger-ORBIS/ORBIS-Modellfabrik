import logging
from lib.display import *
from lib.Factory import *
from lib.Sound import *

_tr0 = None
_tr = None
_dg = None
res = None


def initlog_GUI(_tr0, _tr, _dg):
    global res
    logging.TRACE0_GUI = _tr0
    logging.addLevelName(logging.TRACE0_GUI , 'TRACE0_GUI')
    logging.TRACE_GUI = _tr
    logging.addLevelName(logging.TRACE_GUI , 'TRACE_GUI')
    logging.DEBUG_GUI = _dg
    logging.addLevelName(logging.DEBUG_GUI, 'DEBUG_GUI')


def on_txt_button_nfc_read_clicked(event):
    global _tr0, _tr, _dg, res
    logging.log(logging.TRACE_GUI, '-')
    res = reqVGR_Nfc('read')
    beep()


def on_txt_button_nfc_delete_clicked(event):
    global _tr0, _tr, _dg, res
    logging.log(logging.TRACE_GUI, '-')
    res = reqVGR_Nfc('delete')
    beep()


display.button_clicked("txt_button_nfc_read", on_txt_button_nfc_read_clicked)
display.button_clicked("txt_button_nfc_delete", on_txt_button_nfc_delete_clicked)


