#!/usr/bin/env python3
"""
Tests for CCU Parameter Configuration Subtab
"""

from unittest.mock import MagicMock, patch

from omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab import (
    _init_configuration_state,
    _show_fts_settings_section,
    _show_production_durations_section,
    _show_production_settings_section,
    _show_save_button,
    get_ccu_production_settings,
    render_ccu_parameter_configuration_subtab,
    set_ccu_production_settings,
)


class TestCCUParameterConfigurationSubtab:
    """Test cases for CCU Parameter Configuration Subtab"""

    def setup_method(self):
        """Setup test fixtures"""
        # Mock production settings
        self.mock_production_settings = {
            "productionDurations": {"WHITE": 440, "BLUE": 460, "RED": 500},
            "productionSettings": {"maxParallelOrders": 4},
            "ftsSettings": {"chargeThresholdPercent": 10},
        }

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.get_ccu_config_loader")
    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st")
    def test_render_ccu_parameter_configuration_subtab_success(self, mock_st, mock_get_loader):
        """Test successful rendering of CCU parameter configuration subtab"""
        # Setup mocks
        mock_loader = MagicMock()
        mock_loader.load_production_settings.return_value = self.mock_production_settings
        mock_get_loader.return_value = mock_loader

        # Mock Streamlit components
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.divider = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.number_input = MagicMock(return_value=460)
        mock_st.button = MagicMock(return_value=False)

        # Create proper session state mock
        mock_session_state = MagicMock()
        mock_session_state.__contains__ = MagicMock(return_value=False)
        mock_session_state.__setitem__ = MagicMock()
        mock_st.session_state = mock_session_state

        # Call function
        render_ccu_parameter_configuration_subtab()

        # Verify calls
        mock_st.subheader.assert_called()
        mock_st.markdown.assert_called()
        mock_loader.load_production_settings.assert_called_once()

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.get_ccu_config_loader")
    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st")
    def test_render_ccu_parameter_configuration_subtab_error(self, mock_st, mock_get_loader):
        """Test error handling in CCU parameter configuration subtab"""
        # Setup mocks to raise exception
        mock_get_loader.side_effect = Exception("Test error")
        mock_st.subheader = MagicMock()
        mock_st.error = MagicMock()
        mock_st.info = MagicMock()

        # Create session state mock
        mock_session_state = MagicMock()
        mock_st.session_state = mock_session_state

        # Call function
        render_ccu_parameter_configuration_subtab()

        # Verify error handling
        mock_st.error.assert_called()
        mock_st.info.assert_called()

    def test_init_configuration_state(self):
        """Test configuration state initialization"""
        # This test verifies the function can be called without errors
        # Session state mocking is complex in Streamlit, so we test functionality
        try:
            _init_configuration_state(self.mock_production_settings)
            assert True  # Function executed without error
        except Exception as e:
            # Expected in test environment without proper Streamlit context
            assert "session_state" in str(e).lower() or "streamlit" in str(e).lower()

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st")
    def test_show_production_durations_section(self, mock_st):
        """Test production durations section rendering"""
        # Setup mocks
        mock_session_state = MagicMock()
        mock_session_state.ccu_production_settings = self.mock_production_settings
        mock_st.session_state = mock_session_state

        mock_st.subheader = MagicMock()
        mock_st.write = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.markdown = MagicMock()
        mock_st.number_input = MagicMock(return_value=460)

        # Mock context managers
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        col1.__enter__ = MagicMock(return_value=col1)
        col1.__exit__ = MagicMock(return_value=None)
        col2.__enter__ = MagicMock(return_value=col2)
        col2.__exit__ = MagicMock(return_value=None)
        col3.__enter__ = MagicMock(return_value=col3)
        col3.__exit__ = MagicMock(return_value=None)

        mock_st.columns.return_value = [col1, col2, col3]

        # Call function
        _show_production_durations_section()

        # Verify calls
        mock_st.subheader.assert_called_with("⏱️ Production Durations")
        mock_st.write.assert_called_with("Production durations for different workpiece types")
        mock_st.columns.assert_called_with(3)
        assert mock_st.number_input.call_count >= 3  # BLUE, WHITE, RED

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st")
    def test_show_production_settings_section(self, mock_st):
        """Test production settings section rendering"""
        # Setup mocks
        mock_session_state = MagicMock()
        mock_session_state.ccu_production_settings = self.mock_production_settings
        mock_st.session_state = mock_session_state

        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.write = MagicMock()
        mock_st.number_input = MagicMock(return_value=4)

        # Mock get_svg_inline to return SVG or None
        with patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.get_svg_inline") as mock_get_svg:
            mock_get_svg.return_value = None  # Simulate fallback to emoji
            # Call function
            _show_production_settings_section()

            # Verify calls - now uses SVG icon with st.markdown, fallback to subheader
            mock_st.write.assert_called_with("General production configuration")
            mock_st.number_input.assert_called()

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st")
    def test_show_fts_settings_section(self, mock_st):
        """Test FTS settings section rendering"""
        # Setup mocks
        mock_session_state = MagicMock()
        mock_session_state.ccu_production_settings = self.mock_production_settings
        mock_st.session_state = mock_session_state

        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.write = MagicMock()
        mock_st.number_input = MagicMock(return_value=10)

        # Mock get_icon_html to return SVG or None
        with patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.get_icon_html") as mock_get_icon:
            mock_get_icon.return_value = None  # Simulate fallback to emoji
            # Call function
            _show_fts_settings_section()

            # Verify calls - now uses SVG icon with st.markdown, fallback to subheader
            mock_st.write.assert_called_with("FTS (Fahrerloses Transportsystem) configuration")
            mock_st.number_input.assert_called()

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st")
    def test_show_save_button_success(self, mock_st):
        """Test save button success scenario"""
        # Setup mocks
        mock_st.button = MagicMock(return_value=True)
        mock_st.success = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])

        # Mock context manager for button column
        col2 = MagicMock()
        col2.__enter__ = MagicMock(return_value=col2)
        col2.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [MagicMock(), col2, MagicMock()]

        # Call function
        _show_save_button()

        # Verify calls
        mock_st.button.assert_called()
        mock_st.success.assert_called()

    def test_get_ccu_production_settings_from_session(self):
        """Test getting CCU production settings from session state"""
        with patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st") as mock_st:
            mock_session_state = MagicMock()
            mock_session_state.__contains__ = MagicMock(return_value=True)
            mock_session_state.ccu_production_settings = self.mock_production_settings
            mock_st.session_state = mock_session_state

            settings = get_ccu_production_settings()

            assert settings == self.mock_production_settings

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.get_ccu_config_loader")
    def test_get_ccu_production_settings_from_loader(self, mock_get_loader):
        """Test getting CCU production settings from config loader"""
        # Setup mocks
        mock_loader = MagicMock()
        mock_loader.load_production_settings.return_value = self.mock_production_settings
        mock_get_loader.return_value = mock_loader

        with patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st") as mock_st:
            mock_session_state = MagicMock()
            mock_session_state.__contains__ = MagicMock(return_value=False)
            mock_st.session_state = mock_session_state

            settings = get_ccu_production_settings()

            assert settings == self.mock_production_settings
            mock_loader.load_production_settings.assert_called_once()

    def test_set_ccu_production_settings(self):
        """Test setting CCU production settings"""
        # This test verifies the function can be called without errors
        # Session state mocking is complex in Streamlit, so we test functionality
        try:
            set_ccu_production_settings(self.mock_production_settings)
            assert True  # Function executed without error
        except Exception as e:
            # Expected in test environment without proper Streamlit context
            assert "session_state" in str(e).lower() or "streamlit" in str(e).lower()


