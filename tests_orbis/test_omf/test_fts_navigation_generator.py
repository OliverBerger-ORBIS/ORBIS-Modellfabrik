"""
Unit Tests für FTS Navigation Message Generator
Testet generate_fts_navigation_message() und Dashboard Integration
"""

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from src_orbis.omf.tools.message_generator import MessageGenerator


class TestFTSNavigationGenerator:
    """Test-Klasse für FTS Navigation Message Generator"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.generator = MessageGenerator()

    def test_generate_fts_navigation_message_dps_hbw(self):
        """Test: DPS-HBW Route generieren"""
        # Arrange
        route_type = "DPS_HBW"
        load_type = "WHITE"
        load_id = "04798eca341290"
        
        # Act
        message = self.generator.generate_fts_navigation_message(
            route_type=route_type,
            load_type=load_type,
            load_id=load_id
        )
        
        # Assert
        assert message is not None
        assert message["topic"] == "fts/v1/ff/5iO4/order"
        assert "orderId" in message["payload"]
        assert message["payload"]["serialNumber"] == "5iO4"
        assert message["payload"]["orderUpdateId"] == 0
        
        # Nodes prüfen
        nodes = message["payload"]["nodes"]
        assert len(nodes) == 4
        assert nodes[0]["id"] == "SVR4H73275"  # DPS
        assert nodes[-1]["id"] == "SVR3QA0022"  # HBW
        
        # Edges prüfen
        edges = message["payload"]["edges"]
        assert len(edges) == 3
        assert edges[0]["id"] == "SVR4H73275-2"
        assert edges[0]["length"] == 380
        
        # DOCK Action prüfen
        dock_action = nodes[-1]["action"]
        assert dock_action["type"] == "DOCK"
        assert dock_action["metadata"]["loadType"] == load_type
        assert dock_action["metadata"]["loadId"] == load_id

    def test_generate_fts_navigation_message_hbw_dps(self):
        """Test: HBW-DPS Route generieren"""
        # Arrange
        route_type = "HBW_DPS"
        load_type = "RED"
        
        # Act
        message = self.generator.generate_fts_navigation_message(
            route_type=route_type,
            load_type=load_type
        )
        
        # Assert
        assert message is not None
        assert message["topic"] == "fts/v1/ff/5iO4/order"
        
        # Nodes prüfen (umgekehrte Route)
        nodes = message["payload"]["nodes"]
        assert len(nodes) == 4
        assert nodes[0]["id"] == "SVR3QA0022"  # HBW
        assert nodes[-1]["id"] == "SVR4H73275"  # DPS
        
        # DOCK Action prüfen
        dock_action = nodes[-1]["action"]
        assert dock_action["type"] == "DOCK"
        assert dock_action["metadata"]["loadType"] == load_type

    def test_generate_fts_navigation_message_unknown_route(self):
        """Test: Unbekannte Route"""
        # Arrange
        route_type = "UNKNOWN_ROUTE"
        
        # Act
        message = self.generator.generate_fts_navigation_message(route_type=route_type)
        
        # Assert
        assert message is None

    def test_generate_fts_navigation_message_uuid_generation(self):
        """Test: UUID-Generierung für orderId und action.id"""
        # Arrange
        route_type = "DPS_HBW"
        
        # Act
        message = self.generator.generate_fts_navigation_message(route_type=route_type)
        
        # Assert
        assert message is not None
        
        # orderId prüfen
        order_id = message["payload"]["orderId"]
        assert order_id.startswith("fts-navigation-dps_hbw-")
        assert len(order_id) == len("fts-navigation-dps_hbw-") + 8  # 8 hex chars
        
        # action.id prüfen (alle Actions haben UUID)
        nodes = message["payload"]["nodes"]
        for node in nodes:
            if "action" in node and "id" in node["action"]:
                action_id = node["action"]["id"]
                # UUID-Format prüfen (36 chars mit Bindestrichen)
                assert len(action_id) == 36
                assert action_id.count("-") == 4

    def test_generate_fts_navigation_message_custom_order_id(self):
        """Test: Custom orderId verwenden"""
        # Arrange
        route_type = "DPS_HBW"
        custom_order_id = "custom-order-123"
        
        # Act
        message = self.generator.generate_fts_navigation_message(
            route_type=route_type,
            order_id=custom_order_id
        )
        
        # Assert
        assert message is not None
        assert message["payload"]["orderId"] == custom_order_id

    def test_generate_fts_navigation_message_custom_load_id(self):
        """Test: Custom loadId verwenden"""
        # Arrange
        route_type = "DPS_HBW"
        custom_load_id = "04custom123456"
        
        # Act
        message = self.generator.generate_fts_navigation_message(
            route_type=route_type,
            load_id=custom_load_id
        )
        
        # Assert
        assert message is not None
        nodes = message["payload"]["nodes"]
        dock_action = nodes[-1]["action"]
        assert dock_action["metadata"]["loadId"] == custom_load_id

    def test_generate_fts_navigation_message_timestamp_format(self):
        """Test: Timestamp Format (ISO 8601 mit Z)"""
        # Arrange
        route_type = "DPS_HBW"
        
        # Act
        message = self.generator.generate_fts_navigation_message(route_type=route_type)
        
        # Assert
        assert message is not None
        timestamp = message["payload"]["timestamp"]
        assert timestamp.endswith("Z")
        # ISO 8601 Format prüfen
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_generate_fts_navigation_message_edge_structure(self):
        """Test: Edge-Struktur (length, linkedNodes)"""
        # Arrange
        route_type = "DPS_HBW"
        
        # Act
        message = self.generator.generate_fts_navigation_message(route_type=route_type)
        
        # Assert
        assert message is not None
        edges = message["payload"]["edges"]
        
        for edge in edges:
            assert "id" in edge
            assert "length" in edge
            assert "linkedNodes" in edge
            assert isinstance(edge["length"], int)
            assert isinstance(edge["linkedNodes"], list)
            assert len(edge["linkedNodes"]) == 2

    def test_generate_fts_navigation_message_node_structure(self):
        """Test: Node-Struktur (id, linkedEdges, action)"""
        # Arrange
        route_type = "DPS_HBW"
        
        # Act
        message = self.generator.generate_fts_navigation_message(route_type=route_type)
        
        # Assert
        assert message is not None
        nodes = message["payload"]["nodes"]
        
        for node in nodes:
            assert "id" in node
            assert "linkedEdges" in node
            assert isinstance(node["linkedEdges"], list)
            
            # Action prüfen (nur bei bestimmten Nodes)
            if "action" in node:
                action = node["action"]
                assert "id" in action
                assert "type" in action
                assert action["type"] in ["PASS", "DOCK"]

    def test_generate_fts_navigation_message_load_type_variations(self):
        """Test: Verschiedene loadType Werte"""
        # Arrange
        route_type = "DPS_HBW"
        load_types = ["RED", "BLUE", "WHITE"]
        
        # Act & Assert
        for load_type in load_types:
            message = self.generator.generate_fts_navigation_message(
                route_type=route_type,
                load_type=load_type
            )
            
            assert message is not None
            nodes = message["payload"]["nodes"]
            dock_action = nodes[-1]["action"]
            assert dock_action["metadata"]["loadType"] == load_type


class TestFTSNavigationDashboardIntegration:
    """Test-Klasse für Dashboard Integration"""

    @patch('src_orbis.omf.dashboard.components.steering_factory.st')
    def test_prepare_navigation_message_dps_hbw(self, mock_st):
        """Test: Dashboard Navigation Message für DPS-HBW"""
        # Arrange
        mock_session_state = {}
        mock_st.session_state = mock_session_state
        
        # Act
        from src_orbis.omf.dashboard.components.steering_factory import _prepare_navigation_message
        _prepare_navigation_message("DPS-HBW")
        
        # Assert
        assert "pending_message" in mock_session_state
        message = mock_session_state["pending_message"]
        assert message["type"] == "navigation"
        assert message["topic"] == "fts/v1/ff/5iO4/order"
        assert "orderId" in message["payload"]

    @patch('src_orbis.omf.dashboard.components.steering_factory.st')
    def test_prepare_navigation_message_route_mapping(self, mock_st):
        """Test: Route-Mapping für verschiedene Navigation-Typen"""
        # Arrange
        mock_session_state = {}
        mock_st.session_state = mock_session_state
        
        # Act
        from src_orbis.omf.dashboard.components.steering_factory import _prepare_navigation_message
        
        # Test verschiedene Navigation-Typen
        navigation_types = ["DPS-HBW", "RED-Prod", "BLUE-Prod", "WHITE-Prod"]
        
        for nav_type in navigation_types:
            _prepare_navigation_message(nav_type)
            
            # Assert
            assert "pending_message" in mock_session_state
            message = mock_session_state["pending_message"]
            assert message["type"] == "navigation"
            assert message["topic"] == "fts/v1/ff/5iO4/order"
            assert "orderId" in message["payload"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
