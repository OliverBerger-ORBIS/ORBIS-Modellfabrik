import logging
import time
from lib.calibration_commands import *
from lib.calibration_data import *
from lib.calibration_mode import *
from lib.controller import *
from lib.display import *
from lib.DPS import *
from lib.Factory import *
from lib.Factory_Variables import *
from lib.Nfc import *
from lib.reset_utils import *
from lib.robotic_arm import *
from lib.Sound import *
from lib.vda5050 import *

_tr0 = None
_tr = None
_dg = None
taguid = None
num = None
history_ts = None
m = None
k = None
w_uid = None
w_color = None
state = None
action = None
status = None
success = None
result = None
output_instant_action = None
_code = None
_active = None
_target = None
valid = None
mi = None
res = None
mask = None
wp_uid = None
_unused = None
ACTION_INPUT_RGB = None
uid = None
last_color = None
STATE_FAILED = None
state_code = None
state_active = None
STATE_IDLE = None
ResetException = None
ACTION_RGB_NFC = None
current_status = None
ACTION_NFC_DROP = None
ACTION_PICK_NFC = None
STATE_RESET = None
_workpiece = None
ts_readuid = None
_ts_state = None
count_write = None
workpiece_state_history = None
ACTION_DROP = None
ACTION_NFC_NIO = None
STATE_INPUT_RUNNING = None
STATE_RGB_IDLE = None
STATE_RGB_NFC_RUNNING = None
STATE_NFC_IDLE = None
STATE_NIO_RUNNING = None
STATE_OUT_RUNNING = None
STATE_DROP_RUNNING = None
STATE_PICK_NFC_RUNNING = None
STATE_PROCESSING_OUTPUT = None
list_nfctag_history = None
index = None
color = None
actionCommand = None
ACTION_NFC_OUT = None
STATE_RGB_NIO_RUNNING = None
state_target = None
map_nfctag_history = None
i = None
ts_dsi = None
STATE_PROCESSING_UNLOAD = None
_state = None
valid_processed = None
delivery_action = None
bit = None
_type = None
_mask = None
_vts = None
wp = None
data = None
req = None
ACTION_PROCESS_OUTPUT = None
STATE_PROCESSING_INPUT = None
STATE_PROCESSING_INPUT_IDLE = None
def delivery_write_history(action):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    wp_uid = nfc_read_uid()
    logging.log(logging.TRACE_VGR, wp_uid)
    _workpiece = None
    workpiece_state_history = None
    color = None
    uid = None
    valid_processed = False
    valid = False
    if action.get("command") == "PICK":
        _workpiece = action.get("metadata").get("workpiece")
        if _workpiece != None:
            workpiece_state_history = _workpiece.get("history")
            uid = _workpiece.get("workpieceId")
            color = _workpiece.get("type")
            valid_processed = _workpiece.get("state") == "PROCESSED"
    else:
        print("-------------------Wrong command--------------------------")
    print('------------------------------------------------------------------- validation ---------------')
    valid = wp_uid == uid
    res = False
    if valid and valid_processed:
        print('------------------------------------------------------------------- Delete history ---------------')
        res = nfc_delete()
        if res == False:
            print('------------------------------------------------------------------- Delivery delete history failed ---------------')
            vda_set_warning('NFC_workpieceId_mismatch')
        map_nfctag_history = None
        list_nfctag_history = [None] * 8
        print('------------------------------------------------------------------- start writing ---------------')
        for processing_point in workpiece_state_history:
            print(processing_point)
            ts = int(processing_point["ts"])
            _code = processing_point["code"]
            if isinstance(_code, int) and _code % 100 == 0 and _code >= 100 and _code <= 800:
                set_nfctag_item(uid, int(_code/100),ts)

        # nfc history code:
        # 100 = "Anlieferung Rohware"
        # 200 = "Qualitätskontrolle"
        # 300 = "Einlagerung"
        # 400 = "Auslagerung"
        # 500 = "Bearbeitung Brennofen"
        # 600 = "Bearbeitung Fräse"
        # 700 = "Sortierung"
        # 800 = "Versand Ware"
        set_nfctag_item(uid, 8, (time.time() * 1000))
        # state "PROCESSED" is proofed
        res = nfc_write_history(uid, color, 1)
    else:
        print('------------- Not Valid ---------------')
        if _workpiece != None:
            if valid != True:
                print('------------------------------------------------------------------- WorkpieceId doesnt match with Workpiece ---------------')
                vda_set_warning('NFC_workpieceId_mismatch')
            if valid_processed != True:
                print('------------------------------------------------------------------- Not Processed ---------------')
                vda_set_warning('workpiece_state_not_PROCESSED')
            if workpiece_state_history == None:
                print('------------------------------------------------------------------- No Workpiece History ---------------')
                vda_set_warning('workpiece_no_history')
        else:
            vda_set_warning('no_workpiece_in_metadata')
    return res

