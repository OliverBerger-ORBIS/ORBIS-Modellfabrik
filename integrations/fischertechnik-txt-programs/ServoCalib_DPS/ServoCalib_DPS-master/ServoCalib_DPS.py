import json
import subprocess
import time
from datetime import datetime
from os.path import exists

from lib.controller import *
from lib.display import *

deg = None
target_pos_s1 = None
target_pos_s2 = None
target_pos_s3 = None
fileCalib = None
calib_json = None
s_step = None
calib_map = None


def writeCalib():
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    print('writeCalib')
    subprocess.Popen(['chmod', '777', '/opt/ft/workspaces/ServoCalib_DPS.json'])
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    calib_map = {
        "ts": ts,
        "servo_degree_S1": get_degree_offset_S1(),
        "servo_degree_S2": get_degree_offset_S2(),
        "servo_degree_S3": get_degree_offset_S3(),
    }
    print(calib_map)
    calib_json = json.dumps(calib_map)
    fileCalib = open('/opt/ft/workspaces/ServoCalib_DPS.json', 'w', encoding='utf8')
    fileCalib.write(calib_json)
    fileCalib.close()


def readCalib():
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    print('readCalib')
    fileCalib = open('/opt/ft/workspaces/ServoCalib_DPS.json', encoding='utf8')
    calib_json = fileCalib.read()
    fileCalib.close()
    calib_map = json.loads(calib_json)
    print(calib_map)
    target_pos_s1 = int(degree2raw(float(calib_map['servo_degree_S1'])))
    target_pos_s2 = int(degree2raw(float(calib_map['servo_degree_S2'])))
    target_pos_s3 = int(degree2raw(float(calib_map['servo_degree_S3'])))
    print(target_pos_s1, target_pos_s2, target_pos_s3)
    display.set_attr("txt_slider_s1.value", str(target_pos_s1))
    display.set_attr("txt_slider_s2.value", str(target_pos_s2))
    display.set_attr("txt_slider_s3.value", str(target_pos_s3))


def degree2raw(deg):
    global target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    return deg * (512 / 180)


def on_txt_button_save_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    writeCalib()
    TXT_M.get_loudspeaker().play("06_Car_horn_short.wav", False)
    while True:
        if not (TXT_M.get_loudspeaker().is_playing()):
            break
        time.sleep(0.010)


def get_degree_offset_S1():
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    return (TXT_M_S1_servomotor.get_position()) * (180 / 512)


def get_degree_offset_S2():
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    return (TXT_M_S2_servomotor.get_position()) * (180 / 512)


def get_degree_offset_S3():
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    return (TXT_M_S3_servomotor.get_position()) * (180 / 512)


def on_txt_slider_s1_moved(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    target_pos_s1 = int(event['value'])


def on_txt_slider_s2_moved(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    target_pos_s2 = int(event['value'])


def on_txt_slider_s3_moved(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    target_pos_s3 = int(event['value'])


def on_txt_button_minus1_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    if target_pos_s1 > 0:
        target_pos_s1 = target_pos_s1 - s_step
        display.set_attr("txt_slider_s1.value", str(target_pos_s1))


def on_txt_button_plus1_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    if target_pos_s1 < 512:
        target_pos_s1 = target_pos_s1 + s_step
        display.set_attr("txt_slider_s1.value", str(target_pos_s1))


def on_txt_button_minus2_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    if target_pos_s2 > 0:
        target_pos_s2 = target_pos_s2 - s_step
        display.set_attr("txt_slider_s2.value", str(target_pos_s2))


def on_txt_button_plus2_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    if target_pos_s2 < 512:
        target_pos_s2 = target_pos_s2 + s_step
        display.set_attr("txt_slider_s2.value", str(target_pos_s2))


def on_txt_button_minus3_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    if target_pos_s3 > 0:
        target_pos_s3 = target_pos_s3 - s_step
        display.set_attr("txt_slider_s3.value", str(target_pos_s3))


def on_txt_button_plus3_clicked(event):
    global deg, target_pos_s1, target_pos_s2, target_pos_s3, fileCalib, calib_json, s_step, calib_map
    if target_pos_s3 < 512:
        target_pos_s3 = target_pos_s3 + s_step
        display.set_attr("txt_slider_s3.value", str(target_pos_s3))


display.button_clicked("txt_button_save", on_txt_button_save_clicked)
display.slider_moved("txt_slider_s1", on_txt_slider_s1_moved)
display.slider_moved("txt_slider_s2", on_txt_slider_s2_moved)
display.slider_moved("txt_slider_s3", on_txt_slider_s3_moved)
display.button_clicked("txt_button_minus1", on_txt_button_minus1_clicked)
display.button_clicked("txt_button_plus1", on_txt_button_plus1_clicked)
display.button_clicked("txt_button_minus2", on_txt_button_minus2_clicked)
display.button_clicked("txt_button_plus2", on_txt_button_plus2_clicked)
display.button_clicked("txt_button_minus3", on_txt_button_minus3_clicked)
display.button_clicked("txt_button_plus3", on_txt_button_plus3_clicked)


target_pos_s1 = 256
target_pos_s2 = 256
target_pos_s3 = 256
# set servo, needed for get servo blocks
TXT_M_S1_servomotor.set_position(int(target_pos_s1))
TXT_M_S2_servomotor.set_position(int(target_pos_s2))
TXT_M_S3_servomotor.set_position(int(target_pos_s3))
s_step = 1
if exists('/opt/ft/workspaces/ServoCalib_DPS.json'):
    readCalib()
else:
    writeCalib()
print("init: ", target_pos_s1, target_pos_s2, target_pos_s3)
while True:
    TXT_M_S1_servomotor.set_position(int(min(max(target_pos_s1, 0), 512)))
    TXT_M_S2_servomotor.set_position(int(min(max(target_pos_s2, 0), 512)))
    TXT_M_S3_servomotor.set_position(int(min(max(target_pos_s3, 0), 512)))
    display.set_attr("txt_label_s1_value.text", str(target_pos_s1))
    display.set_attr("txt_label_s1_value2.text", str(f'{get_degree_offset_S1():.1f}'))
    display.set_attr("txt_label_s2_value.text", str(target_pos_s2))
    display.set_attr("txt_label_s2_value2.text", str(f'{get_degree_offset_S2():.1f}'))
    display.set_attr("txt_label_s3_value.text", str(target_pos_s3))
    display.set_attr("txt_label_s3_value2.text", str(f'{get_degree_offset_S3():.1f}'))
    time.sleep(0.3)
