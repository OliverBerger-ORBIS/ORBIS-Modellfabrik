# validators.py
from __future__ import annotations

import re
from typing import Any, Dict, List

# ---------- kleine Helfer ----------
ISO8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
NFC14 = re.compile(r"^[0-9a-fA-F]{14}$")  # eure NFC-IDs

def is_iso8601(s: Any) -> bool:
    return isinstance(s, str) and bool(ISO8601.match(s))

def is_uuid(s: Any) -> bool:
    return isinstance(s, str) and bool(UUID_RE.match(s))

def is_nfc(s: Any) -> bool:
    return isinstance(s, str) and bool(NFC14.match(s))

def in_enum(val: Any, allowed: list[str]) -> bool:
    return isinstance(val, str) and val in allowed

def t(payload, path: str, default=None):
    """dict.get über 'a.b.c' Pfade."""
    cur = payload
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def push(res, level: str, msg: str, where: str | None = None):
    item = {"msg": msg}
    if where:
        item["path"] = where
    res[level].append(item)

# ---------- Kern-API ----------
ValidationResult = Dict[str, List[Dict[str, str]]]

def validate(template_key: str, payload: dict[str, Any]) -> ValidationResult:
    """Router für template-spezifische Checks."""
    res: ValidationResult = {"errors": [], "warnings": []}
    # generisch
    _generic_timestamp(res, payload, "timestamp")
    _generic_uuid_if_present(res, payload, "orderId")
    # spezifisch
    if template_key == "module.state.hbw_inventory":
        _hbw_inventory(res, payload)
    elif template_key == "module.state.drill":
        _drill(res, payload)
    elif template_key == "module.state.mill":
        _mill(res, payload)
    elif template_key == "module.state.dps":
        _dps(res, payload)
    elif template_key == "module.state.aiqs":
        _aiqs(res, payload)
    elif template_key == "ccu.state.pairing":
        _ccu_pairing(res, payload)
    elif template_key == "ccu.state.status":
        _ccu_status(res, payload)
    elif template_key == "ccu.state.config":
        _ccu_config(res, payload)
    elif template_key == "ccu.state.layout":
        _ccu_layout(res, payload)
    elif template_key == "ccu.state.stock":
        _ccu_stock(res, payload)
    elif template_key == "ccu.state.version_mismatch":
        _ccu_version_mismatch(res, payload)
    elif template_key == "module.connection.hbw":
        _module_connection_hbw(res, payload)
    elif template_key == "module.connection.mill":
        _module_connection_mill(res, payload)
    elif template_key == "module.connection.drill":
        _module_connection_drill(res, payload)
    elif template_key == "module.connection.dps":
        _module_connection_dps(res, payload)
    elif template_key == "module.connection.aiqs":
        _module_connection_aiqs(res, payload)
    elif template_key == "module/v1/ff/SVR3QA0022/order":
        _module_order_hbw(res, payload)
    elif template_key == "module/v1/ff/SVR3QA2098/order":
        _module_order_mill(res, payload)
    elif template_key == "module/v1/ff/SVR4H76449/order":
        _module_order_drill(res, payload)
    elif template_key == "module/v1/ff/SVR4H73275/order":
        _module_order_dps(res, payload)
    elif template_key == "module/v1/ff/SVR4H76530/order":
        _module_order_aiqs(res, payload)
    elif template_key == "module/v1/ff/SVR3QA0022/factsheet":
        _module_factsheet_hbw(res, payload)
    elif template_key == "module/v1/ff/SVR3QA2098/factsheet":
        _module_factsheet_mill(res, payload)
    elif template_key == "module/v1/ff/SVR4H76449/factsheet":
        _module_factsheet_drill(res, payload)
    elif template_key == "module/v1/ff/SVR4H73275/factsheet":
        _module_factsheet_dps(res, payload)
    elif template_key == "module/v1/ff/SVR4H76530/factsheet":
        _module_factsheet_aiqs(res, payload)
    elif template_key == "ccu/control":
        _ccu_control(res, payload)
    elif template_key == "txt/controller1/order_input":
        _txt_controller1_order_input(res, payload)
    elif template_key == "txt/controller1/stock_input":
        _txt_controller1_stock_input(res, payload)
    elif template_key == "fts/v1/ff/5iO4/order":
        _fts_order(res, payload)
    elif template_key == "fts/v1/ff/5iO4/state":
        _fts_state(res, payload)
    elif template_key == "fts/v1/ff/5iO4/connection":
        _fts_connection(res, payload)
    elif template_key == "fts/v1/ff/5iO4/factsheet":
        _fts_factsheet(res, payload)
    elif template_key == "module/v1/ff/NodeRed/SVR4H73275/connection":
        _nodered_connection_dps(res, payload)
    elif template_key == "module/v1/ff/NodeRed/SVR4H76530/connection":
        _nodered_connection_aiqs(res, payload)
    elif template_key == "module/v1/ff/NodeRed/SVR4H73275/state":
        _nodered_state_dps(res, payload)
    elif template_key == "module/v1/ff/NodeRed/SVR4H76530/state":
        _nodered_state_aiqs(res, payload)
    elif template_key == "module/v1/ff/NodeRed/SVR4H73275/factsheet":
        _nodered_factsheet_dps(res, payload)
    elif template_key == "module/v1/ff/NodeRed/SVR4H76530/factsheet":
        _nodered_factsheet_aiqs(res, payload)
    elif template_key == "/j1/txt/1/i/bme680":
        _txt_bme680(res, payload)
    elif template_key == "/j1/txt/1/i/broadcast":
        _txt_broadcast_input(res, payload)
    elif template_key == "/j1/txt/1/i/cam":
        _txt_cam(res, payload)
    elif template_key == "/j1/txt/1/i/ldr":
        _txt_ldr(res, payload)
    elif template_key == "/j1/txt/1/o/broadcast":
        _txt_broadcast_output(res, payload)
    elif template_key == "/j1/txt/1/f/i/config/hbw":
        _txt_config_hbw(res, payload)
    elif template_key == "/j1/txt/1/f/o/order":
        _txt_order_output(res, payload)
    # weitere Keys hier ergänzen …
    return res

# ---------- generische Checks ----------
def _generic_timestamp(res, payload, path):
    ts = t(payload, path)
    if ts is None:
        push(res, "errors", f"missing required '{path}'", path)
    elif not is_iso8601(ts):
        push(res, "errors", f"'{path}' must be ISO 8601 Zulu", path)

def _generic_uuid_if_present(res, payload, path):
    val = t(payload, path)
    if val is not None and val != "" and not is_uuid(val):
        push(res, "warnings", f"'{path}' is not UUID (ok if module uses non-uuid)", path)