def nfc_input_history_handle():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    print('------------------------------------------------------------------- Delete history ---------------')
    res = False
    res = nfc_delete()
    if res == True:
        print('------------------------------------------------------------------- Write new history ---------------')
        map_nfctag_history = None
        list_nfctag_history = [None] * 8
        set_nfctag_item(uid, 1, ts_dsi)
        res = nfc_write_history(uid, last_color, 0)
        if res:
            beep_blocked()
            logging.log(logging.DEBUG_VGR, 'nfc tag valid')
        else:
            valid = False
            #move: NiO
    else:
        print('------------------------------------------------------------------- Delete Failed ---------------')
        valid = False
        vda_set_warning('input_nfc_delete_failed')
        #move: NiO

def delivery_verify_nfctag(action):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    wp_uid = nfc_read_uid()
    logging.log(logging.TRACE_VGR, wp_uid)
    _workpiece = None
    workpiece_state_history = None
    color = None
    uid = None
    valid_processed = False
    valid = False
    if action.get("command") == "PICK":
        _workpiece = action.get("metadata").get("workpiece")
        if _workpiece != None:
            workpiece_state_history = _workpiece.get("history")
            uid = _workpiece.get("workpieceId")
            color = _workpiece.get("type")
            valid_processed = _workpiece.get("state") == "PROCESSED"
    else:
        print("-------------------Wrong command--------------------------")
    print('------------------------------------------------------------------- validation ---------------')
    valid = wp_uid == uid
    if valid and valid_processed:
        return True
    print('------------- Not Valid ---------------')
    if _workpiece != None:
        if valid != True:
            print('------------------------------------------------------------------- WorkpieceId doesnt match with Workpiece ---------------')
            vda_set_warning('NFC_workpieceId_mismatch')
        if valid_processed != True:
            print('------------------------------------------------------------------- Not Processed ---------------')
            vda_set_warning('workpiece_state_not_PROCESSED')
        if workpiece_state_history == None:
            print('------------------------------------------------------------------- No Workpiece History ---------------')
            vda_set_warning('workpiece_no_history')
    else:
        vda_set_warning('no_workpiece_in_metadata')
    return False

def handle_NFC():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    uid = nfc_read_uid()
    valid = uid != None and uid != ''
    if valid:
        nfc_input_history_handle()
    else:
        last_color = None
        display.set_attr("txt_label_message2.text", str('uid is None'))
        print('---------------------------------------  No NFC Tag discovered -------------------')



def parkVGR():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    moveRefPark()


def initlog_VGR(_tr0, _tr, _dg):
    global taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.TRACE0_VGR= _tr0
    logging.addLevelName(logging.TRACE0_VGR , 'TRACE0_VGR')
    logging.TRACE_VGR = _tr
    logging.addLevelName(logging.TRACE_VGR , 'TRACE_VGR')
    logging.DEBUG_VGR = _dg
    logging.addLevelName(logging.DEBUG_VGR, 'DEBUG_VGR')


def NiO_exit():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    valid = False
    init_VGRHBW()


