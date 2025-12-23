import base64
import cv2
import datetime
import numpy as np
import subprocess
import time
from datetime import datetime
from fischertechnik.camera.VideoStream import VideoStream
from fischertechnik.machine_learning.ObjectDetector import ObjectDetector
from lib.camera import *
from lib.controller import *
from lib.display import *
from lib.node_red import *

tag = None
value = None
num = None
color = None
ts = None
filename = None
sat = None
hue = None
duration = None
prob = None
keytext = None
pos = None
frame = None
detector = None
result = None
key = None


def on_txt_button_clicked(event):
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    display.set_attr("part_pass_fail.text", str(containInHTML('i', 'processing')))
    print(MakePictureRunKiReturnFoundPart())


def reset_inteface():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    display.set_attr("part_pass_fail.text", str(containInHTML('i', 'Not analysed yet')))
    display.set_attr("green.active", str(False).lower())
    display.set_attr("red.active", str(False).lower())


def containInHTML(tag, value):
    global num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    return ''.join([str(x) for x in ['<', tag, '>', value, '</', tag, '>']])


def MakePictureRunKiReturnFoundPart():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    reset_inteface()
    TXT_SLD_M_O4_led.set_brightness(int(512))
    time.sleep(0.2)
    TXT_SLD_M_O4_led.set_brightness(int(130))
    time.sleep(0.8)
    duration = (time.time() * 1000)
    num = 4
    prob = 0
    keytext = 'No feature found'
    pos = ''
    display.set_attr("part_pass_fail.text", str(containInHTML('i', 'processing')))
    frame = TXT_SLD_M_USB1_1_camera.read_frame()
    #get color from frame
    color = (np.mean(frame[ 80:120,  100:240], axis=(0, 1)))
    color = cv2.cvtColor(np.uint8([[[color[0],color[1],color[2]]]]),cv2.COLOR_BGR2HLS)[0][0]
    hue = color[0] # range 0-180
    sat = color[2] # range 0-255
    detector = ObjectDetector('/opt/ft/workspaces/machine-learning/object-detection/sorting_line/model.tflite', '/opt/ft/workspaces/machine-learning/object-detection/sorting_line/labels.txt')
    result = detector.process_image(frame)
    color = get_color()
    TXT_SLD_M_O4_led.set_brightness(int(0))
    print(result)
    if len(result) > 0:
        prob = result[0]['probability']
        pos = result[0]['position']
        key = result[0]['label']
        keytext = ''
        if key == 'CRACK':
            keytext = 'Cracks in Workpiece'
        elif key == 'MIPO1':
            keytext = '1x milled pocket'
        elif key == 'MIPO2':
            keytext = '2x milled pocket'
        elif key == 'BOHO':
            keytext = 'Round hole'
        elif key == 'BOHOEL':
            keytext = 'Hole elyptical'
        elif key == 'BOHOMIPO1':
            keytext = 'Hole and 1x milled pocket'
        elif key == 'BOHOMIPO2':
            keytext = 'Hole and 2x milled pocket'
        elif key == 'BLANK':
            keytext = 'Workpiece without features'
        else:
            keytext = key
        print('{} {} {} {} {} {}'.format(key, keytext, num, prob, pos, color))
        if key == 'BOHO' and color == 1:
            num = 1
            display.set_attr("green.active", str(True).lower())
        elif key == 'MIPO2' and color == 2:
            num = 2
            display.set_attr("green.active", str(True).lower())
        elif key == 'BOHOMIPO2' and color == 3:
            num = 3
            display.set_attr("green.active", str(True).lower())
        else:
            num = 4
            display.set_attr("red.active", str(True).lower())
    else:
        display.set_attr("red.active", str(True).lower())
    duration = (time.time() * 1000) - duration
    saveFileandPublish()
    display.set_attr("part_pass_fail.text", str(containInHTML('i', '')))
    return num


def get_color():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    if hue >= 85 and hue < 130 and sat >= 40:
        color = 3
    elif (hue >= 130 and hue <= 180 or hue >= 0 and hue < 15) and sat >= 40:
        color = 2
    else:
        color = 1
    return color


def timestamp():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return ts


def saveFileandPublish():
    global tag, value, num, color, ts, filename, sat, hue, duration, prob, keytext, pos, frame, detector, result, key
    filename = '/opt/ft/workspaces/last-image.png'
    print(filename)
    if(pos != ""):
        image = cv2.rectangle(frame, (pos[0], pos[1]), (pos[2], pos[3]), (180,105,0), 2)
    # logging.debug("write png file: ", filename)
    cv2.imwrite(filename, frame)
    subprocess.Popen(['chmod', '777', filename])

    with open(filename, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    imgb64 = "data:image/jpeg;base64," + (my_string.decode('utf-8'))
    time.sleep(0.2)
    displaystr= "<img width='185' height='139' src='" +  imgb64  + "'>"
    display.set_attr("img_label.text", str(displaystr))


display.button_clicked("txt_button", on_txt_button_clicked)


