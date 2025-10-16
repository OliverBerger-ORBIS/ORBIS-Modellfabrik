#!/usr/bin/env python3
"""
Test: CCU Frontend Consumer Implementation

Testet die CCU Frontend Consumer Implementation mit echten Session-Daten.
Verifiziert, dass ccu/order/active Messages korrekt verarbeitet werden.

Autor: OMF Development Team
Datum: 2025-01-15
"""

import json
from pathlib import Path

import pytest

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.production_order_manager import ProductionOrderManager


class TestCcuFrontendConsumer:
    """Test Suite für CCU Frontend Consumer Implementation"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.gateway = CcuGateway()
        self.manager = ProductionOrderManager()

    def test_ccu_frontend_consumer_implementation(self):
        """Test: CCU Frontend Consumer mit echten Session-Daten"""

        # Test Session-Daten
        test_sessions = [
            'data/omf-data/sessions/auftrag-blau_1.log',
            'data/omf-data/sessions/auftrag-rot_1.log',
            'data/omf-data/sessions/auftrag-weiss_1.log'
        ]

        total_orders_processed = 0
        total_steps_processed = 0
        processed_orders = {}

        for session_file in test_sessions:
            print(f"\n=== TEST: {session_file} ===")

            # Lade Session-Daten
            session_path = Path(session_file)
            if not session_path.exists():
                pytest.skip(f"Session file not found: {session_file}")

            with open(session_path) as f:
                ccu_active_messages = []

                # Sammle alle ccu/order/active Messages
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            message = json.loads(line.strip())
                            topic = message.get('topic', '')

                            if 'ccu/order/active' in topic:
                                payload = message.get('payload', {})

                                if isinstance(payload, str):
                                    payload = json.loads(payload)

                                if isinstance(payload, list) and len(payload) > 0:
                                    ccu_active_messages.append((topic, payload, message.get('timestamp', '')))

                        except json.JSONDecodeError:
                            continue

            print(f"Gefunden: {len(ccu_active_messages)} ccu/order/active Messages mit Daten")

            if not ccu_active_messages:
                print(f"⚠️ Keine ccu/order/active Messages mit Daten in {session_file}")
                continue

            # Verarbeite jede Message
            for topic, payload, timestamp in ccu_active_messages:
                print("\n--- Verarbeite Message ---")
                print(f"Topic: {topic}")
                print(f"Orders: {len(payload)}")

                meta = {'timestamp': timestamp}

                # Test: Gateway Processing
                result = self.gateway.on_mqtt_message(topic, payload, meta)
                assert result == True, f"Gateway processing failed for {topic}"
                print(f"✅ Gateway Result: {result}")

                # Test: ProductionOrderManager
                self.manager.process_ccu_order_active(topic, payload, meta)

                # Zähle verarbeitete Orders und Steps
                for order in payload:
                    order_id = order.get('orderId', '')
                    production_steps = order.get('productionSteps', [])
                    order_type = order.get('type', '')

                    if order_id and production_steps:
                        total_orders_processed += 1
                        total_steps_processed += len(production_steps)

                        processed_orders[order_id] = {
                            'type': order_type,
                            'steps': len(production_steps),
                            'session': session_file
                        }

                        print(f"✅ Order {order_id[:8]}... ({order_type}): {len(production_steps)} steps")

                        # Zeige erste 3 Steps
                        for i, step in enumerate(production_steps[:3]):
                            step_id = step.get('id', 'unknown')
                            step_state = step.get('state', 'unknown')
                            step_type = step.get('type', 'unknown')
                            print(f"  {i+1}. {step_id} - {step_state} - {step_type}")

                        # Test: get_complete_production_plan
                        test_order = {'orderId': order_id, 'type': order_type, 'orderType': 'PRODUCTION'}
                        production_plan = self.manager.get_complete_production_plan(test_order)
                        assert len(production_plan) > 0, f"Production plan should not be empty for {order_type}"
                        print(f"  ✅ Production Plan: {len(production_plan)} steps")

        # Assertions
        assert total_orders_processed > 0, "Should process at least one order"
        assert total_steps_processed > 0, "Should process at least one step"
        assert len(processed_orders) > 0, "Should have processed orders"

        print("\n=== SUMMARY ===")
        print(f"✅ Total Orders verarbeitet: {total_orders_processed}")
        print(f"✅ Total Steps verarbeitet: {total_steps_processed}")
        print("✅ Gateway Processing: Erfolgreich")
        print("✅ ProductionOrderManager: Erfolgreich")
        print("✅ Production Plans: Generiert")

        # UI Integration Test
        print("\n=== UI INTEGRATION TEST ===")
        assert len(self.manager.mqtt_steps) > 0, "Manager should have stored orders"
        print(f"✅ Manager hat {len(self.manager.mqtt_steps)} Orders gespeichert")

        for order_id in self.manager.mqtt_steps:
            steps = self.manager.mqtt_steps[order_id]
            print(f"  Order {order_id[:8]}...: {len(steps)} steps für UI Display")
            assert len(steps) > 0, f"Order {order_id} should have steps"

        return processed_orders

    def test_schema_validation(self):
        """Test: Schema-Validierung für ccu/order/active"""

        # Test mit korrekter Array-Struktur
        valid_message = [
            {
                'orderId': 'test-123',
                'orderType': 'PRODUCTION',
                'type': 'BLUE',
                'timestamp': '2025-01-01T12:00:00Z',
                'productionSteps': [
                    {
                        'id': 'step-1',
                        'type': 'MANUFACTURE',
                        'state': 'FINISHED',
                        'moduleType': 'HBW',
                        'command': 'PICK'
                    }
                ],
                'receivedAt': '2025-01-01T12:00:00Z',
                'startedAt': '2025-01-01T12:00:00Z',
                'state': 'ACTIVE',
                'workpieceId': 'wp-123'
            }
        ]

        # Test: Gateway Processing (mit Schema-Validierung)
        result = self.gateway.on_mqtt_message('ccu/order/active', valid_message, {'timestamp': '2025-01-01T12:00:00Z'})
        assert result == True, "Schema validation should pass for valid message"

        # Test: ProductionOrderManager Processing
        self.manager.process_ccu_order_active('ccu/order/active', valid_message, {'timestamp': '2025-01-01T12:00:00Z'})

        # Verifizierung
        assert 'test-123' in self.manager.mqtt_steps, "Order should be stored in manager"
        assert len(self.manager.mqtt_steps['test-123']) == 1, "Should have 1 production step"

        print("✅ Schema-Validierung erfolgreich")

    def test_empty_ccu_order_active(self):
        """Test: Leere ccu/order/active Messages"""

        # Test mit leerem Array
        empty_message = []

        # Test: Gateway Processing
        result = self.gateway.on_mqtt_message('ccu/order/active', empty_message, {'timestamp': '2025-01-01T12:00:00Z'})
        assert result == True, "Empty array should be valid"

        # Test: ProductionOrderManager Processing
        initial_count = len(self.manager.mqtt_steps)
        self.manager.process_ccu_order_active('ccu/order/active', empty_message, {'timestamp': '2025-01-01T12:00:00Z'})

        # Verifizierung: Keine neuen Orders hinzugefügt
        assert len(self.manager.mqtt_steps) == initial_count, "No new orders should be added"

        print("✅ Leere ccu/order/active Messages erfolgreich verarbeitet")

    def test_production_workflows(self):
        """Test: Production Workflows für verschiedene Order Types"""

        # Test BLUE Order
        blue_order = {
            'orderId': 'blue-test-123',
            'orderType': 'PRODUCTION',
            'type': 'BLUE',
            'timestamp': '2025-01-01T12:00:00Z',
            'productionSteps': [],
            'receivedAt': '2025-01-01T12:00:00Z',
            'startedAt': '2025-01-01T12:00:00Z',
            'state': 'ACTIVE',
            'workpieceId': 'wp-blue'
        }

        test_order = {'orderId': 'blue-test-123', 'type': 'BLUE', 'orderType': 'PRODUCTION'}
        blue_plan = self.manager.get_complete_production_plan(test_order)

        # BLUE sollte 16 Steps haben (nicht 15!)
        assert len(blue_plan) == 16, f"BLUE should have 16 steps, got {len(blue_plan)}"

        # Test RED Order
        test_order = {'orderId': 'red-test-123', 'type': 'RED', 'orderType': 'PRODUCTION'}
        red_plan = self.manager.get_complete_production_plan(test_order)

        # RED sollte 16 Steps haben (nicht 11!)
        assert len(red_plan) == 16, f"RED should have 16 steps, got {len(red_plan)}"

        # Test WHITE Order
        test_order = {'orderId': 'white-test-123', 'type': 'WHITE', 'orderType': 'PRODUCTION'}
        white_plan = self.manager.get_complete_production_plan(test_order)

        # WHITE sollte 16 Steps haben (nicht 11!)
        assert len(white_plan) == 16, f"WHITE should have 16 steps, got {len(white_plan)}"

        print("✅ Production Workflows korrekt generiert")
        print(f"  BLUE: {len(blue_plan)} steps (16 Steps)")
        print(f"  RED: {len(red_plan)} steps (16 Steps)")
        print(f"  WHITE: {len(white_plan)} steps (16 Steps)")


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v", "-s"])
