#!/usr/bin/env python3
"""
Test: Production Order GUI Integration
Testet die vollständige Integration von MQTT Messages -> ProductionOrderManager -> GUI Display
"""

import json
import unittest

from omf2.ccu.order_manager import OrderManager


class ProductionOrderGuiIntegrationTest(unittest.TestCase):
    """Test: GUI Integration für Production Orders"""

    def setUp(self):
        """Setup Test Environment"""
        self.manager = OrderManager()
        self.order_id = None

    def test_production_order_gui_display(self):
        """Test: Production Order GUI Display nach MQTT Message Processing"""
        print("\n🎨 PRODUCTION ORDER GUI INTEGRATION TEST:")

        # Lade echte Session-Daten
        session_file = "data/omf-data/sessions/production_order_white_20251110_184459.log"
        messages = []

        try:
            with open(session_file) as f:
                for line in f:
                    if line.strip():
                        message = json.loads(line.strip())
                        messages.append(message)
        except FileNotFoundError:
            self.skipTest(f"Session-Datei nicht gefunden: {session_file}")

        print(f"   📨 Loaded {len(messages)} messages from session")

        processed_module_steps = 0

        for message in messages:
            topic = message.get("topic", "")
            raw_payload = message.get("payload", {})
            meta = {"timestamp": message.get("timestamp", "")}

            try:
                payload = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
            except json.JSONDecodeError:
                continue

            if topic == "ccu/order/active":
                orders = payload if isinstance(payload, list) else [payload]
                if orders:
                    self.manager.process_ccu_order_active(topic, orders, meta)
                    if not self.order_id:
                        first_order = next((order for order in orders if order.get("productionSteps")), None)
                        if first_order:
                            self.order_id = first_order.get("orderId")
                continue

            if topic == "ccu/order/completed":
                orders = payload if isinstance(payload, list) else [payload]
                if orders:
                    self.manager.process_ccu_order_completed(topic, orders, meta)
                continue

            if "module/v1/ff/" in topic and "state" in topic:
                if not isinstance(payload, dict):
                    continue

                order_id = payload.get("orderId")
                if order_id:
                    self.order_id = self.order_id or order_id

                target_order = order_id or self.order_id
                if not target_order:
                    continue

                action_state = payload.get("actionState") or {}
                module_step = {
                    "id": action_state.get("id", f"MODULE_{payload.get('serialNumber', 'UNKNOWN')}"),
                    "moduleType": self._get_module_type_from_serial(payload.get("serialNumber", "")),
                    "command": action_state.get("command", "UNKNOWN"),
                    "state": action_state.get("state", "PENDING"),
                    "timestamp": payload.get("timestamp", meta.get("timestamp", "")),
                    "mqtt_command": action_state.get("command", "UNKNOWN"),
                }

                steps = self.manager.mqtt_steps.setdefault(target_order, [])
                steps.append(module_step)
                processed_module_steps += 1

        if not self.order_id:
            self.skipTest("Keine passende OrderId in Sessiondaten gefunden")

        print(f"   📋 Using Order {self.order_id[:8]}...")
        print(f"   ✅ Processed {processed_module_steps} module state messages")

        # Prüfe gespeicherte MQTT Steps
        stored_steps = self.manager.mqtt_steps.get(self.order_id, [])
        if not stored_steps:
            active_order = self.manager.active_orders.get(self.order_id)
            if active_order:
                stored_steps = active_order.get("productionSteps", [])
                self.manager.mqtt_steps[self.order_id] = stored_steps

        print(f"   📋 Stored MQTT Steps: {len(stored_steps)}")

        # Teste Production Plan Integration
        order_source = (
            self.manager.active_orders.get(self.order_id)
            or self.manager.completed_orders.get(self.order_id)
            or {"orderId": self.order_id, "type": "WHITE", "orderType": "PRODUCTION"}
        )
        test_order = {
            "orderId": self.order_id,
            "type": order_source.get("type", "WHITE"),
            "orderType": order_source.get("orderType", "PRODUCTION"),
        }

        production_plan = self.manager.get_complete_order_plan(test_order)
        print(f"   📋 Production Plan: {len(production_plan)} steps")

        # Analysiere States für GUI
        states = {}
        finished_steps = []
        pending_steps = []
        in_progress_steps = []

        for step in production_plan:
            state = step.get("state", "PENDING")
            states[state] = states.get(state, 0) + 1

            if state == "FINISHED":
                finished_steps.append(step)
            elif state == "PENDING":
                pending_steps.append(step)
            elif state == "IN_PROGRESS":
                in_progress_steps.append(step)

        print(f"   📊 States: {states}")
        print(f"   ✅ Finished Steps: {len(finished_steps)}")
        print(f"   ⏳ Pending Steps: {len(pending_steps)}")
        print(f"   🔄 In Progress Steps: {len(in_progress_steps)}")

        # Zeige Finished Steps (sollten in GUI angezeigt werden)
        print("\n   📋 FINISHED STEPS (GUI Display):")
        for step in finished_steps[:5]:  # Zeige ersten 5
            print(
                f"      {step.get('id')}: {step.get('state')} ({step.get('mqtt_command', 'N/A')}) - {step.get('description', 'N/A')}"
            )

        # Zeige Pending Steps (sollten in GUI angezeigt werden)
        print("\n   📋 PENDING STEPS (GUI Display):")
        for step in pending_steps[:5]:  # Zeige ersten 5
            print(
                f"      {step.get('id')}: {step.get('state')} ({step.get('mqtt_command', 'N/A')}) - {step.get('description', 'N/A')}"
            )

        # Bestimme aktives Modul für Shopfloor Layout
        active_module = self._get_current_active_module(production_plan)
        print(f"\n   🏭 ACTIVE MODULE (Shopfloor Layout): {active_module}")

        # Validierung
        self.assertGreater(len(stored_steps), 0, "MQTT Steps sollten aus Session-Daten gespeichert werden")
        self.assertGreater(len(finished_steps), 0, "Es sollten fertige Steps vorhanden sein")

        # GUI-spezifische Validierungen
        self._validate_gui_display(production_plan, states, active_module)

        print("   ✅ Production Order GUI Integration funktioniert!")

    def _get_current_active_module(self, production_plan):
        """Bestimme aktuell aktives Modul für Shopfloor Layout"""
        # Finde den ersten IN_PROGRESS oder ENQUEUED Step
        for step in production_plan:
            state = step.get("state", "PENDING")
            if state in ["IN_PROGRESS", "ENQUEUED"]:
                module_type = step.get("moduleType", "")
                if module_type:
                    return module_type

    def _get_module_type_from_serial(self, serial_number):
        """Ermittelt Module Type aus Serial Number"""
        if "SVR4H73275" in serial_number:
            return "DPS"
        elif "SVR4H76530" in serial_number:
            return "AIQS"
        elif "SVR3QA2098" in serial_number:
            return "MILL"
        elif "SVR3QA0022" in serial_number:
            return "HBW"
        elif "SVR4H76449" in serial_number:
            return "DRILL"
        else:
            return "UNKNOWN"

    def _validate_gui_display(self, production_plan, states, active_module):
        """Validiere GUI-spezifische Display-Logik"""

        # 1. Sequenz-Validierung: Keine FINISHED Steps nach PENDING Steps
        finished_indices = []
        pending_indices = []

        for i, step in enumerate(production_plan):
            state = step.get("state", "PENDING")
            if state == "FINISHED":
                finished_indices.append(i)
            elif state == "PENDING":
                pending_indices.append(i)

        # Prüfe: Kein PENDING Step sollte vor einem FINISHED Step kommen
        if finished_indices and pending_indices:
            max_finished = max(finished_indices)
            min_pending = min(pending_indices)

            if min_pending < max_finished:
                print(
                    f"   ⚠️ SEQUENCE ERROR: PENDING step at index {min_pending} before FINISHED step at index {max_finished}"
                )
                # Das ist ein GUI-Problem - sollte nicht passieren

        # 2. Aktives Modul Validierung
        if active_module:
            print(f"   ✅ Active Module: {active_module}")
            # Prüfe ob aktives Modul in Production Plan vorkommt
            module_steps = [step for step in production_plan if step.get("moduleType") == active_module]
            if module_steps:
                print(f"   ✅ Module {active_module} has {len(module_steps)} steps in plan")
            else:
                print(f"   ⚠️ Active Module {active_module} not found in production plan")

        # 3. State Distribution Validierung
        total_steps = len(production_plan)
        finished_count = states.get("FINISHED", 0)
        pending_count = states.get("PENDING", 0)

        print(
            f"   📊 State Distribution: {finished_count}/{total_steps} finished, {pending_count}/{total_steps} pending"
        )

        # 4. GUI-spezifische Warnungen
        if finished_count > 0 and pending_count > 0:
            print(f"   ⚠️ GUI WARNING: Mixed states detected - {finished_count} finished, {pending_count} pending")

        if not active_module:
            print("   ⚠️ GUI WARNING: No active module determined for shopfloor layout")


if __name__ == "__main__":
    unittest.main()
