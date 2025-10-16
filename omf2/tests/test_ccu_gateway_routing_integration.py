#!/usr/bin/env python3
"""
CCU Gateway Routing Integration Tests
Testet echte Message-Routing-Funktionalität

KRITISCH: Diese Tests verifizieren echte Funktionalität, nicht nur Konfiguration!
"""
import unittest
from unittest.mock import MagicMock, patch

from omf2.ccu.ccu_gateway import CcuGateway


class TestCcuGatewayRoutingIntegration(unittest.TestCase):
    """Echte Integration-Tests für CCU Gateway Routing"""

    def setUp(self):
        """Setup für jeden Test"""
        self.gateway = CcuGateway()

    def test_ccu_order_active_goes_to_order_manager(self):
        """Test: ccu/order/active → Order Manager (nicht Stock Manager)"""
        test_message = [{"orderId": "test-123", "type": "BLUE", "orderType": "PRODUCTION"}]
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch.object(self.gateway, "_get_order_manager") as mock_order_manager:
            mock_manager = MagicMock()
            mock_order_manager.return_value = mock_manager

            # Message routen
            self.gateway._route_ccu_message("ccu/order/active", test_message, meta)

            # VERIFIZIEREN: Order Manager wurde aufgerufen
            mock_manager.process_ccu_order_active.assert_called_once_with("ccu/order/active", test_message, meta)

    def test_ccu_order_completed_goes_to_order_manager(self):
        """Test: ccu/order/completed → Order Manager"""
        test_message = [{"orderId": "test-123", "type": "BLUE", "orderType": "PRODUCTION"}]
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch.object(self.gateway, "_get_order_manager") as mock_order_manager:
            mock_manager = MagicMock()
            mock_order_manager.return_value = mock_manager

            # Message routen
            self.gateway._route_ccu_message("ccu/order/completed", test_message, meta)

            # VERIFIZIEREN: Order Manager wurde aufgerufen
            mock_manager.process_ccu_order_completed.assert_called_once_with("ccu/order/completed", test_message, meta)

    def test_stock_topic_goes_to_stock_manager(self):
        """Test: /j1/txt/1/f/i/stock → Stock Manager (nicht Order Manager)"""
        test_message = {"stockItems": [{"location": "A1", "workpiece": {"type": "BLUE"}}]}
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch.object(self.gateway, "_get_stock_manager") as mock_stock_manager:
            mock_manager = MagicMock()
            mock_stock_manager.return_value = mock_manager

            # Message routen
            self.gateway._route_ccu_message("/j1/txt/1/f/i/stock", test_message, meta)

            # VERIFIZIEREN: Stock Manager wurde aufgerufen
            mock_manager.process_stock_message.assert_called_once_with("/j1/txt/1/f/i/stock", test_message, meta)

    def test_sensor_topic_goes_to_sensor_manager(self):
        """Test: /j1/txt/1/i/bme680 → Sensor Manager"""
        test_message = {"temperature": 25.5, "humidity": 60.0}
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch.object(self.gateway, "_get_sensor_manager") as mock_sensor_manager:
            mock_manager = MagicMock()
            mock_sensor_manager.return_value = mock_manager

            # Message routen
            self.gateway._route_ccu_message("/j1/txt/1/i/bme680", test_message, meta)

            # VERIFIZIEREN: Sensor Manager wurde aufgerufen
            mock_manager.process_sensor_message.assert_called_once_with("/j1/txt/1/i/bme680", test_message, meta)

    def test_module_topic_goes_to_module_manager(self):
        """Test: module/v1/ff/SVR3QA0022/state → Module Manager"""
        test_message = {"serialNumber": "SVR3QA0022", "state": "RUNNING"}
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch.object(self.gateway, "_get_module_manager") as mock_module_manager:
            mock_manager = MagicMock()
            mock_module_manager.return_value = mock_manager

            # Message routen
            self.gateway._route_ccu_message("module/v1/ff/SVR3QA0022/state", test_message, meta)

            # VERIFIZIEREN: Module Manager wurde aufgerufen
            mock_manager.process_module_message.assert_called_once_with(
                "module/v1/ff/SVR3QA0022/state", test_message, meta
            )

    def test_fts_topic_goes_to_module_manager(self):
        """Test: fts/v1/ff/5iO4/state → Module Manager"""
        test_message = {"serialNumber": "5iO4", "state": "MOVING"}
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch.object(self.gateway, "_get_module_manager") as mock_module_manager:
            mock_manager = MagicMock()
            mock_module_manager.return_value = mock_manager

            # Message routen
            self.gateway._route_ccu_message("fts/v1/ff/5iO4/state", test_message, meta)

            # VERIFIZIEREN: Module Manager wurde aufgerufen
            mock_manager.process_module_message.assert_called_once_with("fts/v1/ff/5iO4/state", test_message, meta)

    def test_unknown_topic_does_not_crash(self):
        """Test: Unbekannte Topics crashen nicht"""
        test_message = {"unknown": "data"}
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        # Sollte nicht crashen
        result = self.gateway._route_ccu_message("unknown/topic", test_message, meta)
        self.assertTrue(result)  # Sollte True zurückgeben (nicht als Fehler behandeln)

    def test_routing_priority_order(self):
        """Test: Routing-Priorität (Sensor → Module → Stock → Order)"""
        # Teste, dass Stock Topics nicht an Order Manager gehen
        test_message = {"stockItems": [{"location": "A1", "workpiece": {"type": "BLUE"}}]}
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch("omf2.ccu.stock_manager.get_stock_manager") as mock_stock_manager, patch(
            "omf2.ccu.order_manager.get_order_manager"
        ) as mock_order_manager:

            mock_stock_manager_instance = MagicMock()
            mock_order_manager_instance = MagicMock()
            mock_stock_manager.return_value = mock_stock_manager_instance
            mock_order_manager.return_value = mock_order_manager_instance

            # Message routen
            self.gateway._route_ccu_message("/j1/txt/1/f/i/stock", test_message, meta)

            # VERIFIZIEREN: Stock Manager wurde aufgerufen
            mock_stock_manager_instance.process_stock_message.assert_called_once()

            # VERIFIZIEREN: Order Manager wurde NICHT aufgerufen
            mock_order_manager_instance.process_ccu_order_active.assert_not_called()
            mock_order_manager_instance.process_ccu_order_completed.assert_not_called()

    def test_order_topics_do_not_go_to_stock_manager(self):
        """Test: Order Topics gehen nicht an Stock Manager"""
        test_message = [{"orderId": "test-123", "type": "BLUE", "orderType": "PRODUCTION"}]
        meta = {"timestamp": "2025-10-16T14:00:00Z"}

        with patch("omf2.ccu.stock_manager.get_stock_manager") as mock_stock_manager, patch(
            "omf2.ccu.order_manager.get_order_manager"
        ) as mock_order_manager:

            mock_stock_manager_instance = MagicMock()
            mock_order_manager_instance = MagicMock()
            mock_stock_manager.return_value = mock_stock_manager_instance
            mock_order_manager.return_value = mock_order_manager_instance

            # Message routen
            self.gateway._route_ccu_message("ccu/order/active", test_message, meta)

            # VERIFIZIEREN: Order Manager wurde aufgerufen
            mock_order_manager_instance.process_ccu_order_active.assert_called_once()

            # VERIFIZIEREN: Stock Manager wurde NICHT aufgerufen
            mock_stock_manager_instance.process_stock_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