def init_map_nfctag_history():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    #nfc history code:
    # 100 = "Anlieferung Rohware"
    # 200 = "Qualitätskontrolle"
    # 300 = "Einlagerung"
    # 400 = "Auslagerung"
    # 500 = "Bearbeitung Brennofen"
    # 600 = "Bearbeitung Fräse"
    # 700 = "Sortierung"
    # 800 = "Versand Ware"
    #map of items:
    #uid -> [ts, code]*8
    map_nfctag_history = {}


def set_nfctag_item(taguid, num, history_ts):
    global _tr0, _tr, _dg, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, num)
    if taguid != None:
        print("item: ", taguid, " ", num, " ", history_ts)
        if map_nfctag_history == None:
            init_map_nfctag_history()
        if map_get_uid(map_nfctag_history, taguid) == None:
            list_nfctag_history = [None] * 8
        else:
            list_nfctag_history = map_get_uid(map_nfctag_history, taguid)
        list_nfctag_history[int(num - 1)] = history_ts / 1000
        map_nfctag_history[taguid] = list_nfctag_history
    print("set_nfctag_item: ", map_nfctag_history)


def map_get_uid(m, k):
    global _tr0, _tr, _dg, taguid, num, history_ts, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE0_VGR, '-')
    if m != None:
        mi = m.get(k)
    return mi


def nfc_write_history(w_uid, w_color, state):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    # nfc_data:
    #   0:nfc uid:
    #     workpiece NTAG213:  7 bytes
    #     card + blue key Mifare: 4 bytes
    #   1:byte0: state: 0:RAW, 1:PROCESSED, 2:REJECTED
    #   2:byte1: type: 0:NONE, 1:WHITE, 2:RED, 3:BLUE
    #   3:byte2: mask timestamps
    #   4:byte3: none (reserved)
    #   5:byte4...4+(8*8): vts[8]: int64_t (8 bytes)
    res = False
    count_write = 0
    while True:
        taguid = w_uid
        _state = state
        if w_color == 'WHITE':
            _type = 1
        elif w_color == 'RED':
            _type = 2
        elif w_color == 'BLUE':
            _type = 3
        else:
            _type = 0
        _mask = map_get_msk()
        _vts = map_get_uid(map_nfctag_history, taguid)
        print("_state", _state)
        print("_type", _type)
        print("_mask", _mask)
        print("_vts", _vts)
        res = nfc_write(_state, _type, _mask, _vts)
        #HINT: res=nfc_write is always false
        data = nfc_read()
        #print(data)
        res = (get_nfc_data_state()) == _state and (get_nfc_data_type()) == _type and (get_nfc_data_mask()) == _mask
        print("res: ", res)
        count_write = (count_write if isinstance(count_write, (int, float)) else 0) + 1
        if res or count_write >= 3:
            return res
            break
        else:
            print(data)
        time.sleep(1)
    return res


def map_get_msk():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    mask = 0
    if list_nfctag_history != None:
        print("list_nfctag_history: ", list_nfctag_history)
        index = 0
        for i in list_nfctag_history:
            #print("i: ", i)
            bit = bin(1 if i != None else 0)
            #print("bit: ", bit)
            if bit == bin(1):
                mask += 2 ** index
            #print("mask: ", mask)
            index = (index if isinstance(index, (int, float)) else 0) + 1
    print("map_get_msk: ", mask)
    return mask


def reset_dps_silent():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    set_output_announced(None)
    calibration_mode_disable()
    calibration_reload()
    display.set_attr("txt_label_message2.text", str(''))
    display.set_attr("txt_label_message.text", str(''))
    _set_state_VGR(4, 1, 'home')
    release()
    moveRefHome()
    _set_state_VGR(1, 0, '')
    set_state_dsi(0)
    reset_clear_request()
    vda_reset()
    set_status(STATE_RESET)


def reset_dps():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    reset_dps_silent()
    vda_publish_status()


