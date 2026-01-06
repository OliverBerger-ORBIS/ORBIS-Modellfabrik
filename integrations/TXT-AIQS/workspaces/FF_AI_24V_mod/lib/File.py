import json
import os
import sys
from os.path import exists

device_id = None
file_device_id = None
device_id_json = None


def readDeviceIdFromFile():
  global device_id, file_device_id, device_id_json
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
    file_device_id.write('{{"deviceId":"{}"}}'.format(device_id) + '\n')
    file_device_id.close()
  if not device_id:
    sys.exit("deviceId for sps missing")
  return device_id


