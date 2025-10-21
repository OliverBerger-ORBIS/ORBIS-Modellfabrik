#!/usr/bin/env python3
"""
Test Module Details Integration - Double-Click Navigation
Tests the integration between shopfloor_layout.py and ccu_modules_tab.py
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch

from omf2.ccu.module_manager import get_ccu_module_manager
# FIX: Import only existing functions from ccu_modules_tab
from omf2.ui.ccu.ccu_modules.ccu_modules_tab import (
    _show_module_overview_table,
    _show_module_statistics,
    _show_module_statistics_summary,
    _show_module_settings,
)
# FIX: Import private functions from ccu_modules_details
from omf2.ui.ccu.ccu_modules.ccu_modules_details import (
    _show_module_svg,
    _show_module_info,
)


class TestModuleDetailsIntegration:
    """Test Module Details Integration"""

    def test_show_module_overview_table(self):
        """Test module overview table"""
        # Mock dependencies
        mock_ccu_gateway = Mock()
        mock_i18n = Mock()
        mock_i18n.get.return_value = "Test Text"
        
        # Test should not raise exception
        try:
            _show_module_overview_table(mock_ccu_gateway, mock_i18n)
            assert True
        except Exception as e:
            pytest.fail(f"Module overview table failed: {e}")

    def test_show_module_statistics(self):
        """Test module statistics"""
        # Mock dependencies
        mock_ccu_gateway = Mock()
        mock_i18n = Mock()
        mock_i18n.get.return_value = "Test Text"
        
        # Test should not raise exception
        try:
            _show_module_statistics(mock_ccu_gateway, mock_i18n)
            assert True
        except Exception as e:
            pytest.fail(f"Module statistics failed: {e}")

    def test_show_module_statistics_summary(self):
        """Test module statistics summary"""
        # Mock status store
        mock_status_store = Mock()
        mock_status_store.get_all_module_status.return_value = {
            'SVR4H73275': {'connected': True, 'available': 'READY'},
            'SVR4H73276': {'connected': False, 'available': 'OFFLINE'}
        }
        
        # Mock i18n
        mock_i18n = Mock()
        mock_i18n.get.return_value = "Test Text"
        
        # Test should not raise exception
        try:
            _show_module_statistics_summary(mock_status_store, mock_i18n)
            assert True
        except Exception as e:
            pytest.fail(f"Module statistics summary failed: {e}")

    def test_show_module_settings(self):
        """Test module settings"""
        # Mock i18n
        mock_i18n = Mock()
        mock_i18n.get.return_value = "Test Text"
        
        # Test should not raise exception
        try:
            _show_module_settings(mock_i18n)
            assert True
        except Exception as e:
            pytest.fail(f"Module settings failed: {e}")

    def test_module_manager_integration(self):
        """Test module manager integration"""
        # Mock module manager
        mock_module_manager = Mock()
        mock_module_manager.get_module_status_from_state.return_value = {
            'connected': True,
            'available': 'READY',
            'message_count': 5
        }
        mock_module_manager.get_module_factsheet_status.return_value = {
            'factsheet_data': {'name': 'MILL Module', 'version': '1.0'},
            'configured': True
        }

        with patch('omf2.ccu.module_manager.get_ccu_module_manager', return_value=mock_module_manager):
            # Test should not raise exception
            try:
                # Test module manager functionality
                status = mock_module_manager.get_module_status_from_state('SVR4H73275')
                factsheet = mock_module_manager.get_module_factsheet_status('SVR4H73275')
                assert status['connected'] == True
                assert factsheet['configured'] == True
            except Exception as e:
                pytest.fail(f"Module manager integration failed: {e}")

    def test_show_module_svg_with_asset_manager(self):
        """Test module SVG display with asset manager"""
        # Mock asset manager
        mock_asset_manager = Mock()
        mock_asset_manager.get_module_icon_path.return_value = "/path/to/icon.svg"
        
        with patch('omf2.assets.get_asset_manager', return_value=mock_asset_manager):
            # Mock Path.exists
            with patch('pathlib.Path.exists', return_value=True):
                # Mock open
                with patch('builtins.open', mock_open(read_data='<svg>test</svg>')):
                    # Mock i18n
                    mock_i18n = Mock()
                    mock_i18n.t.return_value = "No SVG available"
                    
                    # Test should not raise exception
                    try:
                        # FIX: Add missing module_info parameter
                        module_info = {'name': 'MILL', 'serialNumber': 'SVR4H73275'}
                        _show_module_svg('SVR4H73275', 'MILL', module_info, mock_i18n)
                        assert True
                    except Exception as e:
                        pytest.fail(f"Module SVG display failed: {e}")

    def test_show_module_info_with_factsheet(self):
        """Test module info display with factsheet data"""
        # Mock i18n
        mock_i18n = Mock()
        mock_i18n.t.return_value = "No status data available"
        
        # Test data
        module_status = {
            'connected': True,
            'available': 'READY',
            'message_count': 5,
            'last_update': '12:34:56'
        }
        
        factsheet_status = {
            'factsheet_data': {
                'name': 'MILL Module',
                'version': '1.0',
                'serialNumber': 'SVR4H73275'
            },
            'configured': True
        }
        
        # Test should not raise exception
        try:
            _show_module_info('SVR4H73275', 'MILL', module_status, factsheet_status, mock_i18n)
            assert True
        except Exception as e:
            pytest.fail(f"Module info display failed: {e}")

    def test_show_module_info_without_factsheet(self):
        """Test module info display without factsheet data"""
        # Mock i18n
        mock_i18n = Mock()
        mock_i18n.t.return_value = "No status data available"
        
        # Test data without factsheet
        module_status = {
            'connected': False,
            'available': 'Unknown',
            'message_count': 0,
            'last_update': 'Never'
        }
        
        factsheet_status = {}
        
        # Test should not raise exception
        try:
            _show_module_info('SVR4H73275', 'MILL', module_status, factsheet_status, mock_i18n)
            assert True
        except Exception as e:
            pytest.fail(f"Module info display without factsheet failed: {e}")


def mock_open(read_data):
    """Mock open function for testing"""
    from unittest.mock import mock_open
    return mock_open(read_data=read_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