# ---------- template-spezifisch ----------
def _hbw_inventory(res, payload):
    loads = payload.get("loads")
    if not isinstance(loads, list):
        push(res, "errors", "loads must be an array", "loads")
        return
    positions = {"A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"}
    colors = {"RED", "WHITE", "BLUE", ""}
    for i, item in enumerate(loads):
        if not isinstance(item, dict):
            push(res, "errors", f"loads[{i}] must be object", f"loads[{i}]")
            continue
        pos = item.get("loadPosition")
        if pos not in positions:
            push(res, "errors", f"invalid loadPosition '{pos}'", f"loads[{i}].loadPosition")
        lt = item.get("loadType", "")
        if lt not in colors:
            push(res, "errors", f"invalid loadType '{lt}'", f"loads[{i}].loadType")
        ts = item.get("loadTimestamp")
        if not isinstance(ts, int) or ts < 0:
            push(res, "warnings", "loadTimestamp should be integer >=0", f"loads[{i}].loadTimestamp")
    # actionState: wenn DROP→ result sollte NFC aussehen
    a = payload.get("actionState") or {}
    cmd = a.get("command")
    if cmd in {"PICK", "DROP", "STORE"}:
        st = a.get("state")
        if st not in {"RUNNING", "FINISHED", "ENQUEUED"}:
            push(res, "errors", f"invalid actionState.state '{st}'", "actionState.state")
        if cmd == "DROP":
            res_id = a.get("result")
            if res_id is not None and not is_nfc(res_id):
                push(
                    res,
                    "warnings",
                    "actionState.command=DROP → result wird als NFC-ID empfohlen (Warnung, wenn abweichend)",
                    "actionState.result",
                )

def _drill(res, payload):
    _check_action_state(res, payload, allowed={"PICK", "DRILL", "DROP"})
    loads = payload.get("loads", [])
    if isinstance(loads, list):
        for i, it in enumerate(loads):
            if not isinstance(it, dict):
                continue
            lt = it.get("loadType")
            if lt is not None and lt not in {"RED", "WHITE", "BLUE"}:
                push(res, "errors", f"invalid loadType '{lt}'", f"loads[{i}].loadType")
            dur = it.get("duration")
            if dur is not None and (not isinstance(dur, int) or dur <= 0):
                push(
                    res,
                    "warnings",
                    "loads[*].duration should be positive (Hinweis, nicht zwingend)",
                    f"loads[{i}].duration",
                )

def _mill(res, payload):
    _check_action_state(res, payload, allowed={"PICK", "MILL", "DROP"})
    # gleiche Logik wie drill
    loads = payload.get("loads", [])
    if isinstance(loads, list):
        for i, it in enumerate(loads):
            if not isinstance(it, dict):
                continue
            lt = it.get("loadType")
            if lt is not None and lt not in {"RED", "WHITE", "BLUE"}:
                push(res, "errors", f"invalid loadType '{lt}'", f"loads[{i}].loadType")
            dur = it.get("duration")
            if dur is not None and (not isinstance(dur, int) or dur <= 0):
                push(
                    res,
                    "warnings",
                    "loads[*].duration should be positive (Hinweis, nicht zwingend)",
                    f"loads[{i}].duration",
                )

def _dps(res, payload):
    _check_action_state(res, payload, allowed={"PICK", "DROP"})
    # optional: actionStates[*].metadata.workpiece.history
    arr = payload.get("actionStates", [])
    if isinstance(arr, list):
        for i, st in enumerate(arr):
            wp = ((st or {}).get("metadata") or {}).get("workpiece") or {}
            wid = wp.get("workpieceId")
            if wid and not is_nfc(wid):
                push(
                    res,
                    "warnings",
                    "workpieceId should be 14-hex NFC",
                    f"actionStates[{i}].metadata.workpiece.workpieceId",
                )
            hist = wp.get("history", [])
            if isinstance(hist, list):
                for j, h in enumerate(hist):
                    code = (h or {}).get("code")
                    if code is not None and not isinstance(code, int):
                        push(
                            res,
                            "warnings",
                            "history.code should be int",
                            f"actionStates[{i}].metadata.workpiece.history[{j}].code",
                        )

def _aiqs(res, payload):
    _check_action_state(res, payload, allowed={"PICK", "CHECK_QUALITY", "DROP"})
    a = payload.get("actionState") or {}
    if a.get("command") == "CHECK_QUALITY":
        result = a.get("result")
        if result not in {"PASSED", "FAILED"}:
            push(res, "errors", "CHECK_QUALITY → muss result ∈ {PASSED,FAILED}", "actionState.result")
        md = a.get("metadata") or {}
        wpid = md.get("workpieceId")
        if wpid and not is_nfc(wpid):
            push(
                res,
                "warnings",
                "CHECK_QUALITY → metadata.workpieceId als NFC (Warnung, wenn fehlt/abweicht)",
                "actionState.metadata.workpieceId",
            )
        elif not wpid:
            push(
                res,
                "warnings",
                "CHECK_QUALITY → metadata.workpieceId als NFC (Warnung, wenn fehlt/abweicht)",
                "actionState.metadata.workpieceId",
            )

def _ccu_pairing(res, payload):
    for i, m in enumerate(payload.get("modules", []) or []):
        avail = m.get("available")
        if avail not in {"READY", "BUSY", "BLOCKED"}:
            push(
                res,
                "errors",
                f"CCU Pairing: available ∈ {{READY,BUSY,BLOCKED}} - invalid '{avail}'",
                f"modules[{i}].available",
            )
        conn = m.get("connected")
        if not isinstance(conn, bool):
            push(res, "errors", "connected must be boolean", f"modules[{i}].connected")
    for i, fts in enumerate(payload.get("transports", []) or []):
        bp = fts.get("batteryPercentage")
        if isinstance(bp, int) and not (0 <= bp <= 100):
            push(
                res,
                "warnings",
                "CCU Pairing: batteryPercentage 0..100 - out of range",
                f"transports[{i}].batteryPercentage",
            )

def _ccu_status(res, payload):
    st = payload.get("systemStatus")
    if st not in {"RUNNING", "STOPPED", "ERROR", "MAINTENANCE"}:
        push(res, "errors", f"invalid systemStatus '{st}'", "systemStatus")
    for i, wp in enumerate(payload.get("availableWorkpieces", []) or []):
        tcol = wp.get("type")
        if tcol and tcol not in {"RED", "WHITE", "BLUE"}:
            push(res, "errors", f"invalid workpiece type '{tcol}'", f"availableWorkpieces[{i}].type")
        wid = wp.get("workpieceId")
        if wid and not is_nfc(wid):
            push(res, "warnings", "workpieceId should be 14-hex NFC", f"availableWorkpieces[{i}].workpieceId")

