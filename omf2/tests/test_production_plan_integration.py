#!/usr/bin/env python3
"""
Test für Production Plan Integration mit MQTT Messages
Testet ob MQTT Messages korrekt in Production Plan Steps integriert werden
"""

import json
import unittest
from unittest.mock import MagicMock
from pathlib import Path
from typing import List, Dict, Any


class ProductionPlanIntegrationTest(unittest.TestCase):
    """Test für Production Plan Integration mit MQTT Messages"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Import ProductionOrderManager
        from omf2.ccu.production_order_manager import ProductionOrderManager
        self.manager = ProductionOrderManager()
        
        # Test Order
        self.test_order = {
            'orderId': 'test-order-123',
            'type': 'BLUE',
            'orderType': 'PRODUCTION'
        }
    
    def test_mqtt_step_storage_and_integration(self):
        """Test: MQTT Step Storage und Production Plan Integration"""
        print(f"\n🧪 MQTT STEP STORAGE AND INTEGRATION TEST:")
        
        # 1. Simuliere MQTT Messages
        test_messages = [
            {
                'topic': 'module/v1/ff/SVR3QA0022/state',
                'payload': {
                    'actionState': {
                        'orderId': 'test-order-123',
                        'command': 'PICK',
                        'state': 'RUNNING',
                        'id': 'hbw-pick-001'
                    }
                },
                'meta': {'timestamp': '2025-01-01T10:00:00Z'}
            },
            {
                'topic': 'fts/v1/ff/5iO4/state',
                'payload': {
                    'actionState': {
                        'orderId': 'test-order-123',
                        'command': 'DOCK',
                        'state': 'FINISHED',
                        'id': 'fts-dock-001'
                    }
                },
                'meta': {'timestamp': '2025-01-01T10:05:00Z'}
            },
            {
                'topic': 'module/v1/ff/SVR4H76449/state',
                'payload': {
                    'actionState': {
                        'orderId': 'test-order-123',
                        'command': 'DRILL',
                        'state': 'IN_PROGRESS',
                        'id': 'drill-process-001'
                    }
                },
                'meta': {'timestamp': '2025-01-01T10:10:00Z'}
            }
        ]
        
        print(f"   📨 Processing {len(test_messages)} MQTT messages...")
        
        # 2. Verarbeite MQTT Messages
        for message in test_messages:
            topic = message['topic']
            payload = message['payload']
            meta = message['meta']
            
            if 'module/v1/ff/' in topic:
                self.manager.process_module_state_message(topic, payload, meta)
            elif 'fts/v1/ff/' in topic:
                self.manager.process_fts_state_message(topic, payload, meta)
        
        # 3. Prüfe MQTT Steps Storage
        order_id = 'test-order-123'
        stored_steps = self.manager.mqtt_steps.get(order_id, [])
        print(f"   📋 Stored MQTT Steps: {len(stored_steps)}")
        
        for i, step in enumerate(stored_steps):
            print(f"      Step {i+1}: {step.get('moduleType')} {step.get('command')} - {step.get('state')}")
        
        # 4. Teste Production Plan Integration
        print(f"   📋 Testing Production Plan Integration...")
        
        # Generiere Production Plan
        production_plan = self.manager.get_complete_production_plan(self.test_order)
        print(f"      Generated plan: {len(production_plan)} steps")
        
        # Zeige States
        states = {}
        for step in production_plan:
            state = step.get('state', 'PENDING')
            states[state] = states.get(state, 0) + 1
        
        print(f"      States: {states}")
        
        # 5. Prüfe ob MQTT Steps integriert wurden
        non_pending_steps = [step for step in production_plan if step.get('state') != 'PENDING']
        print(f"      Non-PENDING Steps: {len(non_pending_steps)}")
        
        for step in non_pending_steps:
            print(f"         {step.get('id')}: {step.get('state')} ({step.get('mqtt_command')})")
        
        # 6. Validierung
        self.assertGreater(len(stored_steps), 0, "MQTT Steps sollten gespeichert werden")
        self.assertGreater(len(non_pending_steps), 0, "Einige Production Plan Steps sollten aktualisiert werden")
        
        print(f"   ✅ MQTT Step Storage und Integration funktioniert!")
    
    def test_real_session_data_integration(self):
        """Test: Echte Session-Daten Integration"""
        print(f"\n🧪 REAL SESSION DATA INTEGRATION TEST:")
        
        # Lade echte Session-Daten
        session_file = 'data/omf-data/sessions/auftrag-weiss_1.log'
        messages = []
        
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if line.strip():
                        message = json.loads(line.strip())
                        messages.append(message)
        except FileNotFoundError:
            self.skipTest(f"Session-Datei nicht gefunden: {session_file}")
        
        print(f"   📨 Loaded {len(messages)} messages from session")
        
        # Filtere Module State Messages für eine spezifische Order
        order_id = '258beef9-6001-43a2-b7d4-01ed50f4b155'
        order_messages = []
        
        for message in messages:
            payload = message.get('payload', {})
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue
            
            if isinstance(payload, dict) and payload.get('orderId') == order_id:
                order_messages.append(message)
        
        print(f"   📋 Found {len(order_messages)} messages for Order {order_id[:8]}...")
        
        # Verarbeite Order Messages
        processed_count = 0
        for message in order_messages:
            topic = message.get('topic', '')
            payload = message.get('payload', {})
            meta = {'timestamp': message.get('timestamp', '')}
            
            # Parse Payload
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue
            
            # Verarbeite je nach Topic
            if 'module/v1/ff/' in topic:
                self.manager.process_module_state_message(topic, payload, meta)
                processed_count += 1
            elif 'fts/v1/ff/' in topic:
                self.manager.process_fts_state_message(topic, payload, meta)
                processed_count += 1
        
        print(f"   ✅ Processed {processed_count} MQTT messages")
        
        # Prüfe gespeicherte MQTT Steps
        stored_steps = self.manager.mqtt_steps.get(order_id, [])
        print(f"   📋 Stored MQTT Steps: {len(stored_steps)}")
        
        # Teste Production Plan Integration
        test_order = {
            'orderId': order_id,
            'type': 'WHITE',
            'orderType': 'PRODUCTION'
        }
        
        production_plan = self.manager.get_complete_production_plan(test_order)
        print(f"   📋 Production Plan: {len(production_plan)} steps")
        
        # Zeige States
        states = {}
        for step in production_plan:
            state = step.get('state', 'PENDING')
            states[state] = states.get(state, 0) + 1
        
        print(f"   📊 States: {states}")
        
        # Zeige aktualisierte Steps
        updated_steps = [step for step in production_plan if step.get('state') != 'PENDING']
        print(f"   🔄 Updated Steps: {len(updated_steps)}")
        
        for step in updated_steps[:5]:  # Zeige ersten 5
            print(f"      {step.get('id')}: {step.get('state')} ({step.get('mqtt_command')})")
        
        # Validierung
        self.assertGreater(len(stored_steps), 0, "MQTT Steps sollten aus Session-Daten gespeichert werden")
        self.assertGreater(len(updated_steps), 0, "Production Plan Steps sollten durch Session-Daten aktualisiert werden")
        
        print(f"   ✅ Real Session Data Integration funktioniert!")


if __name__ == '__main__':
    unittest.main()
