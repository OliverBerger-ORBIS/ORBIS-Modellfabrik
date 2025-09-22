import math
import threading
import time

import fischertechnik.utility.math as ft_math
from fischertechnik.controller.Motor import Motor
from lib.battery_gauge import *
from lib.battery_monitor import *
from lib.charger import *
from lib.collision import *
from lib.controller import *
from lib.display import *
from lib.lib_move_async import *
from lib.lib_move_sync import *
from lib.line_follower import *
from lib.mqtt_utils import *
from lib.net_utils import *
from lib.ui_tools import *
from lib.util import *
from lib.vda5050 import *

current_command = None
is_last_command = None
result_code = None
unexpected = None
instant_action = None
nodeId = None
action = None
the_map = None
key = None
default_value = None
distance = None
reset_initiated = None
current_node_id = None
last_node_id = None
speed = None
soc = None
light_docking_active = None
temp = None
_VERSION = None
instant_action_temp = None
order = None
undock_result = None
button_closed_left_prev = None
retries = None
wrongStartPosition = None
drive_sequence = None
DEFAULT_DOCKING_DISTANCE = None
FTS_DOCKING_OFFSET = None
v = None
dir2 = None
v_line_speed = None
is_docked_at_position = None
counter = None
ACTION_DOCK = None
COMMAND_DRIVE = None
ACTION_TURN = None
ACTION_PASS = None
INSTANT_ACTION_INITIAL_DOCK = None
v_line_slow = None
INSTANT_ACTION_CLEAR_LOAD_HANDLER = None
INSTANT_ACTION_RESET = None
INSTANT_ACTION_STOP_CHARGE = None
NODE_ID_UNKNOWN = None
us_left = None
BAY_LEFT = None
BAY_OFFSET_DIST = None
BAY_RIGHT = None
BAY_CENTER = None
old_dir = None
charging_stopped = None
ResetException = None
v_slow = None
us_right = None
turn = None
offset_counter_light = None
ERROR_LINE_LOST = None
state = None
offsetdiff_us1_us2 = None
button_closed_left = None
button_closed_right = None
dist_min = None
button_closed_right_prev = None
limit_pos_left = None
limit_pos_right = None
line_left = None
line_right = None
dist_stop_line = None


def run_command(current_command, is_last_command):
    global result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    vda_set_driving(True)
    display.set_attr("txt_status_driving.active", str(True).lower())
    if ACTION_DOCK == current_command['type']:
        vda_set_action_status(current_command['action'], vda_status_initializing())
        vda_publish_status()
        display.set_attr("label_status.text", 'Docking...')
        print('Start Docking...')
        do_docking_action(current_command['action'], current_command['nodeId'])
    elif COMMAND_DRIVE == current_command['type']:
        print('Driving...')
        display.set_attr("label_status.text", 'Driving...')
        vda_wait_for_load_handling(False)
        vda_publish_status()
        if map_has_key(current_command, 'distance'):
            if is_docked_at_position:
                temp = do_undock_drive(current_command['distance'])
            else:
                temp = line_follow_for_distance(current_command['distance'])
        else:
            print('Error: Drive command without distance.')
            temp = False
        abortIfResetInitiated()
        if temp:
            last_node_id = current_command['nodeId']
            vda_set_last_node_id(last_node_id)
        else:
            vda_add_fatal_error(ERROR_LINE_LOST)
            vda_order_driven_through(current_command['nodeId'], current_command['edgeId'])
            fail_remaining_sequence()
            require_reset()
    elif ACTION_TURN == current_command['type']:
        vda_set_action_status(current_command['action'], vda_status_initializing())
        vda_wait_for_load_handling(False)
        vda_publish_status()
        display.set_attr("label_status.text", 'Turning...')
        print('Start Turning...')
        do_turning_action(current_command['action'])
    elif ACTION_PASS == current_command['type']:
        print('Pass node...')
        vda_set_action_status(current_command['action'], vda_status_finished())
    elif INSTANT_ACTION_INITIAL_DOCK == current_command['type']:
        do_initial_docking_action(current_command['action'], current_command['nodeId'])
    if is_last_command:
        display.set_attr("txt_status_driving.active", str(False).lower())
        vda_set_driving(False)
        if not (display.get_attr("txt_status_error.active")):
            vda_order_clear_nodes_edges()
            vda_clear_order_id()
            display.set_attr("label_status.text", 'Ready.')
    abortIfResetInitiated()
    vda_publish_status()