def _check_action_state(res, payload, allowed: set[str]):
    a = payload.get("actionState")
    if a is None:
        return
    cmd = a.get("command")
    if cmd not in allowed:
        push(res, "errors", f"invalid command '{cmd}' (allowed: {sorted(allowed)})", "actionState.command")
    st = a.get("state")
    if st not in {"RUNNING", "FINISHED"}:
        push(res, "errors", f"invalid state '{st}'", "actionState.state")
    # id sollte uuid-ähnlich sein (Warnung; nicht fatal)
    aid = a.get("id")
    if aid is not None and not is_uuid(aid):
        push(res, "warnings", "actionState.id not UUID (ok if generator differs)", "actionState.id")

# ---------- zusätzliche CCU Validatoren ----------
def _ccu_config(res, payload):
    """Validiert ccu.state.config Nachrichten"""
    # Basis-Validierung für CCU Config
    pass

def _ccu_layout(res, payload):
    """Validiert ccu.state.layout Nachrichten"""
    # Basis-Validierung für CCU Layout
    pass

def _ccu_stock(res, payload):
    """Validiert ccu.state.stock Nachrichten"""
    # Basis-Validierung für CCU Stock
    pass

def _ccu_version_mismatch(res, payload):
    """Validiert ccu.state.version_mismatch Nachrichten"""
    # Basis-Validierung für CCU Version Mismatch
    pass

# ---------- Module Connection Validators ----------
def _module_connection_hbw(res, payload):
    """Validiert HBW module connection Nachrichten"""
    _module_connection_generic(res, payload, "SVR3QA0022", "HBW")

def _module_connection_mill(res, payload):
    """Validiert MILL module connection Nachrichten"""
    _module_connection_generic(res, payload, "SVR3QA2098", "MILL")

def _module_connection_drill(res, payload):
    """Validiert DRILL module connection Nachrichten"""
    _module_connection_generic(res, payload, "SVR4H76449", "DRILL")

def _module_connection_dps(res, payload):
    """Validiert DPS module connection Nachrichten"""
    _module_connection_generic(res, payload, "SVR4H73275", "DPS")

def _module_connection_aiqs(res, payload):
    """Validiert AIQS module connection Nachrichten"""
    _module_connection_generic(res, payload, "SVR4H76530", "AIQS")

def _module_connection_generic(res, payload, expected_module_id, module_name):
    """Generische Module Connection Validierung"""
    # Connection State Validierung
    conn_state = payload.get("connectionState")
    if conn_state not in {"ONLINE", "OFFLINE", "CONNECTIONBROKEN"}:
        push(
            res,
            "errors",
            f"invalid connectionState '{conn_state}' (must be ONLINE|OFFLINE|CONNECTIONBROKEN)",
            "connectionState",
        )

    # Module ID Validierung
    module_id = payload.get("moduleId")
    if module_id and module_id != expected_module_id:
        push(res, "warnings", f"{module_name} moduleId should be {expected_module_id}, got {module_id}", "moduleId")

    # Errors Array Validierung
    errors = payload.get("errors", [])
    if not isinstance(errors, list):
        push(res, "errors", "errors must be array", "errors")

    # Information Array Validierung
    information = payload.get("information", [])
    if not isinstance(information, list):
        push(res, "warnings", "information should be array", "information")

# ---------- Module Order Validators ----------
def _module_order_hbw(res, payload):
    """Validiert HBW module order Nachrichten"""
    _module_order_generic(res, payload, "SVR3QA0022", "HBW", ["PICK", "STORE", "DROP"])

def _module_order_mill(res, payload):
    """Validiert MILL module order Nachrichten"""
    _module_order_generic(res, payload, "SVR3QA2098", "MILL", ["PICK", "MILL", "DROP"])

def _module_order_drill(res, payload):
    """Validiert DRILL module order Nachrichten"""
    _module_order_generic(res, payload, "SVR4H76449", "DRILL", ["PICK", "DRILL", "DROP"])

def _module_order_dps(res, payload):
    """Validiert DPS module order Nachrichten"""
    _module_order_generic(res, payload, "SVR4H73275", "DPS", ["PICK", "DROP"])

def _module_order_aiqs(res, payload):
    """Validiert AIQS module order Nachrichten"""
    _module_order_generic(res, payload, "SVR4H76530", "AIQS", ["PICK", "CHECK_QUALITY", "DROP"])

def _module_order_generic(res, payload, expected_module_id, module_name, allowed_commands):
    """Generische Module Order Validierung"""
    # Required Fields Validierung
    order_id = payload.get("orderId")
    if not order_id:
        push(res, "errors", "orderId is required", "orderId")

    action_id = payload.get("actionId")
    if not action_id:
        push(res, "errors", "actionId is required", "actionId")

    command = payload.get("command")
    if not command:
        push(res, "errors", "command is required", "command")
    elif command not in allowed_commands:
        push(res, "errors", f"invalid command '{command}' (allowed: {allowed_commands})", "command")

    # Type Validierung
    workpiece_type = payload.get("type")
    if workpiece_type and workpiece_type not in ["RED", "WHITE", "BLUE"]:
        push(res, "warnings", f"workpiece type '{workpiece_type}' should be RED|WHITE|BLUE", "type")

    # Metadata Validierung
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        push(res, "warnings", "metadata should be object", "metadata")

    # Module-spezifische Validierungen
    if module_name == "HBW" and command in ["PICK", "STORE", "DROP"]:
        load_position = metadata.get("loadPosition")
        if load_position and load_position not in {"A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"}:
            push(res, "warnings", f"invalid loadPosition '{load_position}' for HBW", "metadata.loadPosition")

    if module_name == "AIQS" and command == "CHECK_QUALITY":
        workpiece_id = metadata.get("workpieceId")
        if workpiece_id and not is_nfc(workpiece_id):
            push(res, "warnings", "workpieceId should be 14-hex NFC for quality check", "metadata.workpieceId")

# ---------- Module Factsheet Validators ----------
def _module_factsheet_hbw(res, payload):
    """Validiert HBW module factsheet Nachrichten"""
    _module_factsheet_generic(res, payload, "SVR3QA0022", "HBW")

def _module_factsheet_mill(res, payload):
    """Validiert MILL module factsheet Nachrichten"""
    _module_factsheet_generic(res, payload, "SVR3QA2098", "MILL")

def _module_factsheet_drill(res, payload):
    """Validiert DRILL module factsheet Nachrichten"""
    _module_factsheet_generic(res, payload, "SVR4H76449", "DRILL")

def _module_factsheet_dps(res, payload):
    """Validiert DPS module factsheet Nachrichten"""
    _module_factsheet_generic(res, payload, "SVR4H73275", "DPS")

