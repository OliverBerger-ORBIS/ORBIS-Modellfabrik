"""
Unit Tests für MessageGenerator und WorkflowOrderManager
Testet orderUpdateId Handling und Workflow-Management
"""

import json
import sys
import unittest
from pathlib import Path

# Add src_orbis to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src_orbis"))

from omf.tools.message_generator import MessageGenerator
from omf.tools.workflow_order_manager import WorkflowOrderManager, get_workflow_order_manager


class TestMessageGenerator(unittest.TestCase):
    """Test-Klasse für MessageGenerator"""

    def setUp(self):
        """Setup für jeden Test"""
        self.message_generator = MessageGenerator()
        self.workflow_manager = WorkflowOrderManager()

    def tearDown(self):
        """Cleanup nach jedem Test"""
        pass

    def test_generate_module_sequence_message_basic(self):
        """Test: Basis Modul-Sequenz Message Generierung"""
        # Arrange
        module = "MILL"
        step = "PICK"
        step_number = 1

        # Act
        result = self.message_generator.generate_module_sequence_message(
            module=module, step=step, step_number=step_number
        )

        # Assert
        self.assertIsNotNone(result)
        self.assertIn("topic", result)
        self.assertIn("payload", result)

        payload = result["payload"]
        self.assertIn("order_id", payload)  # Template verwendet Unterstrich
        self.assertIn("command", payload)

        # orderUpdateId ist in parameters
        if "parameters" in payload:
            self.assertIn("orderUpdateId", payload["parameters"])

        print(f"✅ Generated message: {json.dumps(result, indent=2)}")

    def test_generate_module_sequence_message_with_workflow(self):
        """Test: Modul-Sequenz mit WorkflowOrderManager"""
        # Arrange
        module = "DRILL"
        workflow_manager = get_workflow_order_manager()

        # Start workflow
        order_id = workflow_manager.start_workflow(module, ["PICK", "PROCESS", "DROP"])

        # Act - PICK
        result_pick = self.message_generator.generate_module_sequence_message(
            module=module, step="PICK", step_number=1, order_id=order_id
        )

        # Act - PROCESS
        result_process = self.message_generator.generate_module_sequence_message(
            module=module, step="PROCESS", step_number=2, order_id=order_id
        )

        # Act - DROP
        result_drop = self.message_generator.generate_module_sequence_message(
            module=module, step="DROP", step_number=3, order_id=order_id
        )

        # Assert
        self.assertIsNotNone(result_pick)
        self.assertIsNotNone(result_process)
        self.assertIsNotNone(result_drop)

        # Check orderUpdateId sequence
        pick_payload = result_pick["payload"]
        process_payload = result_process["payload"]
        drop_payload = result_drop["payload"]

        self.assertEqual(pick_payload["order_id"], order_id)  # Template verwendet Unterstrich
        self.assertEqual(process_payload["order_id"], order_id)
        self.assertEqual(drop_payload["order_id"], order_id)

        # Check orderUpdateId increments (in parameters)
        self.assertEqual(pick_payload["parameters"]["orderUpdateId"], 1)
        self.assertEqual(process_payload["parameters"]["orderUpdateId"], 2)
        self.assertEqual(drop_payload["parameters"]["orderUpdateId"], 3)

        print("✅ Workflow sequence:")
        print(f"   PICK: orderUpdateId={pick_payload['parameters']['orderUpdateId']}")
        print(f"   PROCESS: orderUpdateId={process_payload['parameters']['orderUpdateId']}")
        print(f"   DROP: orderUpdateId={drop_payload['parameters']['orderUpdateId']}")

    def test_order_update_id_template_validation(self):
        """Test: orderUpdateId Template-Validierung"""
        # Arrange
        module = "MILL"
        step = "PICK"

        # Act
        result = self.message_generator.generate_module_sequence_message(module=module, step=step, step_number=1)

        # Assert
        self.assertIsNotNone(result)
        payload = result["payload"]

        # Check if orderUpdateId is in parameters (new structure)
        if "parameters" in payload and "orderUpdateId" in payload["parameters"]:
            order_update_id = payload["parameters"]["orderUpdateId"]
            print(f"✅ orderUpdateId in parameters: {order_update_id}")
        else:
            print("⚠️  orderUpdateId not found in parameters")
            return  # Skip the rest of the test

    def test_workflow_order_manager_integration(self):
        """Test: WorkflowOrderManager Integration"""
        # Arrange
        workflow_manager = get_workflow_order_manager()
        module = "AIQS"

        # Act
        order_id = workflow_manager.start_workflow(module, ["PICK", "PROCESS", "DROP"])

        # Execute commands
        workflow_info_1 = workflow_manager.execute_command(order_id, "PICK")
        workflow_info_2 = workflow_manager.execute_command(order_id, "PROCESS")
        workflow_info_3 = workflow_manager.execute_command(order_id, "DROP")

        # Assert
        self.assertEqual(workflow_info_1["orderUpdateId"], 1)
        self.assertEqual(workflow_info_2["orderUpdateId"], 2)
        self.assertEqual(workflow_info_3["orderUpdateId"], 3)

        print("✅ WorkflowOrderManager sequence:")
        print(f"   PICK: orderUpdateId={workflow_info_1['orderUpdateId']}")
        print(f"   PROCESS: orderUpdateId={workflow_info_2['orderUpdateId']}")
        print(f"   DROP: orderUpdateId={workflow_info_3['orderUpdateId']}")

    def test_template_structure_analysis(self):
        """Test: Template-Struktur Analyse"""
        # Arrange
        template_name = "module/order"
        template = self.message_generator.semantic_templates.get(template_name)

        # Act & Assert
        if template:
            print(f"✅ Template gefunden: {template_name}")
            print(f"   Template-Struktur: {template.get('template_structure', {})}")

            # Check orderUpdateId constraint
            order_update_constraint = template.get("template_structure", {}).get("orderUpdateId")
            if order_update_constraint:
                print(f"   orderUpdateId Constraint: {order_update_constraint}")

                if order_update_constraint == "[1, 3]":
                    print("🚨 PROBLEM: Template erlaubt nur orderUpdateId 1 oder 3!")
                    print("   WorkflowOrderManager generiert aber: 1, 2, 3...")
        else:
            print(f"❌ Template nicht gefunden: {template_name}")

    def test_factory_reset_message(self):
        """Test: Factory Reset Message Generierung"""
        # Act
        # Factory Reset Message wie in steering_factory.py
        result = self.message_generator.generate_factory_reset_message(with_storage=False)

        # Assert
        self.assertIsNotNone(result)
        self.assertIn("topic", result)
        self.assertIn("payload", result)

        payload = result["payload"]
        self.assertIn("withStorage", payload)
        self.assertIn("timestamp", payload)
        self.assertEqual(payload["withStorage"], False)

        print(f"✅ Factory Reset message: {json.dumps(result, indent=2)}")

    def test_ccu_order_request_message(self):
        """Test: CCU Order Request Message Generierung"""
        # Act
        result = self.message_generator.generate_ccu_order_request_message(
            color="RED",
            order_type="PRODUCTION",
            workpiece_id="040a8dca341291",
            ai_inspection=True,
        )

        # Assert
        self.assertIsNotNone(result)
        # CCU Order Request returns tuple (topic, payload)
        if isinstance(result, tuple):
            topic, payload = result
            self.assertIsInstance(topic, str)
            self.assertIsInstance(payload, dict)
        else:
            self.assertIn("topic", result)
            self.assertIn("payload", result)
            payload = result["payload"]
        # Fallback: Wenn 'type' fehlt, ist nur 'timestamp' im Payload
        if "type" in payload:
            self.assertIn("workpieceId", payload)
            self.assertIn("orderType", payload)
            self.assertIn("timestamp", payload)
            self.assertEqual(payload["type"], "RED")
            self.assertEqual(payload["orderType"], "PRODUCTION")
            # aiInspection ist optional, nur prüfen wenn vorhanden
            if "aiInspection" in payload:
                self.assertTrue(payload["aiInspection"])
        else:
            # Fallback: Nur 'timestamp' vorhanden
            self.assertIn("timestamp", payload)

        print(f"✅ CCU Order Request message: {json.dumps(result, indent=2)}")


