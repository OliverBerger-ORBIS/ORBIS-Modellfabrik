import base64
import cv2
import fischertechnik.utility.math as ft_math
import json
import logging
import math
import os
import time
from datetime import datetime
from lib.Axes1Ref import *
from lib.camera import *
from lib.controller import *
from lib.Factory_Variables import *
from lib.mqtt_utils import *
from lib.Time import *

_tr0 = None
_tr = None
_dg = None
message = None
camera_image = None
payload_bme680 = None
payload_ldr = None
payload_cam = None
payload_broadcast = None
pos_pan = None
rel_pan = None
rel_tilt = None
pos_tilt = None
last_humidity_alarm = None
last_movement_alarm = None
last_temperature_alarm = None
controller_name = None
limit_pan = None
limit_tilt = None


def initlog_FCL(_tr0, _tr, _dg):
    global message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    logging.TRACE0_FCL = _tr0
    logging.addLevelName(logging.TRACE0_FCL , 'TRACE0_FCL')
    logging.TRACE_FCL = _tr
    logging.addLevelName(logging.TRACE_FCL , 'TRACE_FCL')
    logging.DEBUG_FCL = _dg
    logging.addLevelName(logging.DEBUG_FCL, 'DEBUG_FCL')


def start_publish_threads_sensoric():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    set_bme680_period(5)
    set_ldr_period(5)
    set_camera_fps(1)
    set_cloud_active(True)
    set_camera_on(True)
    set_init_finished(True)
    threading.Thread(target=publish_bme680, daemon=True).start()
    threading.Thread(target=publish_ldr, daemon=True).start()
    threading.Thread(target=publish_camera, daemon=True).start()
    threading.Thread(target=publish_broadcast, args=('init', ), daemon=True).start()


def publish_bme680():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    while True:
        payload_bme680 = '{{"ts":"{}","t":{:.1f},"rt":{:.1f},"h":{:.1f},"rh":{:.1f},"p":{:.1f},"iaq":{},"aq":{},"gr":{}}}'.format(timestamp_utcnow(), (TXT_M_I2C_1_environment_sensor.get_temperature()) - 4, 0, TXT_M_I2C_1_environment_sensor.get_humidity(), 0, TXT_M_I2C_1_environment_sensor.get_pressure(), TXT_M_I2C_1_environment_sensor.get_indoor_air_quality_as_number(), TXT_M_I2C_1_environment_sensor.get_accuracy(), 0)
        mqtt_publish('/j1/txt/1/i/bme680', payload_bme680)
        time.sleep((get_bme680_period()))


def publish_ldr():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    while True:
        payload_ldr = '{{"ts":"{}", "br":{:.1f}, "ldr":{}}}'.format(timestamp_utcnow(), round((65000 - TXT_M_I4_photo_resistor.get_resistance()) / 650, 1), TXT_M_I4_photo_resistor.get_resistance())
        mqtt_publish('/j1/txt/1/i/ldr', payload_ldr)
        time.sleep((get_ldr_period()))


def publish_camera():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    logging.log(logging.TRACE_FCL, '-')
    camera_image = []
    while True:
        if not not len(camera_image):
            if get_camera_on():
                payload_cam = '{{"ts":"{}","data":"{}"}}'.format(timestamp_utcnow(), frame_to_base64(camera_image))
                mqtt_publish('/j1/txt/1/i/cam', payload_cam)
        time.sleep((1 / (get_camera_fps())))


def callback(event):
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    if TXT_M_I2C_1_environment_sensor.get_humidity() > 80:
        # logging.log(logging.TRACE0_FCL, '-')
        if time.time() - last_humidity_alarm >= (get_alarm_timer()):
            publish_humidity_alarm()
            last_humidity_alarm = time.time()



def image_callback(event):
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    camera_image = event.value


def motion_callback(event):
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    # logging.log(logging.TRACE0_FCL, '-')
    if last_movement_alarm != None:
        if time.time() - last_movement_alarm >= (get_alarm_timer()):
            publish_movement_alarm()
            last_movement_alarm = time.time()


