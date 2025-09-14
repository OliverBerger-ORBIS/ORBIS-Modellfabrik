"""
ModuleStateManager - Automatisches Timing-Management für Modul-Sequenzen

Verwaltet Modul-Status und automatische Sequenz-Ausführung basierend auf MQTT-Status-Updates.
Ersetzt die manuelle Sichtkontrolle durch automatisches Timing-Management.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from threading import Event, Thread
from typing import Any, Dict, List, Optional

from .mqtt_gateway import MqttGateway
from .omf_mqtt_client import OmfMqttClient

# Logging konfigurieren
logger = logging.getLogger("omf.module_state_manager")


class ModuleState(Enum):
    """Modul-Status basierend auf Node-RED Flows Analyse"""

    IDLE = "IDLE"
    PICKBUSY = "PICKBUSY"
    WAITING_AFTER_PICK = "WAITING_AFTER_PICK"
    MILLBUSY = "MILLBUSY"
    DRILLBUSY = "DRILLBUSY"
    CHECKBUSY = "CHECKBUSY"
    WAITING_AFTER_MILL = "WAITING_AFTER_MILL"
    WAITING_AFTER_DRILL = "WAITING_AFTER_DRILL"
    WAITING_AFTER_CHECK = "WAITING_AFTER_CHECK"
    DROPBUSY = "DROPBUSY"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"


class CommandType(Enum):
    """Verfügbare Commands basierend auf module_config.yml"""

    PICK = "PICK"
    DROP = "DROP"
    STORE = "STORE"
    MILL = "MILL"
    DRILL = "DRILL"
    CHECK_QUALITY = "CHECK_QUALITY"
    INPUT_RGB = "INPUT_RGB"
    RGB_NFC = "RGB_NFC"
    NAVIGATE = "NAVIGATE"
    START_CHARGING = "start_charging"
    STOP_CHARGING = "stop_charging"
    GET_STATUS = "get_status"


@dataclass
class ModuleInfo:
    """Informationen über ein Modul"""

    module_id: str
    module_name: str
    module_type: str
    serial_number: str
    current_state: ModuleState = ModuleState.IDLE
    last_update: datetime = None
    is_available: bool = True


@dataclass
class SequenceStep:
    """Ein Schritt in einer Modul-Sequenz"""

    command: CommandType
    expected_state: ModuleState
    timeout: int = 30  # Sekunden
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ModuleSequence:
    """Eine komplette Modul-Sequenz (z.B. PICK → MILL → DROP)"""

    module_id: str
    sequence_name: str
    steps: List[SequenceStep]
    current_step: int = 0
    status: str = "pending"  # pending, running, completed, error
    order_id: str = None
    order_update_id: int = 0


class ModuleStateManager:
    """
    Singleton für Modul-Status-Management und automatische Sequenz-Ausführung

    Basiert auf Node-RED Flows Analyse:
    - Order Handling Engine (4567 Zeilen Code)
    - Modul-Status-Übergänge (IDLE → PICKBUSY → WAITING_AFTER_PICK → etc.)
    - Automatisches Timing-Management
    """

    _instance = None
    _modules: Dict[str, ModuleInfo] = {}
    _sequences: Dict[str, ModuleSequence] = {}
    _mqtt_client: Optional[OmfMqttClient] = None
    _gateway: Optional[MqttGateway] = None
    _running: bool = False
    _monitor_thread: Optional[Thread] = None
    _stop_event: Event = Event()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, mqtt_client: OmfMqttClient, gateway: MqttGateway):
        """Initialisiert den ModuleStateManager mit MQTT-Client und Gateway"""
        self._mqtt_client = mqtt_client
        self._gateway = gateway

        # Modul-Informationen basierend auf module_config.yml
        self._modules = {
            "AIQS": ModuleInfo(
                module_id="AIQS", module_name="Qualitätsprüfung", module_type="Processing", serial_number="SVR4H76530"
            ),
            "MILL": ModuleInfo(
                module_id="MILL", module_name="Fräsen", module_type="Processing", serial_number="SVR3QA2098"
            ),
            "DRILL": ModuleInfo(
                module_id="DRILL", module_name="Bohren", module_type="Processing", serial_number="SVR4H76449"
            ),
            "HBW": ModuleInfo(
                module_id="HBW", module_name="Hochregallager", module_type="Storage", serial_number="SVR3QA0022"
            ),
            "DPS": ModuleInfo(
                module_id="DPS",
                module_name="Warenein- und Ausgang",
                module_type="Input/Output",
                serial_number="SVR4H73275",
            ),
            "FTS": ModuleInfo(
                module_id="FTS",
                module_name="Fahrerloses Transportsystem",
                module_type="Transport",
                serial_number="CHRG0",
            ),
        }

        # MQTT-Subscription für Modul-Status
        self._subscribe_to_module_states()

        # Monitor-Thread starten
        self._start_monitor_thread()

        logger.info("ModuleStateManager initialisiert")

    def _subscribe_to_module_states(self):
        """Abonniert MQTT-Topics für Modul-Status-Updates (per-topic subscription)"""
        if not self._mqtt_client:
            logger.error("MQTT-Client nicht verfügbar")
            return

        # Topic-Filter für alle Module sammeln
        topic_filters = []

        # Status-Topics für alle Module
        for module in self._modules.values():
            topic_filter = f"module/v1/ff/{module.serial_number}/state"
            topic_filters.append(topic_filter)
            logger.info(f"Filter hinzugefügt: {topic_filter}")

        # Connection-Topics für alle Module
        for module in self._modules.values():
            topic_filter = f"module/v1/ff/{module.serial_number}/connection"
            topic_filters.append(topic_filter)
            logger.info(f"Filter hinzugefügt: {topic_filter}")

        # Per-topic subscription für alle Filter
        self._mqtt_client.subscribe_many(topic_filters, qos=1)
        logger.info(f"Per-topic subscription für {len(topic_filters)} Filter aktiviert")

    def _start_monitor_thread(self):
        """Startet den Monitor-Thread für Status-Updates"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._stop_event.clear()
        self._running = True
        self._monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Monitor-Thread gestartet")

    def _monitor_loop(self):
        """Hauptschleife für Status-Monitoring"""
        while self._running and not self._stop_event.is_set():
            try:
                # Status-Updates verarbeiten
                self._process_status_updates()

                # Laufende Sequenzen überwachen
                self._monitor_sequences()

                # Kurz warten
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Fehler im Monitor-Loop: {e}")
                time.sleep(1)

    def _process_status_updates(self):
        """Verarbeitet MQTT-Status-Updates"""
        if not self._mqtt_client:
            return

        # Status-Updates aus MQTT-Buffer lesen (per-topic subscription)
        for module in self._modules.values():
            topic_filter = f"module/v1/ff/{module.serial_number}/state"
            buffer = self._mqtt_client.get_buffer(topic_filter, maxlen=10)

            for message in buffer:
                self._update_module_state(module, message)

    def _update_module_state(self, module: ModuleInfo, message: Dict[str, Any]):
        """Aktualisiert den Status eines Moduls basierend auf MQTT-Nachricht"""
        try:
            payload = message.get("payload", {})
            state_str = payload.get("state", "UNKNOWN")
            status_str = payload.get("status", "UNKNOWN")

            # Status-Update
            if state_str in [s.value for s in ModuleState]:
                module.current_state = ModuleState(state_str)
                module.last_update = datetime.now(timezone.utc)
                module.is_available = status_str == "OK"

                logger.debug(f"Modul {module.module_id}: {state_str} ({status_str})")

        except Exception as e:
            logger.error(f"Fehler beim Status-Update für {module.module_id}: {e}")

    def _monitor_sequences(self):
        """Überwacht laufende Sequenzen und führt nächste Schritte aus"""
        for sequence_id, sequence in list(self._sequences.items()):
            if sequence.status != "running":
                continue

            try:
                self._process_sequence_step(sequence)
            except Exception as e:
                logger.error(f"Fehler bei Sequenz {sequence_id}: {e}")
                sequence.status = "error"

    def _process_sequence_step(self, sequence: ModuleSequence):
        """Verarbeitet den aktuellen Schritt einer Sequenz"""
        if sequence.current_step >= len(sequence.steps):
            sequence.status = "completed"
            logger.info(f"Sequenz {sequence.sequence_name} abgeschlossen")
            return

        current_step = sequence.steps[sequence.current_step]
        module = self._modules.get(sequence.module_id)

        if not module:
            logger.error(f"Modul {sequence.module_id} nicht gefunden")
            sequence.status = "error"
            return

        # Prüfen ob Modul bereit ist
        if not self._is_module_ready_for_command(module, current_step.command):
            return

        # Command senden
        if self._send_module_command(sequence, current_step):
            # Nächster Schritt vorbereiten
            sequence.current_step += 1
            sequence.order_update_id += 1

            if sequence.current_step >= len(sequence.steps):
                sequence.status = "completed"
                logger.info(f"Sequenz {sequence.sequence_name} abgeschlossen")

    def _is_module_ready_for_command(self, module: ModuleInfo, command: CommandType) -> bool:
        """Prüft ob ein Modul bereit für einen Command ist"""
        if not module.is_available:
            return False

        # Command-spezifische Bereitschaft prüfen
        if command == CommandType.PICK and module.current_state == ModuleState.IDLE:
            return True
        elif command == CommandType.MILL and module.current_state == ModuleState.WAITING_AFTER_PICK:
            return True
        elif command == CommandType.DRILL and module.current_state == ModuleState.WAITING_AFTER_PICK:
            return True
        elif command == CommandType.CHECK_QUALITY and module.current_state == ModuleState.WAITING_AFTER_PICK:
            return True
        elif command == CommandType.DROP and module.current_state in [
            ModuleState.WAITING_AFTER_MILL,
            ModuleState.WAITING_AFTER_DRILL,
            ModuleState.WAITING_AFTER_CHECK,
            ModuleState.WAITING_AFTER_PICK,
        ]:
            return True

        return False

    def _send_module_command(self, sequence: ModuleSequence, step: SequenceStep) -> bool:
        """Sendet einen Modul-Command über MQTT"""
        if not self._gateway:
            logger.error("MQTT-Gateway nicht verfügbar")
            return False

        module = self._modules.get(sequence.module_id)
        if not module:
            return False

        try:
            logger.info(f"Sende Command {step.command.value} an Modul {sequence.module_id}")
            logger.info(f"Topic: module/v1/ff/{module.serial_number}/order")

            # Command über MQTT-Gateway senden
            success = self._gateway.send(
                topic=f"module/v1/ff/{module.serial_number}/order",
                builder=lambda: {
                    "serialNumber": module.serial_number,
                    "orderId": sequence.order_id,
                    "orderUpdateId": sequence.order_update_id,
                    "action": {
                        "command": step.command.value,
                        "id": f"cmd_{int(time.time())}",
                        "metadata": step.metadata or {},
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                ensure_order_id=False,  # orderId wird bereits gesetzt
            )

            if success:
                logger.info(f"Command {step.command.value} an {module.module_id} gesendet")
            else:
                logger.error(f"Fehler beim Senden von {step.command.value} an {module.module_id}")

            return success

        except Exception as e:
            logger.error(f"Exception beim Senden von {step.command.value}: {e}")
            return False

    def start_sequence(
        self, module_id: str, sequence_name: str, commands: List[CommandType], order_id: str = None
    ) -> str:
        """Startet eine neue Modul-Sequenz"""
        logger.info(f"Starte Sequenz für Modul {module_id}: {sequence_name}")
        logger.info(f"Commands: {[cmd.value for cmd in commands]}")

        if module_id not in self._modules:
            logger.error(f"Modul {module_id} nicht gefunden")
            raise ValueError(f"Modul {module_id} nicht gefunden")

        # Sequenz-ID generieren
        sequence_id = f"{module_id}_{sequence_name}_{int(time.time())}"

        # Steps erstellen
        steps = []
        for i, command in enumerate(commands):
            expected_state = self._get_expected_state_for_command(command, i)
            step = SequenceStep(command=command, expected_state=expected_state, timeout=30, metadata={})
            steps.append(step)

        # Sequenz erstellen
        sequence = ModuleSequence(
            module_id=module_id,
            sequence_name=sequence_name,
            steps=steps,
            order_id=order_id or f"order_{int(time.time())}",
            status="running",
        )

        self._sequences[sequence_id] = sequence
        logger.info(f"Sequenz {sequence_name} für {module_id} gestartet: {[c.value for c in commands]}")

        return sequence_id

    def _get_expected_state_for_command(self, command: CommandType, step_index: int) -> ModuleState:
        """Bestimmt den erwarteten Status nach einem Command"""
        if command == CommandType.PICK:
            return ModuleState.PICKBUSY
        elif command in [CommandType.MILL, CommandType.DRILL, CommandType.CHECK_QUALITY]:
            return ModuleState.WAITING_AFTER_PICK
        elif command == CommandType.DROP:
            return ModuleState.DROPBUSY
        else:
            return ModuleState.IDLE

    def get_module_status(self, module_id: str) -> Optional[ModuleInfo]:
        """Gibt den aktuellen Status eines Moduls zurück"""
        return self._modules.get(module_id)

    def get_sequence_status(self, sequence_id: str) -> Optional[ModuleSequence]:
        """Gibt den Status einer Sequenz zurück"""
        return self._sequences.get(sequence_id)

    def stop_sequence(self, sequence_id: str):
        """Stoppt eine laufende Sequenz"""
        if sequence_id in self._sequences:
            self._sequences[sequence_id].status = "cancelled"
            logger.info(f"Sequenz {sequence_id} gestoppt")

    def get_all_module_status(self) -> Dict[str, ModuleInfo]:
        """Gibt den Status aller Module zurück"""
        return self._modules.copy()

    def get_running_sequences(self) -> Dict[str, ModuleSequence]:
        """Gibt alle laufenden Sequenzen zurück"""
        return {sid: seq for sid, seq in self._sequences.items() if seq.status == "running"}

    def shutdown(self):
        """Beendet den ModuleStateManager"""
        self._running = False
        self._stop_event.set()

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)

        logger.info("ModuleStateManager beendet")


# Singleton-Instanz
_module_state_manager = None


def get_module_state_manager() -> ModuleStateManager:
    """Gibt die Singleton-Instanz des ModuleStateManager zurück"""
    global _module_state_manager
    if _module_state_manager is None:
        _module_state_manager = ModuleStateManager()
    return _module_state_manager