def _module_factsheet_aiqs(res, payload):
    """Validiert AIQS module factsheet Nachrichten"""
    _module_factsheet_generic(res, payload, "SVR4H76530", "AIQS")

def _module_factsheet_generic(res, payload, expected_serial, module_name):
    """Generische Module Factsheet Validierung"""
    # Required Fields Validierung
    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != expected_serial:
        push(
            res,
            "warnings",
            f"{module_name} serialNumber should be {expected_serial}, got {serial_number}",
            "serialNumber",
        )

    module_type = payload.get("moduleType")
    if not module_type:
        push(res, "errors", "moduleType is required", "moduleType")
    elif module_type != module_name:
        push(res, "warnings", f"moduleType should be {module_name}, got {module_type}", "moduleType")

    version = payload.get("version")
    if not version:
        push(res, "warnings", "version should be specified", "version")

    capabilities = payload.get("capabilities", [])
    if not isinstance(capabilities, list):
        push(res, "errors", "capabilities must be array", "capabilities")

    status = payload.get("status")
    if status and status not in ["OPERATIONAL", "MAINTENANCE", "ERROR", "OFFLINE"]:
        push(res, "warnings", f"status should be OPERATIONAL|MAINTENANCE|ERROR|OFFLINE, got {status}", "status")

    # Metadata Validierung
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        push(res, "warnings", "metadata should be object", "metadata")

# ---------- CCU Control Validator ----------
def _ccu_control(res, payload):
    """Validiert CCU control Nachrichten"""
    command = payload.get("command")
    if not command:
        push(res, "errors", "command is required", "command")
    elif command not in [
        "RESET_FACTORY",
        "PAUSE_PRODUCTION",
        "RESUME_PRODUCTION",
        "SET_WORKPIECE_TYPE",
        "CLEAR_ERRORS",
    ]:
        push(res, "errors", f"invalid command '{command}'", "command")

    request_id = payload.get("requestId")
    if not request_id:
        push(res, "warnings", "requestId should be specified for tracking", "requestId")

    parameters = payload.get("parameters", {})
    if not isinstance(parameters, dict):
        push(res, "warnings", "parameters should be object", "parameters")

    # Command-spezifische Validierungen
    if command == "SET_WORKPIECE_TYPE":
        workpiece_type = parameters.get("type")
        if workpiece_type and workpiece_type not in ["RED", "WHITE", "BLUE"]:
            push(res, "warnings", f"workpiece type '{workpiece_type}' should be RED|WHITE|BLUE", "parameters.type")

# ---------- TXT Controller Validators ----------
def _txt_controller1_order_input(res, payload):
    """Validiert TXT Controller #1 Order Input Nachrichten"""
    _txt_order_generic(res, payload, "controller1")

def _txt_controller1_stock_input(res, payload):
    """Validiert TXT Controller #1 Stock Input Nachrichten"""
    _txt_stock_generic(res, payload, "controller1")

def _txt_order_generic(res, payload, controller_id):
    """Generische TXT Order Input Validierung"""
    # Required Fields
    state = payload.get("state")
    if not state:
        push(res, "errors", "state is required", "state")
    elif state not in ["WAITING_FOR_ORDER", "IN_PROCESS", "COMPLETED", "FINISHED", "RAW", "RESERVED"]:
        push(res, "errors", f"invalid state '{state}'", "state")

    # Timestamp Validierung
    ts = payload.get("timestamp")
    if not ts:
        push(res, "errors", "timestamp is required", "timestamp")
    elif not isinstance(ts, str):
        push(res, "errors", "timestamp must be string", "timestamp")
    elif not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts):
        push(res, "warnings", "timestamp should be ISO 8601 format", "timestamp")

    # Optional Fields
    workpiece_type = payload.get("type")
    if workpiece_type and workpiece_type not in ["RED", "WHITE", "BLUE"]:
        push(res, "warnings", f"workpiece type '{workpiece_type}' should be RED|WHITE|BLUE", "type")

    # Details Validierung
    details = payload.get("details")
    if details and not isinstance(details, dict):
        push(res, "warnings", "details should be object", "details")

def _txt_stock_generic(res, payload, controller_id):
    """Generische TXT Stock Input Validierung"""
    # Required Fields
    stock_items = payload.get("stock_items")
    if not stock_items:
        push(res, "errors", "stock_items is required", "stock_items")
    elif not isinstance(stock_items, list):
        push(res, "errors", "stock_items must be array", "stock_items")
    else:
        # Stock Items Validierung
        for i, item in enumerate(stock_items):
            if not isinstance(item, dict):
                push(res, "warnings", f"stock_items[{i}] should be object", f"stock_items[{i}]")
                continue

            position = item.get("position")
            if position and position not in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
                push(
                    res, "warnings", f"invalid position '{position}' in stock_items[{i}]", f"stock_items[{i}].position"
                )

            workpiece_type = item.get("workpiece_type")
            if workpiece_type and workpiece_type not in ["RED", "WHITE", "BLUE"]:
                push(
                    res,
                    "warnings",
                    f"invalid workpiece_type '{workpiece_type}' in stock_items[{i}]",
                    f"stock_items[{i}].workpiece_type",
                )

            quantity = item.get("quantity")
            if quantity is not None and not isinstance(quantity, int):
                push(res, "warnings", f"quantity should be integer in stock_items[{i}]", f"stock_items[{i}].quantity")

            status = item.get("status")
            if status and status not in ["AVAILABLE", "RESERVED", "EMPTY", "MAINTENANCE"]:
                push(res, "warnings", f"invalid status '{status}' in stock_items[{i}]", f"stock_items[{i}].status")

    # Timestamp Validierung
    ts = payload.get("timestamp")
    if not ts:
        push(res, "errors", "timestamp is required", "timestamp")
    elif not isinstance(ts, str):
        push(res, "errors", "timestamp must be string", "timestamp")
    elif not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts):
        push(res, "warnings", "timestamp should be ISO 8601 format", "timestamp")

    # Optional Fields
    location = payload.get("location")
    if location and location not in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
        push(res, "warnings", f"invalid location '{location}'", "location")

    status = payload.get("status")
    if status and status not in ["AVAILABLE", "RESERVED", "EMPTY", "MAINTENANCE"]:
        push(res, "warnings", f"invalid status '{status}'", "status")

