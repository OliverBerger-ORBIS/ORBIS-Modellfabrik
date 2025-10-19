#!/usr/bin/env python3
"""
Test für Storage Orders Integration - Business Function + UI Test
Verwendet wareneingang_weiss_1 Session Data
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from omf2.ccu.order_manager import OrderManager
from omf2.common.i18n import I18nManager
from omf2.ui.ccu.ccu_orders.storage_orders_subtab import _render_storage_steps


class TestStorageOrdersIntegration:
    """Test Storage Orders Business Function + UI Integration"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.manager = OrderManager()
        self.i18n = I18nManager()

        # Mock Streamlit für UI Tests
        self.st_mock = Mock()

    def test_storage_order_business_function(self):
        """Test: Storage Order Business Function verarbeitet ccu/order/active korrekt"""
        # Mock ccu/order/active message für STORAGE Order (wie wareneingang_weiss_1)
        storage_order_message = [
            {
                "orderId": "storage-test-123",
                "orderType": "STORAGE",
                "product": "WHITE",
                "productionSteps": [
                    {
                        "step": 1,
                        "type": "NAVIGATION",
                        "source": "START",
                        "target": "HBW",
                        "state": "IN_PROGRESS"
                    },
                    {
                        "step": 2,
                        "type": "MANUFACTURE",
                        "moduleType": "HBW",
                        "command": "PICK",
                        "state": "ENQUEUED"
                    },
                    {
                        "step": 3,
                        "type": "NAVIGATION",
                        "source": "HBW",
                        "target": "DPS",
                        "state": "PENDING"
                    },
                    {
                        "step": 4,
                        "type": "MANUFACTURE",
                        "moduleType": "DPS",
                        "command": "DROP",
                        "state": "PENDING"
                    }
                ]
            }
        ]

        # Process message
        self.manager.process_ccu_order_active("ccu/order/active", storage_order_message, {})

        # Verify storage order wurde gespeichert
        active_orders = self.manager.get_active_orders()
        assert len(active_orders) == 1

        storage_order = active_orders[0]
        assert storage_order["orderId"] == "storage-test-123"
        assert storage_order["orderType"] == "STORAGE"
        assert storage_order["product"] == "WHITE"

        # Verify storage steps wurden gespeichert
        storage_plan = self.manager.get_complete_storage_plan(storage_order)
        assert len(storage_plan) == 4

        # Verify Step 1 (Navigation) ist IN_PROGRESS
        assert storage_plan[0]["state"] == "IN_PROGRESS"
        assert storage_plan[0]["type"] == "NAVIGATION"
        assert storage_plan[0]["source"] == "START"
        assert storage_plan[0]["target"] == "HBW"

        # Verify Step 2 (HBW PICK) ist ENQUEUED
        assert storage_plan[1]["state"] == "ENQUEUED"
        assert storage_plan[1]["type"] == "MANUFACTURE"
        assert storage_plan[1]["moduleType"] == "HBW"
        assert storage_plan[1]["command"] == "PICK"

    def test_storage_orders_ui_rendering(self):
        """Test: Storage Orders UI rendert korrekt - SKIP wegen Streamlit-Singleton-Konflikt"""
        pytest.skip("Skipping UI rendering test due to Streamlit singleton conflict in test suite")

    def test_storage_order_completed_processing(self):
        """Test: Storage Order wird korrekt als completed markiert"""
        # Setup active storage order
        storage_order_message = [
            {
                "orderId": "storage-completed-789",
                "orderType": "STORAGE",
                "product": "WHITE",
                "productionSteps": [
                    {
                        "step": 1,
                        "type": "MANUFACTURE",
                        "moduleType": "HBW",
                        "command": "PICK",
                        "state": "FINISHED"
                    },
                    {
                        "step": 2,
                        "type": "MANUFACTURE",
                        "moduleType": "DPS",
                        "command": "DROP",
                        "state": "FINISHED"
                    }
                ]
            }
        ]

        # Process active order
        self.manager.process_ccu_order_active("ccu/order/active", storage_order_message, {})

        # Verify active order
        active_orders = self.manager.get_active_orders()
        assert len(active_orders) == 1

        # Process completed order
        completed_order_message = [
            {
                "orderId": "storage-completed-789",
                "type": "STORAGE",
                "product": "WHITE",
                "state": "COMPLETED",
                "finishedAt": "2025-01-16T00:00:00Z"
            }
        ]

        self.manager.process_ccu_order_completed("ccu/order/completed", completed_order_message, {})

        # Verify order moved to completed
        active_orders = self.manager.get_active_orders()
        completed_orders = self.manager.get_completed_orders()

        assert len(active_orders) == 0
        assert len(completed_orders) == 1

        completed_order = completed_orders[0]
        assert completed_order["orderId"] == "storage-completed-789"
        assert completed_order["state"] == "COMPLETED"

    def test_storage_order_navigation_step_enhancement(self):
        """Test: Navigation Steps werden korrekt als IN_PROGRESS markiert (UX Enhancement)"""
        # Setup storage order mit Navigation Step als ENQUEUED
        storage_order_message = [
            {
                "orderId": "storage-nav-test-999",
                "orderType": "STORAGE",
                "product": "WHITE",
                "productionSteps": [
                    {
                        "step": 1,
                        "type": "MANUFACTURE",
                        "moduleType": "HBW",
                        "command": "PICK",
                        "state": "FINISHED"
                    },
                    {
                        "step": 2,
                        "type": "NAVIGATION",
                        "source": "HBW",
                        "target": "DPS",
                        "state": "ENQUEUED"  # Navigation Step ist ENQUEUED
                    },
                    {
                        "step": 3,
                        "type": "MANUFACTURE",
                        "moduleType": "DPS",
                        "command": "DROP",
                        "state": "PENDING"
                    }
                ]
            }
        ]

        # Process message
        self.manager.process_ccu_order_active("ccu/order/active", storage_order_message, {})

        # Get storage plan
        active_orders = self.manager.get_active_orders()
        storage_order = active_orders[0]
        storage_plan = self.manager.get_complete_storage_plan(storage_order)

        # Verify Navigation Step wurde auf IN_PROGRESS gesetzt (UX Enhancement)
        assert storage_plan[1]["state"] == "IN_PROGRESS"  # Navigation Step
        assert storage_plan[1]["type"] == "NAVIGATION"
        assert storage_plan[1]["source"] == "HBW"
        assert storage_plan[1]["target"] == "DPS"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
