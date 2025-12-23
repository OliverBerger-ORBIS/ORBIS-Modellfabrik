import atexit
import datetime
import json
import os
import signal
import sys
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.mqtt_utils import *
from lib.net_utils import *

valid_actions = None
ts = None
error = None
order = None
color = None
uid = None
action = None
result = None
status = None
orderId = None
_unused_a = None
_unused_b = None
instant = None
allowed_actions = None
infoType = None
value = None
infoLevel = None
infoReferences = None
vda_data = None
orderTopic = None
temp_file = None
temp = None
instantActionTopic = None
vda_valid_actions = None
vda_namespace = None
information = None
vda_temp = None


def vda_init(valid_actions):
    global ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_data = json.loads('{"stateId": 0, "orderId": "", "orderUpdateId": 0, "lastOrderId": "", "lastOrderTimestamp": 0, "actions":[], "errors": []}')
    vda_valid_actions = valid_actions
    vda_namespace = 'module/v1/ff/NodeRed/{}/'.format(mqtt_get_id())
    information = json.loads('{}')


def vda_publish_status():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_temp = {}
    vda_data["stateId"] = vda_data["stateId"] + 1
    vda_temp["operatingMode"] = "TEACHIN" if vda_data.get("teachin") else "AUTOMATIC"
    vda_temp["headerId"] = vda_data["stateId"]
    vda_temp["timestamp"] = vda_timestamp()
    vda_temp["serialNumber"] = mqtt_get_id()
    vda_temp["orderId"] = vda_data["lastOrderId"]
    vda_temp["orderUpdateId"] = vda_data["orderUpdateId"]
    vda_temp["paused"] = vda_data.get("teachin", False) == True
    vda_temp["actionState"] = None
    vda_temp["actionStates"] = vda_data["actions"]

    print("Publishing state update")

    print(vda_data)

    for _action in vda_data["actions"]:
        if not vda_temp["actionState"] or (_action["state"] != "WAITING" and _action["command"] != "factsheetRequest"):
            vda_temp["actionState"] =  {
                    "command": _action["command"],
                    "id": _action.get("id"),
                    "state":  _action["state"],
                    "timestamp": _action.get("timestamp", vda_timestamp())
                }
            if "result" in _action:
                vda_temp["actionState"]["result"] = _action.get("result")
    vda_temp["batteryState"] = {}
    vda_temp["errors"] = vda_data["errors"]
    for _action in vda_data["actions"]:
        if _action["state"] == "FAILED":
            vda_temp["errors"].append({
                "errorType": _action["command"] + "_error",
                "timestamp": _action.get("timestamp", vda_timestamp()),
                "errorLevel":  "WARNING" if _action.get("warning") else "FATAL"
            })
            if "result" in _action:
                _action_state["result"] = _action.get("result")
    vda_temp["information"] = list(information.values())
    mqtt_get_client().publish(topic=str(vda_namespace) + 'state', payload=json.dumps(vda_temp), qos=2, retain=True)


def vda_timestamp():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def vda_parse_timestamp(ts):
    global valid_actions, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def vda_set_warning(error):
    global valid_actions, ts, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_data["errors"].append({
        "errorType": error,
        "timestamp": vda_timestamp(),
        "errorLevel":  "WARNING"
    })


def vda_status_failed():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    return 'FAILED'


def vda_status_initializing():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    return 'INITIALIZING'


def vda_status_running():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    return 'RUNNING'


def vda_status_finished():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    return 'FINISHED'