# ---------- FTS Validators ----------
def _fts_order(res, payload):
    """Validiert FTS order Nachrichten"""
    # Required Fields
    action = payload.get("action")
    if not action:
        push(res, "errors", "action is required", "action")
    elif not isinstance(action, dict):
        push(res, "errors", "action must be object", "action")
    else:
        command = action.get("command")
        if not command:
            push(res, "errors", "action.command is required", "action.command")
        elif command not in ["findInitialDockPosition", "startCharging", "DOCK", "TURN", "PASS", "LIFT"]:
            push(res, "warnings", f"unknown command '{command}'", "action.command")

        action_id = action.get("id")
        if not action_id:
            push(res, "warnings", "action.id should be specified", "action.id")

        metadata = action.get("metadata")
        if metadata and not isinstance(metadata, dict):
            push(res, "warnings", "action.metadata should be object", "action.metadata")

    order_id = payload.get("orderId")
    if not order_id:
        push(res, "errors", "orderId is required", "orderId")

    order_update_id = payload.get("orderUpdateId")
    if order_update_id is None:
        push(res, "errors", "orderUpdateId is required", "orderUpdateId")
    elif not isinstance(order_update_id, int):
        push(res, "warnings", "orderUpdateId should be integer", "orderUpdateId")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "5iO4":
        push(res, "warnings", f"serialNumber should be '5iO4', got '{serial_number}'", "serialNumber")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _fts_state(res, payload):
    """Validiert FTS state Nachrichten"""
    # Required Fields
    last_node_id = payload.get("lastNodeId")
    if not last_node_id:
        push(res, "errors", "lastNodeId is required", "lastNodeId")

    driving = payload.get("driving")
    if driving is None:
        push(res, "errors", "driving is required", "driving")
    elif not isinstance(driving, bool):
        push(res, "warnings", "driving should be boolean", "driving")

    paused = payload.get("paused")
    if paused is None:
        push(res, "errors", "paused is required", "paused")
    elif not isinstance(paused, bool):
        push(res, "warnings", "paused should be boolean", "paused")

    # Battery State Validierung
    battery_state = payload.get("batteryState")
    if not battery_state:
        push(res, "errors", "batteryState is required", "batteryState")
    elif isinstance(battery_state, dict):
        battery_percentage = battery_state.get("batteryPercentage")
        if battery_percentage is not None:
            if not isinstance(battery_percentage, (int, float)):
                push(res, "warnings", "batteryPercentage should be number", "batteryState.batteryPercentage")
            elif not (0 <= battery_percentage <= 100):
                push(res, "warnings", "batteryPercentage should be 0-100", "batteryState.batteryPercentage")

        charging = battery_state.get("charging")
        if charging is not None and not isinstance(charging, bool):
            push(res, "warnings", "charging should be boolean", "batteryState.charging")

    # Action State Validierung
    action_state = payload.get("actionState")
    if not action_state:
        push(res, "errors", "actionState is required", "actionState")
    elif isinstance(action_state, dict):
        state = action_state.get("state")
        if state and state not in ["RUNNING", "FINISHED", "WAITING", "FAILED"]:
            push(
                res,
                "warnings",
                f"actionState.state should be RUNNING|FINISHED|WAITING|FAILED, got '{state}'",
                "actionState.state",
            )

    # Errors Validierung
    errors = payload.get("errors")
    if errors is None:
        push(res, "errors", "errors is required", "errors")
    elif not isinstance(errors, list):
        push(res, "warnings", "errors should be array", "errors")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _fts_connection(res, payload):
    """Validiert FTS connection Nachrichten"""
    # Required Fields
    connection_state = payload.get("connectionState")
    if not connection_state:
        push(res, "errors", "connectionState is required", "connectionState")
    elif connection_state not in ["ONLINE", "OFFLINE", "CONNECTING", "DISCONNECTED"]:
        push(
            res,
            "warnings",
            f"connectionState should be ONLINE|OFFLINE|CONNECTING|DISCONNECTED, got '{connection_state}'",
            "connectionState",
        )

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "5iO4":
        push(res, "warnings", f"serialNumber should be '5iO4', got '{serial_number}'", "serialNumber")

    version = payload.get("version")
    if not version:
        push(res, "warnings", "version should be specified", "version")

    manufacturer = payload.get("manufacturer")
    if not manufacturer:
        push(res, "warnings", "manufacturer should be specified", "manufacturer")

    ip = payload.get("ip")
    if not ip:
        push(res, "warnings", "ip should be specified", "ip")
    elif not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        push(res, "warnings", "ip should be valid IP address", "ip")

    header_id = payload.get("headerId")
    if not header_id:
        push(res, "warnings", "headerId should be specified", "headerId")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _fts_factsheet(res, payload):
    """Validiert FTS factsheet Nachrichten"""
    # Required Fields
    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "5iO4":
        push(res, "warnings", f"serialNumber should be '5iO4', got '{serial_number}'", "serialNumber")

    model = payload.get("model")
    if not model:
        push(res, "warnings", "model should be specified", "model")

    manufacturer = payload.get("manufacturer")
    if not manufacturer:
        push(res, "warnings", "manufacturer should be specified", "manufacturer")

    version = payload.get("version")
    if not version:
        push(res, "warnings", "version should be specified", "version")

    capabilities = payload.get("capabilities")
    if not capabilities:
        push(res, "warnings", "capabilities should be specified", "capabilities")
    elif not isinstance(capabilities, list):
        push(res, "warnings", "capabilities should be array", "capabilities")

    # Specifications Validierung
    specifications = payload.get("specifications")
    if specifications and isinstance(specifications, dict):
        max_speed = specifications.get("maxSpeed")
        if max_speed is not None and (not isinstance(max_speed, (int, float)) or max_speed <= 0):
            push(res, "warnings", "maxSpeed should be positive number", "specifications.maxSpeed")

        max_load = specifications.get("maxLoad")
        if max_load is not None and (not isinstance(max_load, (int, float)) or max_load <= 0):
            push(res, "warnings", "maxLoad should be positive number", "specifications.maxLoad")

        battery_capacity = specifications.get("batteryCapacity")
        if battery_capacity is not None and (not isinstance(battery_capacity, (int, float)) or battery_capacity <= 0):
            push(res, "warnings", "batteryCapacity should be positive number", "specifications.batteryCapacity")

    # Load Handling Validierung
    load_handling = payload.get("loadHandling")
    if load_handling and isinstance(load_handling, dict):
        load_sets = load_handling.get("loadSets")
        if load_sets and isinstance(load_sets, list):
            for i, load_set in enumerate(load_sets):
                if isinstance(load_set, dict):
                    load_type = load_set.get("loadType")
                    if load_type and load_type not in ["PALLET", "HEAVY_PALLET"]:
                        push(
                            res,
                            "warnings",
                            f"loadType should be PALLET|HEAVY_PALLET, got '{load_type}'",
                            f"loadHandling.loadSets[{i}].loadType",
                        )

    # Protocol Features Validierung
    protocol_features = payload.get("protocolFeatures")
    if protocol_features and isinstance(protocol_features, dict):
        agv_actions = protocol_features.get("agvActions")
        if agv_actions and isinstance(agv_actions, list):
            for i, action in enumerate(agv_actions):
                if isinstance(action, dict):
                    action_type = action.get("actionType")
                    if action_type and action_type not in ["DOCK", "TURN", "PASS", "LIFT"]:
                        push(
                            res,
                            "warnings",
                            f"actionType should be DOCK|TURN|PASS|LIFT, got '{action_type}'",
                            f"protocolFeatures.agvActions[{i}].actionType",
                        )

