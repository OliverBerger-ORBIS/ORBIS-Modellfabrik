#!/usr/bin/env python3
"""
Statischer Test für auftrag_weiss_1
Testet Production Step Sequenz mit aufbereiteten Testdaten

Ziele:
1. Testdaten wie MQTT Client + Gateway aufbereiten
2. Business Function (ProductionOrderManager) testen
3. Sequenz-Fehler identifizieren
4. Status-Management validieren
"""

import json
import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock


class WeissOrderStaticTest(unittest.TestCase):
    """Statischer Test für auftrag_weiss_1 mit aufbereiteten Testdaten"""

    def setUp(self):
        """Setup für jeden Test"""
        # Lade echte Session-Daten für auftrag_weiss_1
        self.session_file = "data/omf-data/sessions/auftrag-weiss_1.log"
        self.test_messages = self._load_and_prepare_test_messages()

        # Mock ProductionOrderManager
        self.mock_production_order_manager = MagicMock()

        # Mock Gateway
        self.mock_gateway = MagicMock()
        self.mock_gateway.production_order_manager = self.mock_production_order_manager

    def _load_and_prepare_test_messages(self) -> List[Dict[str, Any]]:
        """Lade und bereite Testdaten wie MQTT Client + Gateway auf"""
        messages = []

        try:
            with open(self.session_file) as f:
                for line in f:
                    if line.strip():
                        message = json.loads(line.strip())
                        messages.append(message)
        except FileNotFoundError:
            self.fail(f"Session-Datei nicht gefunden: {self.session_file}")

        # Filtere relevante Topics für Production Orders
        relevant_topics = [
            "ccu/order/request",
            "ccu/order/response",
            "ccu/order/active",
            "ccu/order/completed",
            "module/v1/ff/SVR3QA0022/state",  # HBW
            "module/v1/ff/SVR4H76449/state",  # DRILL
            "module/v1/ff/SVR3QA2098/state",  # MILL
            "module/v1/ff/SVR4H76530/state",  # AIQS
            "module/v1/ff/SVR4H73275/state",  # DPS
            "module/v1/ff/NodeRed/SVR4H73275/state",  # DPS via NodeRED
            "module/v1/ff/NodeRed/SVR4H76530/state",  # AIQS via NodeRED
            "fts/v1/ff/5iO4/state",  # FTS Navigation
        ]

        # Filtere relevante Messages
        relevant_messages = []
        for message in messages:
            topic = message.get("topic", "")
            if any(relevant_topic in topic for relevant_topic in relevant_topics):
                relevant_messages.append(message)

        # Sortiere nach Timestamp
        relevant_messages.sort(key=lambda x: x.get("timestamp", ""))

        return relevant_messages

    def _prepare_gateway_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Bereite Message wie Gateway für Business Manager auf"""
        topic = message.get("topic", "")
        payload_str = message.get("payload", "{}")

        # Parse Payload
        try:
            payload = json.loads(payload_str) if isinstance(payload_str, str) else payload_str
        except json.JSONDecodeError:
            payload = {}

        # Gateway Message Format
        gateway_message = {
            "topic": topic,
            "payload": payload,
            "meta": {
                "timestamp": message.get("timestamp", ""),
                "qos": message.get("qos", 0),
                "retain": message.get("retain", False),
            },
        }

        return gateway_message

    def _extract_order_messages(self, order_id: str) -> List[Dict[str, Any]]:
        """Extrahiere alle Messages für eine spezifische Order-ID"""
        order_messages = []

        for message in self.test_messages:
            payload = message.get("payload", {})

            # Payload kann String oder Dict sein
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

            if isinstance(payload, dict) and payload.get("orderId") == order_id:
                order_messages.append(message)

        return order_messages

    def test_weiss_order_258beef9_detailed_analysis(self):
        """Detaillierte Analyse der Order 258beef9 (Weiß)"""
        order_id = "258beef9-6001-43a2-b7d4-01ed50f4b155"
        order_messages = self._extract_order_messages(order_id)

        self.assertGreater(len(order_messages), 0, f"Keine Messages für Order {order_id} gefunden")

        print(f"\n⚪ WEISS ORDER {order_id[:8]}... DETAILLIERTE ANALYSE:")
        print(f"   Total Messages: {len(order_messages)}")

        # Analysiere jeden Message
        steps = []
        for i, message in enumerate(order_messages):
            topic = message.get("topic", "")
            payload_str = message.get("payload", "{}")
            timestamp = message.get("timestamp", "")

            try:
                payload = json.loads(payload_str) if isinstance(payload_str, str) else payload_str
                action_state = payload.get("actionState", {})

                if action_state:
                    command = action_state.get("command", "")
                    state = action_state.get("state", "")
                    action_id = action_state.get("id", "")

                    # Bestimme Module Type
                    module_type = None
                    if "SVR3QA0022" in topic:
                        module_type = "HBW"
                    elif "SVR4H76449" in topic:
                        module_type = "DRILL"
                    elif "SVR3QA2098" in topic:
                        module_type = "MILL"
                    elif "SVR4H76530" in topic:
                        module_type = "AIQS"
                    elif "SVR4H73275" in topic:
                        module_type = "DPS"
                    elif "5iO4" in topic:
                        module_type = "FTS"

                    step_info = {
                        "index": i + 1,
                        "timestamp": timestamp,
                        "module_type": module_type,
                        "command": command,
                        "state": state,
                        "action_id": action_id,
                        "topic": topic,
                    }

                    steps.append(step_info)

                    # Zeige wichtige Steps
                    if command in ["PICK", "DROP", "DRILL", "MILL", "CHECK_QUALITY", "DOCK"]:
                        print(f"   Step {i+1:2d}: {module_type} {command} - {state} ({timestamp})")

            except json.JSONDecodeError:
                continue

        print("\n   📊 SUMMARY:")
        print(f"      Total Steps: {len(steps)}")

        # Analysiere Commands
        commands = {}
        for step in steps:
            cmd = step["command"]
            commands[cmd] = commands.get(cmd, 0) + 1

        print(f"      Commands: {commands}")

        # Analysiere States
        states = {}
        for step in steps:
            state = step["state"]
            states[state] = states.get(state, 0) + 1

        print(f"      States: {states}")

        # Analysiere Module
        modules = {}
        for step in steps:
            module = step["module_type"]
            modules[module] = modules.get(module, 0) + 1

        print(f"      Modules: {modules}")

        # Erkenne Sequenz-Fehler
        self._detect_sequence_errors(steps)

    def _detect_sequence_errors(self, steps: List[Dict[str, Any]]):
        """Erkenne Sequenz-Fehler in den Production Steps"""
        print("\n   🔍 SEQUENZ-ANALYSE:")

        # Gruppiere Steps nach Module
        module_steps = {}
        for step in steps:
            module = step["module_type"]
            if module not in module_steps:
                module_steps[module] = []
            module_steps[module].append(step)

        # Analysiere jedes Modul
        for module, module_step_list in module_steps.items():
            if len(module_step_list) > 1:
                print(f"      {module}: {len(module_step_list)} Steps")

                # Prüfe auf PICK/DROP Sequenz
                pick_steps = [s for s in module_step_list if s["command"] == "PICK"]
                drop_steps = [s for s in module_step_list if s["command"] == "DROP"]

                if pick_steps and drop_steps:
                    # Prüfe ob PICK vor DROP kommt
                    first_pick = min(pick_steps, key=lambda x: x["index"])
                    first_drop = min(drop_steps, key=lambda x: x["index"])

                    if first_drop["index"] < first_pick["index"]:
                        print("         ⚠️  SEQUENZ-FEHLER: DROP vor PICK!")
                        print(f"            DROP: Step {first_drop['index']} - {first_drop['state']}")
                        print(f"            PICK: Step {first_pick['index']} - {first_pick['state']}")
                    else:
                        print("         ✅ PICK/DROP Sequenz korrekt")

    def test_production_order_manager_integration(self):
        """Test ProductionOrderManager Integration mit echten Daten"""
        order_id = "258beef9-6001-43a2-b7d4-01ed50f4b155"
        order_messages = self._extract_order_messages(order_id)

        print("\n🧪 PRODUCTION ORDER MANAGER INTEGRATION TEST:")

        # Simuliere Gateway Message Processing
        for message in order_messages:
            gateway_message = self._prepare_gateway_message(message)

            # Simuliere Gateway → ProductionOrderManager Call
            topic = gateway_message["topic"]
            payload = gateway_message["payload"]
            gateway_message["meta"]

            # Prüfe ob Message an ProductionOrderManager geroutet werden sollte
            if self._should_route_to_production_order_manager(topic):
                print(f"   📨 Route to ProductionOrderManager: {topic}")
                print(f"      Payload: {json.dumps(payload, indent=2)[:200]}...")

                # Hier würde der echte ProductionOrderManager.process_message() aufgerufen
                # self.mock_production_order_manager.process_message.assert_called_with(topic, payload, meta)

    def _should_route_to_production_order_manager(self, topic: str) -> bool:
        """Prüfe ob Topic an ProductionOrderManager geroutet werden sollte"""
        production_order_topics = [
            "ccu/order/request",
            "ccu/order/response",
            "ccu/order/active",
            "ccu/order/completed",
            "module/v1/ff/SVR3QA0022/state",  # HBW
            "module/v1/ff/SVR4H76449/state",  # DRILL
            "module/v1/ff/SVR3QA2098/state",  # MILL
            "module/v1/ff/SVR4H76530/state",  # AIQS
            "module/v1/ff/SVR4H73275/state",  # DPS
            "module/v1/ff/NodeRed/SVR4H73275/state",  # DPS via NodeRED
            "module/v1/ff/NodeRed/SVR4H76530/state",  # AIQS via NodeRED
            "fts/v1/ff/5iO4/state",  # FTS Navigation
        ]

        return any(prod_topic in topic for prod_topic in production_order_topics)


if __name__ == "__main__":
    unittest.main()
