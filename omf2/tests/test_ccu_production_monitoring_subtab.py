#!/usr/bin/env python3
"""
Tests for CCU Production Monitoring Subtab
"""

import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
from omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab import (
    render_ccu_production_monitoring_subtab,
    _show_process_statistics_section,
    _show_process_management_section,
    _show_process_control_section,
    _refresh_processes,
    _start_process,
    _pause_process,
    _stop_process
)


class TestCCUProductionMonitoringSubtab:
    """Test cases for CCU Production Monitoring Subtab"""
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    def test_render_ccu_production_monitoring_subtab_success(self, mock_st):
        """Test successful rendering of CCU production monitoring subtab"""
        # Mock Streamlit components
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.divider = MagicMock()
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
        mock_st.metric = MagicMock()
        mock_st.button = MagicMock(return_value=False)
        
        # Mock context managers
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.expander.return_value = mock_expander
        
        # Mock context managers for columns (need 5 columns for process management)
        mock_cols = [MagicMock() for _ in range(5)]
        for mock_col in mock_cols:
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=None)
        
        # Mock different column counts for different sections
        def mock_columns(n):
            if n == 5:
                return mock_cols
            else:
                return [MagicMock() for _ in range(n)]
        
        mock_st.columns.side_effect = mock_columns
        
        # Call function
        render_ccu_production_monitoring_subtab()
        
        # Verify calls
        mock_st.subheader.assert_called()
        mock_st.markdown.assert_called()
        mock_st.expander.assert_called()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    def test_render_ccu_production_monitoring_subtab_error(self, mock_st):
        """Test error handling in CCU production monitoring subtab"""
        # Setup mocks to raise exception
        mock_st.subheader.side_effect = Exception("Test error")
        mock_st.error = MagicMock()
        mock_st.info = MagicMock()
        
        # Call function
        render_ccu_production_monitoring_subtab()
        
        # Verify error handling
        mock_st.error.assert_called()
        mock_st.info.assert_called()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    def test_show_process_statistics_section(self, mock_st):
        """Test process statistics section rendering"""
        # Setup mocks
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()])
        mock_st.metric = MagicMock()
        
        # Mock context managers
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.expander.return_value = mock_expander
        
        for mock_col in mock_st.columns.return_value:
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=None)
        
        # Call function
        _show_process_statistics_section()
        
        # Verify calls
        mock_st.expander.assert_called_with("📊 Process Statistics", expanded=True)
        mock_st.columns.assert_called_with(4)
        assert mock_st.metric.call_count == 4  # Four metrics
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    def test_show_process_management_section(self, mock_st):
        """Test process management section rendering"""
        # Setup mocks
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.markdown = MagicMock()
        # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [2, 2, 2, 2, 1])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.button = MagicMock(return_value=False)
        mock_st.divider = MagicMock()
        mock_st.container = MagicMock(return_value=MagicMock())
        mock_st.write = MagicMock()
        mock_st.progress = MagicMock()
        
        # Mock context managers
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.expander.return_value = mock_expander
        
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_st.container.return_value = mock_container
        
        for mock_col in mock_st.columns.return_value:
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=None)
        
        # Call function
        _show_process_management_section()
        
        # Verify calls
        mock_st.expander.assert_called_with("📋 Process Management", expanded=True)
        mock_st.markdown.assert_called_with("### Active Processes")
        # Verify both columns calls: first with 3 columns, then with [2, 2, 2, 2, 1]
        assert mock_st.columns.call_count >= 2
        mock_st.columns.assert_any_call(3)
        mock_st.columns.assert_any_call([2, 2, 2, 2, 1])
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    def test_show_process_control_section(self, mock_st):
        """Test process control section rendering"""
        # Setup mocks
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.markdown = MagicMock()
        # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [2, 2, 2, 2, 1])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.button = MagicMock(return_value=False)
        
        # Mock context managers
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.expander.return_value = mock_expander
        
        for mock_col in mock_st.columns.return_value:
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=None)
        
        # Call function
        _show_process_control_section()
        
        # Verify calls
        mock_st.expander.assert_called_with("🎛️ Process Control", expanded=True)
        mock_st.markdown.assert_called_with("### Process Actions")
        mock_st.columns.assert_called_with(3)
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.request_refresh')
    def test_refresh_processes(self, mock_request_refresh, mock_st):
        """Test refresh processes functionality"""
        mock_st.success = MagicMock()
        
        _refresh_processes()
        
        mock_st.success.assert_called()
        mock_request_refresh.assert_called_once()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.request_refresh')
    def test_start_process(self, mock_request_refresh, mock_st):
        """Test start process functionality"""
        mock_st.success = MagicMock()
        
        _start_process()
        
        mock_st.success.assert_called()
        mock_request_refresh.assert_called_once()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.request_refresh')
    def test_pause_process(self, mock_request_refresh, mock_st):
        """Test pause process functionality"""
        mock_st.warning = MagicMock()
        
        _pause_process()
        
        mock_st.warning.assert_called()
        mock_request_refresh.assert_called_once()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.request_refresh')
    def test_stop_process(self, mock_request_refresh, mock_st):
        """Test stop process functionality"""
        mock_st.error = MagicMock()
        
        _stop_process()
        
        mock_st.error.assert_called()
        mock_request_refresh.assert_called_once()


class TestCCUProductionMonitoringSubtabIntegration:
    """Integration tests for CCU Production Monitoring Subtab"""
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab.st')
    def test_full_rendering_integration(self, mock_st):
        """Test full rendering integration"""
        # Setup comprehensive mocks
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.divider = MagicMock()
        mock_st.expander = MagicMock(return_value=MagicMock())
        # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [2, 2, 2, 2, 1])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.metric = MagicMock()
        mock_st.button = MagicMock(return_value=False)
        mock_st.container = MagicMock(return_value=MagicMock())
        mock_st.write = MagicMock()
        mock_st.progress = MagicMock()
        
        # Mock context managers
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.expander.return_value = mock_expander
        
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_st.container.return_value = mock_container
        
        for mock_col in mock_st.columns.return_value:
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=None)
        
        # Call function
        render_ccu_production_monitoring_subtab()
        
        # Verify main structure
        mock_st.subheader.assert_called_with("📊 Production Monitoring")
        # Verify markdown calls (there are multiple markdown calls in the component)
        mock_st.markdown.assert_any_call("Real-time monitoring of active production processes")
        mock_st.divider.assert_called()
        
        # Verify expanders were called
        assert mock_st.expander.call_count >= 3  # Statistics, Management, Control
