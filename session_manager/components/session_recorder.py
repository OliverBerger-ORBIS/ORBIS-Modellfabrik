"""
Session Recorder Komponente
Einfache 1:1 Aufnahme von MQTT-Nachrichten
"""

import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from ..utils.logging_config import get_logger
from ..utils.path_constants import PROJECT_ROOT
from ..utils.recording_topic_filter import (
    CUSTOM_FILTER_MODE_EXCLUDE,
    CUSTOM_FILTER_MODE_INCLUDE,
    CUSTOM_FILTER_MODE_NONE,
    EXCLUSION_PRESET_ANALYSIS,
    EXCLUSION_PRESET_NO_CAM,
    EXCLUSION_PRESET_NONE,
    should_write_message_to_session_log,
)
from ..utils.session_meta_line import (
    build_session_meta_line,
    detect_ccu_version_via_runtime_image,
    extract_ccu_version_from_messages,
)
from ..utils.ui_refresh import RerunController
from ..utils.utc_iso_timestamp import utc_iso_timestamp_ms

logger = get_logger("omf.helper_apps.session_manager.components.session_recorder")

# Session Manager Logging-System verwenden (wie ursprünglich)
# logger = logging.getLogger("session_manager.session_recorder")  # Duplikat entfernt


# Thread-sichere Nachrichten-Sammlung
class ThreadSafeMessageBuffer:
    def __init__(self):
        self._messages = []
        self._lock = threading.Lock()

    def add_message(self, message: Dict[str, Any]):
        with self._lock:
            self._messages.append(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        with self._lock:
            return self._messages.copy()

    def clear(self):
        with self._lock:
            self._messages.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._messages)


# Globale Nachrichten-Sammlung (thread-sicher)
message_buffer = ThreadSafeMessageBuffer()

# Flags für on_message_received (Callback läuft im MQTT-Thread – kein st.session_state)
_recording_active = False
_include_retained = False
_recording_exclusion_preset = "none"
_recording_custom_filter_mode = "none"
_recording_custom_filter_topics: list[str] = []


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


def _local_mqtt_related_pids() -> tuple[set[int], str]:
    mqtt_related_ports = (1883, 1884, 1885, 8883, 9001)
    all_pids: set[int] = set()
    for p in mqtt_related_ports:
        pids, err = _local_listener_pids(p)
        if err:
            return set(), err
        all_pids.update(pids)
    return all_pids, ""


def _mqtt_single_instance_preflight(host: str, port: int) -> tuple[bool, str]:
    if not _is_local_mqtt_host(host):
        return True, ""

    pids, err = _local_listener_pids(int(port))
    if err:
        return False, f"MQTT preflight failed: {err}"
    if len(pids) > 1:
        pid_list = ", ".join(str(pid) for pid in sorted(pids))
        return False, (
            f"Duplicate MQTT listeners detected on {host}:{port} (pids: {pid_list}). "
            "Stop extra broker instances before recording."
        )

    all_pids, related_err = _local_mqtt_related_pids()
    if related_err:
        return False, f"MQTT preflight failed: {related_err}"
    if len(all_pids) > 1:
        pid_list = ", ".join(str(pid) for pid in sorted(all_pids))
        return False, (
            f"MQTT preflight failed: multiple local MQTT-related listener processes detected ({pid_list}). "
            "Ensure exactly one broker instance is running."
        )
    return True, ""


