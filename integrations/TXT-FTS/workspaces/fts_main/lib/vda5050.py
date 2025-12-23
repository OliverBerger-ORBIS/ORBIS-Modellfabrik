import atexit
import datetime
import json
import os
import signal
import sys
import time
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.battery_gauge import *
from lib.mqtt_utils import *
from lib.net_utils import *
from lib.util import *

validActions = None
validPositions = None
ts = None
order = None
nodeId = None
value = None
action = None
status = None
edgeId = None
code = None
instant = None
warning = None
allowed_actions = None
x = None
y = None
waiting = None
error_type = None
position = None
loadType = None
loadId = None
last_state_update_ts = None
vda_data = None
temp_file = None
factsheet = None
version = None
volt_percentage = None
vda_namespace = None
temp = None
volt_upper_limit = None
volt_lower_limit = None
volt_current_voltage = None
vda_temp = None


def vda_last_state_update_ts():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return last_state_update_ts


def vda_publish_status():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    last_state_update_ts = time.time()
    volt_percentage = return_volt_percentage_value()
    volt_upper_limit = return_volt_upper_limit()
    volt_lower_limit = return_volt_lower_limit()
    volt_current_voltage = return_volt_voltage()
    vda_temp = {}
    vda_data["stateId"] = vda_data["stateId"] + 1
    vda_temp["headerId"] = vda_data["stateId"]
    vda_temp["timestamp"] = vda_timestamp()
    vda_temp["serialNumber"] = util_get_controller_id()
    vda_temp["orderId"] = vda_data["lastOrderId"]
    vda_temp["orderUpdateId"] = vda_data["orderUpdateId"]
    vda_temp["lastNodeId"] = vda_data["lastNodeId"]
    vda_temp["lastCode"] = vda_data.get("lastCode", "")
    vda_temp["waitingForLoadHandling"] = vda_data.get("waitingForLoadHandling", False)
    vda_temp["nodeStates"] = []
    for _node in vda_data.get("nodes", []):
        vda_temp["nodeStates"].append({"id": _node["id"]})
    vda_temp["edgeStates"] = []
    for _edge in vda_data.get("edges", []):
        vda_temp["edgeStates"].append({"id": _edge["id"]})
    vda_temp["lastNodeSequenceId"] = 0
    vda_temp["driving"] = vda_data.get("driving", False)
    vda_temp["paused"] = vda_data.get("paused", False)
    _actionStates=[]
    for _action in vda_data.get("actions", []):
        _actionStates.append({
            "command": _action.get("type"),
            "id": _action.get("id"),
            "timestamp": _action.get("timestamp", vda_timestamp()),
            "state": _action.get("state", "WAITING")
        })
    vda_temp["actionStates"] = _actionStates
    vda_temp["load"] = []
    for _pos, _load in vda_data.get("loadMap", {}).items():
        vda_temp["load"].append({
            "loadPosition": _pos,
            "loadType": _load.get("loadType"),
            "loadId": _load.get("loadId")
        })
    vda_temp["batteryState"] = {
        "charging": vda_data.get("charging", False),
        "percentage": volt_percentage,
        "maxVolt":volt_upper_limit,
        "minVolt":volt_lower_limit,
        "currentVoltage": volt_current_voltage
    }
    vda_temp["errors"] = []
    vda_temp["errors"].extend(vda_data["errors"])
    vda_temp["errors"].extend(vda_data["orderErrors"])
    if vda_data.get("activeAction"):
        _action = vda_data["activeAction"]
        vda_temp["actionState"] = {
            "command": _action.get("type"),
            "id": _action.get("id"),
            "timestamp": _action.get("timestamp", vda_timestamp()),
            "state": _action.get("state", "WAITING")
        }
    for _action in vda_data.get("actions", []):
        if _action.get("state") == "FAILED":
            vda_temp["errors"].append({
                "errorType":  _action.get("type", "UNKNOWN") + "_ERROR",
                "errorLevel":  "WARNING" if _action.get("warning") else "FATAL"
            })

    mqtt_get_client().publish(topic=str(vda_namespace) + 'state', payload=json.dumps(vda_temp), qos=2, retain=True)