def thread_VGR():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    ResetException = reset_get_ResetException()
    ts_readuid = 0
    vdacmd_set_calibration_started(False)
    if True:
        # copy lib to TXT 4.0 controller:
        # from:
        #  - ff-modul-dps/robotic_arm
        #  - https://github.com/dmholtz/ft_robot/tree/ft_dps/robotic_arm/
        # to:
        #  - /usr/lib/python3.5/site-packages/robotic_arm
        init_robotic_arm()
    else:
        pass
    _set_state_VGR(1, 0, '')
    logging.log(logging.TRACE_VGR, 'Initializing Module State')
    init_module_state_constants()
    current_status = STATE_IDLE
    while True:
        try:
            calibration_started = vdacmd_is_calibration_started()
            calibration_requested = vdacmd_is_calibration_requested()
            if not calibration_requested and not calibration_started:
                _main_loop_vgr()
            elif calibration_requested and not calibration_started:
                calibration_mode_start()
        except ResetException:
            reset_dps()
        except BaseException:
            logging.exception("Unexpected exception in main loop")
            handle_mainloop_exception()
        time.sleep(0.05)


def set_status(status):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    _unused = set_status_check(status)


def start_vda_action():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    action = vda_get_action()
    if not action:
        return
    print('Received action')
    print(action)
    actionCommand = action['command']
    print('Received action command')
    print(actionCommand)
    if current_status == STATE_IDLE and actionCommand == ACTION_INPUT_RGB:
        vda_set_action_status(action, vda_status_running())
        print('start processing input workpiece')
        set_status(STATE_INPUT_RUNNING)
    elif current_status == STATE_IDLE and actionCommand == ACTION_PICK_NFC:
        print('start processing output workpiece')
        vda_set_action_status(action, vda_status_running())
        set_status(STATE_PICK_NFC_RUNNING)
    elif current_status == STATE_NFC_IDLE and actionCommand == ACTION_NFC_DROP:
        print('Loading workpiece on vehicle')
        vda_set_action_status(action, vda_status_running())
        set_status(STATE_DROP_RUNNING)
    elif current_status == STATE_NFC_IDLE and actionCommand == ACTION_NFC_NIO:
        print('discarding workpiece')
        vda_set_action_status(action, vda_status_running())
        set_status(STATE_NIO_RUNNING)
    elif current_status == STATE_NFC_IDLE and actionCommand == ACTION_NFC_OUT:
        print('delivering workpiece')
        vda_set_action_status(action, vda_status_running())
        set_status(STATE_OUT_RUNNING)
    elif current_status == STATE_RGB_IDLE and actionCommand == ACTION_RGB_NFC:
        print('moving workpiece to NFC reader')
        vda_set_action_status(action, vda_status_running())
        set_status(STATE_RGB_NFC_RUNNING)
    else:
        vda_set_action_status(action, vda_status_failed())
        set_status(STATE_FAILED)


# Setup the module state machine to manage, what actions can be executed
def init_module_state_constants():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    ACTION_INPUT_RGB = 'INPUT_RGB'
    ACTION_RGB_NFC = 'RGB_NFC'
    ACTION_NFC_DROP = 'DROP'
    ACTION_NFC_NIO = 'DISCARD'
    ACTION_NFC_OUT = 'DELIVER'
    ACTION_PICK_NFC = 'PICK'
    STATE_IDLE = 'Waiting for workpiece'
    STATE_RESET = 'Resetting...'
    STATE_INPUT_RUNNING = 'Processing workpiece input'
    STATE_RGB_IDLE = 'Waiting for workpiece recognition'
    STATE_RGB_NFC_RUNNING = 'Moving workpiece to NFC reader'
    STATE_NFC_IDLE = 'Waiting for workpiece decision'
    STATE_DROP_RUNNING = 'Loading workpiece to AGV for stockpiling'
    STATE_NIO_RUNNING = 'Discarding workpiece'
    STATE_OUT_RUNNING = 'Delivering workpiece'
    STATE_PICK_NFC_RUNNING = 'Unloading workpiece from AGV'
    ACTION_DROP = 'DROP'
    ACTION_PROCESS_OUTPUT = 'PICK'
    STATE_PROCESSING_OUTPUT = 'Processing for delivery'
    STATE_IDLE = 'Waiting for workpiece'
    STATE_FAILED = 'Action failed'
    STATE_PROCESSING_INPUT = 'Processing workpiece input'
    STATE_PROCESSING_INPUT_IDLE = 'Waiting for stockpiling'
    STATE_PROCESSING_UNLOAD = 'Loading AGV for stockpiling'


