"""
Object Detection Capture Workflow (MVP)

Goal:
- Prepare synchronized capture sessions with minimal MQTT metadata feed
- Store files in a dedicated per-session folder
- Keep video control manual (OBS) in MVP, but provide a guided flow
"""

from __future__ import annotations

import atexit
import json
import re
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import streamlit as st

from ..utils.logging_config import get_logger
from ..utils.path_constants import PROJECT_ROOT
from ..utils.utc_iso_timestamp import utc_iso_timestamp_ms
from .settings_manager import SettingsManager

try:
    import paho.mqtt.client as mqtt

    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None


logger = get_logger("session_manager.object_detection_capture")

_SESSION_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_ORDER_ID_KEYS = {"orderid", "order_id", "productionorderid", "transportorderid"}
_NFC_TAG_KEYS = {"nfctag", "nfc_tag", "nfcid", "nfc_id", "tagid"}
_PHASE_KEYS = {"phase", "step", "orderphase", "state"}

_runtime_lock = threading.Lock()
_runtime: dict[str, Any] = {
    "active": False,
    "connected": False,
    "client": None,
    "session_name": "",
    "session_dir": None,
    "manifest_path": None,
    "meta_file": None,
    "full_file": None,
    "topic_filters": ["#"],
    "save_full_events": False,
    "full_events_exclusion_preset": "none",
    "captured_min_events": 0,
    "captured_full_events": 0,
    "last_order_id": "",
    "last_nfc_tag": "",
    "started_at": "",
}

_shutdown_registered = False

# Optional full-events exclusion presets (for QA log only)
FULL_EVENTS_PRESET_NONE = "none"
FULL_EVENTS_PRESET_EXCLUDE_CAM = "exclude_cam"
FULL_EVENTS_PRESET_EXCLUDE_APS_SENSORS = "exclude_aps_sensors"
FULL_EVENTS_PRESET_EXCLUDE_ARDUINO = "exclude_arduino"
FULL_EVENTS_PRESET_EXCLUDE_ALL_SENSORS = "exclude_all_sensors"
VALID_FULL_EVENTS_PRESETS = {
    FULL_EVENTS_PRESET_NONE,
    FULL_EVENTS_PRESET_EXCLUDE_CAM,
    FULL_EVENTS_PRESET_EXCLUDE_APS_SENSORS,
    FULL_EVENTS_PRESET_EXCLUDE_ARDUINO,
    FULL_EVENTS_PRESET_EXCLUDE_ALL_SENSORS,
}


def _get_default_settings() -> dict[str, Any]:
    return {
        "base_directory": "data/osf-data/sessions/object-detection",
        "mqtt_broker": {
            "host": "192.168.0.100",
            "port": 1883,
            "qos": 1,
            "timeout": 5,
            "username": "default",
            "password": "default",
        },
        "capture": {
            "topic_filters": ["#"],
            "save_full_events": False,
            "full_events_exclusion_preset": FULL_EVENTS_PRESET_NONE,
            "video_filename": "video.mp4",
        },
    }


def _load_settings(settings_manager: SettingsManager) -> dict[str, Any]:
    raw = settings_manager.get_setting("object_detection", "capture_settings", {})
    defaults = _get_default_settings()
    if not isinstance(raw, dict):
        return defaults

    merged = {
        "base_directory": str(raw.get("base_directory", defaults["base_directory"]) or defaults["base_directory"]),
        "mqtt_broker": dict(defaults["mqtt_broker"]),
        "capture": dict(defaults["capture"]),
    }
    if isinstance(raw.get("mqtt_broker"), dict):
        merged["mqtt_broker"].update(raw["mqtt_broker"])
    if isinstance(raw.get("capture"), dict):
        merged["capture"].update(raw["capture"])
    return merged


def _save_settings(settings_manager: SettingsManager, settings: dict[str, Any]) -> None:
    settings_manager.set_setting("object_detection", "capture_settings", settings)


def _sanitize_session_name(session_name: str) -> str:
    return (session_name or "").strip()