def handle_mqtt_connected(result_code):
    global current_command, is_last_command, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    # show connection status on display and send online status
    display.set_attr("label_mqtt_info.text", str(mqtt_connect_result_to_string(result_code)))
    if not result_code:
        display.set_attr("txt_status_connected.active", str(True).lower())
        vda_send_connection_online()
        vda_publish_status()


def setup_mqtt():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    display.set_attr("label_mqtt_info.text", 'Connecting to MQTT...')
    vda_setup_offline_notifications()
    mqtt_get_client().set_disconnect_callback(handle_mqtt_disconnected)
    mqtt_get_client().set_connect_callback(handle_mqtt_connected)
    mqtt_connect_always()
    mqtt_get_client().subscribe(topic=vda_get_instant_action_topic(), callback=mqtt_instant_action_callback, qos=1)
    mqtt_get_client().subscribe(topic=vda_get_order_topic(), callback=mqtt_order_callback, qos=1)
    mqtt_wait_connected()
    # online status will be sent by connection callback


def handle_mqtt_disconnected(unexpected):
    global current_command, is_last_command, result_code, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    # show reconnection status on display
    display.set_attr("txt_status_connected.active", str(False).lower())
    if unexpected:
        display.set_attr("label_mqtt_info.text", 'Reconnecting: Unexpected disconnect')
    else:
        display.set_attr("label_mqtt_info.text", 'Disconnected')


def set_v():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    soc = return_volt_percentage_value()
    if soc < 0:
        soc = 0
    if soc <= 30:
        v_line_speed = ft_math.map(soc, 30, 0, 400, 400)
        v_line_slow = ft_math.map(soc, 30, 0, -180, -300)
        v_slow = ft_math.map(soc, 30, 0, 180, 300)
        line_init(v_line_speed, v_line_slow, v_slow)
        v = ft_math.map(soc, 30, 0, 250, 350)
    elif soc > 40:
        v_line_speed = 400
        v_line_slow = -180
        v_slow = 180
        line_init(v_line_speed, v_line_slow, v_slow)
        v = 250
    print(f'soc:{soc} v_line_speed:{v_line_speed} v_line_slow:{v_line_slow} v_slow:{v_slow} v:{v}')


def mqtt_instant_action_callback(message):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    vda_handle_default_instant_actions(message.payload.decode("utf-8"))
    for instant_action_temp in vda_get_custom_instant_actions(
        message.payload.decode("utf-8"),
        [
            INSTANT_ACTION_CLEAR_LOAD_HANDLER,
            INSTANT_ACTION_INITIAL_DOCK,
            INSTANT_ACTION_RESET,
            INSTANT_ACTION_STOP_CHARGE,
        ],
    ):
        if instant_action_temp.get("actionType") == INSTANT_ACTION_CLEAR_LOAD_HANDLER and is_docked_at_position:
            vda_wait_for_load_handling(False)
            _metadata = instant_action_temp.get("metadata", {})
            _dropped = _metadata.get("loadDropped")
            _position = _metadata.get("loadPosition", is_docked_at_position)
            _loadId = _metadata.get("loadId", None)
            _type = _metadata.get("loadType")
            if is_docked_at_position and is_docked_at_position != _position:
                print(
                    "clearLoadHandler: docked position ",
                    is_docked_at_position,
                    " differs from cleared position:",
                    _position,
                )
            if _dropped and _position:
                vda_set_load(_position, None, None)
            elif not _dropped and _position:
                vda_set_load(_position, _type, _loadId)
            ui_set_load_indicators()
            vda_set_instant_action_status(instant_action_temp, vda_status_finished(), False)
        elif instant_action_temp.get("actionType") == INSTANT_ACTION_INITIAL_DOCK:
            _metadata = instant_action_temp.get("metadata", {})
            _nodeId = _metadata.get("nodeId")
            queue_instant_action_initial_dock(instant_action_temp, _nodeId)
        elif instant_action_temp.get("actionType") == INSTANT_ACTION_RESET:
            reset_initiated = True
        elif instant_action_temp.get("actionType") == INSTANT_ACTION_STOP_CHARGE:
            stop_charging_instant_action(instant_action_temp)
        else:
            vda_set_instant_action_status(instant_action_temp, vda_status_failed(), True)
    vda_publish_status()


