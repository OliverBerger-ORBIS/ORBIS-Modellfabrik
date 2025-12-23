import json
import time
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.Nfc import *

mqtt_client = None
nfc_order = None
gateway_local_mqtt = None
nfc_content = None
workpieceId = None
state_content = None
type_content = None
ts = None
nfc_delete_res = None
response_to_broker = None
def nfc_commands_handler(nfc_order):
    global mqtt_client, gateway_local_mqtt, nfc_content, workpieceId, state_content, type_content, ts, nfc_delete_res, response_to_broker
    nfc_content = None
    nfc_order = nfc_order.get("cmd")
    if nfc_order == 'read' or nfc_order == 'delete':
        nfc_content = nfc_read()
        workpieceId = None
        state_content = None
        type_content = None
        ts = (time.time() * 1000)
        workpieceId = nfc_content[0]
        state_content = nfc_content[1]
        type_content = nfc_content[2]
        if nfc_order == 'read':
            print('----------------------- read content -----------------------')
        elif nfc_order == 'delete':
            print('----------------------- delete content -----------------------')
            nfc_delete_res = nfc_write(state_content, type_content, 0, [0] * 8)
        print('----------------------- NFC data -----------------------')
        print_nfc_data()
        # in CCU
        # In Delivery                    = 100  --> ModuleType.DPS and command ModuleCommandType.DROP
        # Quality Assurance      = 200  --> ModuleType.AIQS and command ModuleCommandType.CHECK_QUALITY
        # Stockpiling                   = 300  --> ModuleType.HBW and command ModuleCommandType.PICK
        # Stock removal             = 400  --> ModuleType.HBW and command ModuleCommandType.DROP
        # Processing Furnace   = 500  --> ModuleType.FURNACE and command ModuleCommandType.FIRE
        # Processing Mill           = 600  --> ModuleType.MILL and command ModuleCommandType.MILL
        # Processing Drill          = 700  --> ModuleType.DRILL and command ModuleCommandType.DRILL
        # Shipping                       = 800  --> ModuleType.DPS and command ModuleCommandType.PICK

        # on Chip
        # nfc_content[4][0] = "Anlieferung Rohware"
        # nfc_content[4][1] = "Qualitätskontrolle"
        # nfc_content[4][2] = "Einlagerung"
        # nfc_content[4][3] = "Auslagerung"
        # nfc_content[4][4] = "Bearbeitung Brennofen"
        # nfc_content[4][5] = "Bearbeitung Fräse"
        # nfc_content[4][6] = "Bearbeitung Bohren"
        # nfc_content[4][7] = "Versand Ware"

        # for UI
        # 100 = "Anlieferung Rohware"
        # 700 = "Qualitätskontrolle"
        # 300 = "Einlagerung"
        # 400 = "Auslagerung"
        # 500 = "Bearbeitung Brennofen"
        # 600 = "Bearbeitung Fräse"
        # 601 = "Bearbeitung Bohren"
        # 800 = "Versand Ware"


        history = []
        response_to_broker = {}
        if nfc_order != "delete":
            i = 0
            while i<8:
                if nfc_content[4][i] != 0.0 and nfc_content[4][i] != None:
                    if i == 1:
                        history.append({"ts": int(nfc_content[4][i])*1000, "code": 700})
                    elif i == 6:
                        history.append({"ts": int(nfc_content[4][i])*1000, "code": 601})
                    else:
                        history.append({"ts": int(nfc_content[4][i])*1000, "code": (i+1)*100})
                i+=1
            history.sort(key=lambda el: el["ts"])

        workpieceId = nfc_content[0]
        state_content = nfc_content[1]
        type_content = nfc_content[2]
        state = "NONE"

        if state_content == 1:
            state = "PROCESSED"
        elif state_content == 2:
            state = "REJECTED"
        elif state_content == 0:
            state = "RAW"
        else:
            state = "NONE"

        if type_content == 1:
            color = "WHITE"
        elif type_content == 2:
            color = "RED"
        elif type_content == 3:
            color = "BLUE"
        else:
            color = "NONE"

        response_to_broker = {
            "ts" : ts,
            "workpiece" : {
                "id" :workpieceId,
                "state" : state,
                "type" : color
            },
            "history":history
        }
        gateway_local_mqtt.publish(topic='/j1/txt/1/f/i/nfc/ds', payload=json.dumps(response_to_broker), qos=2, retain=False)
        print('----------------------- MQTT End -----------------------')
    else:
        print('----------------------- MQTT ORDER NOT DEFINED -----------------------')



def nfc_commands_setup(mqtt_client):
    global nfc_order, gateway_local_mqtt, nfc_content, workpieceId, state_content, type_content, ts, nfc_delete_res, response_to_broker
    gateway_local_mqtt = mqtt_client
    mqtt_client.subscribe(topic='/j1/txt/1/f/o/nfc/ds', callback=nfc_commands_callback, qos=2)


def nfc_commands_callback(message):
    global mqtt_client, nfc_order, gateway_local_mqtt, nfc_content, workpieceId, state_content, type_content, ts, nfc_delete_res, response_to_broker
    nfc_commands_handler(json.loads(message.payload.decode("utf-8")))



