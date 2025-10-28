#!/usr/bin/env python3
"""
Unit tests for Order Status Completion Bug Fix

Tests that when an order's final step transitions to COMPLETED:
1. order.status is updated to 'COMPLETED'
2. last step.state is set and persisted as 'COMPLETED'

Tests cover both PRODUCTION and STORAGE orders, and edge cases.
"""

import unittest
from typing import Any, Dict

from omf2.ccu.order_manager import OrderManager


class TestOrderStatusCompletion(unittest.TestCase):
    """Test Order Status Completion Logic"""

    def setUp(self):
        """Setup for each test"""
        self.order_manager = OrderManager()

    def tearDown(self):
        """Cleanup after each test"""
        # Clear order manager state
        self.order_manager.active_orders.clear()
        self.order_manager.completed_orders.clear()
        self.order_manager.mqtt_steps.clear()

    def _create_test_order(
        self, order_id: str, order_type: str = "PRODUCTION", workpiece_type: str = "RED", num_steps: int = 3
    ) -> Dict[str, Any]:
        """Create a test order with specified parameters"""
        steps = []
        for i in range(num_steps):
            step = {
                "id": f"step-{i}",
                "type": "NAVIGATION" if i % 2 == 0 else "MANUFACTURE",
                "state": "FINISHED" if i < num_steps - 1 else "IN_PROGRESS",
                "source": f"MODULE_{i}",
                "target": f"MODULE_{i+1}",
            }
            if step["type"] == "MANUFACTURE":
                step["command"] = "PICK" if i == 1 else "DROP"
                step["moduleType"] = f"MODULE_{i}"
            steps.append(step)

        order = {
            "orderId": order_id,
            "orderType": order_type,
            "type": workpiece_type,
            "state": "IN_PROGRESS",
            "productionSteps": steps,
            "timestamp": "2025-01-01T00:00:00.000Z",
        }
        return order

    def test_order_status_set_to_completed_on_completion(self):
        """Test: order.status is set to 'COMPLETED' when order completes"""
        # Setup: Create active order
        order_id = "test-order-001"
        active_order = self._create_test_order(order_id, "PRODUCTION")

        # Process as active order first
        self.order_manager.process_ccu_order_active(
            topic="ccu/order/active",
            message=[active_order],
            meta={"timestamp": "2025-01-01T00:00:00.000Z"},
        )

        # Verify order is active
        self.assertIn(order_id, self.order_manager.active_orders)

        # Complete the order
        completed_order = active_order.copy()
        completed_order["state"] = "FINISHED"
        completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"

        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[completed_order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # Verify order moved to completed
        self.assertNotIn(order_id, self.order_manager.active_orders)
        self.assertIn(order_id, self.order_manager.completed_orders)

        # FIX VERIFICATION: Check that status is set to COMPLETED
        completed = self.order_manager.completed_orders[order_id]
        self.assertEqual(completed["status"], "COMPLETED", "Order status should be set to 'COMPLETED'")

    def test_last_step_state_set_to_completed(self):
        """Test: last step.state is set to 'COMPLETED' when order completes"""
        # Setup: Create active order with steps
        order_id = "test-order-002"
        active_order = self._create_test_order(order_id, "PRODUCTION", num_steps=4)

        # Process as active order first
        self.order_manager.process_ccu_order_active(
            topic="ccu/order/active",
            message=[active_order],
            meta={"timestamp": "2025-01-01T00:00:00.000Z"},
        )

        # Complete the order
        completed_order = active_order.copy()
        completed_order["state"] = "FINISHED"
        completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"
        # Mark all steps as FINISHED
        for step in completed_order["productionSteps"]:
            step["state"] = "FINISHED"

        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[completed_order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # FIX VERIFICATION: Check that last step state is COMPLETED
        steps = self.order_manager.mqtt_steps[order_id]
        self.assertGreater(len(steps), 0, "Order should have steps")

        last_step = steps[-1]
        self.assertEqual(last_step["state"], "COMPLETED", "Last step state should be set to 'COMPLETED'")

    def test_storage_order_completion(self):
        """Test: STORAGE orders also get status='COMPLETED' and last step state='COMPLETED'"""
        # Setup: Create storage order
        order_id = "test-storage-001"
        active_order = self._create_test_order(order_id, "STORAGE", "BLUE", num_steps=4)

        # Process as active order first
        self.order_manager.process_ccu_order_active(
            topic="ccu/order/active",
            message=[active_order],
            meta={"timestamp": "2025-01-01T00:00:00.000Z"},
        )

        # Complete the order
        completed_order = active_order.copy()
        completed_order["state"] = "FINISHED"
        completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"
        for step in completed_order["productionSteps"]:
            step["state"] = "FINISHED"

        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[completed_order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # FIX VERIFICATION: Check status and last step for STORAGE orders
        completed = self.order_manager.completed_orders[order_id]
        self.assertEqual(completed["status"], "COMPLETED", "STORAGE order status should be 'COMPLETED'")

        steps = self.order_manager.mqtt_steps[order_id]
        last_step = steps[-1]
        self.assertEqual(last_step["state"], "COMPLETED", "STORAGE order last step should be 'COMPLETED'")

    def test_order_without_steps_defensive(self):
        """Test: Orders without steps are handled defensively (no crash)"""
        # Setup: Create order without steps
        order_id = "test-order-no-steps"
        order = {
            "orderId": order_id,
            "orderType": "PRODUCTION",
            "type": "RED",
            "state": "FINISHED",
            "productionSteps": [],  # Empty steps
            "finishedAt": "2025-01-01T00:01:00.000Z",
        }

        # Should not crash
        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # Verify order is stored with status
        self.assertIn(order_id, self.order_manager.completed_orders)
        completed = self.order_manager.completed_orders[order_id]
        self.assertEqual(completed["status"], "COMPLETED", "Order without steps should still have status=COMPLETED")

    def test_order_with_partial_steps(self):
        """Test: Order with some completed steps handled correctly"""
        # Setup: Create order with partial steps
        order_id = "test-order-partial"
        active_order = self._create_test_order(order_id, "PRODUCTION", num_steps=3)

        # Mark only first step as finished
        active_order["productionSteps"][0]["state"] = "FINISHED"
        active_order["productionSteps"][1]["state"] = "IN_PROGRESS"
        active_order["productionSteps"][2]["state"] = "ENQUEUED"

        # Process as active
        self.order_manager.process_ccu_order_active(
            topic="ccu/order/active",
            message=[active_order],
            meta={"timestamp": "2025-01-01T00:00:00.000Z"},
        )

        # Now complete the order (all steps should be FINISHED in completion message)
        completed_order = active_order.copy()
        completed_order["state"] = "FINISHED"
        completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"
        for step in completed_order["productionSteps"]:
            step["state"] = "FINISHED"

        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[completed_order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # Verify completion
        completed = self.order_manager.completed_orders[order_id]
        self.assertEqual(completed["status"], "COMPLETED")

        steps = self.order_manager.mqtt_steps[order_id]
        last_step = steps[-1]
        self.assertEqual(last_step["state"], "COMPLETED", "Last step should be COMPLETED after order completion")

    def test_direct_completed_order_without_active(self):
        """Test: Order that arrives as completed without being in active_orders first"""
        # Setup: Create completed order directly
        order_id = "test-direct-completed"
        completed_order = self._create_test_order(order_id, "PRODUCTION", num_steps=3)
        completed_order["state"] = "FINISHED"
        completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"
        for step in completed_order["productionSteps"]:
            step["state"] = "FINISHED"

        # Process as completed without being in active first
        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[completed_order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # Verify order is stored with status
        self.assertIn(order_id, self.order_manager.completed_orders)
        completed = self.order_manager.completed_orders[order_id]
        self.assertEqual(completed["status"], "COMPLETED", "Direct completed order should have status=COMPLETED")

    def test_multiple_orders_completion(self):
        """Test: Multiple orders can be completed in batch"""
        # Setup: Create multiple orders
        order_ids = ["test-multi-001", "test-multi-002", "test-multi-003"]
        orders = []

        for order_id in order_ids:
            order = self._create_test_order(order_id, "PRODUCTION" if order_id.endswith("001") else "STORAGE")
            orders.append(order)

        # Process all as active
        self.order_manager.process_ccu_order_active(
            topic="ccu/order/active", message=orders, meta={"timestamp": "2025-01-01T00:00:00.000Z"}
        )

        # Complete all orders
        completed_orders = []
        for order in orders:
            completed_order = order.copy()
            completed_order["state"] = "FINISHED"
            completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"
            for step in completed_order["productionSteps"]:
                step["state"] = "FINISHED"
            completed_orders.append(completed_order)

        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=completed_orders,
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # Verify all orders completed with status
        for order_id in order_ids:
            self.assertIn(order_id, self.order_manager.completed_orders)
            completed = self.order_manager.completed_orders[order_id]
            self.assertEqual(completed["status"], "COMPLETED", f"Order {order_id} should have status=COMPLETED")

    def test_last_step_running_state_converted_to_completed(self):
        """Test: Last step with RUNNING state is converted to COMPLETED"""
        # Setup: Create order with last step in RUNNING state
        order_id = "test-running-last"
        active_order = self._create_test_order(order_id, "PRODUCTION", num_steps=3)
        active_order["productionSteps"][-1]["state"] = "RUNNING"

        # Process as active
        self.order_manager.process_ccu_order_active(
            topic="ccu/order/active",
            message=[active_order],
            meta={"timestamp": "2025-01-01T00:00:00.000Z"},
        )

        # Complete the order
        completed_order = active_order.copy()
        completed_order["state"] = "FINISHED"
        completed_order["finishedAt"] = "2025-01-01T00:01:00.000Z"

        self.order_manager.process_ccu_order_completed(
            topic="ccu/order/completed",
            message=[completed_order],
            meta={"timestamp": "2025-01-01T00:01:00.000Z"},
        )

        # Verify last step is COMPLETED
        steps = self.order_manager.mqtt_steps[order_id]
        last_step = steps[-1]
        self.assertEqual(
            last_step["state"],
            "COMPLETED",
            "Last step with RUNNING state should be converted to COMPLETED",
        )


if __name__ == "__main__":
    unittest.main()
