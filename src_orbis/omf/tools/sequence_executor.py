"""
SequenceExecutor - Führt Sequenzen aus (YML + Python)
Verwaltet die Ausführung von Workflow-Sequenzen mit Wait-Schritten
"""

import json
import threading
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

try:
    from .workflow_order_manager import workflow_order_manager
except ImportError:
    from workflow_order_manager import workflow_order_manager


class StepStatus(Enum):
    """Status eines Sequenz-Schritts"""

    PENDING = "pending"
    READY = "ready"
    SENT = "sent"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SequenceStep:
    """Ein Schritt in einer Sequenz"""

    step_id: int
    name: str
    topic: str
    payload: Dict[str, Any]
    wait_condition: Optional[Dict[str, Any]] = None
    status: StepStatus = StepStatus.PENDING
    context_vars: Dict[str, Any] = None

    def __post_init__(self):
        if self.context_vars is None:
            self.context_vars = {}


@dataclass
class SequenceDefinition:
    """Definition einer Sequenz"""

    name: str
    description: str
    steps: List[SequenceStep]
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


class WaitHandler:
    """Behandelt Wait-Schritte zwischen Commands"""

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.waiting_steps: Dict[str, Dict] = {}
        self._wait_thread = None
        self._stop_waiting = False

    def start_waiting(self, order_id: str, step: SequenceStep, callback: Callable, wait_condition: Dict = None):
        """Startet Warten auf ein Event"""
        self.waiting_steps[order_id] = {
            "step": step,
            "callback": callback,
            "start_time": time.time(),
            "wait_condition": wait_condition or {"type": "timeout", "duration": 30},
        }

        if not self._wait_thread or not self._wait_thread.is_alive():
            self._stop_waiting = False
            self._wait_thread = threading.Thread(target=self._wait_worker, daemon=True)
            self._wait_thread.start()

    def stop_waiting(self, order_id: str):
        """Stoppt Warten für eine Order"""
        if order_id in self.waiting_steps:
            del self.waiting_steps[order_id]

    def get_remaining_wait_time(self, order_id: str) -> float:
        """Gibt die verbleibende Wartezeit in Sekunden zurück"""
        if order_id not in self.waiting_steps:
            return 0.0

        wait_info = self.waiting_steps[order_id]
        wait_condition = wait_info["wait_condition"]

        if wait_condition.get("type") == "timeout":
            duration = wait_condition.get("duration", 30)
            elapsed = time.time() - wait_info["start_time"]
            remaining = max(0, duration - elapsed)
            return remaining

        return 0.0

    def _wait_worker(self):
        """Worker-Thread für Event-Waiting"""
        while not self._stop_waiting and self.waiting_steps:
            for order_id, wait_info in list(self.waiting_steps.items()):
                step = wait_info["step"]
                callback = wait_info["callback"]
                wait_condition = wait_info["wait_condition"]

                # Prüfe auf Timeout-Bedingung
                if wait_condition.get("type") == "timeout":
                    duration = wait_condition.get("duration", 30)
                    if time.time() - wait_info["start_time"] >= duration:
                        # Timeout erreicht - Schritt als erfolgreich markieren
                        print(f"⏰ Timeout erreicht ({duration}s) für Schritt: {step.name}")
                        callback(order_id, step, True)
                        del self.waiting_steps[order_id]
                else:
                    # Prüfe auf eingehende MQTT-Nachrichten (für andere Bedingungen)
                    if self._check_wait_condition(wait_condition):
                        # Wait-Bedingung erfüllt
                        callback(order_id, step, True)
                        del self.waiting_steps[order_id]
                    elif time.time() - wait_info["start_time"] > 30:  # Fallback Timeout
                        # Timeout erreicht
                        callback(order_id, step, False)
                        del self.waiting_steps[order_id]

            time.sleep(0.1)  # Kurze Pause

    def _check_wait_condition(self, condition: Dict[str, Any]) -> bool:
        """Prüft ob Wait-Bedingung erfüllt ist"""
        if not condition:
            return True

        # Einfache Implementierung - kann erweitert werden
        # Prüfe auf eingehende MQTT-Nachrichten
        if self.mqtt_client and hasattr(self.mqtt_client, "get_recent_messages"):
            recent_messages = self.mqtt_client.get_recent_messages()
            for msg in recent_messages:
                if self._message_matches_condition(msg, condition):
                    return True

        return False

    def _message_matches_condition(self, message: Dict, condition: Dict[str, Any]) -> bool:
        """Prüft ob Nachricht der Bedingung entspricht"""
        if "topic" in condition and message.get("topic") != condition["topic"]:
            return False

        if "payload_contains" in condition:
            payload = message.get("payload", {})
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except (json.JSONDecodeError, TypeError):
                    return False

            for key, value in condition["payload_contains"].items():
                if payload.get(key) != value:
                    return False

        return True