def mqtt_order_callback(message):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    if vda_process_order(message.payload.decode("utf-8")):
        order = vda_get_order()
        wrongStartPosition = False
        _prev_position = last_node_id
        drive_sequence = []
        _allnodes = order.get("nodes")
        wrongStartPosition = _allnodes and _allnodes[0].get("id") != last_node_id
        for _node in _allnodes:
            _nextEdge = None
            for _edge in order.get("edges"):
                if _edge["id"] in _node.get("linkedEdges", []) and _prev_position in _edge.get("linkedNodes", []):
                    _nextEdge = _edge
                    break
            if _prev_position == _node["id"]:
                print("PLAN: STAY at current node  " + _node["id"])
                if _node.get("action"):
                    drive_sequence.append(
                        {"type": _node["action"].get("type"), "nodeId": _node["id"], "action": _node["action"]}
                    )
                    print("PLAN: ACTION " + _node["action"].get("type"))
            elif not _nextEdge:
                print("PLAN: UNKNOWN PATH to " + _node["id"] + " from current location")
                wrongStartPosition = True
                if _node.get("action"):
                    # add it to the sequence to fail it later
                    drive_sequence.append({"type": _node["action"].get("type"), "action": _node["action"]})
                    print("PLAN: ACTION " + _node["action"].get("type"))
            else:
                _prev_position = _node["id"]
                _action = _node.get("action")
                _dict = {"type": COMMAND_DRIVE, "nodeId": _node["id"], "edgeId": _nextEdge["id"]}
                if _nextEdge.get("length"):
                    _dict["distance"] = _nextEdge.get("length")
                if not _action or _action.get("type") != ACTION_DOCK:
                    drive_sequence.append(_dict)
                    print(
                        "PLAN: DRIVING to "
                        + _node["id"]
                        + " via edge "
                        + _nextEdge["id"]
                        + " distance: "
                        + str(_nextEdge.get("length", "unknown"))
                    )
                if _action:
                    drive_sequence.append({"type": _action.get("type"), "action": _action, "nodeId": _node["id"]})
                    print("PLAN: ACTION " + _node["action"].get("type") + " at " + _node["id"])

        if wrongStartPosition or last_node_id == NODE_ID_UNKNOWN:
            print(f'PLAN Error: Currently at {last_node_id}, wrong start position: {wrongStartPosition} or UNKNOWN')
            fail_remaining_sequence()
            vda_clear_order_id()
            vda_order_clear_nodes_edges()
    vda_publish_status()


def do_mainloop():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    abortIfResetInitiated()
    if not not len(drive_sequence):
        set_v()
        current_command = drive_sequence.pop(0)
        run_command(current_command, not len(drive_sequence))
    abortIfResetInitiated()
    time.sleep(0.05)


def queue_instant_action_initial_dock(instant_action, nodeId):
    global current_command, is_last_command, result_code, unexpected, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    # this instant action can only run when
    # the FTS does not know its position
    # and no order is currently queued
    if nodeId and not len(drive_sequence) and last_node_id == NODE_ID_UNKNOWN:
        drive_sequence = [{"type": INSTANT_ACTION_INITIAL_DOCK, "action": instant_action, "nodeId": nodeId}]
        vda_clear_warnings()
        vda_set_instant_action_status(instant_action, vda_status_initializing(), True)
    else:
        vda_set_instant_action_status(instant_action, vda_status_failed(), True)
        display.set_attr("label_status.text", 'Warning: Initial dock already performed.')


