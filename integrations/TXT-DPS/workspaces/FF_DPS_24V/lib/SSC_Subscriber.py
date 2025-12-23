import json
import logging
import time
from datetime import datetime
from datetime import timezone
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.Factory_Variables import *
from lib.Time import *

mqttclient = None
ldr_period = None
camera_fps = None
keep_alive_timestamp = None
bme680_period = None
camera_on = None
msgk = None


def setup_input_from_dashboard(mqttclient):
    global ldr_period, camera_fps, keep_alive_timestamp, bme680_period, camera_on, msgk
    mqttclient.subscribe(topic='/j1/txt/1/c/bme680', callback=bme680_period_callback, qos=2)
    mqttclient.subscribe(topic='/j1/txt/1/c/ldr', callback=ldr_period_callback, qos=2)
    mqttclient.subscribe(topic='/j1/txt/1/c/cam', callback=cam_period_callback, qos=2)
    mqttclient.subscribe(topic='/j1/txt/1/c/broadcast', callback=broadcast_period_callback, qos=2)


def bme680_period_callback(message):
    global mqttclient, ldr_period, camera_fps, keep_alive_timestamp, bme680_period, camera_on, msgk
    print('------------------------------------------------------ ldr änderung')
    # logging.log(logging.TRACE_FCL, '-')
    if (get_init_finished()) and not not len(message.payload.decode("utf-8")):
        msg = json.loads(message.payload.decode("utf-8"))
        bme680_period = msg['period']
        set_bme680_period(bme680_period)



def ldr_period_callback(message):
    global mqttclient, ldr_period, camera_fps, keep_alive_timestamp, bme680_period, camera_on, msgk
    # logging.log(logging.TRACE_FCL, '-')
    if (get_init_finished()) and not not len(message.payload.decode("utf-8")):
        msg= json.loads(message.payload.decode("utf-8"))
        ldr_period = msg['period']
        set_ldr_period(ldr_period)



def cam_period_callback(message):
    global mqttclient, ldr_period, camera_fps, keep_alive_timestamp, bme680_period, camera_on, msgk
    # logging.log(logging.TRACE_FCL, '-')
    if (get_init_finished()) and not not len(message.payload.decode("utf-8")):
        msg= json.loads(message.payload.decode("utf-8"))
        camera_fps = msg['fps']
        camera_on = msg['on']
        set_camera_fps(camera_fps)
        set_camera_on(camera_on)



def broadcast_period_callback(message):
    global mqttclient, ldr_period, camera_fps, keep_alive_timestamp, bme680_period, camera_on, msgk
    # logging.log(logging.TRACE_FCL, '-')
    set_cloud_active(True)
    if keep_alive_timestamp == None:
        # logging.log(logging.DEBUG_FCL, 'set keep alive value')
        set_keep_alive(time.time())
    if (get_init_finished()) and not not len(message.payload.decode("utf-8")):
        msg= json.loads(message.payload.decode("utf-8"))
        last_msg = msg["ts"]
        msgk = msg["message"]
        if msgk == 'keep-alive':
            set_keep_alive(to_datetime_utc(last_msg).timestamp())



