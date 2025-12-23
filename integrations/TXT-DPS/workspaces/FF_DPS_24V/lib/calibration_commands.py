import time
from fischertechnik.controller.Motor import Motor
from lib.calibration_data import *
from lib.calibration_mode import *
from lib.controller import *
from lib.display import *
from lib.Factory_Variables import *
from lib.robotic_arm import *
from lib.vda5050 import *

_tr0 = None
_tr = None
_dg = None
action = None
parameter = None
default_value = None
value = None
positions = None
actionType = None
calibration_requested = None
calibration_started = None
i = None
FAILED_BEFORE = None
test_position = None
calibration_park_queued = None
actionState = None
current_position = None


def initlog_VDACMD(_tr0, _tr, _dg):
    global action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    logging.TRACE0_VDACMD = _tr0
    logging.addLevelName(logging.TRACE0_VDACMD , 'TRACE0_VDACMD')
    logging.TRACE_VDACMD = _tr
    logging.addLevelName(logging.TRACE_VDACMD , 'TRACE_VDACMD')
    logging.DEBUG_VDACMD = _dg
    logging.addLevelName(logging.DEBUG_VDACMD, 'DEBUG_VDACMD')


def calibration_mode_start():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    logging.debug("- calibration_mode_start")
    calibration_mode_enable()
    actionState = calibration_requested
    vda_set_instant_action_status(actionState, vda_status_running())
    vda_publish_status()
    vdacmd_perform_reset()
    calibration_started = True
    calibration_mode_enable()
    calibration_mode_set_status_value(calibration_mode_get_key_available_positions(), ','.join(['REF', 'HOME_BASE', 'HOME_INPUT', 'HOME_OUTPUT', 'NIO_APPROACH', 'NIO_TARGET', 'CS_APPROACH', 'CS_TARGET', 'NFC_APPROACH', 'NFC_TARGET', 'INPUT_PICK_APPROACH_A', 'INPUT_PICK_APPROACH_B', 'INPUT_PICK_TARGET', 'OUTPUT_DROP_APPROACH_A', 'OUTPUT_DROP_APPROACH_B', 'OUTPUT_DROP_TARGET', 'FTS_PICK_APPROACH_A', 'FTS_PICK_APPROACH_B', 'FTS_PICK_TARGET', 'FTS_DROP_APPROACH_A', 'FTS_DROP_APPROACH_B', 'FTS_DROP_TARGET', 'GRIP_ON', 'GRIP_OFF', 'PARK']))
    calibration_mode_set_status_value(calibration_mode_get_key_current_position(), current_position)
    current_position = 'REF'
    FAILED_BEFORE = False
    calibration_mode_update_status()
    print(actionState)
    vda_set_instant_action_status(actionState, vda_status_finished())
    vda_publish_status()
    calibration_mode_run_queued_park()


def vdacmd_perform_reset():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    while not not (get_robot_active()):
        time.sleep(0.2)
    calibration_started = False
    calibration_requested = False
    FAILED_BEFORE = False
    calibration_mode_disable()
    calibration_reload()
    moveRefHome()


def get_metadata_parameter(action, parameter, default_value):
    global _tr0, _tr, _dg, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    return action.get("metadata", {}).get(parameter, default_value)


def vdacmd_is_calibration_requested():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    return calibration_requested


def vdacmd_is_calibration_started():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    return calibration_started


def vdacmd_set_calibration_requested(value):
    global _tr0, _tr, _dg, action, parameter, default_value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    calibration_requested = value


def vdacmd_set_calibration_started(value):
    global _tr0, _tr, _dg, action, parameter, default_value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    calibration_started = value


def calibration_reference_position():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    if not (get_robot_active()):
        set_robot_active(1)
        moveRefHome()
        set_robot_active(0)


def calibration_move_robot_from_ref(positions):
    global _tr0, _tr, _dg, action, parameter, default_value, value, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    if not (get_robot_active()):
        set_robot_active(1)
        moveRefHome()
        try:
            calibration_move_to_position_internal(positions)
        except BaseException:
            logging.exception("CALIBRATION Error during move")
            calibration_move_handle_error()
        set_robot_active(0)


def calibration_move_to_position(positions):
    global _tr0, _tr, _dg, action, parameter, default_value, value, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    if not (get_robot_active()):
        set_robot_active(1)
        try:
            calibration_move_to_position_internal(positions)
        except BaseException:
            logging.exception("CALIBRATION Error during move")
            calibration_move_handle_error()
        set_robot_active(0)