def set_status_check(status):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    if current_status == STATE_IDLE and (status == STATE_PROCESSING_OUTPUT or status == STATE_INPUT_RUNNING or status == STATE_PICK_NFC_RUNNING):
        current_status = status
    elif current_status == STATE_INPUT_RUNNING and status == STATE_RGB_IDLE:
        current_status = status
    elif current_status == STATE_RGB_IDLE and (status == STATE_RGB_NFC_RUNNING or status == STATE_RGB_NIO_RUNNING):
        current_status = status
    elif current_status == STATE_RGB_NFC_RUNNING and status == STATE_NFC_IDLE:
        current_status = status
    elif current_status == STATE_NFC_IDLE and status == STATE_NIO_RUNNING:
        current_status = status
    elif current_status == STATE_NFC_IDLE and status == STATE_OUT_RUNNING:
        current_status = status
    elif current_status == STATE_NFC_IDLE and status == STATE_DROP_RUNNING:
        current_status = status
    elif current_status == STATE_PICK_NFC_RUNNING and status == STATE_NFC_IDLE:
        current_status = status
    elif current_status != STATE_FAILED and status == STATE_FAILED:
        current_status = status
    elif (current_status == STATE_NIO_RUNNING or current_status == STATE_OUT_RUNNING or current_status == STATE_DROP_RUNNING or current_status == STATE_FAILED or not current_status) and status == STATE_IDLE:
        current_status = status
    elif status == STATE_RESET:
        current_status = STATE_IDLE
    elif current_status != STATE_PROCESSING_OUTPUT and status == STATE_IDLE:
        current_status = status
    else:
        return False
    print(current_status)
    display.set_attr("txt_label_message.text", str(current_status))
    return True