def callback2(event):
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    if TXT_M_I2C_1_environment_sensor.get_temperature() < 4:
        logging.log(logging.TRACE0_FCL, '-')
        if time.time() - last_temperature_alarm >= (get_alarm_timer()):
            publish_temperature_alarm()
            last_temperature_alarm = time.time()



def publish_movement_alarm():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    logging.log(logging.TRACE_FCL, '-')
    mqtt_publish('/j1/txt/1/i/alert', '{{"ts":"{}","id":"{}","data":"{}","code":{}}}'.format(timestamp_utcnow(), 'cam', frame_to_base64(camera_image), '100'))


def publish_temperature_alarm():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    logging.log(logging.TRACE_FCL, '-')
    mqtt_publish('/j1/txt/1/i/alert', '{{"ts":"{}","id":"{}","data":"{}","code":{}}}'.format(timestamp_utcnow(), 'bme680/t', TXT_M_I2C_1_environment_sensor.get_temperature(), '200'))


def publish_humidity_alarm():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    logging.log(logging.TRACE_FCL, '-')
    mqtt_publish('/j1/txt/1/i/alert', '{{"ts":"{}","id":"{}","data":"{}","code":{}}}'.format(timestamp_utcnow(), 'bme680/t', TXT_M_I2C_1_environment_sensor.get_temperature(), '200'))


def publish_broadcast(message):
    global _tr0, _tr, _dg, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    logging.log(logging.TRACE_FCL, '-')
    controller_name = os.uname()[1]
    payload_broadcast = '{{"ts":"{}","hardwareId":"{}","hardwareModel":"{}","softwareName":"{}","softwareVersion":"{}","message":"{}"}}'.format(timestamp_utcnow(), controller_name, 'TXT 4.0', 'APS', get_version(), message)
    mqtt_publish('/j1/txt/1/i/broadcast', payload_broadcast)


def publish_ptu_pos():
    global _tr0, _tr, _dg, message, camera_image, payload_bme680, payload_ldr, payload_cam, payload_broadcast, pos_pan, rel_pan, rel_tilt, pos_tilt, last_humidity_alarm, last_movement_alarm, last_temperature_alarm, controller_name, limit_pan, limit_tilt
    # logging.log(logging.TRACE_FCL, '-')
    pos_pan = 0
    pos_tilt = 0
    if pos_pan != None and pos_tilt != None:
        limit_pan = (get_ABSLIMIT())[3]
        limit_tilt = (get_ABSLIMIT())[4]
        rel_pan = (ft_math.map(pos_pan, 0, limit_pan, 0, 200) - 100) / 100
        rel_tilt = (ft_math.map(pos_tilt, 0, limit_tilt, 0, 200) - 100) / 100
        logging.log(logging.DEBUG_FCL, '%d (%d) %d (%d) %f %f', pos_pan, limit_pan, pos_tilt, limit_tilt, rel_pan, rel_tilt)
        print('publish_ptu_pos', pos_pan, limit_pan, pos_tilt, limit_tilt, rel_pan, rel_tilt)
        mqtt_publish('/j1/txt/1/i/ptu/pos', '{{"ts":"{}", "pan":{:.2f}, "tilt":{:.2f}}}'.format(timestamp_utcnow(), rel_pan, rel_tilt))


TXT_M_I2C_1_environment_sensor.add_change_listener("humidity", callback)
TXT_M_USB1_1_camera.add_change_listener("image", image_callback)
TXT_M_I2C_1_environment_sensor.add_change_listener("temperature", callback2)

motion_detector.add_detection_listener(motion_callback)

def frame_to_base64(frame):
        result = ""
        success, image = cv2.imencode(".jpeg", frame, [1, 30])
        if success:
                result = "data:image/jpeg;base64," + base64.b64encode(image).decode("utf-8")
        return result

