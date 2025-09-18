#!/usr/bin/env python3
"""
Unit Tests für MessageGenerator - Alle Befehle

Umfassende Tests für alle Befehle des MessageGenerators:
- Factory Reset
- FTS Commands
- Module Sequences
- Module Steps
"""

from pathlib import Path
import json
import unittest
from datetime import datetime

# Add omf to path for imports

from omf.tools.message_generator import MessageGenerator

class TestMessageGeneratorCommands(unittest.TestCase):
    """Test-Klasse für alle MessageGenerator Befehle"""

    def setUp(self):
        """Setup vor jedem Test"""
        self.message_generator = MessageGenerator()

    # ========================================
    # FACTORY RESET TESTS
    # ========================================

    def test_factory_reset_basic(self):
        """Test: Factory Reset Basis-Funktionalität"""
        message = self.message_generator.generate_factory_reset_message(with_storage=False)

        self.assertIsNotNone(message, "Factory Reset Message darf nicht None sein")
        self.assertEqual(message["topic"], "ccu/set/reset", "Topic muss 'ccu/set/reset' sein")
        self.assertIn("withStorage", message["payload"], "withStorage muss im Payload sein")
        self.assertFalse(message["payload"]["withStorage"], "withStorage muss False sein")

    def test_factory_reset_with_storage(self):
        """Test: Factory Reset mit Storage"""
        message = self.message_generator.generate_factory_reset_message(with_storage=True)

        self.assertIsNotNone(message, "Factory Reset Message darf nicht None sein")
        self.assertTrue(message["payload"]["withStorage"], "withStorage muss True sein")

    # ========================================
    # FTS COMMAND TESTS
    # ========================================

    def test_fts_charge_command(self):
        """Test: FTS Charge (Laden) Befehl"""
        message = self.message_generator.generate_fts_command_message("charge")

        self.assertIsNotNone(message, "FTS Charge Message darf nicht None sein")
        self.assertEqual(message["topic"], "fts/v1/ff/5iO4/command", "Topic muss korrekt sein")

        payload = message["payload"]
        self.assertEqual(payload["serialNumber"], "5iO4", "serialNumber muss '5iO4' sein")
        self.assertEqual(payload["action"]["command"], "CHARGE", "Command muss 'CHARGE' sein")
        self.assertIn("orderId", payload, "orderId muss vorhanden sein")
        self.assertEqual(payload["orderUpdateId"], 1, "orderUpdateId muss 1 sein")

    def test_fts_dock_to_dps_command(self):
        """Test: FTS Dock to DPS Befehl"""
        message = self.message_generator.generate_fts_command_message("dock_to_dps")

        self.assertIsNotNone(message, "FTS Dock Message darf nicht None sein")
        self.assertEqual(message["topic"], "fts/v1/ff/5iO4/command", "Topic muss korrekt sein")
        self.assertEqual(message["payload"]["action"]["command"], "DOCK_TO_DPS", "Command muss 'DOCK_TO_DPS' sein")

    def test_fts_dock_to_mill_command(self):
        """Test: FTS Dock to Mill Befehl"""
        message = self.message_generator.generate_fts_command_message("dock_to_mill")

        self.assertIsNotNone(message, "FTS Dock to Mill Message darf nicht None sein")
        self.assertEqual(message["payload"]["action"]["command"], "DOCK_TO_MILL", "Command muss 'DOCK_TO_MILL' sein")

    def test_fts_undock_command(self):
        """Test: FTS Undock Befehl"""
        message = self.message_generator.generate_fts_command_message("undock")

        self.assertIsNotNone(message, "FTS Undock Message darf nicht None sein")
        self.assertEqual(message["payload"]["action"]["command"], "UNDOCK", "Command muss 'UNDOCK' sein")

    def test_fts_message_structure(self):
        """Test: FTS Message hat korrekte Struktur"""
        message = self.message_generator.generate_fts_command_message("charge")
        payload = message["payload"]

        # Erforderliche Top-Level Felder
        required_fields = ["serialNumber", "orderId", "orderUpdateId", "action", "timestamp"]
        for field in required_fields:
            self.assertIn(field, payload, f"Feld '{field}' fehlt im Payload")

        # Action-Struktur
        action = payload["action"]
        action_fields = ["id", "command", "metadata"]
        for field in action_fields:
            self.assertIn(field, action, f"Feld '{field}' fehlt in action")

        # Metadata-Struktur
        metadata = action["metadata"]
        metadata_fields = ["priority", "timeout", "type"]
        for field in metadata_fields:
            self.assertIn(field, metadata, f"Feld '{field}' fehlt in metadata")

    def test_fts_command_case_handling(self):
        """Test: FTS Commands werden korrekt in Großbuchstaben konvertiert"""
        test_commands = ["charge", "CHARGE", "dock_to_dps", "DOCK_TO_DPS"]

        for cmd in test_commands:
            message = self.message_generator.generate_fts_command_message(cmd)
            self.assertIsNotNone(message, f"Message für '{cmd}' darf nicht None sein")

            expected_command = cmd.upper()
            actual_command = message["payload"]["action"]["command"]
            self.assertEqual(actual_command, expected_command, f"Command '{cmd}' sollte '{expected_command}' sein")

    # ========================================
    # MODULE SEQUENCE TESTS
    # ========================================

    def test_module_sequence_mill(self):
        """Test: MILL Module Sequence"""
        # Starte einen neuen Workflow, damit die orderId existiert
        from omf.tools.workflow_order_manager import get_workflow_order_manager

        workflow_manager = get_workflow_order_manager()
        order_id = workflow_manager.start_workflow("MILL", ["PICK", "MILL", "DROP"])

        for step_num, step in enumerate(["PICK", "MILL", "DROP"], 1):
            message = self.message_generator.generate_module_sequence_message("MILL", step, step_num, order_id)

            self.assertIsNotNone(message, f"MILL {step} Message darf nicht None sein")
            self.assertIn("module/v1/ff/", message["topic"], "Topic muss Modul-Format haben")

            payload = message["payload"]
            self.assertEqual(payload["command"], step, f"Command muss '{step}' sein")
            self.assertEqual(payload["order_id"], order_id, "order_id muss übereinstimmen")
            self.assertIn("orderUpdateId", payload["parameters"], "orderUpdateId muss vorhanden sein")
            self.assertEqual(payload["parameters"]["subActionId"], step_num, f"subActionId muss {step_num} sein")

    def test_module_sequence_aiqs(self):
        """Test: AIQS Module Sequence"""
        # Starte einen neuen Workflow, damit die orderId existiert
        from omf.tools.workflow_order_manager import get_workflow_order_manager

        workflow_manager = get_workflow_order_manager()
        order_id = workflow_manager.start_workflow("AIQS", ["PICK", "CHECK_QUALITY", "DROP"])

        for step_num, step in enumerate(["PICK", "CHECK_QUALITY", "DROP"], 1):
            message = self.message_generator.generate_module_sequence_message("AIQS", step, step_num, order_id)

            self.assertIsNotNone(message, f"AIQS {step} Message darf nicht None sein")
            payload = message["payload"]
            self.assertEqual(payload["command"], step, f"Command muss '{step}' sein")

    def test_module_sequence_drill(self):
        """Test: DRILL Module Sequence"""
        # Starte einen neuen Workflow, damit die orderId existiert
        from omf.tools.workflow_order_manager import get_workflow_order_manager

        workflow_manager = get_workflow_order_manager()
        order_id = workflow_manager.start_workflow("DRILL", ["PICK", "DRILL", "DROP"])

        for step_num, step in enumerate(["PICK", "DRILL", "DROP"], 1):
            message = self.message_generator.generate_module_sequence_message("DRILL", step, step_num, order_id)

            self.assertIsNotNone(message, f"DRILL {step} Message darf nicht None sein")
            payload = message["payload"]
            self.assertEqual(payload["command"], step, f"Command muss '{step}' sein")

    def test_module_sequence_order_id_generation(self):
        """Test: Module Sequence generiert OrderId automatisch wenn nicht angegeben"""
        message1 = self.message_generator.generate_module_sequence_message("MILL", "PICK", 1)
        message2 = self.message_generator.generate_module_sequence_message("MILL", "MILL", 2)

        self.assertIsNotNone(message1, "Message 1 darf nicht None sein")
        self.assertIsNotNone(message2, "Message 2 darf nicht None sein")

        # OrderIds sollten generiert worden sein
        order_id1 = message1["payload"]["order_id"]
        order_id2 = message2["payload"]["order_id"]

        self.assertIsNotNone(order_id1, "OrderId 1 darf nicht None sein")
        self.assertIsNotNone(order_id2, "OrderId 2 darf nicht None sein")
        self.assertIsInstance(order_id1, str, "OrderId 1 muss String sein")
        self.assertIsInstance(order_id2, str, "OrderId 2 muss String sein")

    def test_module_sequence_invalid_module(self):
        """Test: Module Sequence mit ungültigem Modul"""
        message = self.message_generator.generate_module_sequence_message("INVALID_MODULE", "PICK", 1)

        # Sollte None zurückgeben oder Fallback verwenden
        # Je nach Implementierung kann dies variieren
        if message is not None:
            # Wenn Fallback verwendet wird, sollte Topic trotzdem gültig sein
            self.assertIn("topic", message, "Topic sollte vorhanden sein")
            self.assertIn("payload", message, "Payload sollte vorhanden sein")

    # ========================================
    # MESSAGE STRUCTURE TESTS
    # ========================================

    def test_all_messages_have_topic_and_payload(self):
        """Test: Alle Nachrichten haben Topic und Payload"""
        test_cases = [
            ("factory_reset", lambda: self.message_generator.generate_factory_reset_message(False)),
            ("fts_charge", lambda: self.message_generator.generate_fts_command_message("charge")),
            ("mill_pick", lambda: self.message_generator.generate_module_sequence_message("MILL", "PICK", 1)),
        ]

        for name, generator in test_cases:
            with self.subTest(command=name):
                message = generator()

                self.assertIsNotNone(message, f"Message '{name}' darf nicht None sein")
                self.assertIsInstance(message, dict, f"Message '{name}' muss Dict sein")
                self.assertIn("topic", message, f"Topic fehlt in '{name}'")
                self.assertIn("payload", message, f"Payload fehlt in '{name}'")
                self.assertIsInstance(message["topic"], str, f"Topic in '{name}' muss String sein")
                self.assertIsInstance(message["payload"], dict, f"Payload in '{name}' muss Dict sein")

    def test_all_messages_have_timestamp(self):
        """Test: Alle Nachrichten haben Timestamp"""
        test_cases = [
            ("factory_reset", lambda: self.message_generator.generate_factory_reset_message(False)),
            ("fts_charge", lambda: self.message_generator.generate_fts_command_message("charge")),
            ("mill_pick", lambda: self.message_generator.generate_module_sequence_message("MILL", "PICK", 1)),
        ]

        for name, generator in test_cases:
            with self.subTest(command=name):
                message = generator()

                self.assertIsNotNone(message, f"Message '{name}' darf nicht None sein")
                self.assertIn("timestamp", message["payload"], f"Timestamp fehlt in '{name}' payload")

                timestamp = message["payload"]["timestamp"]
                self.assertIsInstance(timestamp, str, f"Timestamp in '{name}' muss String sein")
                self.assertGreater(len(timestamp), 0, f"Timestamp in '{name}' darf nicht leer sein")

    def test_all_messages_json_serializable(self):
        """Test: Alle Nachrichten sind JSON-serialisierbar"""
        test_cases = [
            ("factory_reset", lambda: self.message_generator.generate_factory_reset_message(False)),
            ("fts_charge", lambda: self.message_generator.generate_fts_command_message("charge")),
            ("mill_pick", lambda: self.message_generator.generate_module_sequence_message("MILL", "PICK", 1)),
        ]

        for name, generator in test_cases:
            with self.subTest(command=name):
                message = generator()

                self.assertIsNotNone(message, f"Message '{name}' darf nicht None sein")

                try:
                    json_str = json.dumps(message)
                    self.assertIsInstance(json_str, str, f"JSON-String für '{name}' muss String sein")

                    # Test Deserialisierung
                    deserialized = json.loads(json_str)
                    self.assertEqual(
                        deserialized, message, f"Deserialisierte Message '{name}' muss gleich Original sein"
                    )
                except (TypeError, ValueError) as e:
                    self.fail(f"Message '{name}' kann nicht zu JSON serialisiert werden: {e}")

    # ========================================
    # TOPIC VALIDATION TESTS
    # ========================================

    def test_topic_formats(self):
        """Test: Topic-Formate sind korrekt"""
        # Factory Reset
        factory_msg = self.message_generator.generate_factory_reset_message(False)
        self.assertEqual(factory_msg["topic"], "ccu/set/reset", "Factory Reset Topic falsch")

        # FTS Commands
        fts_msg = self.message_generator.generate_fts_command_message("charge")
        self.assertEqual(fts_msg["topic"], "fts/v1/ff/5iO4/command", "FTS Topic falsch")

        # Module Commands (wenn Serial Number verfügbar)
        module_msg = self.message_generator.generate_module_sequence_message("MILL", "PICK", 1)
        if module_msg:  # Nur testen wenn Message generiert wurde
            self.assertIn("module/v1/ff/", module_msg["topic"], "Module Topic Format falsch")
            self.assertIn("/order", module_msg["topic"], "Module Topic muss '/order' enthalten")

    # ========================================
    # ERROR HANDLING TESTS
    # ========================================

    def test_error_handling_fts_empty_command(self):
        """Test: FTS Fehlerbehandlung bei leerem Command"""
        message = self.message_generator.generate_fts_command_message("")

        # Je nach Implementierung könnte None zurückgegeben werden oder leerer Command
        if message is not None:
            self.assertIn("action", message["payload"], "Action sollte vorhanden sein")
            # Command könnte leer oder transformiert sein

    def test_error_handling_module_empty_step(self):
        """Test: Module Fehlerbehandlung bei leerem Step"""
        message = self.message_generator.generate_module_sequence_message("MILL", "", 1)

        # Je nach Implementierung könnte None zurückgegeben werden oder leerer Command
        if message is not None:
            self.assertIn("command", message["payload"], "Command sollte vorhanden sein")

    def test_performance_multiple_generations(self):
        """Test: Performance bei mehrfachen Generierungen"""
        start_time = datetime.now()

        # Generiere viele Nachrichten
        for i in range(100):
            factory_msg = self.message_generator.generate_factory_reset_message(i % 2 == 0)
            fts_msg = self.message_generator.generate_fts_command_message("charge")

            self.assertIsNotNone(factory_msg, f"Factory Message {i} darf nicht None sein")
            self.assertIsNotNone(fts_msg, f"FTS Message {i} darf nicht None sein")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Sollte schnell sein (weniger als 1 Sekunde für 200 Messages)
        self.assertLess(duration, 1.0, "MessageGenerator sollte schnell sein")

    # ========================================
    # CRITICAL INTEGRATION TESTS
    # ========================================

    def test_critical_all_commands_work(self):
        """KRITISCHER TEST: Alle wichtigen Befehle funktionieren"""
        critical_commands = [
            ("factory_reset_false", lambda: self.message_generator.generate_factory_reset_message(False)),
            ("factory_reset_true", lambda: self.message_generator.generate_factory_reset_message(True)),
            ("fts_charge", lambda: self.message_generator.generate_fts_command_message("charge")),
            ("fts_dock_to_dps", lambda: self.message_generator.generate_fts_command_message("dock_to_dps")),
            ("fts_undock", lambda: self.message_generator.generate_fts_command_message("undock")),
        ]

        for name, generator in critical_commands:
            with self.subTest(command=name):
                try:
                    message = generator()

                    # KRITISCHE PRÜFUNGEN
                    self.assertIsNotNone(message, f"KRITISCH: '{name}' Message darf nicht None sein")
                    self.assertIn("topic", message, f"KRITISCH: '{name}' muss Topic haben")
                    self.assertIn("payload", message, f"KRITISCH: '{name}' muss Payload haben")

                    # JSON-Serialisierung muss funktionieren
                    json.dumps(message)

                except Exception as e:
                    self.fail(f"KRITISCHER FEHLER: Befehl '{name}' funktioniert nicht! Fehler: {e}")

if __name__ == "__main__":
    print("🧪 Starte MessageGenerator Command Tests...")
    print("⚠️  Diese Tests prüfen alle wichtigen Befehle des MessageGenerators")

    # Führe Tests aus
    unittest.main(verbosity=2, exit=False)

    print("\n" + "=" * 60)
    print("🎯 FAZIT: MessageGenerator Command Tests abgeschlossen")
    print("=" * 60)