def do_docking_action(action, nodeId):
    global current_command, is_last_command, result_code, unexpected, instant_action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print("do_docking_action ## action / nodeId:", [action, nodeId])
    if last_node_id == nodeId:
        abortIfResetInitiated()
        vda_set_action_status(action, vda_status_running())
        vda_publish_status()
        if action_get_parameter(action, 'charge', False):
            do_docking_charger(action)
        else:
            do_docking_with_bay(action, nodeId, last_node_id)
        last_node_id = nodeId
        vda_set_last_node_id(last_node_id)
        vda_set_action_status(action, vda_status_finished())
        vda_publish_status()
    else:
        if (line_find_left_right()) and do_rotate_align_docking() and (line_find_left_right()):
            abortIfResetInitiated()
            vda_set_action_status(action, vda_status_running())
            vda_publish_status()
            if action_get_parameter(action, 'charge', False):
                do_docking_charger(action)
            else:
                do_docking_with_bay(action, nodeId, last_node_id)
            last_node_id = nodeId
            vda_set_last_node_id(last_node_id)
            vda_set_action_status(action, vda_status_finished())
            vda_publish_status()
        else:
            abortIfResetInitiated()
            util_stop_driving()
            vda_set_action_status(action, vda_status_failed())
            vda_publish_status()
            require_reset()


def declareResetException():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line

    class ResetException(Exception):
        "Raised when the the current action is aborted du to a reset"

        pass

    return ResetException


# Checks if a map contains a key. Missing from the Data structure functions
def map_has_key(the_map, key):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    return key in the_map


# Checks if a map contains a key. Missing from the Data structure functions
def action_get_parameter(action, key, default_value):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, the_map, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    return action.get("metadata", {}).get(key, default_value)


def abortIfResetInitiated():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    if reset_initiated:
        raise ResetException()


def do_turning_action(action):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    vda_set_action_status(action, vda_status_running())
    vda_publish_status()
    # Try to undock
    temp = undock_if_necessary()
    turn = action.get("metadata", {}).get("direction")
    # Only perform the turn when undocking was not necessary or succeeded
    if temp:
        if turn == 'LEFT':
            print('left')
            temp = line_rotate_left_and_find(90)
        elif turn == 'RIGHT':
            temp = line_rotate_right_and_find(90)
            print('right')
        elif turn == 'BACK':
            temp = line_rotate_left_and_find(180)
            print('back')
        else:
            temp = False
    if temp:
        vda_set_action_status(action, vda_status_finished())
        vda_publish_status()
    else:
        vda_set_action_status(action, vda_status_failed())
        vda_publish_status()
        require_reset()


def fail_remaining_sequence():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    while not not len(drive_sequence):
        temp = drive_sequence.pop(0)
        if map_has_key(temp, 'action'):
            vda_set_action_status(temp['action'], vda_status_failed())


def do_undock_drive(distance):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    light_docking_active = True
    temp = True
    if is_docked_at_position:
        print('Undocking...')
        if is_docked_at_position == BAY_LEFT:
            move_left_distance(v, BAY_OFFSET_DIST)
        elif is_docked_at_position == BAY_RIGHT:
            move_right_distance(v, BAY_OFFSET_DIST)
        temp = line_find_left_right()
        if temp:
            temp = line_follow_for_distance(distance - FTS_DOCKING_OFFSET)
    is_docked_at_position = False
    light_docking_active = False
    return temp


def do_initial_docking_action(instant_action, nodeId):
    global current_command, is_last_command, result_code, unexpected, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    if (line_find_left_right()) and do_rotate_align_docking() and (line_find_left_right()):
        vda_set_instant_action_status(instant_action, vda_status_running(), True)
        vda_publish_status()
        run_basic_docking_sequence()
        is_docked_at_position = BAY_CENTER
        last_node_id = nodeId
        vda_set_last_node_id(last_node_id)
        vda_set_instant_action_status(instant_action, vda_status_finished(), True)
        vda_publish_status()
        display.set_attr("label_status.text", 'Ready')
    else:
        util_stop_driving()
        vda_set_instant_action_status(instant_action, vda_status_failed(), True)
        vda_publish_status()
        require_reset()


def require_reset():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    display.set_attr("label_status.text", 'Error: Press Reset and reinitialize at DPS')
    display.set_attr("txt_status_error.active", str(True).lower())


def on_btn_reset_clicked(event):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    do_send_global_reset()


def reset_state():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    display.set_attr("label_status.text", 'Start initial docking to DPS.')
    display.set_attr("txt_status_driving.active", str(False).lower())
    display.set_attr("txt_status_error.active", str(False).lower())
    last_node_id = NODE_ID_UNKNOWN
    drive_sequence = []
    is_docked_at_position = False
    reset_initiated = False
    charger_disconnect()
    util_stop_driving()
    vda_reset_order()
    vda_set_charging(False)
    vda_set_paused(False)
    ui_set_load_indicators()
    vda_set_driving(False)
    vda_wait_for_load_handling(False)
    vda_set_last_node_id(last_node_id)