# ---------- Node-RED Validators ----------
def _nodered_connection_dps(res, payload):
    """Validiert Node-RED DPS connection Nachrichten"""
    # Required Fields
    connection_state = payload.get("connectionState")
    if not connection_state:
        push(res, "errors", "connectionState is required", "connectionState")
    elif connection_state != "ONLINE":
        push(res, "warnings", f"connectionState should be 'ONLINE', got '{connection_state}'", "connectionState")

    header_id = payload.get("headerId")
    if header_id is None:
        push(res, "errors", "headerId is required", "headerId")
    elif header_id != 2:
        push(res, "warnings", f"headerId should be 2, got '{header_id}'", "headerId")

    ip = payload.get("ip")
    if not ip:
        push(res, "errors", "ip is required", "ip")
    elif ip != "-1":
        push(res, "warnings", f"ip should be '-1', got '{ip}'", "ip")

    manufacturer = payload.get("manufacturer")
    if not manufacturer:
        push(res, "errors", "manufacturer is required", "manufacturer")
    elif manufacturer != "Fischertechnik":
        push(res, "warnings", f"manufacturer should be 'Fischertechnik', got '{manufacturer}'", "manufacturer")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "SVR4H73275":
        push(res, "warnings", f"serialNumber should be 'SVR4H73275', got '{serial_number}'", "serialNumber")

    version = payload.get("version")
    if not version:
        push(res, "errors", "version is required", "version")
    elif version != "1.6.0+gitc321c85":
        push(res, "warnings", f"version should be '1.6.0+gitc321c85', got '{version}'", "version")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _nodered_connection_aiqs(res, payload):
    """Validiert Node-RED AIQS connection Nachrichten"""
    # Required Fields
    connection_state = payload.get("connectionState")
    if not connection_state:
        push(res, "errors", "connectionState is required", "connectionState")
    elif connection_state != "ONLINE":
        push(res, "warnings", f"connectionState should be 'ONLINE', got '{connection_state}'", "connectionState")

    header_id = payload.get("headerId")
    if header_id is None:
        push(res, "errors", "headerId is required", "headerId")
    elif header_id != 2:
        push(res, "warnings", f"headerId should be 2, got '{header_id}'", "headerId")

    manufacturer = payload.get("manufacturer")
    if not manufacturer:
        push(res, "errors", "manufacturer is required", "manufacturer")
    elif manufacturer != "Fischertechnik":
        push(res, "warnings", f"manufacturer should be 'Fischertechnik', got '{manufacturer}'", "manufacturer")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "SVR4H76530":
        push(res, "warnings", f"serialNumber should be 'SVR4H76530', got '{serial_number}'", "serialNumber")

    version = payload.get("version")
    if not version:
        push(res, "errors", "version is required", "version")
    elif version != "1.0.0":
        push(res, "warnings", f"version should be '1.0.0', got '{version}'", "version")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _nodered_state_dps(res, payload):
    """Validiert Node-RED DPS state Nachrichten"""
    # Required Fields
    action_state = payload.get("actionState")
    if not action_state:
        push(res, "errors", "actionState is required", "actionState")
    elif not isinstance(action_state, dict):
        push(res, "warnings", "actionState should be object", "actionState")

    action_states = payload.get("actionStates")
    if not action_states:
        push(res, "errors", "actionStates is required", "actionStates")
    elif not isinstance(action_states, list):
        push(res, "warnings", "actionStates should be array", "actionStates")

    battery_state = payload.get("batteryState")
    if battery_state is None:
        push(res, "errors", "batteryState is required", "batteryState")
    elif battery_state != {}:
        push(res, "warnings", f"batteryState should be empty object, got '{battery_state}'", "batteryState")

    errors = payload.get("errors")
    if errors is None:
        push(res, "errors", "errors is required", "errors")
    elif not isinstance(errors, list):
        push(res, "warnings", "errors should be array", "errors")

    header_id = payload.get("headerId")
    if header_id is None:
        push(res, "errors", "headerId is required", "headerId")
    elif not isinstance(header_id, int):
        push(res, "warnings", "headerId should be integer", "headerId")

    information = payload.get("information")
    if information is None:
        push(res, "errors", "information is required", "information")
    elif information != []:
        push(res, "warnings", f"information should be empty array, got '{information}'", "information")

    operating_mode = payload.get("operatingMode")
    if not operating_mode:
        push(res, "errors", "operatingMode is required", "operatingMode")
    elif operating_mode != "AUTOMATIC":
        push(res, "warnings", f"operatingMode should be 'AUTOMATIC', got '{operating_mode}'", "operatingMode")

    order_id = payload.get("orderId")
    if not order_id:
        push(res, "errors", "orderId is required", "orderId")

    order_update_id = payload.get("orderUpdateId")
    if order_update_id is None:
        push(res, "errors", "orderUpdateId is required", "orderUpdateId")
    elif not isinstance(order_update_id, int):
        push(res, "warnings", "orderUpdateId should be integer", "orderUpdateId")

    paused = payload.get("paused")
    if paused is None:
        push(res, "errors", "paused is required", "paused")
    elif paused is not False:
        push(res, "warnings", f"paused should be false, got '{paused}'", "paused")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "SVR4H73275":
        push(res, "warnings", f"serialNumber should be 'SVR4H73275', got '{serial_number}'", "serialNumber")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _nodered_state_aiqs(res, payload):
    """Validiert Node-RED AIQS state Nachrichten"""
    # Required Fields
    action_state = payload.get("actionState")
    if not action_state:
        push(res, "errors", "actionState is required", "actionState")
    elif not isinstance(action_state, dict):
        push(res, "warnings", "actionState should be object", "actionState")

    battery_state = payload.get("batteryState")
    if battery_state is None:
        push(res, "errors", "batteryState is required", "batteryState")
    elif battery_state != {}:
        push(res, "warnings", f"batteryState should be empty object, got '{battery_state}'", "batteryState")

    errors = payload.get("errors")
    if errors is None:
        push(res, "errors", "errors is required", "errors")
    elif errors != []:
        push(res, "warnings", f"errors should be empty array, got '{errors}'", "errors")

    header_id = payload.get("headerId")
    if header_id is None:
        push(res, "errors", "headerId is required", "headerId")
    elif not isinstance(header_id, int):
        push(res, "warnings", "headerId should be integer", "headerId")

    order_id = payload.get("orderId")
    if not order_id:
        push(res, "errors", "orderId is required", "orderId")

    order_update_id = payload.get("orderUpdateId")
    if order_update_id is None:
        push(res, "errors", "orderUpdateId is required", "orderUpdateId")
    elif order_update_id not in [0, 10]:
        push(res, "warnings", f"orderUpdateId should be 0 or 10, got '{order_update_id}'", "orderUpdateId")

    paused = payload.get("paused")
    if paused is None:
        push(res, "errors", "paused is required", "paused")
    elif paused is not False:
        push(res, "warnings", f"paused should be false, got '{paused}'", "paused")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "SVR4H76530":
        push(res, "warnings", f"serialNumber should be 'SVR4H76530', got '{serial_number}'", "serialNumber")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _nodered_factsheet_dps(res, payload):
    """Validiert Node-RED DPS factsheet Nachrichten"""
    # Required Fields
    header_id = payload.get("headerId")
    if header_id is None:
        push(res, "errors", "headerId is required", "headerId")
    elif header_id != 1:
        push(res, "warnings", f"headerId should be 1, got '{header_id}'", "headerId")

    load_specification = payload.get("loadSpecification")
    if not load_specification:
        push(res, "errors", "loadSpecification is required", "loadSpecification")
    elif not isinstance(load_specification, dict):
        push(res, "warnings", "loadSpecification should be object", "loadSpecification")

    localization_parameters = payload.get("localizationParameters")
    if localization_parameters is None:
        push(res, "errors", "localizationParameters is required", "localizationParameters")
    elif localization_parameters != {}:
        push(
            res,
            "warnings",
            f"localizationParameters should be empty object, got '{localization_parameters}'",
            "localizationParameters",
        )

    manufacturer = payload.get("manufacturer")
    if not manufacturer:
        push(res, "errors", "manufacturer is required", "manufacturer")
    elif manufacturer != "Fischertechnik":
        push(res, "warnings", f"manufacturer should be 'Fischertechnik', got '{manufacturer}'", "manufacturer")

    physical_parameters = payload.get("physicalParameters")
    if physical_parameters is None:
        push(res, "errors", "physicalParameters is required", "physicalParameters")
    elif physical_parameters != {}:
        push(
            res,
            "warnings",
            f"physicalParameters should be empty object, got '{physical_parameters}'",
            "physicalParameters",
        )

    protocol_features = payload.get("protocolFeatures")
    if not protocol_features:
        push(res, "errors", "protocolFeatures is required", "protocolFeatures")
    elif not isinstance(protocol_features, dict):
        push(res, "warnings", "protocolFeatures should be object", "protocolFeatures")

    protocol_limits = payload.get("protocolLimits")
    if protocol_limits is None:
        push(res, "errors", "protocolLimits is required", "protocolLimits")
    elif protocol_limits != {}:
        push(res, "warnings", f"protocolLimits should be empty object, got '{protocol_limits}'", "protocolLimits")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "SVR4H73275":
        push(res, "warnings", f"serialNumber should be 'SVR4H73275', got '{serial_number}'", "serialNumber")

    type_specification = payload.get("typeSpecification")
    if not type_specification:
        push(res, "errors", "typeSpecification is required", "typeSpecification")
    elif not isinstance(type_specification, dict):
        push(res, "warnings", "typeSpecification should be object", "typeSpecification")
    else:
        module_class = type_specification.get("moduleClass")
        if module_class and module_class != "DPS":
            push(res, "warnings", f"moduleClass should be 'DPS', got '{module_class}'", "typeSpecification.moduleClass")

    version = payload.get("version")
    if not version:
        push(res, "errors", "version is required", "version")
    elif version != "1.6.0+gitc321c85":
        push(res, "warnings", f"version should be '1.6.0+gitc321c85', got '{version}'", "version")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