def _main_loop_vgr():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    reset_raise_exception_if_requested()
    start_vda_action()
    if (get_factory_error_state()) == 'VGR':
        print('VGR: error')
        _set_state_VGR(4, 0, '')
        display.set_attr("txt_label_message.text", str('ERROR VGR: Please confirm with ACK button!'))
    elif (getcmd_reqVGR_Nfc()) != None:
        print('VGR: check cmd NFC read, delete')
        if (getcmd_reqVGR_Nfc()) == 'read_uid':
            logging.log(logging.TRACE_VGR, "read_uid")
            res = nfc_read_uid()
            if res != None:
                beep()
                display.set_attr("txt_label_message.text", str('Read UID NFC'))
                display.set_attr("txt_label_message2.text", str(''))
        elif (getcmd_reqVGR_Nfc()) == 'read':
            logging.log(logging.TRACE_VGR, "read")
            res = nfc_read()
            if res != None:
                beep()
                display.set_attr("txt_label_message.text", str('Read NFC'))
                display.set_attr("txt_label_message2.text", str(''))
        elif (getcmd_reqVGR_Nfc()) == 'delete':
            logging.log(logging.TRACE_VGR, "delete")
            res = nfc_delete()
            if res != None:
                beep()
                display.set_attr("txt_label_message.text", str('Delete NFC'))
                display.set_attr("txt_label_message2.text", str(''))
        else:
            display.set_attr("txt_label_message.text", str('Uknown cmd'))
            display.set_attr("txt_label_message2.text", str(''))
        res = reqVGR_Nfc(None)
    elif current_status == STATE_INPUT_RUNNING:
        print('VGR: ----------------------------------DSI----------------------------------')
        set_state_dsi(1)
        ts_dsi = (time.time() * 1000)
        display.set_attr("txt_label_message.text", str('Delivery raw material'))
        display.set_attr("txt_label_message2.text", str(''))
        _set_state_VGR(2, 1, 'hbw')
        valid = True
        wp = [time.time(), None, None, False]
        din2cs1()
        time.sleep(1)
        if get_output_announced():
            move_to_nio_for_output(get_output_announced())
        else:
            set_vda_action_result(None)
            complete_vda_action(set_status_check(STATE_RGB_IDLE))
    elif current_status == STATE_RGB_NFC_RUNNING:
        logging.log(logging.DEBUG_VGR, 'color: %s', last_color)
        cs2nfc1()
        print('VGR: --------------------------------NFC----------------------------')
        release()
        handle_NFC()
        action = vda_get_action()
        last_color = action.get("metadata", {}).get("type")
        print('VGR: ----------------------------NFC END------------------------')
        if valid:
            wp = [time.time(), uid, last_color, False]
            valid = wp != None
            display.set_attr("txt_label_message2.text", str('Color: {} uid: {}'.format(last_color, uid)))
            logging.log(logging.DEBUG_VGR, 'wp valid')
        if get_output_announced():
            valid = False
        if not valid:
            print('----------------------------- Moving to NiO --------------------------')
            grip()
            nfc2nio()
            moveRefHome()
            print('----------------------------- Setting State: Reset--------------------------')
            if get_output_announced():
                clear_state_for_output(get_output_announced())
            else:
                complete_vda_action(set_status_check(STATE_RESET))
        if valid:
            print('Returning nfc id for workpiece')
            set_vda_action_result(uid)
            complete_vda_action(set_status_check(STATE_NFC_IDLE))
    elif current_status == STATE_PROCESSING_UNLOAD or current_status == STATE_DROP_RUNNING:
        logging.log(logging.DEBUG_VGR, 'ackHBW=2')
        print('command received to output the workpiece')
        grip()
        nfc2fts()
        complete_vda_action(set_status_check(STATE_RESET))
        fts2homeRef()
        valid = True
        set_state_dsi(0)
        set_nfctag_item(uid, 3, (time.time() * 1000))
        display.set_attr("txt_label_message.text", str(''))
        display.set_attr("txt_label_message2.text", str(''))
    elif (get_output_announced()) and (current_status == STATE_RGB_IDLE or current_status == STATE_NFC_IDLE):
        move_to_nio_for_output(get_output_announced())
    elif current_status == STATE_PROCESSING_OUTPUT or current_status == STATE_PICK_NFC_RUNNING:
        set_output_announced(None)
        # name and output are to be defined
        deliverFtsToOut()
    elif (get_output_announced()) and current_status == STATE_IDLE:
        clear_state_for_output(get_output_announced())
    _set_state_VGR(1, 0, '')
    time.sleep(0.5)


def vgr_get_valid_actions():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    init_module_state_constants()
    return [ACTION_INPUT_RGB, ACTION_RGB_NFC, ACTION_NFC_DROP, ACTION_PICK_NFC]


def handle_mainloop_exception():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    if 0 < first_index([STATE_PROCESSING_OUTPUT, STATE_INPUT_RUNNING, STATE_PICK_NFC_RUNNING, STATE_RGB_NFC_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_NIO_RUNNING], current_status):
        display.set_attr("txt_label_message2.text", str('ERROR: Invalid target coordinates for position'))
    moveRefHome()
    complete_vda_action(False)
    set_status(STATE_FAILED)
    display.set_attr("txt_label_message.text", str('Action failed. Factory reset required.'))


def complete_vda_action(success):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    action = vda_get_action()
    if not action:
        return
    if success:
        vda_set_action_status(action, vda_status_finished())
    else:
        vda_set_action_status(action, vda_status_failed())


def set_vda_action_result(result):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    action = vda_get_action()
    if not action:
        return
    vda_set_action_result(action, result)