def calibration_move_to_position_internal(positions):
    global _tr0, _tr, _dg, action, parameter, default_value, value, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    for i in positions:
        move_ptp(i, 0)


def calibration_move_handle_error():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    display.set_attr("txt_label_message.text", str('ERROR: Invalid coordinates for tested position.'))
    calibration_mode_set_status_value('INFO', 'ERROR: Invalid coordinates for tested position.')
    FAILED_BEFORE = True


def calibration_mode_actions(actionType, action):
    global _tr0, _tr, _dg, parameter, default_value, value, positions, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    logging.debug("Calibrating:  %s  %s", actionType, action)
    if actionType == (calibration_mode_get_instant_action_start()):
        calibration_park_queued = False
        calibration_requested = action
    if calibration_requested and not calibration_started:
        calibration_mode_action_during_init(actionType, action)
    if not calibration_started:
        return
    display.set_attr("txt_label_message.text", str('Calibrating...'))
    if actionType == (calibration_mode_get_instant_action_set()):
        _calib = action.get("metadata", {}).get("references", [])
        if _calib:
            for k in _calib:
                _key = k.get("referenceKey")
                _value = k.get("referenceValue")
                if _key and _value:
                    calibration_set(_key, _value)
        calibration_mode_update_status()
    elif actionType == (calibration_mode_get_instant_action_test()):
        calibration_mode_action_test_position(actionType, action)
    elif actionType == (calibration_mode_get_instant_action_store()):
        _calib = action.get("metadata", {}).get("references", [])
        if _calib:
            for k in _calib:
                _key = k.get("referenceKey")
                _value = k.get("referenceValue")
                if _key and _value:
                    calibration_set(_key, _value)
        calibration_save()
        calibration_mode_update_status()
    elif actionType == (calibration_mode_get_instant_action_stop()):
        calibration_started = False
        calibration_mode_disable()
        vdacmd_perform_reset()
        display.set_attr("txt_label_message.text", str('Ready.'))
        vda_set_instant_action_status(action, vda_status_finished())
    elif actionType == (calibration_mode_get_instant_action_reset()):
        if get_metadata_parameter(action, 'factory', None):
            calibration_reset_defaults()
        else:
            calibration_reload()
        calibration_mode_update_status()
    elif actionType == (calibration_mode_get_instant_action_select()):
        calibration_mode_action_select_position(actionType, action)
    vda_publish_status()