def _validate_session_name(session_name: str) -> tuple[bool, str]:
    if not session_name:
        return False, "Session-Name fehlt."
    if not _SESSION_NAME_PATTERN.match(session_name):
        return False, "Session-Name erlaubt nur A-Z, a-z, 0-9, Punkt, Unterstrich und Minus."
    return True, ""


def _resolve_base_dir(base_directory: str) -> Path:
    path = Path(base_directory)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _is_local_mqtt_host(host: str) -> bool:
    normalized = (host or "").strip().lower()
    return normalized in {"", "localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _local_listener_pids(port: int) -> tuple[set[int], str]:
    try:
        result = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{int(port)}", "-sTCP:LISTEN"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return set(), "lsof not available"
    except Exception as exc:
        return set(), str(exc)

    if result.returncode != 0 and not result.stdout.strip():
        return set(), ""

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return set(), ""

    pids: set[int] = set()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            pids.add(int(parts[1]))
        except ValueError:
            continue
    return pids, ""


def _mqtt_single_instance_preflight(host: str, port: int) -> tuple[bool, str]:
    if not _is_local_mqtt_host(host):
        return True, ""
    pids, err = _local_listener_pids(int(port))
    if err:
        return False, err
    if len(pids) > 1:
        pid_list = ", ".join(str(pid) for pid in sorted(pids))
        return False, f"Mehrere lokale Broker-Listener erkannt (PIDs: {pid_list})."
    return True, ""


def _tcp_preflight(host: str, port: int, timeout: int) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, int(port)), timeout=max(1, int(timeout))):
            return True, ""
    except Exception as exc:
        return False, str(exc)


def _mqtt_rule_matches(rule: str, topic: str) -> bool:
    if not rule:
        return False
    if rule == "#":
        return True

    rule_parts = rule.split("/")
    topic_parts = topic.split("/")

    ti = 0
    for part in rule_parts:
        if part == "#":
            return True
        if ti >= len(topic_parts):
            return False
        if part == "+":
            ti += 1
            continue
        if part != topic_parts[ti]:
            return False
        ti += 1
    return ti == len(topic_parts)


def _topic_allowed(topic: str, filters: list[str]) -> bool:
    if not filters:
        return True
    return any(_mqtt_rule_matches(rule.strip(), topic) for rule in filters if rule.strip())


def _normalize_full_events_preset(preset: str | None) -> str:
    if not preset or preset not in VALID_FULL_EVENTS_PRESETS:
        return FULL_EVENTS_PRESET_NONE
    return preset


def _is_cam_topic(topic: str) -> bool:
    return topic == "/j1/txt/1/i/cam" or topic.startswith("/j1/txt/1/i/cam/")


def _is_aps_sensor_topic(topic: str) -> bool:
    # APS/TXT-side sensors commonly used in logs
    return topic in {
        "/j1/txt/1/i/bme680",
        "/j1/txt/1/i/bme",
        "/j1/txt/1/c/bme680",
        "/j1/txt/1/i/ldr",
        "/j1/txt/1/c/ldr",
    }


def _is_arduino_sensor_topic(topic: str) -> bool:
    return topic.startswith("osf/arduino/")


def _full_events_allowed(topic: str, preset: str) -> bool:
    normalized = _normalize_full_events_preset(preset)
    if normalized == FULL_EVENTS_PRESET_NONE:
        return True
    if normalized == FULL_EVENTS_PRESET_EXCLUDE_CAM:
        return not _is_cam_topic(topic)
    if normalized == FULL_EVENTS_PRESET_EXCLUDE_APS_SENSORS:
        return not (_is_cam_topic(topic) or _is_aps_sensor_topic(topic))
    if normalized == FULL_EVENTS_PRESET_EXCLUDE_ARDUINO:
        return not _is_arduino_sensor_topic(topic)
    if normalized == FULL_EVENTS_PRESET_EXCLUDE_ALL_SENSORS:
        return not (_is_cam_topic(topic) or _is_aps_sensor_topic(topic) or _is_arduino_sensor_topic(topic))
    return True