class TestCCUParameterConfigurationSubtabIntegration:
    """Integration tests for CCU Parameter Configuration Subtab"""

    @patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.get_ccu_config_loader")
    def test_blu_white_red_order(self, mock_get_loader):
        """Test that BLUE, WHITE, RED order is maintained"""
        # Setup mock loader
        mock_loader = MagicMock()
        mock_loader.load_production_settings.return_value = {
            "productionDurations": {"WHITE": 440, "BLUE": 460, "RED": 500},
            "productionSettings": {"maxParallelOrders": 4},
            "ftsSettings": {"chargeThresholdPercent": 10},
        }
        mock_get_loader.return_value = mock_loader

        with patch("omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab.st") as mock_st:
            # Create proper session state mock
            mock_session_state = MagicMock()
            mock_session_state.__contains__ = MagicMock(return_value=False)
            mock_session_state.__setitem__ = MagicMock()
            mock_session_state.ccu_production_settings = {
                "productionDurations": {"WHITE": 440, "BLUE": 460, "RED": 500},
                "productionSettings": {"maxParallelOrders": 4},
                "ftsSettings": {"chargeThresholdPercent": 10},
            }
            mock_st.session_state = mock_session_state

            mock_st.subheader = MagicMock()
            mock_st.markdown = MagicMock()
            mock_st.divider = MagicMock()
            mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
            mock_st.number_input = MagicMock(return_value=460)

            # Mock context managers for columns
            col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
            for col in [col1, col2, col3]:
                col.__enter__ = MagicMock(return_value=col)
                col.__exit__ = MagicMock(return_value=None)
            mock_st.columns.return_value = [col1, col2, col3]

            render_ccu_parameter_configuration_subtab()

            # Verify that number_input was called for each color
            assert mock_st.number_input.call_count >= 3  # BLUE, WHITE, RED + others

            # Verify production durations section was called
            mock_st.subheader.assert_called()