def undock_if_necessary():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    return do_undock_drive(DEFAULT_DOCKING_DISTANCE + FTS_DOCKING_OFFSET)


def do_docking_with_bay(action, current_node_id, last_node_id):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, the_map, key, default_value, distance, reset_initiated, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print("do_docking_with_bay ## action:", action)
    print("do_docking_with_bay ## [current_node_id, last_node_id]:", [current_node_id, last_node_id])
    if current_node_id != last_node_id:
        run_basic_docking_sequence()
    else:
        run_loading_bay_docking_sequence()
    do_docking_to_bay(action)
    do_docking_fine_fwd()
    if not action_get_parameter(action, 'noLoadChange', False):
        vda_wait_for_load_handling(True)
        vda_set_load(
            is_docked_at_position,
            action_get_parameter(action, 'loadType', None),
            action_get_parameter(action, 'loadId', None),
        )
        ui_set_load_indicators()


def run_loading_bay_docking_sequence():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    do_docking_fine_fwd()
    undock_result = do_undock_drive(0)
    do_docking_fine_light()
    do_docking_fine_fwd()


def run_basic_docking_sequence():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    do_docking_near()
    do_docking_find_ref(v)
    do_docking_fine_fwd()
    do_docking_fine_light()
    do_docking_fine_fwd()


def do_rotate_align_docking():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('ROTATE ULTRASONIC ALIGN 180')
    temp = 0
    while True:
        abortIfResetInitiated()
        us_left = TXT_M_I7_ultrasonic_distance_meter.get_distance()
        us_right = TXT_M_I8_ultrasonic_distance_meter.get_distance()
        print(f'distance left: {us_left} distance right: {us_right}')
        if us_left == 1023 or us_left >= dist_min or us_right == 1023 or us_right >= dist_min:
            temp = (temp if isinstance(temp, (int, float)) else 0) + 1
            print('Invalid Ultrasonic readings')
            # Retry the sensors a few times if the data is invalid once.
            # Allow up to 5 false readins during one docking sequence
            if temp > 5:
                return False
            display.set_attr("label_status.text", str(f'Error: distance left: {us_left} distance right: {us_right}'))
            continue
        elif us_left < 15 and us_right < 15:
            print('forward (away from module)')
            TXT_M_M1_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M2_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M3_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M4_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M1_encodermotor.start_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)
        elif math.fabs(us_left - us_right) <= offsetdiff_us1_us2:
            print('stop (aligned to dock)')
            TXT_M_M1_encodermotor.stop_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)
            break
        elif us_left < us_right:
            print('rotate left')
            TXT_M_M1_encodermotor.set_speed(int(v_slow), Motor.CW)
            TXT_M_M3_encodermotor.set_speed(int(v_slow), Motor.CW)
            TXT_M_M2_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M4_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M1_encodermotor.start_sync(TXT_M_M3_encodermotor, TXT_M_M2_encodermotor, TXT_M_M4_encodermotor)
        elif us_left > us_right:
            print('rotate right')
            TXT_M_M1_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M3_encodermotor.set_speed(int(v_slow), Motor.CCW)
            TXT_M_M2_encodermotor.set_speed(int(v_slow), Motor.CW)
            TXT_M_M4_encodermotor.set_speed(int(v_slow), Motor.CW)
            TXT_M_M1_encodermotor.start_sync(TXT_M_M3_encodermotor, TXT_M_M2_encodermotor, TXT_M_M4_encodermotor)
        else:
            print('unknown')
            util_stop_driving()
            if True:
                return False
        time.sleep(0.02)
    move_rotate_left(512, 180)
    return True


def do_docking_to_bay(action):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    light_docking_active = True
    temp = action.get("metadata", {}).get("loadPosition")
    if temp == BAY_LEFT:
        move_right_distance(v, BAY_OFFSET_DIST)
        is_docked_at_position = BAY_LEFT
    elif temp == BAY_RIGHT:
        move_left_distance(v, BAY_OFFSET_DIST)
        is_docked_at_position = BAY_RIGHT
    else:
        is_docked_at_position = BAY_CENTER
    print(''.join([str(x) for x in ['Docked at:', is_docked_at_position, ' Distance ', BAY_OFFSET_DIST]]))
    display.set_attr(
        "label_status.text",
        str(''.join([str(x2) for x2 in ['Docked at:', is_docked_at_position, ' Distance ', BAY_OFFSET_DIST]])),
    )
    light_docking_active = False