def clear_state_for_output(output_instant_action):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    set_status(STATE_RESET)
    _newOrderId = "";
    if get_output_announced() is not None:
        _newOrderId = get_output_announced().get("metadata", {}).get("orderId", "")
    vda_assign_order(_newOrderId)
    set_output_announced(None)
    vda_set_instant_action_status(output_instant_action, vda_status_finished())
    vda_publish_status()


def move_to_nio_for_output(output_instant_action):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    _set_state_VGR(2, 1, 'nio')
    set_output_announced(None)
    release()
    grip()
    nfc2nio()
    moveRefHome()
    clear_state_for_output(output_instant_action)


def _set_state_VGR(_code, _active, _target):
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE0_VGR, '-')
    if state_code != _code or state_active != _active or state_target != _target:
        _ts_state = 0
        state_code = _code
        state_active = _active
        state_target = _target
        set_robot_active(_active)


def deliverFtsToOut():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    _set_state_VGR(2, 1, 'dso')
    display.set_attr("txt_label_message2.text", str(''))
    logging.log(logging.TRACE_VGR, '-')
    print('starting output')
    fts2nfc1()
    # verify if the NFC tag can be read
    # and all data is valid.
    # directly send the success/failure message
    delivery_action = vda_get_action()
    if delivery_verify_nfctag(delivery_action):
        set_vda_action_result('PASSED')
        complete_vda_action(set_status_check(STATE_IDLE))
        valid = delivery_write_history(delivery_action)
        # publish the errors if writing failed.
        if not valid:
            vda_publish_status()
    else:
        valid = False
        set_vda_action_result('FAILED')
        complete_vda_action(set_status_check(STATE_IDLE))
    if valid:
        grip()
        print('History was written')
        display.set_attr("txt_label_message2.text", str(''))
        print('moving to DSO')
        nfc2dout()
        beep_blocked()
        set_state_dso(1)
        dout2homeRef()
    else:
        grip()
        nfc2nio()
        release()
        nio2homeRef2()
        req = reqHBW_fetchContainer(None)


def get_state_code_VGR():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE0_VGR, '-')
    return state_code


def get_state_active_VGR():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE0_VGR, '-')
    return state_active


def grip():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    TXT_M_O7_compressor.on()
    time.sleep(2)
    TXT_M_O8_magnetic_valve.on()


def release():
    global _tr0, _tr, _dg, taguid, num, history_ts, m, k, w_uid, w_color, state, action, status, success, result, output_instant_action, _code, _active, _target, valid, mi, res, mask, wp_uid, _unused, ACTION_INPUT_RGB, uid, last_color, STATE_FAILED, state_code, state_active, STATE_IDLE, ResetException, ACTION_RGB_NFC, current_status, ACTION_NFC_DROP, ACTION_PICK_NFC, STATE_RESET, _workpiece, ts_readuid, _ts_state, count_write, workpiece_state_history, ACTION_DROP, ACTION_NFC_NIO, STATE_INPUT_RUNNING, STATE_RGB_IDLE, STATE_RGB_NFC_RUNNING, STATE_NFC_IDLE, STATE_NIO_RUNNING, STATE_OUT_RUNNING, STATE_DROP_RUNNING, STATE_PICK_NFC_RUNNING, STATE_PROCESSING_OUTPUT, list_nfctag_history, index, color, actionCommand, ACTION_NFC_OUT, STATE_RGB_NIO_RUNNING, state_target, map_nfctag_history, i, ts_dsi, STATE_PROCESSING_UNLOAD, _state, valid_processed, delivery_action, bit, _type, _mask, _vts, wp, data, req, ACTION_PROCESS_OUTPUT, STATE_PROCESSING_INPUT, STATE_PROCESSING_INPUT_IDLE
    logging.log(logging.TRACE_VGR, '-')
    TXT_M_O8_magnetic_valve.off()
    TXT_M_O7_compressor.off()
    time.sleep(2)


def first_index(my_list, elem):
    try: index = my_list.index(elem) + 1
    except: index = 0
    return index

