import logging
import os
import time
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.display import *
from lib.machine_learning import *
from lib.mqtt_utils import *
from lib.vda5050 import *

status = None
unexpected = None
success = None
result_code = None
action = None
parameter = None
default_value = None
ACTION_PICK = None
STATE_IDLE = None
has_order = None
_unused = None
ACTION_DROP = None
STATE_PICKING = None
controllerid = None
current_status = None
ACTION_PROCESS = None
STATE_IDLE_WITH_STOCK = None
num = None
STATE_RESET = None
RESULT_PASSED = None
STATE_FAILED = None
STATE_PROCESSING = None
RESULT_FAILED = None
STATE_PICKING_DONE = None
actionCommand = None
MovementSpeed = None
STATE_PROCESSING_IDLE = None
PositionPASSED = None
PositionFAILED = None
PositionCamera = None
dubblepart = None


def main_SLD():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    print('Initializing Module')
    init_supported_module_actions()
    print('Setup state machine')
    init_module_state_machine()
    print('Setup MQTT Connection')
    setup_mqtt_connection()
    print('Setup hardware config')
    MovementSpeed = 300
    PositionPASSED = -132
    PositionFAILED = 200
    PositionCamera = 105
    dubblepart = False
    num = -1
    print('Starting loop')
    while True:
        try:
        	mainSLDexternal_th()
        except Exception as e:
        	print(e)
        	clean_exit()
        time.sleep(1)


# Defines the actions this module supports. Can be extracted from the modules README.md
def init_supported_module_actions():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    ACTION_PICK = 'PICK'
    ACTION_DROP = 'DROP'
    ACTION_PROCESS = 'CHECK_QUALITY'
    RESULT_PASSED = 'PASSED'
    RESULT_FAILED = 'FAILED'
    vda_init([ACTION_PICK, ACTION_PROCESS, ACTION_DROP])


# Setup the module state machine to manage, what actions can be executed
def init_module_state_machine():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    STATE_IDLE = 'STATE_IDLE'
    STATE_PICKING = 'STATE_PICKING'
    STATE_IDLE_WITH_STOCK = 'STATE_IDLE_WITH_STOCK'
    STATE_FAILED = 'STATE_FAILED'
    STATE_PICKING_DONE = 'STATE_PICKING_DONE'
    STATE_FAILED = 'STATE_FAILED'
    STATE_PROCESSING = 'STATE_PROCESSING'
    STATE_PROCESSING_IDLE = 'STATE_PROCESSING_IDLE'
    current_status = STATE_IDLE


def start_vda_action():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    action = vda_get_action()
    print(action)
    if not action and current_status != STATE_FAILED and current_status != STATE_IDLE:
        print('No Action, no execution')
        set_status(STATE_IDLE)
    if not action:
        return
    print('Received action')
    print(action)
    actionCommand = action['command']
    print('Received action command')
    print(actionCommand)
    if current_status == STATE_IDLE and actionCommand == ACTION_PROCESS:
        vda_set_action_status(action, vda_status_running())
        print('start processing')
        set_status(STATE_PROCESSING)
    else:
        vda_set_action_status(action, vda_status_failed())
        set_status(STATE_FAILED)


def mainSLDexternal_th():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    start_vda_action()
    if current_status == STATE_PROCESSING:
        num = MakePictureRunKiReturnFoundPart()
        print(num)
        if num == 1 or num == 2 or num == 3:
            print('Check successful')
            vda_set_current_action_result(RESULT_PASSED)
            complete_vda_action(set_status_check(STATE_IDLE))
        else:
            set_status(STATE_RESET)
            vda_set_current_action_result(RESULT_FAILED)
            complete_vda_action(True)
    elif current_status == STATE_IDLE:
        pass
    else:
        print('No mapped action found')


# Connect to the mqtt broker, subscribe to all relevant topics and add the respective callbacksd
def setup_mqtt_connection():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    controllerid = os.uname()[1]
    display.set_attr("label_mqtt_status.text", str('connecting to MQTT ...'))
    vda_setup_offline_notifications()
    mqtt_get_client().set_disconnect_callback(handle_mqtt_disconnected)

    mqtt_get_client().set_connect_callback(handle_mqtt_connected)
    mqtt_connect_and_wait()
    print('Subscribing to instant actions')
    mqtt_get_client().subscribe(topic=vda_get_instant_action_topic(), callback=mqtt_instant_action_callback, qos=2)
    print('Subscribing to orders')
    mqtt_get_client().subscribe(topic=vda_get_order_topic(), callback=order_callback, qos=2)
    mqtt_wait_connected()


def mqtt_instant_action_callback(message):
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    print('Instant action callback triggered')
    vda_handle_instant_actions(message.payload.decode("utf-8"))



def clean_exit():
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    os._exit(os.EX_OK)


def order_callback(message):
    global status, unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    has_order = vda_process_order(message.payload.decode("utf-8"))
    vda_publish_status()



def set_status(status):
    global unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    _unused = set_status_check(status)


def handle_mqtt_disconnected(unexpected):
    global status, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    display.set_attr("mqtt_green.active", str(False).lower())
    if unexpected:
        display.set_attr("label_mqtt_status.text", str('Reconnecting: unexpected disconnect'))
    else:
        display.set_attr("label_mqtt_status.text", str('Disconnected'))


def complete_vda_action(success):
    global status, unexpected, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    action = vda_get_action()
    if not action:
        return
    if success:
        vda_set_action_status(action, vda_status_finished())
    else:
        vda_set_action_status(action, vda_status_failed())


def handle_mqtt_connected(result_code):
    global status, unexpected, success, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    display.set_attr("label_mqtt_status.text", str(mqtt_connect_result_to_string(result_code)))
    display.set_attr("mqtt_green.active", str(not result_code).lower())
    if not result_code:
        vda_send_connection_online()
        vda_publish_status()


def get_metadata_parameter(action, parameter, default_value):
    global status, unexpected, success, result_code, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    try:
      return action.get("metadata", {}).get(parameter, default_value)
    except:
      pass
    return default_value


def set_status_check(status):
    global unexpected, success, result_code, action, parameter, default_value, ACTION_PICK, STATE_IDLE, has_order, _unused, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, num, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
    if current_status == STATE_IDLE and status == STATE_PROCESSING:
        current_status = status
    elif (current_status == STATE_PROCESSING or current_status == STATE_FAILED or not current_status) and status == STATE_IDLE:
        current_status = status
    elif current_status != STATE_FAILED and status == STATE_FAILED:
        current_status = status
    elif status == STATE_RESET:
        current_status = STATE_IDLE
    else:
        return False
    print(current_status)
    return True