def _extract_candidate_values(node: Any, keys: set[str], out: list[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if str(k).strip().lower() in keys and v not in (None, ""):
                out.append(str(v))
            _extract_candidate_values(v, keys, out)
    elif isinstance(node, list):
        for item in node:
            _extract_candidate_values(item, keys, out)


def _extract_min_fields(payload_raw: str) -> tuple[str, str, str]:
    try:
        payload = json.loads(payload_raw)
    except Exception:
        return "", "", ""

    order_values: list[str] = []
    nfc_values: list[str] = []
    phase_values: list[str] = []
    _extract_candidate_values(payload, _ORDER_ID_KEYS, order_values)
    _extract_candidate_values(payload, _NFC_TAG_KEYS, nfc_values)
    _extract_candidate_values(payload, _PHASE_KEYS, phase_values)
    return (
        order_values[0] if order_values else "",
        nfc_values[0] if nfc_values else "",
        phase_values[0] if phase_values else "",
    )


def _build_manifest(session_name: str, session_dir: Path, settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "object_detection_capture_manifest",
        "session_name": session_name,
        "sequence_id": session_name,
        "session_directory": str(session_dir),
        "video_file": settings["capture"].get("video_filename", "video.mp4"),
        "created_at": utc_iso_timestamp_ms(),
        "capture_started_at": utc_iso_timestamp_ms(),
        "capture_ended_at": "",
        "broker": {
            "host": settings["mqtt_broker"]["host"],
            "port": int(settings["mqtt_broker"]["port"]),
            "qos": int(settings["mqtt_broker"]["qos"]),
        },
        "topic_filters": settings["capture"].get("topic_filters", ["#"]),
        "save_full_events": bool(settings["capture"].get("save_full_events", False)),
        "full_events_exclusion_preset": _normalize_full_events_preset(
            str(settings["capture"].get("full_events_exclusion_preset", FULL_EVENTS_PRESET_NONE))
        ),
        "counts": {"meta_min_events": 0, "full_events": 0},
        "latest": {"order_id": "", "nfc_tag": ""},
        "notes": "MVP workflow: OBS recording remains manual.",
    }


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _od_on_connect(client, userdata, flags, rc):
    if rc == 0:
        with _runtime_lock:
            _runtime["connected"] = True
        client.subscribe("#")
        logger.info("✅ Object Detection Capture MQTT verbunden")
    else:
        logger.error("❌ Object Detection Capture MQTT connect rc=%s", rc)


def _od_on_message(client, userdata, msg):
    ts = utc_iso_timestamp_ms()
    topic = str(msg.topic)
    try:
        payload_raw = msg.payload.decode("utf-8")
    except Exception:
        payload_raw = msg.payload.decode("utf-8", errors="replace")

    with _runtime_lock:
        if not _runtime["active"]:
            return

        # Optional full events log for later QA correlation (kept separate from AI feed)
        if (
            _runtime["save_full_events"]
            and _runtime["full_file"] is not None
            and _full_events_allowed(topic, str(_runtime.get("full_events_exclusion_preset", FULL_EVENTS_PRESET_NONE)))
        ):
            full_entry = {
                "topic": topic,
                "payload": payload_raw,
                "timestamp": ts,
                "qos": getattr(msg, "qos", 0),
                "retain": getattr(msg, "retain", False),
            }
            _runtime["full_file"].write(json.dumps(full_entry, ensure_ascii=False) + "\n")
            _runtime["captured_full_events"] += 1

        if not _topic_allowed(topic, _runtime["topic_filters"]):
            return

        order_id, nfc_tag, phase = _extract_min_fields(payload_raw)
        if not order_id and not nfc_tag and not phase:
            return

        if order_id:
            _runtime["last_order_id"] = order_id
        if nfc_tag:
            _runtime["last_nfc_tag"] = nfc_tag

        meta_entry = {
            "ts": ts,
            "sequence_id": _runtime["session_name"],
            "topic": topic,
            "order_id": order_id,
            "nfc_tag": nfc_tag,
            "phase": phase,
        }
        if _runtime["meta_file"] is not None:
            _runtime["meta_file"].write(json.dumps(meta_entry, ensure_ascii=False) + "\n")
            _runtime["captured_min_events"] += 1


def _close_runtime_files() -> None:
    if _runtime["meta_file"] is not None:
        try:
            _runtime["meta_file"].close()
        except Exception:
            pass
    if _runtime["full_file"] is not None:
        try:
            _runtime["full_file"].close()
        except Exception:
            pass
    _runtime["meta_file"] = None
    _runtime["full_file"] = None


def _disconnect_runtime_client() -> None:
    client = _runtime.get("client")
    if client is None:
        return
    try:
        client.loop_stop()
    except Exception:
        pass
    try:
        client.disconnect()
    except Exception:
        pass
    _runtime["client"] = None
    _runtime["connected"] = False


def _shutdown_runtime_cleanup() -> None:
    """Best-effort cleanup for interpreter shutdown (helps on Windows)."""
    with _runtime_lock:
        has_client = _runtime.get("client") is not None
        has_files = _runtime.get("meta_file") is not None or _runtime.get("full_file") is not None
        _runtime["active"] = False
    if has_client:
        _disconnect_runtime_client()
    if has_files:
        _close_runtime_files()


def _ensure_shutdown_hook() -> None:
    global _shutdown_registered
    if _shutdown_registered:
        return
    atexit.register(_shutdown_runtime_cleanup)
    _shutdown_registered = True


def _preflight_checks(session_name: str, settings: dict[str, Any]) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    valid_name, name_reason = _validate_session_name(session_name)
    checks.append(("Session-Name validieren", valid_name, name_reason if not valid_name else "OK"))

    if not MQTT_AVAILABLE:
        checks.append(("Python Paket `paho-mqtt`", False, "Nicht installiert"))
    else:
        checks.append(("Python Paket `paho-mqtt`", True, "OK"))

    base_dir = _resolve_base_dir(settings["base_directory"])
    try:
        base_dir.mkdir(parents=True, exist_ok=True)
        probe = base_dir / ".od_write_probe.tmp"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        checks.append(("Ablagepfad schreiben", True, str(base_dir)))
    except Exception as exc:
        checks.append(("Ablagepfad schreiben", False, str(exc)))

    if valid_name:
        session_dir = base_dir / session_name
        if session_dir.exists():
            with _runtime_lock:
                active_same_session = bool(_runtime.get("active")) and str(_runtime.get("session_name")) == session_name
            if active_same_session:
                checks.append(("Session-Ordner aktiv in Verwendung", True, str(session_dir)))
            else:
                checks.append(("Session-Ordner bereits vorhanden", False, str(session_dir)))
        else:
            checks.append(("Session-Ordner frei", True, str(session_dir)))

    host = str(settings["mqtt_broker"]["host"])
    port = int(settings["mqtt_broker"]["port"])
    timeout = int(settings["mqtt_broker"]["timeout"])
    tcp_ok, tcp_reason = _tcp_preflight(host, port, timeout)
    checks.append((f"Broker erreichbar ({host}:{port})", tcp_ok, tcp_reason if not tcp_ok else "OK"))

    singleton_ok, singleton_reason = _mqtt_single_instance_preflight(host, port)
    checks.append(
        (
            "Lokaler Broker Single-Instance Check",
            singleton_ok,
            singleton_reason if not singleton_ok else "OK oder nicht lokal relevant",
        )
    )

    topics = settings["capture"].get("topic_filters", ["#"])
    valid_topics = [str(t).strip() for t in topics if str(t).strip()]
    checks.append(("Topic-Filter gesetzt", bool(valid_topics), ", ".join(valid_topics) if valid_topics else "Leer"))
    return checks


def _start_capture(session_name: str, settings: dict[str, Any]) -> tuple[bool, str]:
    _ensure_shutdown_hook()
    with _runtime_lock:
        if _runtime["active"]:
            return False, "Capture läuft bereits."

    valid, reason = _validate_session_name(session_name)
    if not valid:
        return False, reason
    if not MQTT_AVAILABLE:
        return False, "paho-mqtt ist nicht verfügbar."

    base_dir = _resolve_base_dir(settings["base_directory"])
    session_dir = base_dir / session_name
    if session_dir.exists():
        return False, f"Session-Ordner existiert bereits: {session_dir}"
    session_dir.mkdir(parents=True, exist_ok=False)

    manifest_path = session_dir / "manifest.json"
    meta_path = session_dir / "meta_min.jsonl"
    full_path = session_dir / "events_full.log"
    manifest = _build_manifest(session_name, session_dir, settings)
    _write_manifest(manifest_path, manifest)

    meta_file = open(meta_path, "w", encoding="utf-8", buffering=1)
    meta_file.write(
        json.dumps(
            {
                "kind": "meta_header",
                "created_at": utc_iso_timestamp_ms(),
                "sequence_id": session_name,
                "fields": ["ts", "sequence_id", "topic", "order_id", "nfc_tag", "phase"],
            },
            ensure_ascii=False,
        )
        + "\n"
    )
    meta_file.flush()

    full_file = None
    save_full_events = bool(settings["capture"].get("save_full_events", False))
    full_events_exclusion_preset = _normalize_full_events_preset(
        str(settings["capture"].get("full_events_exclusion_preset", FULL_EVENTS_PRESET_NONE))
    )
    if save_full_events:
        full_file = open(full_path, "w", encoding="utf-8", buffering=1)

    try:
        assert mqtt is not None
        client = mqtt.Client(client_id=f"session_manager_od_{int(time.time())}")
        broker = settings["mqtt_broker"]
        username = str(broker.get("username", "") or "").strip()
        password = str(broker.get("password", "") or "")
        if username:
            client.username_pw_set(username, password)
        client.on_connect = _od_on_connect
        client.on_message = _od_on_message
        client.connect(str(broker["host"]), int(broker["port"]), int(broker["timeout"]))
        client.loop_start()
    except Exception as exc:
        meta_file.close()
        if full_file is not None:
            full_file.close()
        return False, f"MQTT-Verbindung fehlgeschlagen: {exc}"

    with _runtime_lock:
        _runtime.update(
            {
                "active": True,
                "connected": False,
                "client": client,
                "session_name": session_name,
                "session_dir": session_dir,
                "manifest_path": manifest_path,
                "meta_file": meta_file,
                "full_file": full_file,
                "topic_filters": [
                    str(t).strip() for t in settings["capture"].get("topic_filters", ["#"]) if str(t).strip()
                ],
                "save_full_events": save_full_events,
                "full_events_exclusion_preset": full_events_exclusion_preset,
                "captured_min_events": 0,
                "captured_full_events": 0,
                "last_order_id": "",
                "last_nfc_tag": "",
                "started_at": utc_iso_timestamp_ms(),
            }
        )

    for _ in range(30):
        with _runtime_lock:
            if _runtime["connected"]:
                return True, f"OD-Session gestartet: {session_dir}"
        time.sleep(0.1)

    _stop_capture(video_filename=settings["capture"].get("video_filename", "video.mp4"), aborted=True)
    return False, "MQTT Connect-Timeout beim Start."


def _stop_capture(video_filename: str, aborted: bool = False) -> tuple[bool, str]:
    client_to_disconnect = False
    files_to_close = False
    with _runtime_lock:
        if not _runtime["active"] and not aborted:
            return False, "Keine aktive OD-Session."

        manifest_path = _runtime.get("manifest_path")
        started_at = _runtime.get("started_at")
        min_count = int(_runtime.get("captured_min_events", 0))
        full_count = int(_runtime.get("captured_full_events", 0))
        latest_order = str(_runtime.get("last_order_id", ""))
        latest_nfc = str(_runtime.get("last_nfc_tag", ""))

        client_to_disconnect = _runtime.get("client") is not None
        files_to_close = _runtime.get("meta_file") is not None or _runtime.get("full_file") is not None
        _runtime["active"] = False

    # Important: disconnect/close outside lock to avoid callback deadlocks on Windows.
    if client_to_disconnect:
        _disconnect_runtime_client()
    if files_to_close:
        _close_runtime_files()

    if isinstance(manifest_path, Path) and manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["capture_ended_at"] = utc_iso_timestamp_ms()
            manifest["video_file"] = video_filename or manifest.get("video_file", "video.mp4")
            manifest["counts"] = {"meta_min_events": min_count, "full_events": full_count}
            manifest["latest"] = {"order_id": latest_order, "nfc_tag": latest_nfc}
            manifest["status"] = "aborted" if aborted else "finished"
            manifest["capture_started_at"] = started_at
            _write_manifest(manifest_path, manifest)
        except Exception as exc:
            logger.error("Manifest Update fehlgeschlagen: %s", exc)

    with _runtime_lock:
        _runtime.update(
            {
                "connected": False,
                "session_name": "",
                "session_dir": None,
                "manifest_path": None,
                "topic_filters": ["#"],
                "save_full_events": False,
                "full_events_exclusion_preset": FULL_EVENTS_PRESET_NONE,
                "started_at": "",
            }
        )
    if aborted:
        return False, "OD-Session abgebrochen."
    return True, f"OD-Session gestoppt ({min_count} minimale Events)."


def show_object_detection_capture():
    """Streamlit UI: Object Detection MVP capture workflow."""
    st.header("🎯 Object Detection")
    st.markdown(
        "MVP-Workflow fuer Datenerfassung: **Session-Ordner automatisch anlegen**, "
        "**minimales MQTT-Feed (`order_id`, `nfc_tag`) mitschreiben**, Video weiter manuell via OBS."
    )

    settings_manager = SettingsManager()
    settings = _load_settings(settings_manager)

    if "od_session_name" not in st.session_state:
        st.session_state.od_session_name = ""
    if "od_topic_filters" not in st.session_state:
        st.session_state.od_topic_filters = "\n".join(settings["capture"].get("topic_filters", ["#"]))
    if "od_video_filename" not in st.session_state:
        st.session_state.od_video_filename = str(settings["capture"].get("video_filename", "video.mp4"))
    if "od_save_full_events" not in st.session_state:
        st.session_state.od_save_full_events = bool(settings["capture"].get("save_full_events", False))
    if "od_full_events_exclusion_preset" not in st.session_state:
        st.session_state.od_full_events_exclusion_preset = _normalize_full_events_preset(
            str(settings["capture"].get("full_events_exclusion_preset", FULL_EVENTS_PRESET_NONE))
        )
    if "od_base_directory" not in st.session_state:
        st.session_state.od_base_directory = str(settings["base_directory"])
    if "od_mqtt_host" not in st.session_state:
        st.session_state.od_mqtt_host = str(settings["mqtt_broker"]["host"])
    if "od_mqtt_port" not in st.session_state:
        st.session_state.od_mqtt_port = int(settings["mqtt_broker"]["port"])
    if "od_mqtt_qos" not in st.session_state:
        st.session_state.od_mqtt_qos = int(settings["mqtt_broker"]["qos"])
    if "od_mqtt_timeout" not in st.session_state:
        st.session_state.od_mqtt_timeout = int(settings["mqtt_broker"]["timeout"])
    if "od_mqtt_username" not in st.session_state:
        st.session_state.od_mqtt_username = str(settings["mqtt_broker"].get("username", ""))
    if "od_mqtt_password" not in st.session_state:
        st.session_state.od_mqtt_password = str(settings["mqtt_broker"].get("password", ""))

    st.subheader("1) Session vorbereiten")
    st.session_state.od_session_name = st.text_input(
        "Session-Name",
        value=st.session_state.od_session_name,
        placeholder="z. B. object-detection_white-1",
        help="Wird 1:1 als Ordnername verwendet.",
    )

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        st.session_state.od_base_directory = st.text_input(
            "Ablage-Basisverzeichnis",
            value=st.session_state.od_base_directory,
            help="Pro Session wird darunter ein Ordner mit dem Session-Namen erstellt.",
        )
        st.session_state.od_video_filename = st.text_input(
            "Video-Dateiname (manuell in OBS verwenden)",
            value=st.session_state.od_video_filename,
        )
    with col_cfg2:
        st.session_state.od_save_full_events = st.checkbox(
            "Optionale Voll-Events separat speichern (`events_full.log`)",
            value=st.session_state.od_save_full_events,
            help="Nicht fuer AI-Feed, nur fuer spaetere QA-Korrelation.",
        )
        st.caption("Topic-Filter (ein Muster pro Zeile; MQTT Wildcards `+` und `#` erlaubt)")
        st.session_state.od_topic_filters = st.text_area(
            "Topic-Filter",
            value=st.session_state.od_topic_filters,
            height=100,
            label_visibility="collapsed",
        )
        st.session_state.od_full_events_exclusion_preset = st.selectbox(
            "Preset-Ausschluss fuer optionale Full-Events",
            options=[
                FULL_EVENTS_PRESET_NONE,
                FULL_EVENTS_PRESET_EXCLUDE_CAM,
                FULL_EVENTS_PRESET_EXCLUDE_APS_SENSORS,
                FULL_EVENTS_PRESET_EXCLUDE_ARDUINO,
                FULL_EVENTS_PRESET_EXCLUDE_ALL_SENSORS,
            ],
            index=[
                FULL_EVENTS_PRESET_NONE,
                FULL_EVENTS_PRESET_EXCLUDE_CAM,
                FULL_EVENTS_PRESET_EXCLUDE_APS_SENSORS,
                FULL_EVENTS_PRESET_EXCLUDE_ARDUINO,
                FULL_EVENTS_PRESET_EXCLUDE_ALL_SENSORS,
            ].index(st.session_state.od_full_events_exclusion_preset),
            help=(
                "Gilt nur fuer `events_full.log` (QA/Korrelation). "
                "Der minimale OD-Feed (`meta_min.jsonl`) bleibt davon unberuehrt."
            ),
        )

    st.markdown("#### MQTT Broker")
    broker_col1, broker_col2, broker_col3 = st.columns(3)
    with broker_col1:
        st.session_state.od_mqtt_host = st.text_input("Host", value=st.session_state.od_mqtt_host, key="od_host_input")
        st.session_state.od_mqtt_username = st.text_input(
            "Username (optional)", value=st.session_state.od_mqtt_username, key="od_user_input"
        )
    with broker_col2:
        st.session_state.od_mqtt_port = st.number_input(
            "Port", min_value=1, max_value=65535, value=int(st.session_state.od_mqtt_port), key="od_port_input"
        )
        st.session_state.od_mqtt_password = st.text_input(
            "Password (optional)", value=st.session_state.od_mqtt_password, type="password", key="od_pass_input"
        )
    with broker_col3:
        st.session_state.od_mqtt_qos = st.selectbox(
            "QoS",
            options=[0, 1, 2],
            index=(
                [0, 1, 2].index(int(st.session_state.od_mqtt_qos))
                if int(st.session_state.od_mqtt_qos) in [0, 1, 2]
                else 1
            ),
            key="od_qos_select",
        )
        st.session_state.od_mqtt_timeout = st.number_input(
            "Timeout (s)",
            min_value=1,
            max_value=60,
            value=int(st.session_state.od_mqtt_timeout),
            key="od_timeout_input",
        )

    broker = {
        "host": st.session_state.od_mqtt_host.strip() or "localhost",
        "port": int(st.session_state.od_mqtt_port),
        "qos": int(st.session_state.od_mqtt_qos),
        "timeout": int(st.session_state.od_mqtt_timeout),
        "username": st.session_state.od_mqtt_username.strip(),
        "password": st.session_state.od_mqtt_password,
    }
    st.caption(
        f"MQTT Broker fuer OD-Capture: `{broker['host']}:{broker['port']}` (QoS {broker['qos']}, Timeout {broker['timeout']}s)"
    )

    if st.button("💾 OD-Einstellungen speichern", key="od_save_settings_btn"):
        new_settings = {
            "base_directory": st.session_state.od_base_directory.strip() or _get_default_settings()["base_directory"],
            "mqtt_broker": broker,
            "capture": {
                "topic_filters": [
                    line.strip() for line in st.session_state.od_topic_filters.splitlines() if line.strip()
                ]
                or ["#"],
                "save_full_events": bool(st.session_state.od_save_full_events),
                "full_events_exclusion_preset": _normalize_full_events_preset(
                    st.session_state.od_full_events_exclusion_preset
                ),
                "video_filename": st.session_state.od_video_filename.strip() or "video.mp4",
            },
        }
        _save_settings(settings_manager, new_settings)
        st.success("OD-Einstellungen gespeichert.")
        settings = new_settings

    active = bool(_runtime.get("active"))

    st.subheader("2) Preflight")
    effective_settings = {
        "base_directory": st.session_state.od_base_directory.strip() or settings["base_directory"],
        "mqtt_broker": settings["mqtt_broker"],
        "capture": {
            "topic_filters": [line.strip() for line in st.session_state.od_topic_filters.splitlines() if line.strip()]
            or ["#"],
            "save_full_events": bool(st.session_state.od_save_full_events),
            "full_events_exclusion_preset": _normalize_full_events_preset(
                st.session_state.od_full_events_exclusion_preset
            ),
            "video_filename": st.session_state.od_video_filename.strip() or "video.mp4",
        },
    }
    checks = _preflight_checks(_sanitize_session_name(st.session_state.od_session_name), effective_settings)
    all_ok = True
    for label, ok, detail in checks:
        if ok:
            st.success(f"✅ {label}: {detail}")
        else:
            all_ok = False
            st.error(f"❌ {label}: {detail}")

    st.subheader("3) Aufnahme")
    start_col, stop_col = st.columns(2)
    with start_col:
        if st.button("▶️ OD-Session starten", type="primary", disabled=active or not all_ok):
            ok, msg = _start_capture(_sanitize_session_name(st.session_state.od_session_name), effective_settings)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
            st.rerun()
    with stop_col:
        if st.button("⏹️ OD-Session stoppen", disabled=not active):
            ok, msg = _stop_capture(video_filename=st.session_state.od_video_filename.strip() or "video.mp4")
            if ok:
                st.success(msg)
            else:
                st.error(msg)
            st.rerun()

    with _runtime_lock:
        current_active = bool(_runtime["active"])
        current_connected = bool(_runtime["connected"])
        min_events = int(_runtime["captured_min_events"])
        full_events = int(_runtime["captured_full_events"])
        current_dir = _runtime["session_dir"]

    st.markdown("---")
    st.subheader("Status")
    st.write(f"- Aufnahme aktiv: {'ja' if current_active else 'nein'}")
    st.write(f"- MQTT verbunden: {'ja' if current_connected else 'nein'}")
    st.write(f"- Minimale OD-Events: {min_events}")
    st.write(f"- Full-Events (optional): {full_events}")
    if current_dir:
        st.write(f"- Aktueller Session-Ordner: `{current_dir}`")

    st.markdown("---")
    st.subheader("4) Video (MVP: manuell)")
    st.info(
        "Videoaufnahme bleibt im MVP manuell (z. B. OBS auf Windows):\n"
        "1. Nach `OD-Session starten` Recording in OBS starten\n"
        "2. Nach `OD-Session stoppen` Recording in OBS stoppen\n"
        "3. Video als angegebenen Dateinamen im Session-Ordner ablegen\n\n"
        "Tipp: In OBS den Dateinamen/Pfad im Ausgabemodus vor Start anpassen, "
        "damit kein manuelles Umbenennen mit Timestamp noetig ist."
    )