def do_docking_near():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('DOCKING NEAR')
    button_closed_left_prev = True
    button_closed_left_prev = True
    light_docking_active = True
    time.sleep(0.005)
    display.set_attr("label_status.text", 'Docking to touch')
    while True:
        abortIfResetInitiated()
        state = 0
        button_closed_left = TXT_M_I2_mini_switch.is_closed()
        button_closed_right = TXT_M_I3_mini_switch.is_closed()
        if button_closed_left and button_closed_right:
            time.sleep(0.005)
            util_stop_driving()
            break
        elif button_closed_left_prev == button_closed_left and button_closed_right_prev == button_closed_right:
            # keep the same direction when the switch state did not change
            pass
        elif button_closed_left and not button_closed_right:
            print('rotate left')
            TXT_M_M1_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M3_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M2_encodermotor.set_speed(int(v), Motor.CCW)
            TXT_M_M4_encodermotor.set_speed(int(v), Motor.CCW)
            TXT_M_M1_encodermotor.start_sync(TXT_M_M3_encodermotor, TXT_M_M2_encodermotor, TXT_M_M4_encodermotor)
        elif not button_closed_left and not button_closed_right:
            print('move fwd')
            TXT_M_M1_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M2_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M3_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M4_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M1_encodermotor.start_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)
        elif button_closed_right and not button_closed_left:
            print('rotate right')
            TXT_M_M2_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M4_encodermotor.set_speed(int(v), Motor.CW)
            TXT_M_M3_encodermotor.set_speed(int(v), Motor.CCW)
            TXT_M_M1_encodermotor.set_speed(int(v), Motor.CCW)
            TXT_M_M2_encodermotor.start_sync(TXT_M_M4_encodermotor, TXT_M_M3_encodermotor, TXT_M_M1_encodermotor)
        else:
            pass
        button_closed_right_prev = button_closed_right
        button_closed_left_prev = button_closed_left
        time.sleep(0.001)
    display.set_attr("label_status.text", 'Docking...')
    light_docking_active = False


def do_docking_find_ref(speed):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('DOCKING FIND REF')
    retries = 0
    dir2 = -1
    counter = 0
    old_dir = 0
    light_docking_active = True
    time.sleep(0.01)
    display.set_attr("label_status.text", 'Docking to light')
    # SOmetimes the FTS might be on the edge of the detectable
    # light and confuse the fine docking algorithm. Try to fix it.
    if TXT_M_I1_photo_transistor.is_bright():
        move_left_distance(v, 10)
    while True:
        abortIfResetInitiated()
        if TXT_M_I1_photo_transistor.is_bright():
            print('stop')
            TXT_M_M1_encodermotor.stop_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)
            break
        elif counter < limit_pos_left:
            print('limit left')
            dir2 = 1
            retries = (retries if isinstance(retries, (int, float)) else 0) + 1
        elif counter > limit_pos_right:
            print('limit right')
            dir2 = -1
        else:
            pass
        if old_dir != dir2:
            print('Changing direction')
            TXT_M_M1_encodermotor.set_speed(int(speed * dir2), Motor.CW)
            TXT_M_M2_encodermotor.set_speed(int(speed * dir2), Motor.CCW)
            TXT_M_M3_encodermotor.set_speed(int(speed * dir2), Motor.CCW)
            TXT_M_M4_encodermotor.set_speed(int(speed * dir2), Motor.CW)
            TXT_M_M1_encodermotor.start_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)
            old_dir = dir2
        counter = (counter if isinstance(counter, (int, float)) else 0) + meanCounters() * dir2
        resetCounters()
        time.sleep(0.01)
    display.set_attr("label_status.text", 'Docking...')
    light_docking_active = False


def callback(event):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    if TXT_M_I2_mini_switch.is_closed():
        if (TXT_M_I3_mini_switch.is_closed()) and not light_docking_active:
            TXT_M_M1_encodermotor.stop_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def callback2(event):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    if TXT_M_I3_mini_switch.is_closed():
        if (TXT_M_I2_mini_switch.is_closed()) and not light_docking_active:
            TXT_M_M1_encodermotor.stop_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)