def vda_process_order(order):
    global valid_actions, ts, error, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_data["errors"] = []
    print('Handling incoming order')
    try:
        order = json.loads(order)
    except:
        order = {} # the following check will send an error

    print(order)
    if not ("orderId" in order and "timestamp" in order and "action" in order ):
        vda_data["errors"].append({
            "errorType": "validationError",
            "errorLevel": "WARNING",
            "errorReferences": [
                { "topic": "order" } ,
                { "headerId": order.get("headerId") } ,
                { "orderId": order.get("orderId") } ,
                { "orderUpdateId": order.get("orderUpdateId") }
            ]
        })
        return False

    if (order["orderId"] == vda_data["lastOrderId"]):
        if order.get("orderUpdateId", 0) < vda_data["orderUpdateId"]:
            # send errors when update ID is older than our current update ID
            vda_data["errors"].append({
                "errorType": "orderUpdateError",
                "errorLevel": "WARNING",
                "errorReferences": [
                    { "topic": "order" } ,
                    { "headerId": order.get("headerId") } ,
                    { "orderId": order.get("orderId") } ,
                    { "orderUpdateId": order.get("orderUpdateId") }
                ]
            })
            return False
        elif order.get("orderUpdateId", 0) == vda_data["orderUpdateId"]:
            # ignore duplicate orders
            return True

    _orderErrors=[]
    if vda_data["orderId"]:
        # An order is already in progress, we cannot accept a second order or an update
        _orderErrors.append("")

    if order.get("zoneSetId"):
        _orderErrors.append("zoneSetId")

    if len(_orderErrors):
         vda_data["errors"].append({
            "errorType": "orderError",
            "errorLevel": "WARNING",
            "errorReferences": [
               { "topic": "order" } ,
                { "headerId": order.get("headerId") } ,
                { "orderId": order.get("orderId") } ,
                { "orderUpdateId": order.get("orderUpdateId") }
            ] + [ {i, order.get(i)} for i in _orderErrors if i ]
        })


    _action = order["action"]

    if _action.get("command") not in vda_valid_actions:
        vda_data["errors"].append({
            "errorType": "orderError",
            "errorLevel": "WARNING",
            "errorReferences": [
                { "topic": "order" } ,
                { "headerId": order.get("headerId") } ,
                { "orderId": order.get("orderId") } ,
                { "orderUpdateId": order.get("orderUpdateId") },
                { "actionId": _action.get("id") },
                { "actionCommand": _action.get("command") },
            ]
        })
        return False

    vda_data["orderId"] = order["orderId"]
    vda_data["orderUpdateId"] = order.get("orderUpdateId", 0)
    vda_data["lastOrderId"] = order["orderId"]
    vda_data["lastOrderTimestamp"] = order["timestamp"]

    _action["state"] = "WAITIING"
    _action["timestamp"] = vda_timestamp()

    vda_data["actions"] = [_action]

    return True


def vda_publish_order(color, uid):
    global valid_actions, ts, error, order, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_temp = {}

    vda_temp["timestamp"] = vda_timestamp()
    vda_temp["type"] = color
    vda_temp["workpieceId"] = uid
    vda_temp["orderType"] = "STORAGE"
    mqtt_get_client().publish(topic='ccu/order/request', payload=json.dumps(vda_temp), qos=2, retain=False)


def vda_get_order_topic():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    orderTopic = str(vda_namespace) + 'order'
    print(orderTopic)
    return orderTopic


def vda_get_action():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    for _action in vda_data["actions"]:
        if _action["state"] == "FAILED":
            return None
        if _action["state"] != "FINISHED":
            return _action
    return None


def vda_set_action_result(action, result):
    global valid_actions, ts, error, order, color, uid, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    if not action:
        return
    action["result"] = result



def vda_set_action_status(action, status):
    global valid_actions, ts, error, order, color, uid, result, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    action["state"] = status
    action["timestamp"] = vda_timestamp()
    if status == "FAILED":
        _found = False
        for _action in vda_data["actions"]:
            if _action["id"] == action["id"] and _action["command"] == action["command"]:
                _found = True
            if _found == True:
                _action["state"] = "FAILED"
    if not vda_get_action():
        vda_data["orderId"] = None
    vda_publish_status()


def vda_assign_order(orderId):
    global valid_actions, ts, error, order, color, uid, action, result, status, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_data["errors"] = []
    vda_data["orderId"] = ""
    vda_data["orderUpdateId"] = -1
    vda_data["lastOrderId"] = orderId
    vda_data["lastOrderTimestamp"] = vda_timestamp()
    vda_data["actions"] = []


def vda_is_order_active():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    return not not vda_data["orderId"]


# registers a message to send when exiting the program
# and requests the broker to publish a message when connection is lost
#
# has to be called before connecting to the mqtt broker
def vda_setup_offline_notifications():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    mqtt_get_client().will_set(topic=str(vda_namespace) + 'connection', payload='{{ "headerId": {}, "timestamp": "{}", "version": "{}", "manufacturer": "{}", "serialNumber": "{}", "connectionState": "{}", "ip": "{}"  }}'.format(1, vda_timestamp(), vda_get_factsheet_version(), 'Fischertechnik', mqtt_get_id(), 'CONNECTIONBROKEN', get_ip()), qos=1, retain=True)
    # atexit will be called when the program is stopped with the button on the touchscreen
    atexit.register(vda_send_connection_offline)

    # handle stopping by system shutdown as well
    signal.signal(signal.SIGINT, _vda_handle_signals_int_term)
    signal.signal(signal.SIGTSTP, _vda_handle_signals_int_term)
    signal.signal(signal.SIGTERM, _vda_handle_signals_int_term)


def _vda_handle_signals_int_term(_unused_a, _unused_b):
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    # Handle termination signals gracefully
    # The signal handler is called with two arguments, but this implmentation does not use them.
    # sys.exit will call the function registered with atexit.register(vda_send_connection_offline)
    sys.exit(0)