class SequenceExecutor:
    """Führt Sequenzen aus"""

    def __init__(self, mqtt_client=None):
        self.mqtt_client = mqtt_client
        self.wait_handler = WaitHandler(mqtt_client) if mqtt_client else None
        self.running_sequences: Dict[str, SequenceDefinition] = {}

    def execute_sequence(self, sequence: SequenceDefinition) -> str:
        """Startet Ausführung einer Sequenz"""
        # Workflow-Order erstellen
        order = workflow_order_manager.create_order(sequence.name)
        order.total_steps = len(sequence.steps)

        # Kontext-Variablen aus SequenceDefinition in Order übertragen
        if sequence.context:
            order.context.update(sequence.context)

        # Sequenz speichern
        self.running_sequences[order.order_id] = sequence

        # Alle Schritte initial auf PENDING setzen, ersten auf READY
        if sequence.steps:
            for i, step in enumerate(sequence.steps):
                if i == 0:
                    step.status = StepStatus.READY
                else:
                    step.status = StepStatus.PENDING

            print(f"🚀 Starte Sequenz: {sequence.name}")
            print(f"📋 {len(sequence.steps)} Schritte geplant")
            # Automatisch ersten Schritt ausführen
            self.execute_step(order.order_id, 0)

        return order.order_id

    def execute_step(self, order_id: str, step_index: int) -> bool:
        """Führt einen spezifischen Schritt aus"""
        order = workflow_order_manager.get_order(order_id)
        sequence = self.running_sequences.get(order_id)

        if not order or not sequence or step_index >= len(sequence.steps):
            return False

        step = sequence.steps[step_index]

        # Schritt als gesendet markieren
        step.status = StepStatus.SENT
        workflow_order_manager.update_step(order_id, step_index + 1)

        # MQTT-Nachricht senden
        if self.mqtt_client:
            try:
                # OrderUpdateId vor dem Senden inkrementieren
                order_update_id = workflow_order_manager.increment_update_id(order_id)

                # Erweiterte Kontext-Variablen für Payload-Resolution
                extended_context = order.context.copy()
                extended_context.update(
                    {
                        "orderId": order.order_id,
                        "orderUpdateId": order_update_id,  # Integer, wie Factory-Steuerung
                        "action_id": str(uuid.uuid4()),  # Eindeutige Action-ID für jeden Schritt
                    }
                )

                # Topic und Payload mit Kontext-Variablen ersetzen
                topic = self._resolve_variables(step.topic, extended_context)
                payload = self._resolve_variables(step.payload, extended_context)

                # Reihenfolge der Payload-Elemente korrigieren (wie Factory-Steuerung)
                if isinstance(payload, dict):
                    ordered_payload = {
                        "serialNumber": payload.get("serialNumber"),
                        "action": payload.get("action"),
                        "orderId": payload.get("orderId"),
                        "orderUpdateId": order_update_id,  # Integer, nicht String
                    }
                    payload = ordered_payload

                # MQTT-Nachricht senden (Payload als Dictionary, wie Factory-Steuerung)
                print(f"📤 Sende Nachricht: {topic}")
                print(f"📋 Payload: {json.dumps(payload, indent=2)}")
                self.mqtt_client.publish(topic, payload, qos=1)

                # Automatisch WAIT-Schritt zwischen Nachrichten (5 Sekunden)
                step.status = StepStatus.WAITING
                print("⏰ Warte 5 Sekunden vor nächstem Schritt...")

                # Einfache Timer-basierte Lösung
                def wait_and_continue():
                    time.sleep(5.0)  # 5 Sekunden warten
                    print(f"⏰ Timeout erreicht (5.0s) für Schritt: {step.name}")
                    self._on_wait_completed(order_id, step, True)

                # Timer in separatem Thread starten
                wait_thread = threading.Thread(target=wait_and_continue, daemon=True)
                wait_thread.start()

                return True

            except Exception:
                step.status = StepStatus.ERROR
                workflow_order_manager.set_error(order_id)
                return False

        return False

    def _on_wait_completed(self, order_id: str, step: SequenceStep, success: bool):
        """Callback für abgeschlossene Wait-Schritte"""
        if success:
            step.status = StepStatus.COMPLETED
            print(f"✅ Schritt abgeschlossen: {step.name}")
            # Nächsten Schritt vorbereiten
            self._prepare_next_step(order_id)
            # Prüfen ob Sequenz abgeschlossen oder nächster Schritt ausführen
            self._check_sequence_completion(order_id)
        else:
            step.status = StepStatus.ERROR
            workflow_order_manager.set_error(order_id)

    def _check_sequence_completion(self, order_id: str):
        """Prüft ob Sequenz abgeschlossen ist und führt nächsten Schritt aus"""
        sequence = self.running_sequences.get(order_id)
        if not sequence:
            return

        # Prüfe ob alle Schritte abgeschlossen sind
        all_completed = all(step.status in [StepStatus.COMPLETED] for step in sequence.steps)

        if all_completed:
            workflow_order_manager.complete_order(order_id)
            print(f"✅ Sequenz {sequence.name} abgeschlossen")
        else:
            # Prüfe ob es noch ausstehende Schritte gibt
            pending_steps = [step for step in sequence.steps if step.status in [StepStatus.PENDING, StepStatus.READY]]

            if pending_steps:
                print(f"🔄 {len(pending_steps)} ausstehende Schritte gefunden, führe nächsten aus...")
                # Automatisch nächsten Schritt ausführen
                self._execute_next_step(order_id)
            else:
                print(f"⚠️ Sequenz {sequence.name} hat keine ausstehenden Schritte, aber ist nicht abgeschlossen")
                # Debug: Zeige alle Schritt-Status
                for i, step in enumerate(sequence.steps):
                    print(f"  Schritt {i+1} ({step.name}): {step.status}")

    def _execute_next_step(self, order_id: str):
        """Führt automatisch den nächsten Schritt aus"""
        order = workflow_order_manager.get_order(order_id)
        sequence = self.running_sequences.get(order_id)

        if not order or not sequence:
            print(f"❌ Keine Order oder Sequenz gefunden für {order_id}")
            return

        # Debug: Zeige alle Schritt-Status
        print(f"🔍 Schritt-Status für {sequence.name}:")
        for i, step in enumerate(sequence.steps):
            print(f"  Schritt {i+1} ({step.name}): {step.status}")

        # Finde nächsten ausstehenden Schritt
        next_step_index = None
        for i, step in enumerate(sequence.steps):
            if step.status in [StepStatus.READY, StepStatus.PENDING]:
                next_step_index = i
                print(f"🎯 Nächster Schritt gefunden: {i+1} ({step.name}) - Status: {step.status}")
                break

        if next_step_index is not None:
            print(f"🔄 Führe automatisch Schritt {next_step_index + 1} aus: {sequence.steps[next_step_index].name}")
            self.execute_step(order_id, next_step_index)
        else:
            print(f"❌ Kein nächster Schritt gefunden für {sequence.name}")

    def _prepare_next_step(self, order_id: str):
        """Bereitet nächsten Schritt vor"""
        order = workflow_order_manager.get_order(order_id)
        sequence = self.running_sequences.get(order_id)

        if not order or not sequence:
            return

        # Finde nächsten ausstehenden Schritt
        for i, step in enumerate(sequence.steps):
            if step.status == StepStatus.PENDING:
                step.status = StepStatus.READY
                print(f"📋 Schritt {i + 1} bereit: {step.name}")
                break

        # Debug: Zeige alle Schritt-Status nach der Vorbereitung
        print(f"🔍 Schritt-Status nach Vorbereitung für {sequence.name}:")
        for i, step in enumerate(sequence.steps):
            print(f"  Schritt {i+1} ({step.name}): {step.status}")

    def cancel_sequence(self, order_id: str):
        """Bricht Sequenz ab"""
        workflow_order_manager.cancel_order(order_id)
        if self.wait_handler:
            self.wait_handler.stop_waiting(order_id)

        # Alle verbleibenden Schritte als abgebrochen markieren
        sequence = self.running_sequences.get(order_id)
        if sequence:
            for step in sequence.steps:
                if step.status == StepStatus.PENDING:
                    step.status = StepStatus.ERROR

    def _resolve_variables(self, data: Any, context: Dict[str, Any]) -> Any:
        """Ersetzt Variablen in Topics und Payloads"""
        if isinstance(data, str):
            # Einfache Variable-Ersetzung {{variable}}
            for key, value in context.items():
                data = data.replace(f"{{{{{key}}}}}", str(value))
            return data
        elif isinstance(data, dict):
            # Reihenfolge der Dictionary-Elemente beibehalten
            resolved_dict = {}
            for k, v in data.items():
                resolved_dict[k] = self._resolve_variables(v, context)
            return resolved_dict
        elif isinstance(data, list):
            return [self._resolve_variables(item, context) for item in data]
        else:
            return data

    def get_sequence_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Gibt Status einer Sequenz zurück"""
        order = workflow_order_manager.get_order(order_id)
        sequence = self.running_sequences.get(order_id)

        if not order or not sequence:
            return None

        return {
            "order": order,
            "sequence": sequence,
            "current_step": order.current_step,
            "total_steps": order.total_steps,
            "status": order.status,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "topic": step.topic,
                    "payload": step.payload,
                }
                for step in sequence.steps
            ],
        }
