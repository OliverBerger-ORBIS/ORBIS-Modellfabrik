import base64
import json
import logging
import os
import time
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.controller import *
from lib.display import *
from lib.machine_learning import *
from lib.mqtt_utils import *
from lib.vda5050 import *

result = None
num = None
action = None
parameter = None
default_value = None
status = None
success = None
unexpected = None
result_code = None
ACTION_PICK = None
STATE_IDLE = None
_unused = None
has_order = None
ACTION_DROP = None
STATE_PICKING = None
controllerid = None
current_status = None
ACTION_PROCESS = None
STATE_IDLE_WITH_STOCK = None
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
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
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
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  ACTION_PICK = 'PICK'
  ACTION_DROP = 'DROP'
  ACTION_PROCESS = 'CHECK_QUALITY'
  RESULT_PASSED = 'PASSED'
  RESULT_FAILED = 'FAILED'
  vda_init([ACTION_PICK, ACTION_PROCESS, ACTION_DROP])


# Setup the module state machine to manage, what actions can be executed
def init_module_state_machine():
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
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
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
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
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  start_vda_action()
  if current_status == STATE_PROCESSING:
    num = MakePictureRunKiReturnFoundPart()
    print(num)
    if num == 1 or num == 2 or num == 3:
      print('Check successful with sound amd image')
      vda_set_current_action_result(RESULT_PASSED)
      """
      Ton für erfolgreiche Prüfung abspielen
      """
      TXT_SLD_M.get_loudspeaker().play("01_Airplane.wav", False)
      publish_quality_check_image(RESULT_PASSED, num)
      complete_vda_action(set_status_check(STATE_IDLE))
    else:
      print('Check failure with sound amd image')
      set_status(STATE_RESET)
      vda_set_current_action_result(RESULT_FAILED)
      """
      Ton für fehlgeschlagene Prüfung abspielen
      """
      TXT_SLD_M.get_loudspeaker().play("02_Alarm.wav", False)
      publish_quality_check_image(RESULT_FAILED, num)
      complete_vda_action(True)
  elif current_status == STATE_IDLE:
    pass
  else:
    print('No mapped action found')


# Connect to the mqtt broker, subscribe to all relevant topics and add the respective callbacksd
def setup_mqtt_connection():
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
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


def publish_quality_check_image(result, num):
  global action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  """
  Publiziert das zuletzt gespeicherte AIQS-Bild als Base64 (data URL) zusammen mit Result/Num. result: PASSED | FAILED
  """
  filename = '/opt/ft/workspaces/last-image.png'
  try:
      with open(filename, "rb") as img_file:
          img_data = base64.b64encode(img_file.read()).decode('utf-8')
      payload_obj = {
          "ts": vda_timestamp(),
          "result": result,
          "num": num,
          "data": "data:image/png;base64," + img_data
      }

      mqtt_get_client().publish(
          topic='/j1/txt/1/i/quality_check',
          payload=json.dumps(payload_obj),
          qos=2,
          retain=True
      )
      print('Quality check image published')

  except Exception as e:
      print("Error publishing quality check image")


def set_status(status):
  global result, num, action, parameter, default_value, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  _unused = set_status_check(status)


def clean_exit():
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  os._exit(os.EX_OK)


def mqtt_instant_action_callback(message):
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  print('Instant action callback triggered')
  vda_handle_instant_actions(message.payload.decode("utf-8"))



def complete_vda_action(success):
  global result, num, action, parameter, default_value, status, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  action = vda_get_action()
  if not action:
    return
  if success:
    vda_set_action_status(action, vda_status_finished())
  else:
    vda_set_action_status(action, vda_status_failed())


def order_callback(message):
  global result, num, action, parameter, default_value, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  has_order = vda_process_order(message.payload.decode("utf-8"))
  vda_publish_status()



def handle_mqtt_disconnected(unexpected):
  global result, num, action, parameter, default_value, status, success, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  display.set_attr("mqtt_green.active", str(False).lower())
  if unexpected:
    display.set_attr("label_mqtt_status.text", str('Reconnecting: unexpected disconnect'))
  else:
    display.set_attr("label_mqtt_status.text", str('Disconnected'))


def get_metadata_parameter(action, parameter, default_value):
  global result, num, status, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  try:
    return action.get("metadata", {}).get(parameter, default_value)
  except:
    pass
  return default_value


def handle_mqtt_connected(result_code):
  global result, num, action, parameter, default_value, status, success, unexpected, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
  display.set_attr("label_mqtt_status.text", str(mqtt_connect_result_to_string(result_code)))
  display.set_attr("mqtt_green.active", str(not result_code).lower())
  if not result_code:
    vda_send_connection_online()
    vda_publish_status()


def set_status_check(status):
  global result, num, action, parameter, default_value, success, unexpected, result_code, ACTION_PICK, STATE_IDLE, _unused, has_order, ACTION_DROP, STATE_PICKING, controllerid, current_status, ACTION_PROCESS, STATE_IDLE_WITH_STOCK, STATE_RESET, RESULT_PASSED, STATE_FAILED, STATE_PROCESSING, RESULT_FAILED, STATE_PICKING_DONE, actionCommand, MovementSpeed, STATE_PROCESSING_IDLE, PositionPASSED, PositionFAILED, PositionCamera, dubblepart
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


