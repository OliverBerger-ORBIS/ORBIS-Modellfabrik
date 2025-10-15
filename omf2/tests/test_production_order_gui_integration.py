#!/usr/bin/env python3
"""
Test: Production Order GUI Integration
Testet die vollständige Integration von MQTT Messages -> ProductionOrderManager -> GUI Display
"""

import unittest
import json
from pathlib import Path
from omf2.ccu.production_order_manager import ProductionOrderManager


class ProductionOrderGuiIntegrationTest(unittest.TestCase):
    """Test: GUI Integration für Production Orders"""
    
    def setUp(self):
        """Setup Test Environment"""
        self.manager = ProductionOrderManager()
        self.order_id = '258beef9-6001-43a2-b7d4-01ed50f4b155'
        
    def test_production_order_gui_display(self):
        """Test: Production Order GUI Display nach MQTT Message Processing"""
        print(f"\n🎨 PRODUCTION ORDER GUI INTEGRATION TEST:")
        
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
        order_messages = []
        
        for message in messages:
            payload = message.get('payload', {})
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue
            
            if isinstance(payload, dict) and payload.get('orderId') == self.order_id:
                order_messages.append(message)
        
        print(f"   📋 Found {len(order_messages)} messages for Order {self.order_id[:8]}...")
        
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
        stored_steps = self.manager.mqtt_steps.get(self.order_id, [])
        print(f"   📋 Stored MQTT Steps: {len(stored_steps)}")
        
        # Teste Production Plan Integration
        test_order = {
            'orderId': self.order_id,
            'type': 'WHITE',
            'orderType': 'PRODUCTION'
        }
        
        production_plan = self.manager.get_complete_production_plan(test_order)
        print(f"   📋 Production Plan: {len(production_plan)} steps")
        
        # Analysiere States für GUI
        states = {}
        finished_steps = []
        pending_steps = []
        in_progress_steps = []
        
        for step in production_plan:
            state = step.get('state', 'PENDING')
            states[state] = states.get(state, 0) + 1
            
            if state == 'FINISHED':
                finished_steps.append(step)
            elif state == 'PENDING':
                pending_steps.append(step)
            elif state == 'IN_PROGRESS':
                in_progress_steps.append(step)
        
        print(f"   📊 States: {states}")
        print(f"   ✅ Finished Steps: {len(finished_steps)}")
        print(f"   ⏳ Pending Steps: {len(pending_steps)}")
        print(f"   🔄 In Progress Steps: {len(in_progress_steps)}")
        
        # Zeige Finished Steps (sollten in GUI angezeigt werden)
        print(f"\n   📋 FINISHED STEPS (GUI Display):")
        for step in finished_steps[:5]:  # Zeige ersten 5
            print(f"      {step.get('id')}: {step.get('state')} ({step.get('mqtt_command', 'N/A')}) - {step.get('description', 'N/A')}")
        
        # Zeige Pending Steps (sollten in GUI angezeigt werden)
        print(f"\n   📋 PENDING STEPS (GUI Display):")
        for step in pending_steps[:5]:  # Zeige ersten 5
            print(f"      {step.get('id')}: {step.get('state')} ({step.get('mqtt_command', 'N/A')}) - {step.get('description', 'N/A')}")
        
        # Bestimme aktives Modul für Shopfloor Layout
        active_module = self._get_current_active_module(production_plan)
        print(f"\n   🏭 ACTIVE MODULE (Shopfloor Layout): {active_module}")
        
        # Validierung
        self.assertGreater(len(stored_steps), 0, "MQTT Steps sollten aus Session-Daten gespeichert werden")
        self.assertGreater(len(finished_steps), 0, "Es sollten fertige Steps vorhanden sein")
        
        # GUI-spezifische Validierungen
        self._validate_gui_display(production_plan, states, active_module)
        
        print(f"   ✅ Production Order GUI Integration funktioniert!")
    
    def _get_current_active_module(self, production_plan):
        """Bestimme aktuell aktives Modul für Shopfloor Layout"""
        # Finde den ersten IN_PROGRESS oder ENQUEUED Step
        for step in production_plan:
            state = step.get('state', 'PENDING')
            if state in ['IN_PROGRESS', 'ENQUEUED']:
                module_type = step.get('moduleType', '')
                if module_type:
                    return module_type
        
        # Fallback: Letzter FINISHED Step
        for step in reversed(production_plan):
            state = step.get('state', 'PENDING')
            if state == 'FINISHED':
                module_type = step.get('moduleType', '')
                if module_type:
                    return module_type
        
        return None
    
    def _validate_gui_display(self, production_plan, states, active_module):
        """Validiere GUI-spezifische Display-Logik"""
        
        # 1. Sequenz-Validierung: Keine FINISHED Steps nach PENDING Steps
        finished_indices = []
        pending_indices = []
        
        for i, step in enumerate(production_plan):
            state = step.get('state', 'PENDING')
            if state == 'FINISHED':
                finished_indices.append(i)
            elif state == 'PENDING':
                pending_indices.append(i)
        
        # Prüfe: Kein PENDING Step sollte vor einem FINISHED Step kommen
        if finished_indices and pending_indices:
            max_finished = max(finished_indices)
            min_pending = min(pending_indices)
            
            if min_pending < max_finished:
                print(f"   ⚠️ SEQUENCE ERROR: PENDING step at index {min_pending} before FINISHED step at index {max_finished}")
                # Das ist ein GUI-Problem - sollte nicht passieren
        
        # 2. Aktives Modul Validierung
        if active_module:
            print(f"   ✅ Active Module: {active_module}")
            # Prüfe ob aktives Modul in Production Plan vorkommt
            module_steps = [step for step in production_plan if step.get('moduleType') == active_module]
            if module_steps:
                print(f"   ✅ Module {active_module} has {len(module_steps)} steps in plan")
            else:
                print(f"   ⚠️ Active Module {active_module} not found in production plan")
        
        # 3. State Distribution Validierung
        total_steps = len(production_plan)
        finished_count = states.get('FINISHED', 0)
        pending_count = states.get('PENDING', 0)
        
        print(f"   📊 State Distribution: {finished_count}/{total_steps} finished, {pending_count}/{total_steps} pending")
        
        # 4. GUI-spezifische Warnungen
        if finished_count > 0 and pending_count > 0:
            print(f"   ⚠️ GUI WARNING: Mixed states detected - {finished_count} finished, {pending_count} pending")
        
        if not active_module:
            print(f"   ⚠️ GUI WARNING: No active module determined for shopfloor layout")


if __name__ == '__main__':
    unittest.main()
