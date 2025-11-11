#!/usr/bin/env python3
"""
Production Step Sequence Test Framework
Testet Production Step Sequenz mit echten Session-Daten

Ziele:
1. Aktiver Produktions-Process wird erkannt
2. Verwaltung der Status der Prozessschritte
3. Schritt-für-Schritt Erkennung
4. Reihenfolge-Validierung
5. Status-Korrektur
"""

import json
import unittest
from typing import Any, Dict, List


class ProductionStepSequenceTest(unittest.TestCase):
    """Test Production Step Sequenz mit echten Session-Daten"""

    def setUp(self):
        """Setup für jeden Test"""
        self.session_files = {
            "blau": [
                "data/omf-data/sessions/production_order_blue_20251110_180619.log",
                "data/omf-data/sessions/auftrag-blau_1.log",
            ],
            "weiss": [
                "data/omf-data/sessions/production_order_white_20251110_184459.log",
                "data/omf-data/sessions/auftrag-weiss_1.log",
            ],
            "rot": [
                "data/omf-data/sessions/production_order_red_20251110_180152.log",
                "data/omf-data/sessions/auftrag-rot_1.log",
            ],
        }

        # Relevante Topics für Production Orders
        self.relevant_topics = {
            "ccu_orders": ["ccu/order/request", "ccu/order/response", "ccu/order/active", "ccu/order/completed"],
            "module_states": [
                "module/v1/ff/SVR3QA0022/state",  # HBW
                "module/v1/ff/SVR4H76449/state",  # DRILL
                "module/v1/ff/SVR3QA2098/state",  # MILL
                "module/v1/ff/SVR4H76530/state",  # AIQS
                "module/v1/ff/SVR4H73275/state",  # DPS
            ],
            "nodered_states": [
                "module/v1/ff/NodeRed/SVR4H73275/state",  # DPS via NodeRED
                "module/v1/ff/NodeRed/SVR4H76530/state",  # AIQS via NodeRED
            ],
            "fts_states": ["fts/v1/ff/5iO4/state"],  # FTS Navigation (AGV)
        }

        # Serial Number zu Module Type Mapping
        self.serial_to_module = {
            "SVR3QA0022": "HBW",
            "SVR4H76449": "DRILL",
            "SVR3QA2098": "MILL",
            "SVR4H76530": "AIQS",
            "SVR4H73275": "DPS",
            "5iO4": "FTS",  # FTS (AGV) Serial Number
        }

    def load_session_data(self, session_files: List[str]) -> List[Dict[str, Any]]:
        """Lade Session-Daten aus Log-Datei, probiert mehrere Kandidaten."""
        messages = []
        tried_files: List[str] = []

        for session_file in session_files:
            try:
                with open(session_file) as f:  # pragma: no cover - file IO
                    for line in f:
                        if line.strip():
                            message = json.loads(line.strip())
                            messages.append(message)
                return messages
            except FileNotFoundError:
                tried_files.append(session_file)
                continue
            except json.JSONDecodeError as e:
                self.fail(f"JSON Parse Error in {session_file}: {e}")

        self.fail(f"Session-Datei nicht gefunden: {', '.join(tried_files)}")

        return messages

    def filter_relevant_topics(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtere relevante Topics für Production Orders"""
        relevant_messages = []
        all_relevant_topics = []

        # Sammle alle relevanten Topics
        for topic_group in self.relevant_topics.values():
            all_relevant_topics.extend(topic_group)

        for message in messages:
            topic = message.get("topic", "")
            if any(relevant_topic in topic for relevant_topic in all_relevant_topics):
                relevant_messages.append(message)

        return relevant_messages

    def extract_order_sequence(self, messages: List[Dict[str, Any]], order_id: str) -> List[Dict[str, Any]]:
        """Extrahiere alle Messages für eine spezifische Order-ID"""
        order_messages = []

        for message in messages:
            payload = message.get("payload", {})

            # Payload kann String oder Dict sein
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

            if isinstance(payload, dict) and payload.get("orderId") == order_id:
                order_messages.append(message)

        # Sortiere nach Timestamp
        order_messages.sort(key=lambda x: x.get("timestamp", ""))

        return order_messages

    def find_order_ids(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Finde alle Order-IDs in den Messages"""
        order_ids = set()

        for message in messages:
            payload = message.get("payload", {})

            # Payload kann String oder Dict sein
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

            if isinstance(payload, dict):
                order_id = payload.get("orderId")
                if order_id:
                    order_ids.add(order_id)

        return list(order_ids)

    def analyze_production_steps(self, order_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analysiere Production Steps aus Order Messages"""
        steps = []

        for message in order_messages:
            topic = message.get("topic", "")
            payload = message.get("payload", {})
            timestamp = message.get("timestamp", "")

            # Payload kann String oder Dict sein
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

            if isinstance(payload, dict):
                action_state = payload.get("actionState", {})

                if action_state:
                    command = action_state.get("command", "")
                    state = action_state.get("state", "")
                    action_id = action_state.get("id", "")

                    # Bestimme Module Type
                    module_type = None
                    for serial, module in self.serial_to_module.items():
                        if serial in topic:
                            module_type = module
                            break

                    # Erstelle Step-Info
                    step_info = {
                        "timestamp": timestamp,
                        "module_type": module_type,
                        "command": command,
                        "state": state,
                        "action_id": action_id,
                        "topic": topic,
                        "payload": payload,
                    }

                    steps.append(step_info)

        # Extrahiere Order-ID aus erster Message
        order_id = None
        if order_messages:
            first_payload = order_messages[0].get("payload", {})
            if isinstance(first_payload, str):
                try:
                    first_payload = json.loads(first_payload)
                except json.JSONDecodeError:
                    pass
            if isinstance(first_payload, dict):
                order_id = first_payload.get("orderId")

        return {"total_steps": len(steps), "steps": steps, "order_id": order_id}

    def test_blau_order_sequence(self):
        """Test: Blaue Order - Schritt-für-Schritt Sequenz"""
        # Lade Session-Daten
        messages = self.load_session_data(self.session_files["blau"])
        self.assertGreater(len(messages), 0, "Keine Messages in blau Session gefunden")

        # Filtere relevante Topics
        relevant_messages = self.filter_relevant_topics(messages)
        self.assertGreater(len(relevant_messages), 0, "Keine relevanten Topics in blau Session gefunden")

        # Finde Order-IDs
        order_ids = self.find_order_ids(relevant_messages)
        self.assertGreater(len(order_ids), 0, "Keine Order-IDs in blau Session gefunden")

        print("\n🔵 BLAU ORDER TEST:")
        print(f"   Total Messages: {len(messages)}")
        print(f"   Relevant Messages: {len(relevant_messages)}")
        print(f"   Order IDs gefunden: {order_ids}")

        # Analysiere jede Order-ID
        for order_id in order_ids:
            order_messages = self.extract_order_sequence(relevant_messages, order_id)
            if order_messages:
                analysis = self.analyze_production_steps(order_messages)
                print(f"\n   📋 Order {order_id[:8]}...:")
                print(f"      Total Steps: {analysis['total_steps']}")

                # Zeige erste 5 Steps
                for i, step in enumerate(analysis["steps"][:5]):
                    print(f"      Step {i+1}: {step['module_type']} {step['command']} - {step['state']}")

                if len(analysis["steps"]) > 5:
                    print(f"      ... und {len(analysis['steps']) - 5} weitere Steps")

    def test_weiss_order_sequence(self):
        """Test: Weiße Order - Schritt-für-Schritt Sequenz"""
        # Lade Session-Daten
        messages = self.load_session_data(self.session_files["weiss"])
        self.assertGreater(len(messages), 0, "Keine Messages in weiss Session gefunden")

        # Filtere relevante Topics
        relevant_messages = self.filter_relevant_topics(messages)
        self.assertGreater(len(relevant_messages), 0, "Keine relevanten Topics in weiss Session gefunden")

        # Finde Order-IDs
        order_ids = self.find_order_ids(relevant_messages)
        self.assertGreater(len(order_ids), 0, "Keine Order-IDs in weiss Session gefunden")

        print("\n⚪ WEISS ORDER TEST:")
        print(f"   Total Messages: {len(messages)}")
        print(f"   Relevant Messages: {len(relevant_messages)}")
        print(f"   Order IDs gefunden: {order_ids}")

        # Analysiere jede Order-ID
        for order_id in order_ids:
            order_messages = self.extract_order_sequence(relevant_messages, order_id)
            if order_messages:
                analysis = self.analyze_production_steps(order_messages)
                print(f"\n   📋 Order {order_id[:8]}...:")
                print(f"      Total Steps: {analysis['total_steps']}")

                # Zeige erste 5 Steps
                for i, step in enumerate(analysis["steps"][:5]):
                    print(f"      Step {i+1}: {step['module_type']} {step['command']} - {step['state']}")

                if len(analysis["steps"]) > 5:
                    print(f"      ... und {len(analysis['steps']) - 5} weitere Steps")

    def test_rot_order_sequence(self):
        """Test: Rote Order - Schritt-für-Schritt Sequenz"""
        # Lade Session-Daten
        messages = self.load_session_data(self.session_files["rot"])
        self.assertGreater(len(messages), 0, "Keine Messages in rot Session gefunden")

        # Filtere relevante Topics
        relevant_messages = self.filter_relevant_topics(messages)
        self.assertGreater(len(relevant_messages), 0, "Keine relevanten Topics in rot Session gefunden")

        # Finde Order-IDs
        order_ids = self.find_order_ids(relevant_messages)
        self.assertGreater(len(order_ids), 0, "Keine Order-IDs in rot Session gefunden")

        print("\n🔴 ROT ORDER TEST:")
        print(f"   Total Messages: {len(messages)}")
        print(f"   Relevant Messages: {len(relevant_messages)}")
        print(f"   Order IDs gefunden: {order_ids}")

        # Analysiere jede Order-ID
        for order_id in order_ids:
            order_messages = self.extract_order_sequence(relevant_messages, order_id)
            if order_messages:
                analysis = self.analyze_production_steps(order_messages)
                print(f"\n   📋 Order {order_id[:8]}...:")
                print(f"      Total Steps: {analysis['total_steps']}")

                # Zeige erste 5 Steps
                for i, step in enumerate(analysis["steps"][:5]):
                    print(f"      Step {i+1}: {step['module_type']} {step['command']} - {step['state']}")

                if len(analysis["steps"]) > 5:
                    print(f"      ... und {len(analysis['steps']) - 5} weitere Steps")


if __name__ == "__main__":
    unittest.main()
