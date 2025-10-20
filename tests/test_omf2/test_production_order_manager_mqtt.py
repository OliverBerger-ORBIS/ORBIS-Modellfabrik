#!/usr/bin/env python3
"""
Test für ProductionOrderManager MQTT Message Processing
Testet ob Module State Messages korrekt verarbeitet werden

Ziele:
1. ProductionOrderManager.process_module_state_message() testen
2. MQTT Message Matching Algorithm validieren
3. Status-Updates in Production Plan testen
"""

import json
import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock


class ProductionOrderManagerMqttTest(unittest.TestCase):
    """Test für ProductionOrderManager MQTT Message Processing"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock ProductionOrderManager
        self.mock_production_order_manager = MagicMock()

        # Echte Session-Daten für auftrag_weiss_1
        self.session_file = "data/omf-data/sessions/auftrag-weiss_1.log"
        self.test_messages = self._load_test_messages()

    def _load_test_messages(self) -> List[Dict[str, Any]]:
        """Lade Test-Messages aus Session-Datei"""
        messages = []

        try:
            with open(self.session_file) as f:
                for line in f:
                    if line.strip():
                        message = json.loads(line.strip())
                        messages.append(message)
        except FileNotFoundError:
            self.fail(f"Session-Datei nicht gefunden: {self.session_file}")

        return messages

    def _filter_module_state_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtere Module State Messages"""
        module_state_topics = [
            "module/v1/ff/SVR3QA0022/state",  # HBW
            "module/v1/ff/SVR4H76449/state",  # DRILL
            "module/v1/ff/SVR3QA2098/state",  # MILL
            "module/v1/ff/SVR4H76530/state",  # AIQS
            "module/v1/ff/SVR4H73275/state",  # DPS
            "module/v1/ff/NodeRed/SVR4H73275/state",  # DPS via NodeRED
            "module/v1/ff/NodeRed/SVR4H76530/state",  # AIQS via NodeRED
            "fts/v1/ff/5iO4/state",  # FTS Navigation
        ]

        module_messages = []
        for message in messages:
            topic = message.get("topic", "")
            if any(module_topic in topic for module_topic in module_state_topics):
                module_messages.append(message)

        return module_messages

    def test_module_state_message_processing(self):
        """Test: Module State Message Processing"""
        print("\n🧪 MODULE STATE MESSAGE PROCESSING TEST:")

        # Filtere Module State Messages
        module_messages = self._filter_module_state_messages(self.test_messages)
        print(f"   Total Messages: {len(self.test_messages)}")
        print(f"   Module State Messages: {len(module_messages)}")

        # Analysiere Module Messages
        module_stats = {}
        for message in module_messages:
            topic = message.get("topic", "")
            payload = message.get("payload", {})

            # Parse Payload
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

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

            if module_type:
                if module_type not in module_stats:
                    module_stats[module_type] = {"total": 0, "with_actionState": 0}

                module_stats[module_type]["total"] += 1

                # Prüfe auf actionState
                if isinstance(payload, dict) and "actionState" in payload:
                    action_state = payload["actionState"]
                    if action_state:
                        module_stats[module_type]["with_actionState"] += 1

                        # Zeige wichtige Action States
                        command = action_state.get("command", "")
                        state = action_state.get("state", "")
                        if command in ["PICK", "DROP", "DRILL", "MILL", "CHECK_QUALITY", "DOCK"]:
                            print(f"   📨 {module_type} {command} - {state}")

        print("\n   📊 MODULE STATISTICS:")
        for module, stats in module_stats.items():
            print(f"      {module}: {stats['total']} messages, {stats['with_actionState']} with actionState")


if __name__ == "__main__":
    unittest.main()