def vda_init(validActions, validPositions):
    global ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data = json.loads('{"loadMap": {}, "waitingForLoadHandling": false, "stateId": 0, "order": null, "errors": [], "orderErrors": [], "orderId": "", "lastOrderId": "", "orderUpdateId": 0, "lastOrderTimestamp": "", "lastNodeId": "UNKNOWN", "lastCode": "", "actions": []}')
    vda_data['validActions'] = validActions
    vda_data['validLoadPositions'] = validPositions
    vda_namespace = 'fts/v1/ff/{}/'.format(util_get_controller_id())


def vda_timestamp():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def vda_parse_timestamp(ts):
    global validActions, validPositions, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    if not ts:
        return None
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def vda_status_failed():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return 'FAILED'


def vda_status_initializing():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return 'INITIALIZING'


def vda_status_running():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return 'RUNNING'


def vda_status_finished():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return 'FINISHED'


def vda_process_order(order):
    global validActions, validPositions, ts, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    # returns True if a new order has been accepted, otherwise False
    vda_data["orderErrors"] = []
    try:
        order = json.loads(order)
    except:
        order = {} # the following check will send an error

    if not ("orderId" in order and "timestamp" in order and isinstance(order.get("nodes"), list) and isinstance(order.get("edges"), list) ):
        vda_data["orderErrors"].append({
            "errorType": "validationError",
            "errorLevel": "WARNING",
            "errorReferences": [
                { "referenceKey": "topic", "referenceValue": "order" } ,
                { "referenceKey": "headerId", "referenceValue": order.get("headerId") } ,
                { "referenceKey": "orderId", "referenceValue": order.get("orderId") } ,
                { "referenceKey": "orderUpdateId", "referenceValue": order.get("orderUpdateId") }
            ]
        })
        return False

    if (order["orderId"] == vda_data["lastOrderId"]):
        if order.get("orderUpdateId", 0) < vda_data["orderUpdateId"]:
            # send errors when update ID is older than our current update ID
            vda_data["orderErrors"].append({
                "errorType": "orderUpdateError",
                "errorLevel": "WARNING",
                "errorReferences": [
                    { "referenceKey": "topic", "referenceValue": "order" } ,
                    { "referenceKey": "headerId", "referenceValue": order.get("headerId") } ,
                    { "referenceKey": "orderId", "referenceValue": order.get("orderId") } ,
                    { "referenceKey": "orderUpdateId", "referenceValue": order.get("orderUpdateId") }
                ]
            })
            return False
        elif order.get("orderUpdateId", 0) == vda_data["orderUpdateId"]:
            # ignore duplicate orders
            return False

    _orderErrors=[]
    _has_fatal_errors=any(e.get("errorLevel") == "FATAL" for e in vda_data["errors"])
    if vda_data["orderId"] or vda_data.get("waitingForLoadHandling") or _has_fatal_errors:
        # An order is already in progress, we cannot accept a second order or an update
        # updates will be only accepted if the old order is finished. (Not standard conform!)
        # no orders will be accepted while fatal errors exist
        log_msg = 'DYN_NAV: orderId: {} waitingForLoadHandling: {} has_fatal_error: {}'.format(vda_data['orderId'], vda_data.get('waitingForLoadHandling'), _has_fatal_errors)
        print(log_msg)
        _orderErrors.append("")

    if vda_data.get("paused"):
        log_msg = 'DYN_NAV: orderId: {} device is paused'.format(vda_data['orderId'])
        print(log_msg)
        order["paused"] = True
        _orderErrors.append("paused")


    if order.get("zoneSetId"):
        _orderErrors.append("zoneSetId")

    if len(_orderErrors):
        log_msg = 'DYN_NAV: _orderErrors: {}'.format(_orderErrors)
        print(log_msg)
        vda_data["orderErrors"].append({
            "errorType": "orderError",
            "errorLevel": "WARNING",
            "errorReferences": [
               { "referenceKey": "topic", "referenceValue": "order" } ,
                { "referenceKey": "headerId", "referenceValue": order.get("headerId") } ,
                { "referenceKey": "orderId", "referenceValue": order.get("orderId") } ,
                { "referenceKey": "orderUpdateId", "referenceValue": order.get("orderUpdateId") }
            ] + [ {"referenceKey": i, "referenceValue": order.get(i)} for i in _orderErrors if i ]
        })
        return False

    vda_data["errors"] = [ e for e in vda_data["errors"] if e["errorLevel"] == "FATAL"  ]
    vda_data["order"] = order

    _error_refs = vda_validate_order_actions(order)

    if _error_refs:
        vda_data["orderErrors"].append({
            "errorType": "orderError",
            "errorLevel": "WARNING",
            "errorReferences": [
                { "referenceKey": "topic", "referenceValue": "order" } ,
                { "referenceKey": "headerId", "referenceValue": order.get("headerId") } ,
                { "referenceKey": "orderId", "referenceValue": order.get("orderId") } ,
                { "referenceKey": "orderUpdateId", "referenceValue": order.get("orderUpdateId") },
            ] + _error_refs
        })
        return False

    vda_data["actions"] = vda_get_order_actions(order)
    if len(vda_data["actions"]):
        vda_data["activeAction"] = vda_data["actions"][0]
    vda_data["orderId"] = order["orderId"]
    vda_data["orderUpdateId"] = order.get("orderUpdateId", 0)
    vda_data["lastOrderId"] = order["orderId"]
    vda_data["lastOrderTimestamp"] = order["timestamp"]
    vda_data["lastCode"] = ""

    return True


