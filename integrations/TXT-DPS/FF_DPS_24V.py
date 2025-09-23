import os
import threading
import time

from lib.Axes1Ref import *
from lib.calibration_commands import *
from lib.calibration_data import *
from lib.calibration_mode import *
from lib.controller import *
from lib.display import *
from lib.DPS import *
from lib.Factory import *
from lib.Factory_Variables import *
from lib.File import *
from lib.GUI import *
from lib.iw_log import *
from lib.Log import *
from lib.mqtt_utils import *
from lib.net_utils import *
from lib.Nfc import *
from lib.NFC_Commands import *
from lib.reset_utils import *
from lib.robotic_arm import *
from lib.Sound import *
from lib.SSC_Lights import *
from lib.SSC_Publisher import *
from lib.SSC_Subscriber import *
from lib.Time import *
from lib.vda5050 import *
from lib.VGR import *
from lib.VGR_Axes1Ref import *
from lib.VGR_Display import *

result_code = None
unexpected = None
has_order = None
INSTANT_ACTION_RESET = None
i = None
INSTANT_ACTION_ACCOUNCE_OUTPUT = None
INSTANT_ACTION_CANCEL_STORAGE_ORDER = None
nfc_obj = None


# Defines the actions this module supports. Can be extracted from the modules README.md
def init_supported_module_actions():
    global result_code, unexpected, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    print('Initializing Module')
    INSTANT_ACTION_RESET = 'reset'
    INSTANT_ACTION_ACCOUNCE_OUTPUT = 'announceOutput'
    INSTANT_ACTION_CANCEL_STORAGE_ORDER = 'cancelStorageOrder'
    vda_init(vgr_get_valid_actions())


# Connect to the mqtt broker, subscribe to all relevant topics and add the respective callback
def setup_mqtt_connection():
    global result_code, unexpected, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    controllerid = os.uname()[1]
    print('Connecting to broker')
    display.set_attr("txt_label_message.text", 'Connecting to MQTT...')
    mqtt_get_client().set_disconnect_callback(handle_mqtt_disconnected)
    mqtt_get_client().set_connect_callback(handle_mqtt_connected)
    vda_setup_offline_notifications()
    mqtt_connect_always()
    print('Subscribing to instant actions')
    mqtt_get_client().subscribe(topic=vda_get_instant_action_topic(), callback=mqtt_instant_action_callback, qos=2)
    print('Subscribing to orders')
    mqtt_get_client().subscribe(topic=vda_get_order_topic(), callback=order_callback, qos=2)
    mqtt_wait_connected()


def mqtt_instant_action_callback(message):
    global result_code, unexpected, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    print('Instant action callback triggered')
    for i in vda_handle_instant_actions_get_custom(
        message.payload.decode("utf-8"),
        calibration_mode_extend_list(
            [INSTANT_ACTION_RESET, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER],
            calibration_mode_get_instant_actions(),
        ),
    ):
        if i['actionType'] == INSTANT_ACTION_RESET:
            reset_set_request()
            vda_set_instant_action_status(i, vda_status_running())
        elif 0 < first_index(calibration_mode_get_instant_actions(), i['actionType']):
            calibration_mode_actions(i['actionType'], i)
        elif i['actionType'] == INSTANT_ACTION_ACCOUNCE_OUTPUT:
            set_output_announced(i)
        elif i['actionType'] == INSTANT_ACTION_CANCEL_STORAGE_ORDER:
            set_output_announced(i)


def handle_mqtt_connected(result_code):
    global unexpected, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    display.set_attr("txt_status_connected.active", str(False).lower())
    if not result_code:
        display.set_attr("txt_status_connected.active", str(True).lower())
        vda_send_connection_online()
        vda_publish_status()
        print('Connection to broker established')


def handle_mqtt_disconnected(unexpected):
    global result_code, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    display.set_attr("txt_status_connected.active", str(False).lower())
    if unexpected:
        print('MQTT: Unexpected disconnect')
    else:
        print('MQTT: Disconnected')


def order_callback(message):
    global result_code, unexpected, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    has_order = vda_process_order(message.payload.decode("utf-8"))
    vda_publish_status()


def initializeModule():
    global result_code, unexpected, has_order, INSTANT_ACTION_RESET, i, INSTANT_ACTION_ACCOUNCE_OUTPUT, INSTANT_ACTION_CANCEL_STORAGE_ORDER, nfc_obj
    print('Setup MQTT Connection')
    init_supported_module_actions()
    setup_mqtt_connection()
    setup_input_from_dashboard(mqtt_get_client())
    nfc_commands_setup(mqtt_get_client())


def first_index(my_list, elem):
    try:
        index = my_list.index(elem) + 1
    except:
        index = 0
    return index


reset_init()
display.set_attr("txt_label_version.text", str(f'<h3>APS DPS (Version: {vda_get_factsheet_version()})</h3>'))
display.set_attr("txt_label_message.text", '')
display.set_attr("txt_label_message2.text", '')
set_version(vda_get_factsheet_version())
initlib_log(9)
calibration_init(robot_calibration_get_defaults())
calibration_mode_init()
nfc_obj = nfc_init()
print('Starting threads')
th2 = threading.Thread(target=thread_VGR, args=(), daemon=True)
th4 = threading.Thread(target=thread_DPS, args=(), daemon=True)
th2.start()
th4.start()
loadFileFactoryCalib()
initializeModule()
display.set_attr("txt_button_nfc_read.enabled", str(True).lower())
display.set_attr("txt_button_nfc_read.enabled", str(True).lower())
display.set_attr("txt_button_nfc_read.enabled", str(True).lower())
display.set_attr("txt_label_message.text", 'READY')
print('Threads started, joining...')
start_publish_threads_sensoric()
th2.join()
th4.join()
print('Threads joined')
while True:
    time.sleep(0.5)
