import json
import os
import sys
import threading
import time
from lib.controller import *
from lib.display import *
from lib.Factory_Variables import *
from lib.iw_log import *
from lib.Log import *
from lib.mqtt_utils import *
from lib.net_utils import *
from lib.RemoteGateway import *
from lib.Time import *

temp_file = None
temp = None


def vda_get_factsheet_version():
    global temp_file, temp
    temp_file = open(os.path.join(os.path.dirname(__file__), 'data/factsheet.json'), 'r', encoding='utf8')
    temp = (json.loads(temp_file.read()))['version']
    temp_file.close()
    return temp


display.set_attr("txt_label_version.text", str('<h3>APS CGW (Version: {})</h3>'.format(vda_get_factsheet_version())))
display.set_attr("txt_label_message.text", str(''))
display.set_attr("txt_label_message2.text", str(''))
initlib_log(9)
print('Starting threads')
gateway_setup()
while True:
    time.sleep(0.5)