def vda_set_last_node_id(nodeId):
    global validActions, validPositions, ts, order, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["lastNodeId"] = nodeId


def vda_set_driving(value):
    global validActions, validPositions, ts, order, nodeId, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["driving"] = value


def vda_set_paused(value):
    global validActions, validPositions, ts, order, nodeId, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["paused"] = value


def vda_set_charging(value):
    global validActions, validPositions, ts, order, nodeId, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["charging"] = value


def vda_get_order_topic():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return str(vda_namespace) + 'order'


def vda_get_order():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return vda_data["order"]


def vda_order_clear_nodes_edges():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["nodes"] = []

    vda_data["edges"] = []


def vda_set_action_status(action, status):
    global validActions, validPositions, ts, order, nodeId, value, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    action["state"] = status
    action["timestamp"] = vda_timestamp()
    vda_data["activeAction"] = action


def vda_validate_order_actions(order):
    global validActions, validPositions, ts, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    def _vda_has_empty_bay_or_workpiece(_loadId):
        _loads = vda_data["loadMap"];
        print(_loads)
        if not _loads: # assume no problems when there are no load positions
            return True
        for _pos, _load in _loads.items():
            if not _load or not _load.get("loadId"):
                # success for an empty loading bay
                return True
            if _loadId and _load.get("loadId") == _loadId:
                # success if a bay contains the load with this id
                return True
        return False

    _errors=[]
    for node in order.get("nodes", []):
        _action = node.get("action")
        if (_action):
            print("action", _action)
            if not (_action.get("id") and _action.get("type") in vda_data["validActions"]):
                _errors.append({"referenceKey": "actionId", "referenceValue": _action.get("id")})
            else:
                _loadId = _action.get("metadata", {}).get("loadId")
                _loadType = _action.get("metadata", {}).get("loadType")
                _loadPosition = _action.get("metadata", {}).get("loadPosition")
                _noLoadChange = _action.get("metadata", {}).get("noLoadChange")
                _charge = _action.get("metadata", {}).get("charge")
                if _noLoadChange or _charge:
                    # allow an order with any loading bay if it is a charging order or the load will not change
                    pass
                elif _loadPosition:
                     _loadStored = vda_data.get("loadMap", {}).get(_loadPosition, {}).get("loadId")
                     if (_loadStored and _loadStored != _loadId) or _loadPosition not in vda_data.get("validLoadPositions"):
                        _errors.append({"referenceKey": "loadId", "referenceValue": _loadId})
                        _errors.append({"referenceKey": "loadPosition", "referenceValue": _loadPosition})
                elif (_loadId or _loadType) and not _vda_has_empty_bay_or_workpiece(_loadId):
                    _errors.append({"referenceKey": "loadId", "referenceValue": _loadId})

    if len(_errors):
        return _errors
    return None


def vda_order_driven_through(nodeId, edgeId):
    global validActions, validPositions, ts, order, value, action, status, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    for _node in  vda_data.get("nodes", []):
        if _node["id"] == nodeId:
            vda_data["nodes"].remove(_node)
            break

    for _edge in  vda_data.get("edges", []):
        if _edge["id"] == edgeId:
            vda_data["edges"].remove(_edge)
            break


