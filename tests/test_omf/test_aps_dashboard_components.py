#!/usr/bin/env python3
"""
Test für APS Dashboard Components
Version: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from omf.dashboard.components.aps_overview import show_aps_overview
from omf.dashboard.components.aps_orders import show_aps_orders
from omf.dashboard.components.aps_system_control import show_aps_system_control
from omf.dashboard.components.aps_configuration import show_aps_configuration


class TestAPSDashboardComponents:
    """Test-Klasse für APS Dashboard Components"""
    
    @pytest.fixture
    def mock_mqtt_client(self):
        """Mock MQTT Client"""
        client = Mock()
        client.connected = True
        return client
    
    @pytest.fixture
    def mock_aps_integration(self):
        """Mock APS Integration"""
        integration = Mock()
        integration.get_aps_status.return_value = {
            "mqtt_connected": True,
            "subscribed_topics": 10,
            "controllers": {
                "SVR4H73275": {
                    "moduleType": "DPS",
                    "online": True,
                    "ip_address": "192.168.0.102"
                }
            },
            "orders": {
                "active": 2,
                "completed": 5
            },
            "system_commands": {}
        }
        integration.get_discovered_controllers.return_value = {
            "SVR4H73275": {
                "serial_number": "SVR4H73275",
                "moduleType": "DPS",
                "ip_address": "192.168.0.102",
                "online": True,
                "role": "CCU",
                "functions": ["warehouse", "nfc", "camera"]
            }
        }
        integration.get_active_orders.return_value = {
            "order_001": {
                "orderId": "order_001",
                "type": "STORAGE",
                "status": "RUNNING",
                "color": "RED",
                "workpieceId": "WP_001",
                "targetModule": "DPS"
            }
        }
        integration.get_order_history.return_value = []
        integration.get_orders_by_color.return_value = []
        integration.get_orders_by_status.return_value = []
        integration.get_expected_topics.return_value = []
        integration.get_aps_topics.return_value = {
            "factsheet_topics": ["module/v1/ff/+/factsheet"],
            "state_topics": ["module/v1/ff/+/state"],
            "order_topics": ["module/v1/ff/+/order"],
            "instant_action_topics": ["module/v1/ff/+/instantAction"],
            "system_control_topics": ["ccu/set/+"],
            "fts_topics": ["fts/v1/ff/+/state"]
        }
        integration.create_storage_order.return_value = {
            "orderId": "test_order_001",
            "nodes": [{
                "actions": [{
                    "parameters": {"color": "RED", "workpieceId": "WP_001"}
                }]
            }]
        }
        integration.create_retrieval_order.return_value = {
            "orderId": "test_order_002",
            "nodes": [{
                "actions": [{
                    "parameters": {"color": "BLUE", "workpieceId": "WP_002"}
                }]
            }]
        }
        integration.send_instant_action.return_value = {
            "instantActions": [{
                "actionType": "camera_adjustment",
                "parameters": {"direction": "up", "angle": 10}
            }]
        }
        integration.publish_order.return_value = True
        integration.publish_instant_action.return_value = True
        integration.reset_factory.return_value = True
        integration.charge_fts.return_value = True
        integration.park_factory.return_value = True
        integration.calibrate_system.return_value = True
        integration.send_system_command.return_value = True
        integration.complete_order.return_value = True
        integration.cancel_order.return_value = True
        return integration
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock Streamlit"""
        with patch('streamlit.title') as mock_title, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.error') as mock_error, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.expander') as mock_expander, \
             patch('streamlit.button') as mock_button, \
             patch('streamlit.selectbox') as mock_selectbox, \
             patch('streamlit.text_input') as mock_text_input, \
             patch('streamlit.text_area') as mock_text_area, \
             patch('streamlit.number_input') as mock_number_input, \
             patch('streamlit.checkbox') as mock_checkbox, \
             patch('streamlit.multiselect') as mock_multiselect, \
             patch('streamlit.metric') as mock_metric, \
             patch('streamlit.json') as mock_json, \
             patch('streamlit.code') as mock_code, \
             patch('streamlit.tabs') as mock_tabs, \
             patch('streamlit.rerun') as mock_rerun:
            
            # Mock columns to return list of mocks
            mock_columns.return_value = [Mock(), Mock()]
            
            # Mock columns(2) specifically
            mock_columns.side_effect = lambda n: [Mock() for _ in range(n)]
            
            # Mock expander to return context manager
            mock_expander.return_value.__enter__ = Mock()
            mock_expander.return_value.__exit__ = Mock()
            
            # Mock tabs to return list of mocks
            mock_tabs.return_value = [Mock(), Mock(), Mock(), Mock()]
            
            # Mock button to return False by default
            mock_button.return_value = False
            
            # Mock selectbox to return first option
            mock_selectbox.return_value = "RED"
            
            # Mock text_input to return empty string
            mock_text_input.return_value = ""
            
            # Mock text_area to return empty string
            mock_text_area.return_value = "{}"
            
            # Mock number_input to return default value
            mock_number_input.return_value = 10
            
            # Mock checkbox to return False
            mock_checkbox.return_value = False
            
            # Mock multiselect to return empty list
            mock_multiselect.return_value = []
            
            yield {
                'title': mock_title,
                'markdown': mock_markdown,
                'error': mock_error,
                'success': mock_success,
                'info': mock_info,
                'warning': mock_warning,
                'columns': mock_columns,
                'expander': mock_expander,
                'button': mock_button,
                'selectbox': mock_selectbox,
                'text_input': mock_text_input,
                'text_area': mock_text_area,
                'number_input': mock_number_input,
                'checkbox': mock_checkbox,
                'multiselect': mock_multiselect,
                'metric': mock_metric,
                'json': mock_json,
                'code': mock_code,
                'tabs': mock_tabs,
                'rerun': mock_rerun
            }
    
    def test_aps_overview_component(self, mock_streamlit, mock_mqtt_client, mock_aps_integration):
        """Test APS Overview Component"""
        with patch('omf.dashboard.components.aps_overview.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_overview.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_overview.st') as mock_st:
            
            mock_get_client.return_value = mock_mqtt_client
            mock_mqtt_client.get_aps_integration.return_value = mock_aps_integration
            mock_st.session_state = {}
            
            # Test component execution
            show_aps_overview()
            
            # Verify calls
            mock_streamlit['title'].assert_called_once()
            mock_streamlit['markdown'].assert_called_once()
            mock_get_client.assert_called_once()
    
    def test_aps_orders_component(self, mock_streamlit, mock_mqtt_client, mock_aps_integration):
        """Test APS Orders Component"""
        with patch('omf.dashboard.components.aps_orders.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_orders.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_orders.st') as mock_st:
            
            mock_get_client.return_value = mock_mqtt_client
            mock_mqtt_client.get_aps_integration.return_value = mock_aps_integration
            mock_st.session_state = {}
            
            # Test component execution
            show_aps_orders()
            
            # Verify calls
            mock_streamlit['title'].assert_called_once()
            mock_streamlit['markdown'].assert_called_once()
            mock_get_client.assert_called_once()
    
    def test_aps_system_control_component(self, mock_streamlit, mock_mqtt_client, mock_aps_integration):
        """Test APS System Control Component"""
        with patch('omf.dashboard.components.aps_system_control.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_system_control.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_system_control.st') as mock_st:
            
            mock_get_client.return_value = mock_mqtt_client
            mock_mqtt_client.get_aps_integration.return_value = mock_aps_integration
            mock_st.session_state = {}
            
            # Test component execution
            show_aps_system_control()
            
            # Verify calls
            mock_streamlit['title'].assert_called_once()
            mock_streamlit['markdown'].assert_called_once()
            mock_get_client.assert_called_once()
    
    def test_aps_configuration_component(self, mock_streamlit, mock_mqtt_client, mock_aps_integration):
        """Test APS Configuration Component"""
        with patch('omf.dashboard.components.aps_configuration.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_configuration.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_configuration.st') as mock_st:
            
            mock_get_client.return_value = mock_mqtt_client
            mock_mqtt_client.get_aps_integration.return_value = mock_aps_integration
            mock_st.session_state = {}
            
            # Test component execution
            show_aps_configuration()
            
            # Verify calls
            mock_streamlit['title'].assert_called_once()
            mock_streamlit['markdown'].assert_called_once()
            mock_get_client.assert_called_once()
    
    def test_aps_overview_error_handling(self, mock_streamlit):
        """Test APS Overview Error Handling"""
        with patch('omf.dashboard.components.aps_overview.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_overview.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_overview.st') as mock_st:
            
            # Test MQTT Client not available
            mock_get_client.return_value = None
            mock_st.session_state = {}
            
            show_aps_overview()
            
            mock_streamlit['error'].assert_called_with("❌ MQTT Client nicht verfügbar")
    
    def test_aps_orders_error_handling(self, mock_streamlit):
        """Test APS Orders Error Handling"""
        with patch('omf.dashboard.components.aps_orders.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_orders.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_orders.st') as mock_st:
            
            # Test MQTT Client not available
            mock_get_client.return_value = None
            mock_st.session_state = {}
            
            show_aps_orders()
            
            mock_streamlit['error'].assert_called_with("❌ MQTT Client nicht verfügbar")
    
    def test_aps_system_control_error_handling(self, mock_streamlit):
        """Test APS System Control Error Handling"""
        with patch('omf.dashboard.components.aps_system_control.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_system_control.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_system_control.st') as mock_st:
            
            # Test MQTT Client not available
            mock_get_client.return_value = None
            mock_st.session_state = {}
            
            show_aps_system_control()
            
            mock_streamlit['error'].assert_called_with("❌ MQTT Client nicht verfügbar")
    
    def test_aps_configuration_error_handling(self, mock_streamlit):
        """Test APS Configuration Error Handling"""
        with patch('omf.dashboard.components.aps_configuration.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_configuration.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_configuration.st') as mock_st:
            
            # Test MQTT Client not available
            mock_get_client.return_value = None
            mock_st.session_state = {}
            
            show_aps_configuration()
            
            mock_streamlit['error'].assert_called_with("❌ MQTT Client nicht verfügbar")
    
    def test_aps_integration_activation(self, mock_streamlit, mock_mqtt_client, mock_aps_integration):
        """Test APS Integration Activation"""
        with patch('omf.dashboard.components.aps_overview.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_overview.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_overview.st') as mock_st:
            
            mock_get_client.return_value = mock_mqtt_client
            mock_mqtt_client.get_aps_integration.return_value = None
            mock_mqtt_client.enable_aps_integration.return_value = mock_aps_integration
            mock_st.session_state = {}
            
            show_aps_overview()
            
            mock_mqtt_client.enable_aps_integration.assert_called_once()
    
    def test_aps_integration_activation_failure(self, mock_streamlit, mock_mqtt_client):
        """Test APS Integration Activation Failure"""
        with patch('omf.dashboard.components.aps_overview.ensure_dashboard_client') as mock_get_client, \
             patch('omf.dashboard.components.aps_overview.get_logger') as mock_logger, \
             patch('omf.dashboard.components.aps_overview.st') as mock_st:
            
            mock_get_client.return_value = mock_mqtt_client
            mock_mqtt_client.get_aps_integration.return_value = None
            mock_mqtt_client.enable_aps_integration.return_value = None
            mock_st.session_state = {}
            
            show_aps_overview()
            
            mock_streamlit['error'].assert_called_with("❌ APS Integration konnte nicht aktiviert werden")


if __name__ == "__main__":
    pytest.main([__file__])