def calibration_mode_action_test_position(actionType, action):
    global _tr0, _tr, _dg, parameter, default_value, value, positions, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    if FAILED_BEFORE:
        calibration_mode_action_select_position(actionType, action)
        if True:
            return
    test_position = get_metadata_parameter(action, 'position', 'REF')
    calibration_mode_set_status_value('INFO', None)
    if test_position == 'REF':
        calibration_reference_position()
    elif test_position == 'GRIP_OFF':
        drop()
        test_position = current_position
    elif test_position == 'GRIP_ON':
        gripOnce()
        test_position = current_position
    elif test_position != current_position:
        calibration_mode_set_status_value('INFO', 'Select position before test')
        test_position = current_position
    elif test_position == 'HOME_BASE':
        calibration_move_to_position(['home1'])
    elif test_position == 'HOME_INPUT':
        calibration_move_to_position(['home2'])
    elif test_position == 'HOME_OUTPUT':
        calibration_move_to_position(['home3'])
    elif test_position == 'NIO_APPROACH':
        calibration_move_to_position(['nio'])
    elif test_position == 'NIO_TARGET':
        calibration_move_to_position(['nio', 'nio2'])
    elif test_position == 'CS_APPROACH':
        calibration_move_to_position(['cs'])
    elif test_position == 'CS_TARGET':
        calibration_move_to_position(['cs', 'cs2'])
    elif test_position == 'NFC_APPROACH':
        calibration_move_to_position(['nfc'])
    elif test_position == 'NFC_TARGET':
        calibration_move_to_position(['nfc', 'nfc2'])
    elif test_position == 'INPUT_PICK_APPROACH_A':
        calibration_move_to_position(['dinp'])
    elif test_position == 'INPUT_PICK_APPROACH_B':
        calibration_move_to_position(['dinp', 'dinp2'])
    elif test_position == 'INPUT_PICK_TARGET':
        calibration_move_to_position(['dinp', 'dinp2', 'dinp3'])
    elif test_position == 'INPUT_DROP_APPROACH_A':
        calibration_move_to_position(['dind'])
    elif test_position == 'INPUT_DROP_APPROACH_B':
        calibration_move_to_position(['dind', 'dind2'])
    elif test_position == 'INPUT_DROP_TARGET':
        calibration_move_to_position(['dind', 'dind2', 'dind3'])
    elif test_position == 'FTS_PICK_APPROACH_A':
        calibration_move_to_position(['ftsp1'])
    elif test_position == 'FTS_PICK_APPROACH_B':
        calibration_move_to_position(['ftsp1', 'ftsp2'])
    elif test_position == 'FTS_PICK_TARGET':
        calibration_move_to_position(['ftsp1', 'ftsp2', 'ftsp3'])
    elif test_position == 'FTS_DROP_APPROACH_A':
        calibration_move_to_position(['ftsd1'])
    elif test_position == 'FTS_DROP_APPROACH_B':
        calibration_move_to_position(['ftsd1', 'ftsd2'])
    elif test_position == 'FTS_DROP_TARGET':
        calibration_move_to_position(['ftsd1', 'ftsd2', 'ftsd3'])
    elif test_position == 'OUTPUT_DROP_APPROACH_A':
        calibration_move_to_position(['doutd'])
    elif test_position == 'OUTPUT_DROP_APPROACH_B':
        calibration_move_to_position(['doutd', 'doutd2'])
    elif test_position == 'OUTPUT_DROP_TARGET':
        calibration_move_to_position(['doutd', 'doutd2', 'doutd3'])
    elif test_position == 'OUTPUT_PICK_APPROACH_A':
        calibration_move_to_position(['doutp'])
    elif test_position == 'OUTPUT_PICK_APPROACH_B':
        calibration_move_to_position(['doutp', 'doutp2'])
    elif test_position == 'OUTPUT_PICK_TARGET':
        calibration_move_to_position(['doutp', 'doutp2', 'doutp3'])
    elif test_position == 'PARK':
        print('Test Park Position')
        parkVGR()
    calibration_mode_set_status_value(calibration_mode_get_key_current_position(), test_position)
    current_position = test_position
    calibration_mode_update_status()


def calibration_mode_action_select_position(actionType, action):
    global _tr0, _tr, _dg, parameter, default_value, value, positions, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    FAILED_BEFORE = False
    test_position = get_metadata_parameter(action, 'position', 'REF')
    calibration_mode_set_status_value('INFO', None)
    if test_position == 'REF':
        calibration_reference_position()
    elif test_position == 'HOME_BASE':
        calibration_move_robot_from_ref(['home1'])
    elif test_position == 'HOME_INPUT':
        calibration_move_robot_from_ref(['home1', 'home2'])
    elif test_position == 'HOME_OUTPUT':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3'])
    elif test_position == 'NIO_APPROACH':
        calibration_move_robot_from_ref(['home1', 'home2', 'nio'])
    elif test_position == 'NIO_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'nio', 'nio2'])
    elif test_position == 'CS_APPROACH':
        calibration_move_robot_from_ref(['home1', 'home2', 'cs'])
    elif test_position == 'CS_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'cs', 'cs2'])
    elif test_position == 'NFC_APPROACH':
        calibration_move_robot_from_ref(['home1', 'home2', 'nfc'])
    elif test_position == 'NFC_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'nfc', 'nfc2'])
    elif test_position == 'INPUT_PICK_APPROACH_A':
        calibration_move_robot_from_ref(['home1', 'home2', 'dinp'])
    elif test_position == 'INPUT_PICK_APPROACH_B':
        calibration_move_robot_from_ref(['home1', 'home2', 'dinp', 'dinp2'])
    elif test_position == 'INPUT_PICK_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'dinp', 'dinp2', 'dinp3'])
    elif test_position == 'INPUT_DROP_APPROACH_A':
        calibration_move_robot_from_ref(['home1', 'home2', 'dind'])
    elif test_position == 'INPUT_DROP_APPROACH_B':
        calibration_move_robot_from_ref(['home1', 'home2', 'dind', 'dind2'])
    elif test_position == 'INPUT_DROP_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'dind', 'dind2', 'dind3'])
    elif test_position == 'FTS_PICK_APPROACH_A':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'ftsp1'])
    elif test_position == 'FTS_PICK_APPROACH_B':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'ftsp1', 'ftsp2'])
    elif test_position == 'FTS_PICK_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'ftsp1', 'ftsp2', 'ftsp3'])
    elif test_position == 'FTS_DROP_APPROACH_A':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'ftsd1'])
    elif test_position == 'FTS_DROP_APPROACH_B':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'ftsd1', 'ftsd2'])
    elif test_position == 'FTS_DROP_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'ftsd1', 'ftsd2', 'ftsd3'])
    elif test_position == 'OUTPUT_DROP_APPROACH_A':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'doutd'])
    elif test_position == 'OUTPUT_DROP_APPROACH_B':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'doutd', 'doutd2'])
    elif test_position == 'OUTPUT_DROP_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'doutd', 'doutd2', 'doutd3'])
    elif test_position == 'OUTPUT_PICK_APPROACH_A':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'doutp'])
    elif test_position == 'OUTPUT_PICK_APPROACH_B':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'doutp', 'doutp2'])
    elif test_position == 'OUTPUT_PICK_TARGET':
        calibration_move_robot_from_ref(['home1', 'home2', 'home3', 'doutp', 'doutp2', 'doutp3'])
    elif test_position == 'GRIP_ON':
        gripOnce()
        test_position = current_position
    elif test_position == 'GRIP_OFF':
        drop()
        test_position = current_position
    elif test_position == 'PARK':
        print('Selected Park Position')
        parkVGR()
    calibration_mode_set_status_value(calibration_mode_get_key_current_position(), test_position)
    current_position = test_position
    calibration_mode_update_status()