def vda_set_last_code(code):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    # this is a separate key instead of lastNodeId as navigation with markers is too unreliable

    vda_data["lastCode"] = code


def vda_handle_default_instant_actions(instant):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    try:
        instant = json.loads(instant)
    except:
        instant = {}

    _actions = instant.get("actions", [])
    for _action in _actions:
        if _action.get("actionType", "") == "factsheetRequest":
            vda_data["actions"].append({
                "type": _action.get("actionType"),
                "id": _action.get("actionId"),
                "state": "FINISHED"
            })
            vda_send_factsheet()


def vda_get_order_actions(order):
    global validActions, validPositions, ts, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    _allactions=[]
    for _node in order.get("nodes", []):
        _action = _node.get("action")
        if (_action):
            _allactions.append(_action)
    return _allactions


def vda_set_instant_action_status(action, status, warning):
    global validActions, validPositions, ts, order, nodeId, value, edgeId, code, instant, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    for _action in vda_data["actions"]:
        if _action["id"] == action["actionId"] and _action["type"] == action["actionType"]:
            _action["state"] = status
            _action["timestamp"] = vda_timestamp()
            return
    # if not found
    vda_data["actions"].append({
            "type": action.get("actionType"),
            "id": action.get("actionId"),
            "timestamp": vda_timestamp(),
            "state": status,
            "warning": warning
        })


def vda_get_custom_instant_actions(instant, allowed_actions):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, warning, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    try:
        instant = json.loads(instant)
    except:
        instant = {}

    _custom_actions=[]
    _actions = instant.get("actions", [])

    for _action in _actions:
        _type = _action.get("actionType")
        if _type in allowed_actions:
            _custom_actions.append(_action)
        elif _type != "factsheetRequest":
            vda_data["errors"].append({
                "errorType": "invalidInstantAction",
                "timestamp": vda_timestamp(),
                "errorLevel": "WARNING"
            })

    return _custom_actions


def vda_handle_instant_actions(instant):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    try:
        instant = json.loads(instant)
    except:
        instant = {} # the following check will send an error
    print(instant)
    _actions = instant.get("actions", [])
    for _action in _actions:
        if _action.get("actionType", "") == "factsheetRequest":
            vda_data["actions"].append({
                "type": _action.get("actionType"),
                "id": _action.get("actionId"),
                "state": "FINISHED"
            })
            vda_send_factsheet()
        else:
            vda_data["errors"].append({
                "errorType": "invalidInstantAction",
                "timestamp": vda_timestamp(),
                "errorLevel": "WARNING"
            })
    vda_publish_status()


# registers a message to send when exiting the program
# and requests the broker to publish a message when connection is lost
#
# has to be called before connecting to the mqtt broker
def vda_setup_offline_notifications():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    mqtt_get_client().will_set(topic=str(vda_namespace) + 'connection', payload='{{ "headerId": {}, "timestamp": "{}", "version": "{}", "manufacturer": "{}", "serialNumber": "{}", "connectionState": "{}", "ip": "{}" }}'.format(1, vda_timestamp(), vda_get_factsheet_version(), 'Fischertechnik', util_get_controller_id(), 'CONNECTIONBROKEN', get_ip()), qos=1, retain=True)
    # atexit will be called when the program is stopped with the button on the touchscreen
    atexit.register(vda_send_connection_offline)

    # handle stopping by system shutdown as well
    signal.signal(signal.SIGINT, _vda_handle_signals_int_term)
    signal.signal(signal.SIGTSTP, _vda_handle_signals_int_term)
    signal.signal(signal.SIGTERM, _vda_handle_signals_int_term)


def _vda_handle_signals_int_term(x, y):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    # Handle termination signals gracefully
    # sys.exit will call the function registered with atexit.register(vda_send_connection_offline)
    sys.exit(0)


def vda_send_connection_online():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    print('Sending online status')
    mqtt_get_client().publish(topic=str(vda_namespace) + 'connection', payload='{{ "headerId": {}, "timestamp": "{}", "version": "{}", "manufacturer": "{}", "serialNumber": "{}", "connectionState": "{}", "ip": "{}" }}'.format(2, vda_timestamp(), vda_get_factsheet_version(), 'Fischertechnik', util_get_controller_id(), 'ONLINE', get_ip()), qos=1, retain=True)