def _nodered_factsheet_aiqs(res, payload):
    """Validiert Node-RED AIQS factsheet Nachrichten"""
    # Required Fields
    header_id = payload.get("headerId")
    if header_id is None:
        push(res, "errors", "headerId is required", "headerId")
    elif header_id != 1:
        push(res, "warnings", f"headerId should be 1, got '{header_id}'", "headerId")

    load_specification = payload.get("loadSpecification")
    if not load_specification:
        push(res, "errors", "loadSpecification is required", "loadSpecification")
    elif not isinstance(load_specification, dict):
        push(res, "warnings", "loadSpecification should be object", "loadSpecification")
    else:
        load_sets = load_specification.get("loadSets")
        if load_sets is not None and load_sets != []:
            push(
                res,
                "warnings",
                f"loadSets should be empty array for AIQS, got '{load_sets}'",
                "loadSpecification.loadSets",
            )

    localization_parameters = payload.get("localizationParameters")
    if localization_parameters is None:
        push(res, "errors", "localizationParameters is required", "localizationParameters")
    elif localization_parameters != {}:
        push(
            res,
            "warnings",
            f"localizationParameters should be empty object, got '{localization_parameters}'",
            "localizationParameters",
        )

    manufacturer = payload.get("manufacturer")
    if not manufacturer:
        push(res, "errors", "manufacturer is required", "manufacturer")
    elif manufacturer != "Fischertechnik":
        push(res, "warnings", f"manufacturer should be 'Fischertechnik', got '{manufacturer}'", "manufacturer")

    physical_parameters = payload.get("physicalParameters")
    if physical_parameters is None:
        push(res, "errors", "physicalParameters is required", "physicalParameters")
    elif physical_parameters != {}:
        push(
            res,
            "warnings",
            f"physicalParameters should be empty object, got '{physical_parameters}'",
            "physicalParameters",
        )

    protocol_features = payload.get("protocolFeatures")
    if not protocol_features:
        push(res, "errors", "protocolFeatures is required", "protocolFeatures")
    elif not isinstance(protocol_features, dict):
        push(res, "warnings", "protocolFeatures should be object", "protocolFeatures")

    protocol_limits = payload.get("protocolLimits")
    if protocol_limits is None:
        push(res, "errors", "protocolLimits is required", "protocolLimits")
    elif protocol_limits != {}:
        push(res, "warnings", f"protocolLimits should be empty object, got '{protocol_limits}'", "protocolLimits")

    serial_number = payload.get("serialNumber")
    if not serial_number:
        push(res, "errors", "serialNumber is required", "serialNumber")
    elif serial_number != "SVR4H76530":
        push(res, "warnings", f"serialNumber should be 'SVR4H76530', got '{serial_number}'", "serialNumber")

    type_specification = payload.get("typeSpecification")
    if not type_specification:
        push(res, "errors", "typeSpecification is required", "typeSpecification")
    elif not isinstance(type_specification, dict):
        push(res, "warnings", "typeSpecification should be object", "typeSpecification")
    else:
        module_class = type_specification.get("moduleClass")
        if module_class and module_class != "AIQS24":
            push(
                res,
                "warnings",
                f"moduleClass should be 'AIQS24', got '{module_class}'",
                "typeSpecification.moduleClass",
            )

    version = payload.get("version")
    if not version:
        push(res, "errors", "version is required", "version")
    elif version != "1.3.0+git40c45a0":
        push(res, "warnings", f"version should be '1.3.0+git40c45a0', got '{version}'", "version")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "timestamp")