def _collect_known_topics(settings_manager) -> list[str]:
    """
    Build a topic catalog for custom filter selection.
    Sources: existing session logs, test topic files, and preload topic files.
    """
    known: set[str] = set()

    session_dir = settings_manager.get_session_recorder_directory()
    session_path = Path(session_dir)
    if not session_path.is_absolute():
        session_path = PROJECT_ROOT / session_dir
    if session_path.exists():
        for log_file in sorted(session_path.glob("*.log"), reverse=True)[:30]:
            try:
                with open(log_file, encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        if idx > 1500:
                            break
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                        except Exception:
                            continue
                        topic = str(data.get("topic", "")).strip()
                        if topic:
                            known.add(topic)
            except Exception:
                continue

    for base_dir in (
        PROJECT_ROOT / "data/osf-data/test_topics",
        PROJECT_ROOT / "data/osf-data/test_topics/preloads",
    ):
        if not base_dir.exists():
            continue
        for topic_file in sorted(base_dir.glob("*.json")):
            try:
                with open(topic_file, encoding="utf-8") as f:
                    data = json.load(f)
                topic = str(data.get("topic", "")).strip()
                if topic:
                    known.add(topic)
            except Exception:
                continue

    return sorted(known)


def show_session_recorder():
    """Session Recorder Tab - KISS Design"""

    logger.info("🔴 Session Recorder Tab geladen")

    # RerunController initialisieren
    rerun_controller = RerunController()

    st.header("🔴 Session Recorder")
    st.markdown("Default: Live-MQTT-Daten als Session-Log aufnehmen.")
    st.markdown("`📡 Quelle -> 🛡️ Broker-Check -> 🎙️ Recorder -> 📁 Session-Log-Verzeichnis`")

    # Konfiguration aus Settings laden
    from .settings_manager import SettingsManager

    settings_manager = SettingsManager()
    mqtt_settings = settings_manager.get_session_recorder_mqtt_settings()
    recorder_host = str(mqtt_settings.get("host", "")).strip() or "localhost"
    recorder_is_local = _is_local_mqtt_host(recorder_host)

    st.info(
        "ℹ️ **Live-Aufnahme-Modus:** Session Recorder zeichnet Live-MQTT auf "
        "(z. B. Mode B: Live auf RPi oder Mode C: Live mit lokalem OSF)."
    )
    if recorder_is_local:
        st.warning(
            "Broker-Ziel ist lokal (`localhost`). Fuer ORBIS-Livebetrieb den Fabrik-/RPi-Broker "
            "(typisch `192.168.0.100`) verwenden."
        )
    else:
        st.caption("Broker-Ziel ist extern. Das passt fuer Live-Aufnahmen gegen Fabrik-/RPi-Infrastruktur.")

    # Tab-spezifische Session State initialisieren (vollständig unabhängig)
    if "session_recorder" not in st.session_state:
        st.session_state.session_recorder = {
            "connected": False,
            "recording": False,
            "session_name": "",
            "start_time": None,
            "mqtt_client": None,
            "include_retained": False,
        }

    if "_recorder_source_mode" not in st.session_state:
        st.session_state._recorder_source_mode = "A) Live-MQTT (APS/Testbed)"
    if "_recorder_show_source_picker" not in st.session_state:
        st.session_state._recorder_show_source_picker = False
    if "_recorder_show_broker_panel" not in st.session_state:
        st.session_state._recorder_show_broker_panel = False

    st.subheader("🧭 Bedienungsflow")
    st.caption("Klick auf **Quelle** oder **Broker**, um die jeweilige Konfiguration einzublenden.")
    f1, f2, f3, f4, f5 = st.columns([2.2, 0.6, 2.2, 0.6, 2.2])
    with f1:
        if st.button(
            f"📡 Quelle\n{st.session_state._recorder_source_mode}",
            key="recorder_flow_source_btn",
            use_container_width=True,
        ):
            st.session_state._recorder_show_source_picker = not st.session_state._recorder_show_source_picker
    with f2:
        st.markdown("### ➜")
    with f3:
        if st.button("🔀 Broker\n(mit Check)", key="recorder_flow_broker_btn", use_container_width=True):
            st.session_state._recorder_show_broker_panel = not st.session_state._recorder_show_broker_panel
    with f4:
        st.markdown("### ➜")
    with f5:
        st.info("🎙️ Recorder\n\n📁 Session-Log")

    if st.session_state._recorder_show_source_picker:
        st.markdown("#### 📡 Quelle auswählen")
        st.session_state._recorder_source_mode = st.radio(
            "Recorder-Quelle",
            options=("A) Live-MQTT (APS/Testbed)",),
            key="recorder_source_mode_radio",
            horizontal=False,
        )

    if st.session_state._recorder_show_broker_panel:
        st.markdown("#### 🔀 Broker-Einstellungen")
        st.info(
            f"**Broker:** {mqtt_settings['host']}:{mqtt_settings['port']} | "
            f"**QoS:** {mqtt_settings['qos']} | **Timeout:** {mqtt_settings['timeout']}s"
        )
        if mqtt_settings.get("username"):
            st.info(f"**Auth:** {mqtt_settings['username']} (authentifiziert)")
        else:
            st.info("**Auth:** Keine Authentifizierung")

        ok, reason = _mqtt_single_instance_preflight(mqtt_settings["host"], int(mqtt_settings["port"]))
        if ok:
            st.success("🛡️ Broker-Check: OK (ein Broker aktiv)")
        else:
            st.error(f"🛡️ Broker-Check: {reason}")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(
                "🔌 Broker Verbinden",
                key="recorder_connect_btn",
                disabled=st.session_state.session_recorder["connected"],
            ):
                ok, reason = _mqtt_single_instance_preflight(mqtt_settings["host"], int(mqtt_settings["port"]))
                if not ok:
                    st.error(f"❌ Verbindung blockiert: {reason}")
                elif connect_to_broker(mqtt_settings):
                    st.session_state.session_recorder["connected"] = True
                    st.success("✅ MQTT verbunden!")
                    rerun_controller.request_rerun()
                else:
                    st.error("❌ Verbindung fehlgeschlagen!")
        with c2:
            if st.button(
                "🔌 Broker Trennen",
                key="recorder_disconnect_btn",
                disabled=not st.session_state.session_recorder["connected"],
            ):
                disconnect_from_broker()
                st.session_state.session_recorder["connected"] = False
                st.success("✅ MQTT getrennt!")
                rerun_controller.request_rerun()
        with c3:
            if st.button("⚙️ Zu Einstellungen wechseln", key="recorder_to_settings_btn"):
                st.session_state["main_sidebar_tab"] = "⚙️ Einstellungen"
                st.rerun()

    st.markdown("---")

    # Default-Bedienung
    st.subheader("📝 Standard-Bedienung")
    st.markdown("**Default:** Live-MQTT-Daten als Session-Log aufnehmen.")
    session_name = st.text_input(
        "Session-Name eingeben",
        value=st.session_state.session_recorder["session_name"],
        placeholder="z.B. auftrag-rot-R1",
        help="Name für die aufzunehmende Session",
    )

    if session_name:
        st.session_state.session_recorder["session_name"] = session_name
        st.success(f"✅ Session-Name gesetzt: {session_name}")

    include_retained_flag = st.session_state.session_recorder.get("include_retained", False)

    if not st.session_state.session_recorder["session_name"]:
        st.warning("⚠️ Bitte Session-Name eingeben")
    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "▶️ Aufnahme Starten",
                disabled=st.session_state.session_recorder["recording"],
                type="primary",
            ):
                ok, reason = _mqtt_single_instance_preflight(mqtt_settings["host"], int(mqtt_settings["port"]))
                if not ok:
                    st.error(f"❌ Aufnahme blockiert: {reason}")
                else:
                    started = start_recording(mqtt_settings, rerun_controller)
                    if started:
                        st.session_state.session_recorder["recording"] = True
                        st.session_state.session_recorder["connected"] = True
                        st.session_state.session_recorder["start_time"] = datetime.now()
                        success_msg = "🔴 Aufnahme gestartet!" + (" (inkl. retained)" if include_retained_flag else "")
                        st.success(success_msg)
                        rerun_controller.request_rerun()
                    else:
                        st.error("❌ Verbindung/Aufnahme fehlgeschlagen!")

        with col2:
            if st.button(
                "⏹️ Aufnahme Beenden", disabled=not st.session_state.session_recorder["recording"], type="secondary"
            ):
                stop_recording()
                st.success("⏹️ Aufnahme beendet und gespeichert!")
                rerun_controller.request_rerun()

    with st.expander("🧩 Optionale Details (Retained, Topic-Filter, Meta)", expanded=False):
        include_retained = st.checkbox(
            "Retained Messages am Start miterfassen",
            value=st.session_state.session_recorder.get("include_retained", False),
            help="State/Connection/Factsheet beim Subscribe – nur aktivieren, wenn initialer Stand nötig ist.",
            key="session_recorder_include_retained",
        )
        st.session_state.session_recorder["include_retained"] = include_retained
        st.caption("**Normal:** Nur Nachrichten während der Aufnahme. **Mit Retained:** Zusätzlich initialer Stand.")

        preset_labels = (
            "Alle Topics (unfiltered)",
            "Ohne Kamera (Cam-Payloads ausschließen)",
            "Analyse: ohne Arduino / BME680 / Kamera / LDR (DR-25)",
        )
        preset_values = (EXCLUSION_PRESET_NONE, EXCLUSION_PRESET_NO_CAM, EXCLUSION_PRESET_ANALYSIS)
        current_preset = settings_manager.get_session_recorder_recording_exclusion_preset()
        preset_index = preset_values.index(current_preset) if current_preset in preset_values else 0
        selected_label = st.selectbox(
            "Preset-Filter",
            options=list(preset_labels),
            index=preset_index,
            help=(
                "Baseline: alle Topics. Ohne Kamera: nur Cam-Topics ausfiltern. "
                "Analyse: schreibt keine Messages zu osf/arduino/…, "
                "TXT BME680/Kamera/LDR — kleinere Logs für CCU/FTS/Module (vgl. DR-25)."
            ),
            key=f"session_recorder_preset_{current_preset}",
        )
        new_preset = preset_values[preset_labels.index(selected_label)]
        if new_preset != current_preset:
            settings_manager.set_session_recorder_recording_exclusion_preset(new_preset)

        filter_mode_labels = (
            "Kein zusätzlicher Filter",
            "Custom Exclude (ausgewählte Topics ausschließen)",
            "Custom Include (nur ausgewählte Topics aufnehmen)",
        )
        filter_mode_values = (CUSTOM_FILTER_MODE_NONE, CUSTOM_FILTER_MODE_EXCLUDE, CUSTOM_FILTER_MODE_INCLUDE)
        current_filter_mode = settings_manager.get_session_recorder_custom_filter_mode()
        mode_index = filter_mode_values.index(current_filter_mode) if current_filter_mode in filter_mode_values else 0
        selected_mode_label = st.selectbox(
            "Zusatzfilter-Modus",
            options=list(filter_mode_labels),
            index=mode_index,
            key=f"session_recorder_custom_filter_mode_{current_filter_mode}",
        )
        selected_filter_mode = filter_mode_values[filter_mode_labels.index(selected_mode_label)]
        if selected_filter_mode != current_filter_mode:
            settings_manager.set_session_recorder_custom_filter_mode(selected_filter_mode)
            current_filter_mode = selected_filter_mode

        if current_filter_mode in (CUSTOM_FILTER_MODE_EXCLUDE, CUSTOM_FILTER_MODE_INCLUDE):
            st.markdown("##### 🎯 Custom Topic-Auswahl")
            known_topics = _collect_known_topics(settings_manager)
            persisted_topics = settings_manager.get_session_recorder_custom_filter_topics()
            options = sorted(set(known_topics).union(persisted_topics))
            selected_topics = st.multiselect(
                "Topics auswählen",
                options=options,
                default=[t for t in persisted_topics if t in options],
                help=(
                    "Exakte Topics oder Prefix-Regeln (z. B. /j1/txt/1/i/cam/# oder osf/arduino/*) "
                    "werden unterstützt."
                ),
                key="session_recorder_custom_filter_topics_select",
            )
            custom_topic_add = st.text_input(
                "Topic-Regel hinzufügen (optional)",
                value="",
                placeholder="z. B. /j1/txt/1/i/cam/#",
                key="session_recorder_custom_filter_topic_add",
            ).strip()
            if custom_topic_add:
                selected_topics = sorted(set(selected_topics).union({custom_topic_add}))
            if selected_topics != persisted_topics:
                settings_manager.set_session_recorder_custom_filter_topics(selected_topics)
            st.caption(f"Aktive Custom-Topics: {len(selected_topics)}")

        if st.session_state.session_recorder["recording"]:
            st.markdown("---")
            st.subheader("📋 Session-Meta (optional)")
            st.caption(
                "Wird als **erste Zeile** in der `.log` gespeichert "
                "(ohne topic/payload/timestamp — Replay ignoriert sie)."
            )
            st.selectbox(
                "CCU / Order-Ergebnis (Kurz)",
                options=["unknown", "ok", "nok", "mixed"],
                key="session_recorder_meta_outcome",
                help="Zusammenfassung des Order-Ergebnisses für INVENTORY / Analyse.",
            )
            st.text_input(
                "CCU-Version (optional, Override)",
                value=str(st.session_state.get("session_recorder_meta_ccu_version", "") or ""),
                key="session_recorder_meta_ccu_version",
                placeholder="z. B. 1.3.0-osf.3",
                help=(
                    "Optionaler manueller Override. Ohne Eingabe versucht der Recorder "
                    "die Version automatisch aus CCU-Topics zu erkennen."
                ),
            )
            st.text_area(
                "CCU / Orders (was wurde geordert / Szenario)",
                height=100,
                key="session_recorder_meta_ccu",
                placeholder="z. B. zwei parallele Lageraufträge, Quality-Fail → Ersatzauftrag …",
            )
            st.text_area(
                "Zusätzliche Notiz",
                height=68,
                key="session_recorder_meta_note",
                placeholder="Optional",
            )

    # Status anzeigen
    if st.session_state.session_recorder["recording"]:
        st.markdown("---")
        st.subheader("📊 Aufnahme-Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            message_count = message_buffer.count()
            st.metric("Nachrichten", message_count, delta=None)

        with col2:
            if st.session_state.session_recorder["start_time"]:
                duration = datetime.now() - st.session_state.session_recorder["start_time"]
                minutes, seconds = divmod(duration.seconds, 60)
                duration_str = f"{minutes:02d}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                st.metric("Dauer", duration_str)

        with col3:
            st.metric("Status", "🔴 Aufnahme läuft")

        # Letzte Nachrichten anzeigen
        messages = message_buffer.get_messages()
        if messages:
            st.markdown("**Letzte Nachrichten:**")
            for msg in messages[-5:]:  # Letzte 5 Nachrichten
                st.code(f"{msg['topic']}: {msg['payload'][:100]}...")

        st.caption("🔄 Auto-Refresh aktiv (alle 10s).")
        time.sleep(10)
        st.rerun()


def connect_to_broker(mqtt_settings: Dict[str, Any]) -> bool:
    """Verbindet zum MQTT Broker"""
    try:
        import paho.mqtt.client as mqtt

        # MQTT Client erstellen
        mqtt_client = mqtt.Client(client_id="session_manager_session_recorder")

        # Callback-Funktionen setzen
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message_received

        # Username/Password setzen falls vorhanden
        if mqtt_settings.get("username") and mqtt_settings.get("password"):
            mqtt_client.username_pw_set(mqtt_settings["username"], mqtt_settings["password"])
            logger.info(f"🔐 MQTT Authentifizierung: {mqtt_settings['username']}")

        # Verbinden
        mqtt_client.connect(mqtt_settings["host"], mqtt_settings["port"], mqtt_settings["timeout"])
        mqtt_client.loop_start()

        # Kurz warten, damit Verbindung etabliert wird
        import time

        time.sleep(0.5)

        # MQTT Client in Session State speichern
        st.session_state.session_recorder["mqtt_client"] = mqtt_client

        logger.debug(f"✅ MQTT verbunden: {mqtt_settings['host']}:{mqtt_settings['port']}")
        return True

    except Exception as e:
        logger.error(f"❌ MQTT Verbindungsfehler: {e}")
        return False


def disconnect_from_broker():
    """Trennt MQTT Verbindung"""
    global _recording_active
    try:
        _recording_active = False
        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            st.session_state.session_recorder["mqtt_client"] = None
            logger.debug("✅ MQTT getrennt")
    except Exception as e:
        logger.error(f"❌ MQTT Trennung Fehler: {e}")


def on_connect(client, userdata, flags, rc):
    """Callback für MQTT Verbindung – Subscribe muss NACH Verbindung erfolgen"""
    if rc == 0:
        logger.debug("✅ MQTT Broker verbunden")
        client.subscribe("#")
    else:
        logger.error(f"❌ MQTT Verbindung fehlgeschlagen: {rc}")


def start_recording(mqtt_settings=None, rerun_controller=None) -> bool:
    """
    Startet die Aufnahme. Verbindet bei Bedarf automatisch zum Broker.
    Nur Nachrichten während der Aufnahme werden gespeichert.
    """
    global _recording_active, _include_retained, _recording_exclusion_preset
    global _recording_custom_filter_mode, _recording_custom_filter_topics
    try:
        logger.info("🔴 Session-Aufnahme wird gestartet...")

        # Buffer immer leeren – nur neue Messages ab jetzt
        message_buffer.clear()

        # Flags für Callback setzen (läuft im MQTT-Thread)
        _recording_active = True
        _include_retained = st.session_state.session_recorder.get("include_retained", False)
        from .settings_manager import SettingsManager

        settings_manager = SettingsManager()
        _recording_exclusion_preset = settings_manager.get_session_recorder_recording_exclusion_preset()
        _recording_custom_filter_mode = settings_manager.get_session_recorder_custom_filter_mode()
        _recording_custom_filter_topics = settings_manager.get_session_recorder_custom_filter_topics()

        # Falls nicht verbunden: zuerst verbinden (Subscribe erfolgt in on_connect)
        just_connected = False
        if not st.session_state.session_recorder["mqtt_client"]:
            if not mqtt_settings:
                mqtt_settings = settings_manager.get_session_recorder_mqtt_settings()
            if not connect_to_broker(mqtt_settings):
                _recording_active = False
                return False
            just_connected = True
            if rerun_controller:
                rerun_controller.request_rerun()

        mqtt_client = st.session_state.session_recorder["mqtt_client"]
        if mqtt_client:
            # Subscribe: bei frischem Connect in on_connect; bei erneutem Start (nach Stop) hier
            if not just_connected:
                mqtt_client.subscribe("#")
            logger.info(
                "✅ Session-Aufnahme gestartet - nur Nachrichten während der Aufnahme"
                + (" (inkl. retained)" if _include_retained else "")
            )
            return True
        _recording_active = False
        return False

    except Exception as e:
        logger.error(f"❌ Fehler beim Starten der Aufnahme: {e}")
        _recording_active = False
        return False


def pause_recording():
    """Pausiert die Aufnahme"""
    try:
        logger.info("⏸️ Session-Aufnahme wird pausiert...")

        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            mqtt_client.unsubscribe("#")

            # Session State aktualisieren
            st.session_state.session_recorder["recording"] = False

            logger.info("✅ Session-Aufnahme pausiert - Topics deabonniert")
        else:
            logger.error("❌ Kein MQTT Client verfügbar für Pause")
    except Exception as e:
        logger.error(f"❌ Fehler beim Pausieren der Aufnahme: {e}")


def stop_recording() -> bool:
    """Beendet die Aufnahme und speichert. Setzt ``session_recorder['recording']`` immer zurück (finally)."""
    global _recording_active
    _recording_active = False
    stopped_ok = True
    try:
        logger.info("⏹️ Session-Aufnahme wird gestoppt...")

        # Unsubscribe separat: Broker-Fehler darf Speichern + UI-Reset nicht verhindern
        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            try:
                mqtt_client.unsubscribe("#")
                logger.info("📡 MQTT Topics deabonniert")
            except Exception as ue:
                logger.error(f"❌ MQTT unsubscribe beim Stoppen: {ue}")
                stopped_ok = False

        # Session speichern
        message_count = message_buffer.count()
        if message_count > 0:
            logger.info(f"💾 Session wird gespeichert ({message_count} Messages)...")
            save_session()
            message_buffer.clear()
            st.session_state.session_recorder["session_name"] = ""
            st.session_state.session_recorder["start_time"] = None
            _clear_session_meta_widget_keys()
            logger.info("✅ Session erfolgreich gespeichert")
        else:
            logger.warning("⚠️ Keine Messages zum Speichern vorhanden")

        logger.info("✅ Session-Aufnahme beendet")

    except Exception as e:
        logger.error(f"❌ Fehler beim Stoppen der Aufnahme: {e}")
        stopped_ok = False
    finally:
        st.session_state.session_recorder["recording"] = False

    return stopped_ok


def on_message_received(client, userdata, msg):
    """Callback für empfangene MQTT-Nachrichten – nur während Aufnahme, optional ohne retained"""
    global _recording_active, _include_retained, _recording_exclusion_preset
    global _recording_custom_filter_mode, _recording_custom_filter_topics
    try:
        if not _recording_active:
            return
        is_retain = getattr(msg, "retain", False)
        if is_retain and not _include_retained:
            return
        if not should_write_message_to_session_log(
            msg.topic,
            _recording_exclusion_preset,
            custom_filter_mode=_recording_custom_filter_mode,
            custom_filter_topics=_recording_custom_filter_topics,
        ):
            return

        message = {
            "topic": msg.topic,
            "payload": msg.payload.decode("utf-8"),
            "timestamp": utc_iso_timestamp_ms(),
            "qos": getattr(msg, "qos", 0),
            "retain": is_retain,
        }
        message_buffer.add_message(message)
        logger.debug(f"📨 Nachricht empfangen: {msg.topic} ({len(msg.payload)} bytes)")

    except Exception as e:
        logger.error(f"❌ Nachricht Verarbeitung Fehler: {e}")


def save_session():
    """Speichert die Session-Daten"""
    try:
        logger.info("💾 Session-Datei wird erstellt...")

        from .settings_manager import SettingsManager

        settings_manager = SettingsManager()
        session_directory = settings_manager.get_session_recorder_directory()
        # recording_settings = settings_manager.get_setting("session_recorder", "recording", {})  # Unused for now

        # Session-Verzeichnis erstellen (moderne Paket-Struktur)
        if not Path(session_directory).is_absolute():
            # Paket-relative Pfade verwenden
            # Projekt-Root-relative Pfade für Nutz-Daten verwenden
            project_root = PROJECT_ROOT
            session_dir = project_root / session_directory
        else:
            session_dir = Path(session_directory)
        session_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📁 Session-Verzeichnis: {session_dir}")

        # Dateiname generieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = st.session_state.session_recorder["session_name"]

        # Log-Format speichern (JSON-Zeilen)
        messages = message_buffer.get_messages()
        message_count = len(messages)
        logger.info(f"📊 {message_count} Messages werden gespeichert...")
        mqtt_settings = settings_manager.get_session_recorder_mqtt_settings()
        ccu_version, ccu_version_source = extract_ccu_version_from_messages(messages)
        if ccu_version == "unknown":
            runtime_version, runtime_source = detect_ccu_version_via_runtime_image(str(mqtt_settings.get("host", "")))
            if runtime_version != "unknown":
                ccu_version, ccu_version_source = runtime_version, runtime_source
        manual_ccu_version = str(st.session_state.get("session_recorder_meta_ccu_version", "") or "").strip()
        if not manual_ccu_version and ccu_version == "unknown":
            logger.warning(
                "⚠️ CCU-Version konnte nicht automatisch erkannt werden. "
                "Nutze optional 'CCU-Version (Override)' fuer eindeutige Analysen."
            )

        log_filename = f"{session_name}_{timestamp}.log"
        log_filepath = session_dir / log_filename
        logger.info(f"📝 Log-Datei wird erstellt: {log_filename}")

        ended_at = datetime.now()
        started_at = st.session_state.session_recorder.get("start_time") or ended_at
        meta_line = build_session_meta_line(
            session_name=session_name,
            log_filename=log_filename,
            recording_started_at=started_at,
            recording_ended_at=ended_at,
            recording_exclusion_preset=_recording_exclusion_preset,
            broker_host=str(mqtt_settings.get("host", "")),
            broker_port=int(mqtt_settings.get("port", 1883)),
            ccu_orders_description=str(st.session_state.get("session_recorder_meta_ccu", "") or ""),
            ccu_order_outcome=str(st.session_state.get("session_recorder_meta_outcome", "unknown") or "unknown"),
            note=str(st.session_state.get("session_recorder_meta_note", "") or ""),
            ccu_version=manual_ccu_version or ccu_version,
            ccu_version_source=("manual_override" if manual_ccu_version else ccu_version_source),
        )
        save_log_session(log_filepath, messages, meta_line=meta_line)
        logger.info(f"✅ Log Session gespeichert: {log_filepath}")

        st.success(f"💾 Session gespeichert: {log_filename}")
        logger.info(f"🎉 Session erfolgreich gespeichert: {message_count} Messages")

    except Exception as e:
        logger.error(f"❌ Session Speichern Fehler: {e}")
        st.error(f"❌ Fehler beim Speichern: {e}")


def _clear_session_meta_widget_keys() -> None:
    """Entfernt Meta-Widget-Keys nach Speichern (nächste Aufnahme startet leer)."""
    for k in (
        "session_recorder_meta_ccu",
        "session_recorder_meta_note",
        "session_recorder_meta_outcome",
        "session_recorder_meta_ccu_version",
    ):
        st.session_state.pop(k, None)


def save_log_session(
    filepath: Path,
    messages: List[Dict[str, Any]],
    meta_line: str | None = None,
):
    """Speichert Session als Log-Datei. Optional: erste Zeile session_meta (ohne topic/payload/timestamp)."""
    try:
        logger.debug(f"📝 Log-Datei wird erstellt: {filepath}")

        with open(filepath, "w", encoding="utf-8") as f:
            if meta_line:
                f.write(meta_line.strip() + "\n")
            for msg in messages:
                log_entry = {
                    "topic": msg["topic"],
                    "payload": msg["payload"],
                    "timestamp": msg["timestamp"],
                    "qos": msg.get("qos", 0),
                    "retain": msg.get("retain", False),
                }
                f.write(json.dumps(log_entry) + "\n")

        logger.debug(f"✅ Log Session gespeichert: {len(messages)} Messages in {filepath}")

    except Exception as e:
        logger.error(f"❌ Log Speichern Fehler: {e}")
        raise