def do_docking_fine_fwd():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('DOCKING FINE FWD')
    display.set_attr("label_status.text", 'Docking to contact')
    while True:
        abortIfResetInitiated()
        if (TXT_M_I2_mini_switch.is_open()) or (TXT_M_I3_mini_switch.is_open()):
            print('drive backwards (towards module)')
            move_backward_distance(v, 2)
        else:
            print('finished, touched module')
            break
        time.sleep(0.01)
    display.set_attr("label_status.text", 'Docking...')


def meanCounters():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    temp = math_mean(
        [
            TXT_M_C1_motor_step_counter.get_count(),
            TXT_M_C2_motor_step_counter.get_count(),
            TXT_M_C3_motor_step_counter.get_count(),
            TXT_M_C4_motor_step_counter.get_count(),
        ]
    )
    return temp


def do_docking_fine_light():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('DOCKING FINE LIGHT')
    light_docking_active = True
    display.set_attr("label_status.text", 'Docking to LED')
    if TXT_M_I1_photo_transistor.is_bright():
        TXT_M_M1_encodermotor.set_speed(int(dir2 * v_slow), Motor.CCW)
        TXT_M_M2_encodermotor.set_speed(int(dir2 * v_slow), Motor.CW)
        TXT_M_M3_encodermotor.set_speed(int(dir2 * v_slow), Motor.CW)
        TXT_M_M4_encodermotor.set_speed(int(dir2 * v_slow), Motor.CCW)
        TXT_M_M1_encodermotor.start_sync(TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor)
        while True:
            if TXT_M_I1_photo_transistor.is_dark():
                break
        TXT_M_M1_encodermotor.set_speed(int(dir2 * v_slow), Motor.CW)
        TXT_M_M2_encodermotor.set_speed(int(dir2 * v_slow), Motor.CCW)
        TXT_M_M3_encodermotor.set_speed(int(dir2 * v_slow), Motor.CCW)
        TXT_M_M4_encodermotor.set_speed(int(dir2 * v_slow), Motor.CW)
        TXT_M_M1_encodermotor.set_distance(
            int(offset_counter_light), TXT_M_M2_encodermotor, TXT_M_M3_encodermotor, TXT_M_M4_encodermotor
        )
        while True:
            if not TXT_M_M1_encodermotor.is_running():
                break
            time.sleep(0.010)
    else:
        print('error: no light')
    display.set_attr("label_status.text", 'Docking...')
    light_docking_active = False


def resetCounters():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    TXT_M_C1_motor_step_counter.reset()
    TXT_M_C2_motor_step_counter.reset()
    TXT_M_C3_motor_step_counter.reset()
    TXT_M_C4_motor_step_counter.reset()
    time.sleep(0.005)


def do_docking_charger(action):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    do_docking_near()
    do_docking_fine_fwd()
    vda_set_paused(True)
    vda_set_charging(True)
    is_docked_at_position = BAY_CENTER
    print('CHARGE: Start')
    charging_stopped = False
    display.set_attr("label_status.text", 'Waiting for charger.')
    while True:
        if charger_is_available():
            break
        time.sleep(0.010)
    display.set_attr("label_status.text", 'Enable charging.')
    charger_connect()
    threading.Thread(target=_stop_charging_when_full_th, daemon=True).start()


def _stop_charging_when_full_th():
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, action, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('CHARGE: Waiting for full battery')
    time.sleep(10)
    while not (charger_is_done()):
        for count in range(60):
            time.sleep(1)
            if charging_stopped:
                charging_stopped = False
                if True:
                    return
    print('CHARGE: Detected full battery.')
    ui_util_finish_charging()
    vda_publish_status()