def calibration_mode_action_during_init(actionType, action):
    global _tr0, _tr, _dg, parameter, default_value, value, positions, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    if actionType == (calibration_mode_get_instant_action_select()) and get_metadata_parameter(action, 'position', 'REF') == 'PARK':
        calibration_park_queued = action


def calibration_mode_run_queued_park():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    if calibration_park_queued:
        calibration_mode_action_select_position(calibration_mode_get_instant_action_select(), calibration_park_queued)
        calibration_park_queued = False
        vda_publish_status()


def parkVGR():
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    print('DONE: Implement Action to park the Vacuum Gripper in the desired position')
    print('ref')
    TXT_M_M1_encodermotor.stop_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor)
    TXT_M_M2_encodermotor.set_speed(int(512), Motor.CCW)
    TXT_M_M2_encodermotor.start_sync()
    while True:
        if (TXT_M_I2_mini_switch.is_closed()):
            break
        time.sleep(0.010)
    TXT_M_M2_encodermotor.stop_sync()
    TXT_M_S1_servomotor.set_position(int(256))
    TXT_M_S2_servomotor.set_position(int(256))
    TXT_M_S3_servomotor.set_position(int(256))
    TXT_M_M3_encodermotor.set_speed(int(512), Motor.CCW)
    TXT_M_M3_encodermotor.start_sync()
    while True:
        if (TXT_M_I3_mini_switch.is_closed()):
            break
        time.sleep(0.010)
    TXT_M_M3_encodermotor.stop_sync()
    TXT_M_M1_encodermotor.set_speed(int(512), Motor.CCW)
    TXT_M_M1_encodermotor.start_sync()
    while True:
        if (TXT_M_I1_mini_switch.is_closed()):
            break
        time.sleep(0.010)
    TXT_M_M1_encodermotor.stop_sync()
    print('park pos')
    TXT_M_M3_encodermotor.set_speed(int(512), Motor.CW)
    TXT_M_M3_encodermotor.set_distance(int(490))
    while True:
        if (not TXT_M_M3_encodermotor.is_running()):
            break
        time.sleep(0.010)
    TXT_M_M2_encodermotor.set_speed(int(512), Motor.CW)
    TXT_M_M2_encodermotor.set_distance(int(160))
    while True:
        if (not TXT_M_M2_encodermotor.is_running()):
            break
        time.sleep(0.010)
    TXT_M_M1_encodermotor.set_speed(int(512), Motor.CW)
    TXT_M_M1_encodermotor.set_distance(int(460))
    while True:
        if (not TXT_M_M1_encodermotor.is_running()):
            break
        time.sleep(0.010)
    TXT_M_S2_servomotor.set_position(int(500))
    os._exit(os.EX_OK)


def on_txt_button_park_clicked(event):
    global _tr0, _tr, _dg, action, parameter, default_value, value, positions, actionType, calibration_requested, calibration_started, i, FAILED_BEFORE, test_position, calibration_park_queued, actionState, current_position
    parkVGR()


display.button_clicked("txt_button_park", on_txt_button_park_clicked)