def vda_send_connection_offline():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    print('Shutting down')
    mqtt_get_client().publish(topic=str(vda_namespace) + 'connection', payload='{{ "headerId": {}, "timestamp": "{}", "version": "{}", "manufacturer": "{}", "serialNumber": "{}", "connectionState": "{}", "ip": "{}" }}'.format(3, vda_timestamp(), vda_get_factsheet_version(), 'Fischertechnik', util_get_controller_id(), 'OFFLINE', get_ip()), qos=1, retain=True)
    mqtt_get_client().disconnect()


def vda_send_factsheet():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    temp_file = open(os.path.join(os.path.dirname(__file__), '../data/factsheet.json'), 'r', encoding='utf8')
    temp = json.loads(temp_file.read())
    temp['serialNumber'] = util_get_controller_id()
    temp['timestamp'] = vda_timestamp()
    temp_file.close()
    mqtt_get_client().publish(topic=str(vda_namespace) + 'factsheet', payload=json.dumps(temp), qos=2, retain=True)


def vda_get_factsheet_version():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    factsheet = open(os.path.join(os.path.dirname(__file__), '../data/factsheet.json'), 'r', encoding='utf8')
    version = (json.loads(factsheet.read()))['version']
    factsheet.close()
    return version


def vda_get_instant_action_topic():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return str(vda_namespace) + 'instantAction'


def vda_wait_for_load_handling(waiting):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["waitingForLoadHandling"] = True if waiting else False


def vda_add_fatal_error(error_type):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["errors"].append({
        "errorType":  error_type,
        "errorLevel":  "FATAL"
    })


def vda_remove_warning(error_type):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    # Liste der Fehler durchlaufen und nach dem entsprechenden error_type suchen
    vda_data["errors"] = [error for error in vda_data["errors"] if error["errorType"] != error_type]
    print("Warning removed:")


def vda_reset_order():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["errors"] = [{
            "errorType": "RESET",
            "errorLevel": "WARNING",
            "errorReferences": [
                { "referenceKey": "orderId", "referenceValue": vda_data["lastOrderId"] }
            ] + [  { "referenceKey": "loadId", "referenceValue": _load.get("loadId") } for _load in vda_data["loadMap"].values() if _load.get("loadId") ]
        }]

    # show errors for dismissed actions

    for _action in vda_data["actions"]:
        if _action.get("state") != "FINISHED":
            vda_data["errors"].append({
                "errorType": "ACTION_DISMISSED",
                "errorLevel": "WARNING",
                "errorReferences": [
                    { "referenceKey": "actionId", "referenceValue": _action.get("id") },
                    { "referenceKey": "actionCommand", "referenceValue": _action.get("command") }
                ]
            })

    vda_data["orderId"] = ""
    vda_data["order"] = {}
    vda_data["orderUpdateId"] = 0
    vda_data["actions"] = []
    vda_data["activeAction"] = []
    vda_data["lastOrderId"] = ""
    vda_data["loadMap"] = {}
    vda_data["waitingForLoadHandling"] = False


def vda_set_warning(error_type):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["errors"].append({
        "errorType":  error_type,
        "errorLevel":  "WARNING"
    })
    print("Warning set")


def vda_clear_order_id():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["orderId"] = None


def vda_clear_warnings():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["errors"] = [ e for e in vda_data["errors"] if e["errorLevel"] == "FATAL"  ]


def vda_set_load(position, loadType, loadId):
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    vda_data["loadMap"][position] = {
        "loadId": loadId,
        "loadType": loadType
    }


def vda_get_loads():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    return vda_data['loadMap']


def do_send_global_reset():
    global validActions, validPositions, ts, order, nodeId, value, action, status, edgeId, code, instant, warning, allowed_actions, x, y, waiting, error_type, position, loadType, loadId, last_state_update_ts, vda_data, temp_file, factsheet, version, volt_percentage, vda_namespace, temp, volt_upper_limit, volt_lower_limit, volt_current_voltage, vda_temp
    print('Sending global reset')
    mqtt_get_client().publish(topic='ccu/set/reset', payload='{{ "timestamp": "{}", "withStorage": false }}'.format(vda_timestamp()), qos=1, retain=False)


