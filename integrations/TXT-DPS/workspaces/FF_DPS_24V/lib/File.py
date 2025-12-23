# This file is probably not needed for the 24V version
import json
import logging
import os
import subprocess
import sys
from lib.DPS import *
from lib.VGR_Axes1Ref import *
from os.path import exists

_vgr = None
_dps = None
device_id = None
fileCalib = None
calib_data_VGR = None
file_device_id = None
calib_json = None
calib_data_DPS = None
device_id_json = None
calib_map = None


def loadFileFactoryCalib():
    global _vgr, _dps, device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    if exists('/opt/ft/workspaces/FactoryCalib.json'):
        logging.log(logging.DEBUG, 'load calibration values')
        readFileFactoryCalib()
    else:
        logging.log(logging.DEBUG, 'use default calibration values')
        writeFileFactoryCalib_defaults()
    #subprocess.Popen(['chown', 'ftgui:ftgui', '/opt/ft/workspaces/FactoryCalib.json'])
    subprocess.Popen(['chmod', '777', '/opt/ft/workspaces/FactoryCalib.json'])


def readDeviceIdFromFile():
    global _vgr, _dps, device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    if exists('/opt/ft/workspaces/deviceid.json'):
        file_device_id = open('/opt/ft/workspaces/deviceid.json', 'r', encoding='utf8')
        device_id = (json.loads(file_device_id.read()))['deviceId']
        file_device_id.close()
    else:
        file_device_id = open(os.path.join(os.path.dirname(__file__), '../data/config.json'), 'r', encoding='utf8')
        device_id_json = (json.loads(file_device_id.read()))['mqtt']
        device_id = device_id_json['deviceId']
        file_device_id.close()
        file_device_id = open('/opt/ft/workspaces/deviceid.json', 'w', encoding='utf8')
        file_device_id.write('{{"deviceId":"{}"}}'.format(device_id))
        file_device_id.close()
    if not device_id:
        sys.exit("deviceId for sps missing");
    return device_id


def readFileFactoryCalib():
    global _vgr, _dps, device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    fileCalib = open('/opt/ft/workspaces/FactoryCalib.json', 'r', encoding='utf8')
    calib_json = fileCalib.read()
    fileCalib.close()
    calib_map = json.loads(calib_json)
    #print(calib_map)
    try:
        calib_data_VGR = [calib_map['VGR']['poslist'], calib_map['VGR']['discard'], calib_map['VGR']['offset']]
        calib_data_DPS = [calib_map['DPS']['thresh_white_red'], calib_map['DPS']['thresh_red_blue']]
    except:
        logging.log(logging.DEBUG, 'wrong file format. use default calibration values')
        writeFileFactoryCalib_defaults()
        return
    printData()
    set_calib_data_VGR(calib_data_VGR)
    set_calib_data_DPS(calib_data_DPS)


def writeFileFactoryCalib(_vgr, _dps):
    global device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    calib_data_VGR = _vgr
    calib_data_DPS = _dps
    printData()
    calib_map = {\
    "VGR" : {\
    "poslist" : calib_data_VGR[0],\
    "discard" : calib_data_VGR[1],\
    "offset" : calib_data_VGR[2]\
    },\
    "DPS" : {\
    "thresh_white_red" : calib_data_DPS[0],\
    "thresh_red_blue" : calib_data_DPS[1]\
    }\
    }
    calib_json = json.dumps(calib_map)
    fileCalib = open('/opt/ft/workspaces/FactoryCalib.json', 'w', encoding='utf8')
    fileCalib.write(calib_json)
    fileCalib.close()


def printData():
    global _vgr, _dps, device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    print("VGR: ", calib_data_VGR)
    print("DPS: ", calib_data_DPS)


def writeFileFactoryCalib_current():
    global _vgr, _dps, device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    writeFileFactoryCalib(get_calib_data_VGR(), get_calib_data_DPS())


def writeFileFactoryCalib_defaults():
    global _vgr, _dps, device_id, fileCalib, calib_data_VGR, file_device_id, calib_json, calib_data_DPS, device_id_json, calib_map
    logging.log(logging.TRACE, '-')
    if exists('/opt/ft/workspaces/FactoryCalib.json'):
        fileCalib = open('/opt/ft/workspaces/FactoryCalib.json', 'r', encoding='utf8')
        calib_json = fileCalib.read()
        fileCalib.close()
        if False:
            #TODO: backup
            #save and write to USB Stick -> new buttons in GUI?
            fileCalib = open('/opt/ft/workspaces/FactoryCalib_backup.json', 'w', encoding='utf8')
            fileCalib.write(calib_json)
            fileCalib.close()
    writeFileFactoryCalib(get_calib_data_VGR_defaults(), get_calib_data_DPS_defaults())


