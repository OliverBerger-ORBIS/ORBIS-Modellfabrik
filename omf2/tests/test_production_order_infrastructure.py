#!/usr/bin/env python3
"""
Test-Skript für Production Order Manager Infrastruktur

Testet:
- ProductionOrderManager Initialisierung
- MQTT Message Processing
- Gateway Routing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_production_order_manager_init():
    """Test 1: Manager Initialisierung"""
    print("\n" + "=" * 80)
    print("TEST 1: ProductionOrderManager Initialisierung")
    print("=" * 80)

    try:
        from omf2.ccu.order_manager import get_order_manager

        # Manager initialisieren
        manager = get_order_manager()

        # Prüfen
        assert manager is not None, "Manager should not be None"
        assert hasattr(manager, "active_orders"), "Manager should have active_orders"
        assert hasattr(manager, "completed_orders"), "Manager should have completed_orders"

        print("✅ Manager initialized successfully")
        print(f"   Active orders: {len(manager.active_orders)}")
        print(f"   Completed orders: {len(manager.completed_orders)}")

        return True

    except Exception as e:
        print(f"❌ Manager initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_active_order_message_processing():
    """Test 2: Active Order Message Processing"""
    print("\n" + "=" * 80)
    print("TEST 2: Active Order Message Processing")
    print("=" * 80)

    try:
        from omf2.ccu.order_manager import get_order_manager

        manager = get_order_manager()

        # Mock Active Order Message (aus Schema)
        test_active_message = [
            {
                "orderId": "TEST-ORD-001",
                "orderType": "PRODUCTION",
                "type": "BLUE",
                "timestamp": "2025-10-08T10:00:00Z",
                "state": "PROCESSING",
                "receivedAt": "2025-10-08T09:55:00Z",
                "startedAt": "2025-10-08T09:56:00Z",
                "productionSteps": [
                    {"id": "step-1", "type": "PICK", "state": "COMPLETED"},
                    {"id": "step-2", "type": "PROCESS", "state": "RUNNING"},
                ],
            }
        ]

        # Message verarbeiten
        manager.process_ccu_order_active(
            topic="ccu/order/active", message=test_active_message, meta={"timestamp": "2025-10-08T10:00:00Z"}
        )

        # Prüfen
        active_orders = manager.get_active_orders()
        assert len(active_orders) == 1, f"Should have 1 active order, got {len(active_orders)}"
        assert active_orders[0]["orderId"] == "TEST-ORD-001", "Order ID should match"

        print("✅ Active order message processed successfully")
        print(f"   Active orders: {len(active_orders)}")
        print(f"   Order ID: {active_orders[0]['orderId']}")
        print(f"   Order Type: {active_orders[0]['type']}")
        print(f"   State: {active_orders[0]['state']}")

        return True

    except Exception as e:
        print(f"❌ Active order message processing failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_completed_order_message_processing():
    """Test 3: Completed Order Message Processing"""
    print("\n" + "=" * 80)
    print("TEST 3: Completed Order Message Processing")
    print("=" * 80)

    try:
        from omf2.ccu.order_manager import get_order_manager

        manager = get_order_manager()

        # Mock Completed Order Message (aus Schema)
        test_completed_message = [
            {
                "orderId": "TEST-ORD-002",
                "orderType": "PRODUCTION",
                "type": "RED",
                "timestamp": "2025-10-08T11:00:00Z",
                "state": "COMPLETED",
                "receivedAt": "2025-10-08T10:00:00Z",
                "startedAt": "2025-10-08T10:01:00Z",
                "stoppedAt": "2025-10-08T10:45:00Z",
                "workpieceId": "WP-RED-001",
                "productionSteps": [
                    {"id": "step-1", "type": "PICK", "state": "COMPLETED"},
                    {"id": "step-2", "type": "PROCESS", "state": "COMPLETED"},
                    {"id": "step-3", "type": "DROP", "state": "COMPLETED"},
                ],
            }
        ]

        # Message verarbeiten
        manager.process_ccu_order_completed(
            topic="ccu/order/completed", message=test_completed_message, meta={"timestamp": "2025-10-08T11:00:00Z"}
        )

        # Prüfen
        completed_orders = manager.get_completed_orders()
        assert len(completed_orders) == 1, f"Should have 1 completed order, got {len(completed_orders)}"
        assert completed_orders[0]["orderId"] == "TEST-ORD-002", "Order ID should match"

        print("✅ Completed order message processed successfully")
        print(f"   Completed orders: {len(completed_orders)}")
        print(f"   Order ID: {completed_orders[0]['orderId']}")
        print(f"   Order Type: {completed_orders[0]['type']}")
        print(f"   State: {completed_orders[0]['state']}")

        return True

    except Exception as e:
        print(f"❌ Completed order message processing failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_order_statistics():
    """Test 4: Order Statistics"""
    print("\n" + "=" * 80)
    print("TEST 4: Order Statistics")
    print("=" * 80)

    try:
        from omf2.ccu.order_manager import get_order_manager

        manager = get_order_manager()

        # Statistiken holen
        stats = manager.get_order_statistics()

        print("✅ Order statistics retrieved successfully")
        print(f"   Active count: {stats['active_count']}")
        print(f"   Completed count: {stats['completed_count']}")
        print(f"   Total count: {stats['total_count']}")
        print(f"   STUB mode: {stats['stub_mode']}")

        return True

    except Exception as e:
        print(f"❌ Order statistics failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_all_tests():
    """Führt alle Tests aus"""
    print("\n" + "=" * 80)
    print("PRODUCTION ORDER MANAGER - INFRASTRUKTUR TESTS")
    print("=" * 80)

    results = []

    # Test 1: Initialisierung
    results.append(("Initialisierung", test_production_order_manager_init()))

    # Test 2: Active Order Processing
    results.append(("Active Order Processing", test_active_order_message_processing()))

    # Test 3: Completed Order Processing
    results.append(("Completed Order Processing", test_completed_order_message_processing()))

    # Test 4: Statistics
    results.append(("Order Statistics", test_order_statistics()))

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Infrastructure is ready!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check logs above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