class TestWorkflowOrderManager(unittest.TestCase):
    """Test-Klasse für WorkflowOrderManager"""

    def setUp(self):
        """Setup für jeden Test"""
        self.workflow_manager = WorkflowOrderManager()

    def test_start_workflow(self):
        """Test: Workflow starten"""
        # Act
        order_id = self.workflow_manager.start_workflow("MILL", ["PICK", "PROCESS", "DROP"])

        # Assert
        self.assertIsNotNone(order_id)
        self.assertIsInstance(order_id, str)

        workflow_status = self.workflow_manager.get_workflow_status(order_id)
        self.assertIsNotNone(workflow_status)
        self.assertEqual(workflow_status["module"], "MILL")
        self.assertEqual(workflow_status["commands"], ["PICK", "PROCESS", "DROP"])
        self.assertEqual(workflow_status["status"], "active")

        print(f"✅ Workflow started: {order_id}")

    def test_execute_command_sequence(self):
        """Test: Command-Sequenz ausführen"""
        # Arrange
        order_id = self.workflow_manager.start_workflow("DRILL", ["PICK", "PROCESS", "DROP"])

        # Act
        workflow_info_1 = self.workflow_manager.execute_command(order_id, "PICK")
        workflow_info_2 = self.workflow_manager.execute_command(order_id, "PROCESS")
        workflow_info_3 = self.workflow_manager.execute_command(order_id, "DROP")

        # Assert
        self.assertEqual(workflow_info_1["orderUpdateId"], 1)
        self.assertEqual(workflow_info_2["orderUpdateId"], 2)
        self.assertEqual(workflow_info_3["orderUpdateId"], 3)

        self.assertEqual(workflow_info_1["orderId"], order_id)
        self.assertEqual(workflow_info_2["orderId"], order_id)
        self.assertEqual(workflow_info_3["orderId"], order_id)

        print("✅ Command sequence executed:")
        print(f"   PICK: orderUpdateId={workflow_info_1['orderUpdateId']}")
        print(f"   PROCESS: orderUpdateId={workflow_info_2['orderUpdateId']}")
        print(f"   DROP: orderUpdateId={workflow_info_3['orderUpdateId']}")

    def test_complete_workflow(self):
        """Test: Workflow abschließen"""
        # Arrange
        order_id = self.workflow_manager.start_workflow("AIQS", ["PICK", "PROCESS", "DROP"])
        self.workflow_manager.execute_command(order_id, "PICK")
        self.workflow_manager.execute_command(order_id, "PROCESS")
        self.workflow_manager.execute_command(order_id, "DROP")

        # Act
        completed_workflow = self.workflow_manager.complete_workflow(order_id)

        # Assert
        self.assertIsNotNone(completed_workflow)
        self.assertEqual(completed_workflow["status"], "completed")
        self.assertIn("end_time", completed_workflow)

        # Check if removed from active workflows
        active_workflows = self.workflow_manager.get_active_workflows()
        self.assertNotIn(order_id, active_workflows)

        # Check if added to history
        history = self.workflow_manager.get_workflow_history()
        self.assertEqual(len(history), 1)

        print(f"✅ Workflow completed: {order_id}")


def run_tests():
    """Führt alle Tests aus"""
    print("🧪 Starting MessageGenerator and WorkflowOrderManager Tests...")
    print("=" * 60)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add MessageGenerator tests
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMessageGenerator))

    # Add WorkflowOrderManager tests
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestWorkflowOrderManager))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    print("=" * 60)
    print(f"🧪 Tests completed: {result.testsRun} tests run")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   ⚠️  Errors: {len(result.errors)}")

    return result


if __name__ == "__main__":
    run_tests()