# publishes the online status
def vda_send_connection_online():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    print('Sending online status')
    mqtt_get_client().publish(topic=str(vda_namespace) + 'connection', payload='{{ "headerId": {}, "timestamp": "{}", "version": "{}", "manufacturer": "{}", "serialNumber": "{}", "connectionState": "{}", "ip": "{}" }}'.format(2, vda_timestamp(), vda_get_factsheet_version(), 'Fischertechnik', mqtt_get_id(), 'ONLINE', get_ip()), qos=1, retain=True)


def vda_send_connection_offline():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    print('Shutting down')
    mqtt_get_client().publish(topic=str(vda_namespace) + 'connection', payload='{{ "headerId": {}, "timestamp": "{}", "version": "{}", "manufacturer": "{}", "serialNumber": "{}", "connectionState": "{}", "ip": "{}"  }}'.format(3, vda_timestamp(), vda_get_factsheet_version(), 'Fischertechnik', mqtt_get_id(), 'OFFLINE', get_ip()), qos=1, retain=True)
    mqtt_get_client().disconnect()


def vda_send_factsheet():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    print('Sending fact sheet')
    temp_file = open(os.path.join(os.path.dirname(__file__), '../data/factsheet.json'), 'r', encoding='utf8')
    temp = json.loads(temp_file.read())
    temp['serialNumber'] = mqtt_get_id()
    temp['timestamp'] = vda_timestamp()
    temp_file.close()
    mqtt_get_client().publish(topic=str(vda_namespace) + 'factsheet', payload=json.dumps(temp), qos=2, retain=True)


def vda_get_factsheet_version():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    temp_file = open(os.path.join(os.path.dirname(__file__), '../data/factsheet.json'), 'r', encoding='utf8')
    temp = (json.loads(temp_file.read()))['version']
    temp_file.close()
    return temp


def vda_get_instant_action_topic():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    instantActionTopic = str(vda_namespace) + 'instantAction'
    print(instantActionTopic)
    return instantActionTopic


def vda_handle_instant_actions_get_custom(instant, allowed_actions):
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    try:
        instant = json.loads(instant)
    except:
        instant = {} # the following check will send an error
    print(instant)
    _custom_actions=[]
    _actions = instant.get("actions", [])
    print("get_actions", _actions)
    for _action in _actions:
        _type = _action.get("actionType")
        if _type == "factsheetRequest":
            vda_data["actions"].append({
                "command": _action.get("actionType"),
                "id": _action.get("actionId"),
                "state": "FINISHED"
            })
            vda_send_factsheet()
        elif _type in allowed_actions:
            _custom_actions.append(_action)
        else:
            vda_data["errors"].append({
                "errorType": "invalidInstantAction"
            })

    if (not _custom_actions):
        vda_publish_status()
    temp = _custom_actions

    return temp


def vda_handle_instant_actions(instant):
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    print("Executing instand action")
    try:
        instant = json.loads(instant)
    except:
        instant = {} # the following check will send an error
    print(instant)
    _actions = instant.get("actions", [])
    for _action in _actions:
        if _action.get("actionType", "") == "factsheetRequest":
            vda_data["actions"].append({
                "command": _action.get("actionType"),
                "id": _action.get("actionId"),
                "state": "FINISHED"
            })
            vda_send_factsheet()
        else:
            vda_data["errors"].append({
                "errorType": "invalidInstantAction"
            })
    vda_publish_status()


def vda_set_instant_action_status(action, status):
    global valid_actions, ts, error, order, color, uid, result, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    for _action in vda_data["actions"]:
        if _action["id"] == action.get("actionId") and _action["command"] == action.get("actionType"):
            _action["state"] = status
            _action["timestamp"] = vda_timestamp()
            return
    # if not found
    vda_data["actions"].append({
            "command": action.get("actionType"),
            "id": action.get("actionId"),
            "timestamp": vda_timestamp(),
            "state": status,
            "warning": True
        })
    vda_publish_status()


def vda_reset():
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_data["errors"] = [
            {
                "errorType": "RESET_WARNING",
                "errorLevel": "WARNING",
                "errorReferences": [
                    { "orderId": vda_data["orderId"] } ,
                ]
            }
        ]

    vda_data["orderId"] = ""
    vda_data["orderUpdateId"] = 0
    vda_data["lastOrderId"] = ""
    vda_data["lastOrderTimestamp"] = None
    vda_data["actions"] = []


def vda_delete_information(infoType):
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, value, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    information.pop(infoType, False)


def vda_set_teachin(value):
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, infoType, infoLevel, infoReferences, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_data["teachin"] = value == True


def vda_set_information(infoType, infoLevel, infoReferences):
    global valid_actions, ts, error, order, color, uid, action, result, status, orderId, _unused_a, _unused_b, instant, allowed_actions, value, vda_data, orderTopic, temp_file, temp, instantActionTopic, vda_valid_actions, vda_namespace, information, vda_temp
    vda_delete_information(infoType)
    information[infoType] = {
            'infoType': infoType,
            'infoLevel': infoLevel,
            'infoReferences': infoReferences
        }