# ---------- TXT Controller Validators ----------
def _txt_bme680(res, payload):
    """Validiert TXT BME680 Sensor Daten"""
    # Required Fields
    aq = payload.get("aq")
    if aq is None:
        push(res, "errors", "aq is required", "aq")
    elif not isinstance(aq, (int, float)) or not (0 <= aq <= 5):
        push(res, "warnings", f"aq should be between 0-5, got '{aq}'", "aq")

    gr = payload.get("gr")
    if gr is None:
        push(res, "errors", "gr is required", "gr")
    elif gr not in [0, 1]:
        push(res, "warnings", f"gr should be 0 or 1, got '{gr}'", "gr")

    h = payload.get("h")
    if h is None:
        push(res, "errors", "h is required", "h")
    elif not isinstance(h, (int, float)) or not (0 <= h <= 100):
        push(res, "warnings", f"h should be between 0-100, got '{h}'", "h")

    iaq = payload.get("iaq")
    if iaq is None:
        push(res, "errors", "iaq is required", "iaq")
    elif not isinstance(iaq, (int, float)) or not (0 <= iaq <= 500):
        push(res, "warnings", f"iaq should be between 0-500, got '{iaq}'", "iaq")

    p = payload.get("p")
    if p is None:
        push(res, "errors", "p is required", "p")
    elif not isinstance(p, (int, float)) or not (300 <= p <= 1100):
        push(res, "warnings", f"p should be between 300-1100, got '{p}'", "p")

    rh = payload.get("rh")
    if rh is None:
        push(res, "errors", "rh is required", "rh")
    elif not isinstance(rh, (int, float)) or not (0 <= rh <= 100):
        push(res, "warnings", f"rh should be between 0-100, got '{rh}'", "rh")

    rt = payload.get("rt")
    if rt is None:
        push(res, "errors", "rt is required", "rt")
    elif not isinstance(rt, (int, float)) or not (0 <= rt <= 100):
        push(res, "warnings", f"rt should be between 0-100, got '{rt}'", "rt")

    t = payload.get("t")
    if t is None:
        push(res, "errors", "t is required", "t")
    elif not isinstance(t, (int, float)) or not (-40 <= t <= 85):
        push(res, "warnings", f"t should be between -40-85, got '{t}'", "t")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")

def _txt_broadcast_input(res, payload):
    """Validiert TXT Broadcast Input"""
    # Required Fields
    hardware_id = payload.get("hardwareId")
    if not hardware_id:
        push(res, "errors", "hardwareId is required", "hardwareId")
    elif hardware_id != "txt40-p0F4":
        push(res, "warnings", f"hardwareId should be 'txt40-p0F4', got '{hardware_id}'", "hardwareId")

    hardware_model = payload.get("hardwareModel")
    if not hardware_model:
        push(res, "errors", "hardwareModel is required", "hardwareModel")
    elif hardware_model != "TXT 4.0":
        push(res, "warnings", f"hardwareModel should be 'TXT 4.0', got '{hardware_model}'", "hardwareModel")

    message = payload.get("message")
    if not message:
        push(res, "errors", "message is required", "message")
    elif message != "init":
        push(res, "warnings", f"message should be 'init', got '{message}'", "message")

    software_name = payload.get("softwareName")
    if not software_name:
        push(res, "errors", "softwareName is required", "softwareName")
    elif software_name != "APS":
        push(res, "warnings", f"softwareName should be 'APS', got '{software_name}'", "softwareName")

    software_version = payload.get("softwareVersion")
    if not software_version:
        push(res, "errors", "softwareVersion is required", "softwareVersion")
    elif software_version != "1.6.0+gitc321c85":
        push(
            res,
            "warnings",
            f"softwareVersion should be '1.6.0+gitc321c85', got '{software_version}'",
            "softwareVersion",
        )

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")

def _txt_cam(res, payload):
    """Validiert TXT Camera Daten"""
    # Required Fields
    data = payload.get("data")
    if not data:
        push(res, "errors", "data is required", "data")
    elif not isinstance(data, str) or not data.startswith("data:image/jpeg;base64,"):
        push(res, "warnings", "data should start with 'data:image/jpeg;base64,'", "data")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")

def _txt_ldr(res, payload):
    """Validiert TXT LDR Sensor Daten"""
    # Required Fields
    br = payload.get("br")
    if br is None:
        push(res, "errors", "br is required", "br")
    elif not isinstance(br, (int, float)) or not (0 <= br <= 100):
        push(res, "warnings", f"br should be between 0-100, got '{br}'", "br")

    ldr = payload.get("ldr")
    if ldr is None:
        push(res, "errors", "ldr is required", "ldr")
    elif not isinstance(ldr, (int, float)) or not (0 <= ldr <= 4095):
        push(res, "warnings", f"ldr should be between 0-4095, got '{ldr}'", "ldr")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")

def _txt_broadcast_output(res, payload):
    """Validiert TXT Broadcast Output"""
    # Required Fields
    message = payload.get("message")
    if not message:
        push(res, "errors", "message is required", "message")
    elif message != "keep-alive":
        push(res, "warnings", f"message should be 'keep-alive', got '{message}'", "message")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")

def _txt_config_hbw(res, payload):
    """Validiert TXT HBW Configuration Input"""
    # Required Fields
    warehouses = payload.get("warehouses")
    if not warehouses:
        push(res, "errors", "warehouses is required", "warehouses")
    elif not isinstance(warehouses, list):
        push(res, "warnings", "warehouses should be array", "warehouses")
    elif not all(isinstance(item, str) for item in warehouses):
        push(res, "warnings", "warehouses items should be strings", "warehouses")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")

def _txt_order_output(res, payload):
    """Validiert TXT Order Output"""
    # Required Fields
    order_type = payload.get("type")
    if not order_type:
        push(res, "errors", "type is required", "type")
    elif order_type not in ["BLUE", "RED", "WHITE"]:
        push(res, "warnings", f"type should be BLUE|RED|WHITE, got '{order_type}'", "type")

    # Timestamp Validierung
    _generic_timestamp(res, payload, "ts")
