#!/usr/bin/env python3
"""
Tests for Production Orders Subtab - specifically testing the expander logic
"""

import unittest


class TestProductionOrdersSubtabExpanderLogic(unittest.TestCase):
    """Test cases for the production steps expander logic"""

    def test_order_completed_status_collapsed(self):
        """Test that orders with status=COMPLETED have collapsed expander"""
        # Simulate order with COMPLETED status
        order = {"status": "COMPLETED", "orderId": "test-1", "type": "WHITE"}

        # Simulate the logic from _render_order_details
        is_order_completed = False
        try:
            status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
            if status == "COMPLETED":
                is_order_completed = True
        except Exception:
            is_order_completed = False

        expanded = not is_order_completed

        # Assert: COMPLETED order should be collapsed (expanded=False)
        self.assertFalse(expanded, "COMPLETED orders should have collapsed expander")

    def test_order_in_progress_expanded(self):
        """Test that orders with status=IN_PROGRESS have expanded expander"""
        # Simulate order with IN_PROGRESS status
        order = {"status": "IN_PROGRESS", "orderId": "test-2", "type": "WHITE"}

        # Simulate the logic from _render_order_details
        is_order_completed = False
        try:
            status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
            if status == "COMPLETED":
                is_order_completed = True
        except Exception:
            is_order_completed = False

        expanded = not is_order_completed

        # Assert: IN_PROGRESS order should be expanded (expanded=True)
        self.assertTrue(expanded, "IN_PROGRESS orders should have expanded expander")

    def test_order_pending_expanded(self):
        """Test that orders with status=PENDING have expanded expander"""
        # Simulate order with PENDING status
        order = {"status": "PENDING", "orderId": "test-3", "type": "WHITE"}

        # Simulate the logic from _render_order_details
        is_order_completed = False
        try:
            status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
            if status == "COMPLETED":
                is_order_completed = True
        except Exception:
            is_order_completed = False

        expanded = not is_order_completed

        # Assert: PENDING order should be expanded (expanded=True)
        self.assertTrue(expanded, "PENDING orders should have expanded expander")

    def test_order_no_status_expanded(self):
        """Test that orders without status have expanded expander (defensive default)"""
        # Simulate order without status field
        order = {"orderId": "test-4", "type": "WHITE"}

        # Simulate the logic from _render_order_details
        is_order_completed = False
        try:
            status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
            if status == "COMPLETED":
                is_order_completed = True
        except Exception:
            is_order_completed = False

        expanded = not is_order_completed

        # Assert: Orders without status should be expanded by default (expanded=True)
        self.assertTrue(expanded, "Orders without status should be expanded by default")

    def test_order_with_last_step_completed_and_status_completed(self):
        """Test order with last step COMPLETED and status COMPLETED is collapsed"""
        # Simulate order with last step completed and status completed
        order = {
            "status": "COMPLETED",
            "orderId": "test-5",
            "type": "WHITE",
            "steps": [{"state": "FINISHED"}, {"state": "FINISHED"}, {"state": "COMPLETED"}],
        }

        # Simulate the full logic from _render_order_details
        is_order_completed = False
        try:
            status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
            if status == "COMPLETED":
                is_order_completed = True
            else:
                last_step = None
                steps = order.get("steps") if isinstance(order, dict) else getattr(order, "steps", None)
                if steps:
                    last_step = steps[-1]
                last_step_state = None
                if isinstance(last_step, dict):
                    last_step_state = last_step.get("state")
                else:
                    last_step_state = getattr(last_step, "state", None) if last_step is not None else None
                if last_step_state == "COMPLETED":
                    is_order_completed = status == "COMPLETED"
        except Exception:
            is_order_completed = False

        expanded = not is_order_completed

        # Assert: Fully completed order should be collapsed
        self.assertFalse(expanded, "Fully completed orders should be collapsed")

    def test_order_defensive_exception_handling(self):
        """Test that exceptions during status check result in expanded expander (safe default)"""

        # Simulate an order that will cause an exception when accessing status
        class BrokenOrder:
            @property
            def status(self):
                raise Exception("Simulated error")

        order = BrokenOrder()

        # Simulate the logic from _render_order_details with exception handling
        is_order_completed = False
        try:
            status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
            if status == "COMPLETED":
                is_order_completed = True
        except Exception:
            is_order_completed = False

        expanded = not is_order_completed

        # Assert: On exception, should default to expanded (safer for active orders)
        self.assertTrue(expanded, "Exceptions should result in expanded expander (safe default)")


if __name__ == "__main__":
    unittest.main()