def stop_charging_instant_action(action):
    global current_command, is_last_command, result_code, unexpected, instant_action, nodeId, the_map, key, default_value, distance, reset_initiated, current_node_id, last_node_id, speed, soc, light_docking_active, temp, _VERSION, instant_action_temp, order, undock_result, button_closed_left_prev, retries, wrongStartPosition, drive_sequence, DEFAULT_DOCKING_DISTANCE, FTS_DOCKING_OFFSET, v, dir2, v_line_speed, is_docked_at_position, counter, ACTION_DOCK, COMMAND_DRIVE, ACTION_TURN, ACTION_PASS, INSTANT_ACTION_INITIAL_DOCK, v_line_slow, INSTANT_ACTION_CLEAR_LOAD_HANDLER, INSTANT_ACTION_RESET, INSTANT_ACTION_STOP_CHARGE, NODE_ID_UNKNOWN, us_left, BAY_LEFT, BAY_OFFSET_DIST, BAY_RIGHT, BAY_CENTER, old_dir, charging_stopped, ResetException, v_slow, us_right, turn, offset_counter_light, ERROR_LINE_LOST, state, offsetdiff_us1_us2, button_closed_left, button_closed_right, dist_min, button_closed_right_prev, limit_pos_left, limit_pos_right, line_left, line_right, dist_stop_line
    print('CHARGE: Stop')
    if charger_is_charging():
        ui_util_finish_charging()
        time.sleep(1)
        charging_stopped = not (charger_is_charging())
        vda_set_instant_action_status(
            action, (vda_status_failed()) if (charger_is_charging()) else (vda_status_finished()), True
        )
    else:
        vda_set_instant_action_status(action, vda_status_failed(), True)
    vda_publish_status()


TXT_M_I2_mini_switch.add_change_listener("closed", callback)
TXT_M_I3_mini_switch.add_change_listener("closed", callback2)

display.button_clicked("btn_reset", on_btn_reset_clicked)


def math_mean(myList):
    localList = [e for e in myList if isinstance(e, (float, int))]
    if not localList:
        return
    return float(sum(localList)) / len(localList)


import logging

logging.basicConfig(level=logging.DEBUG)
_VERSION = vda_get_factsheet_version()
display.set_attr("txt_version.text", str(f'<h3>APS FTS (Version: {_VERSION})</h3>'))
charger_init()
battery_start_thread()
ResetException = declareResetException()
reset_initiated = False
NODE_ID_UNKNOWN = 'UNKNOWN'
ERROR_LINE_LOST = 'LINE_LOST_ERROR'
last_node_id = NODE_ID_UNKNOWN
drive_sequence = []
INSTANT_ACTION_CLEAR_LOAD_HANDLER = 'clearLoadHandler'
INSTANT_ACTION_INITIAL_DOCK = 'findInitialDockPosition'
INSTANT_ACTION_RESET = 'reset'
INSTANT_ACTION_STOP_CHARGE = 'stopCharging'
ACTION_DOCK = 'DOCK'
ACTION_TURN = 'TURN'
ACTION_PASS = 'PASS'
COMMAND_DRIVE = 'DRIVE'
BAY_LEFT = '1'
BAY_CENTER = '2'
BAY_RIGHT = '3'
# offset of loading bays in mm
BAY_OFFSET_DIST = 30
# in mm
DEFAULT_DOCKING_DISTANCE = 270
# The length that has to be subtracted from the
# edge length when starting from a docked position
FTS_DOCKING_OFFSET = 105
is_docked_at_position = False
# left I2, I7
# right I3, I8
vda_init([ACTION_DOCK, ACTION_TURN, ACTION_PASS], [BAY_LEFT, BAY_CENTER, BAY_RIGHT])
vda_set_load(BAY_LEFT, None, None)
vda_set_load(BAY_CENTER, None, None)
vda_set_load(BAY_RIGHT, None, None)
ui_set_load_indicators()
vda_set_last_node_id(last_node_id)
line_left = 1
line_right = 2
v_line_speed = 400
v_line_slow = -180
v_slow = 180
line_init(v_line_speed, v_line_slow, v_slow)
v = 250
limit_pos_left = -30
limit_pos_right = 30
offset_counter_light = 7
# Especially the charging station has erroneous readings
# due to the interrupted nature of the guiding bars.
#
# Other modules seem to have issues as well, so set the
# allowed offset between the left and right value high.
offsetdiff_us1_us2 = 10
dist_min = 60
dist_stop_line = 21
setup_mqtt()
display.set_attr("label_status.text", 'Start initial docking to DPS.')
threading.Thread(target=battery_monitor_update_thread, daemon=True).start()
while True:
    try:
        do_mainloop()
    except ResetException:
        if reset_initiated:
            reset_state()
            vda_publish_status()
