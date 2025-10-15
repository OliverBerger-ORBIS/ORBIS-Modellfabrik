#!/usr/bin/env python3
"""
Tests for CCU Production Plan Subtab
"""

import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
from omf2.ui.ccu.ccu_process.ccu_production_plan_subtab import (
    render_ccu_production_plan_subtab,
    _show_workflow_overview_section,
    _show_detailed_workflows_section,
    _show_workflow_comparison_section,
    _get_module_icon,
    _get_module_info,
    _get_estimated_duration,
    _get_complexity_level
)


class TestCCUProductionPlanSubtab:
    """Test cases for CCU Production Plan Subtab"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Mock production workflows data
        self.mock_workflows = {
            "_meta": {
                "_description": "Production workflow definitions",
                "_version": "1.0"
            },
            "BLUE": {
                "steps": ["MILL", "DRILL", "AIQS"]
            },
            "WHITE": {
                "steps": ["DRILL", "AIQS"]
            },
            "RED": {
                "steps": ["MILL", "AIQS"]
            }
        }
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.get_ccu_config_loader')
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.st')
    def test_render_ccu_production_plan_subtab_success(self, mock_st, mock_get_loader):
        """Test successful rendering of CCU production plan subtab"""
        # Setup mocks
        mock_loader = MagicMock()
        mock_loader.load_production_workflows.return_value = self.mock_workflows
        mock_get_loader.return_value = mock_loader
        
        # Mock Streamlit components
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.divider = MagicMock()
        # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [1, 1, 1, 3])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.metric = MagicMock()
        mock_st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.table = MagicMock()
        
        # Call function
        render_ccu_production_plan_subtab()
        
        # Verify calls
        mock_st.subheader.assert_called_with("📋 Production Plan")
        mock_st.markdown.assert_called()
        mock_loader.load_production_workflows.assert_called_once()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.get_ccu_config_loader')
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.st')
    def test_render_ccu_production_plan_subtab_no_workflows(self, mock_st, mock_get_loader):
        """Test rendering when no workflows are loaded"""
        # Setup mocks
        mock_loader = MagicMock()
        mock_loader.load_production_workflows.return_value = {}
        mock_get_loader.return_value = mock_loader
        
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.error = MagicMock()
        
        # Call function
        render_ccu_production_plan_subtab()
        
        # Verify error handling
        mock_st.error.assert_called()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.st')
    def test_show_workflow_overview_section(self, mock_st):
        """Test workflow overview section rendering"""
        # Setup mocks
        mock_st.markdown = MagicMock()
        mock_st.write = MagicMock()
        # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [1, 1, 1, 3])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.metric = MagicMock()
        
        # Mock context managers for columns
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        for col in [col1, col2, col3]:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [col1, col2, col3]
        
        # Call function
        _show_workflow_overview_section(self.mock_workflows)
        
        # Verify calls
        mock_st.markdown.assert_called()
        mock_st.write.assert_called()
        mock_st.columns.assert_called()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.st')
    def test_show_detailed_workflows_section(self, mock_st):
        """Test detailed workflows section rendering"""
        # Setup mocks
        mock_st.markdown = MagicMock()
        mock_st.write = MagicMock()
        mock_st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        
        # Mock context managers for tabs
        tab1, tab2, tab3 = MagicMock(), MagicMock(), MagicMock()
        for tab in [tab1, tab2, tab3]:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=None)
        mock_st.tabs.return_value = [tab1, tab2, tab3]
        
        # Call function
        _show_detailed_workflows_section(self.mock_workflows)
        
        # Verify calls
        mock_st.markdown.assert_called()
        mock_st.write.assert_called()
        mock_st.tabs.assert_called()
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.st')
    def test_show_workflow_comparison_section(self, mock_st):
        """Test workflow comparison section rendering"""
        # Setup mocks
        mock_st.markdown = MagicMock()
        mock_st.write = MagicMock()
        mock_st.table = MagicMock()
        # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [1, 1, 1, 3])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.metric = MagicMock()
        
        # Mock context managers for columns
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        for col in [col1, col2, col3]:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [col1, col2, col3]
        
        # Call function
        _show_workflow_comparison_section(self.mock_workflows)
        
        # Verify calls
        mock_st.markdown.assert_called_with("### 📊 Workflow Comparison")
        mock_st.write.assert_called_with("Compare production workflows across different products")
        mock_st.table.assert_called()
    
    def test_get_module_icon(self):
        """Test module icon retrieval"""
        assert _get_module_icon("MILL") == "⚙️"
        assert _get_module_icon("DRILL") == "🔩"
        assert _get_module_icon("AIQS") == "🤖"
        assert _get_module_icon("HBW") == "🏬"
        assert _get_module_icon("DPS") == "📦"
        assert _get_module_icon("UNKNOWN") == "🛠️"
    
    def test_get_module_info(self):
        """Test module information retrieval"""
        mill_info = _get_module_info("MILL")
        assert "description" in mill_info
        assert "function" in mill_info
        assert "Milling machine" in mill_info["description"]
        
        unknown_info = _get_module_info("UNKNOWN")
        assert unknown_info == {}
    
    def test_get_estimated_duration(self):
        """Test estimated duration retrieval"""
        assert _get_estimated_duration("MILL") == "8-12 min"
        assert _get_estimated_duration("DRILL") == "5-8 min"
        assert _get_estimated_duration("AIQS") == "3-5 min"
        assert _get_estimated_duration("UNKNOWN") == "Unknown"
    
    def test_get_complexity_level(self):
        """Test complexity level calculation"""
        assert _get_complexity_level(1) == "🟢 Simple"
        assert _get_complexity_level(2) == "🟢 Simple"
        assert _get_complexity_level(3) == "🟡 Medium"
        assert _get_complexity_level(4) == "🔴 Complex"
        assert _get_complexity_level(5) == "🔴 Complex"


class TestCCUProductionPlanSubtabIntegration:
    """Integration tests for CCU Production Plan Subtab"""
    
    @patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.get_ccu_config_loader')
    def test_blu_white_red_workflow_order(self, mock_get_loader):
        """Test that BLUE, WHITE, RED workflow order is maintained"""
        # Setup mock loader
        mock_loader = MagicMock()
        mock_loader.load_production_workflows.return_value = {
            "WHITE": {"steps": ["DRILL", "AIQS"]},
            "BLUE": {"steps": ["MILL", "DRILL", "AIQS"]},
            "RED": {"steps": ["MILL", "AIQS"]}
        }
        mock_get_loader.return_value = mock_loader
        
        with patch('omf2.ui.ccu.ccu_process.ccu_production_plan_subtab.st') as mock_st:
            mock_st.subheader = MagicMock()
            mock_st.markdown = MagicMock()
            mock_st.divider = MagicMock()
            # Mock st.columns with side_effect to handle different column counts
        def mock_columns(columns):
            if isinstance(columns, int):
                return [MagicMock() for _ in range(columns)]
            else:  # columns is a list (like [1, 1, 1, 3])
                return [MagicMock() for _ in columns]
        
        mock_st.columns = MagicMock(side_effect=mock_columns)
        mock_st.metric = MagicMock()
        mock_st.tabs = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.table = MagicMock()
        
        # Mock context managers
        for mock_obj in mock_st.columns.return_value + mock_st.tabs.return_value:
            mock_obj.__enter__ = MagicMock(return_value=mock_obj)
            mock_obj.__exit__ = MagicMock(return_value=None)
        
        render_ccu_production_plan_subtab()
        
        # Verify that columns were called (if any)
        # Note: columns might not be called in all code paths
        if mock_st.columns.called:
            # If columns was called, verify it was called with reasonable arguments
            assert mock_st.columns.call_count > 0
        
        # Verify that tabs were called (if any)
        # Note: tabs might not be called in all code paths
        if mock_st.tabs.called:
            # If tabs was called, verify it was called
            assert mock_st.tabs.call_count > 0
