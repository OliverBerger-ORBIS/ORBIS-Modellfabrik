"""
Tests for OMF2 Streamlit Dashboard
Basic smoke tests to ensure components load correctly
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestOMF2Dashboard:
    """Test suite for OMF2 Streamlit Dashboard"""
    
    def test_dashboard_imports(self):
        """Test that dashboard modules can be imported"""
        # Test main dashboard
        from omf2.ui.main_dashboard import MainDashboard
        from omf2.ui.user_manager import UserManager
        
        dashboard = MainDashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'render')
        
        user_manager = UserManager()
        assert user_manager is not None
    
    def test_common_modules_import(self):
        """Test that common modules can be imported"""
        from omf2.common.logger import get_logger
        from omf2.common.i18n import I18nManager
        
        logger = get_logger("test")
        assert logger is not None
        
        i18n = I18nManager()
        assert i18n is not None
        assert "de" in i18n.get_supported_languages()
    
    def test_factory_modules_import(self):
        """Test that factory modules can be imported"""
        from omf2.factory.client_factory import ClientFactory
        
        factory = ClientFactory()
        assert factory is not None
    
    def test_ui_modules_import(self):
        """Test that UI modules can be imported"""  
        from omf2.ui.user_manager import UserManager
        from omf2.ui.main_dashboard import MainDashboard
        
        user_manager = UserManager()
        assert user_manager is not None
        
        dashboard = MainDashboard()
        assert dashboard is not None
    
    def test_ui_components_import(self):
        """Test that UI components can be imported"""
        from omf2.ui.ccu.ccu_overview.ccu_overview_tab import render_ccu_overview_tab
        from omf2.ui.admin.logs.logs_tab import render_logs_tab
        
        assert callable(render_ccu_overview_tab)
        assert callable(render_logs_tab)
    
    def test_i18n_translations(self):
        """Test internationalization functionality"""
        from omf2.common.i18n import I18nManager
        
        i18n = I18nManager()
        
        # Test German translations
        i18n.set_language('de')
        assert i18n.translate('dashboard.title') == 'OMF2 Dashboard'
        assert i18n.translate('roles.admin') == 'Administrator'
        
        # Test English translations
        i18n.set_language('en')
        assert i18n.translate('dashboard.title') == 'OMF2 Dashboard'
        assert i18n.translate('roles.admin') == 'Administrator'
        
        # Test French translations
        i18n.set_language('fr')
        assert i18n.translate('dashboard.title') == 'Tableau de bord OMF2'
        assert i18n.translate('roles.admin') == 'Administrateur'
    
    def test_user_manager_roles(self):
        """Test user manager role functionality"""
        from omf2.ui.user_manager import UserManager
        
        user_manager = UserManager()
        
        # Test available roles
        roles = user_manager.get_available_roles()
        assert 'administrator' in roles
        assert 'supervisor' in roles
        assert 'operator' in roles
        
        # Test role permissions
        admin_components = user_manager.get_role_ui_components('administrator')
        supervisor_components = user_manager.get_role_ui_components('supervisor')
        operator_components = user_manager.get_role_ui_components('operator')
        
        assert len(admin_components) > len(supervisor_components)
        # Supervisor and operator have different but equal number of components
        assert len(supervisor_components) >= len(operator_components)
        assert 'ccu_dashboard' in admin_components
        assert 'ccu_dashboard' in supervisor_components
        assert 'ccu_dashboard' in operator_components
    
    def test_tab_configuration(self):
        """Test tab configuration based on roles"""
        from omf2.ui.user_manager import UserManager
        
        user_manager = UserManager()
        
        # Set role to administrator and get tab config
        user_manager.set_user_role('administrator')
        admin_tabs = user_manager.get_tab_config()
        
        # Set role to supervisor and get tab config
        user_manager.set_user_role('supervisor')
        supervisor_tabs = user_manager.get_tab_config()
        
        # Set role to operator and get tab config
        user_manager.set_user_role('operator')
        operator_tabs = user_manager.get_tab_config()
        
        # Administrator should have more tabs than supervisor and operator
        assert len(admin_tabs) > len(supervisor_tabs)
        assert len(admin_tabs) > len(operator_tabs)
        
        # All should have CCU dashboard
        assert 'ccu_dashboard' in admin_tabs
        assert 'ccu_dashboard' in supervisor_tabs
        assert 'ccu_dashboard' in operator_tabs
        
        # Only administrator should have admin settings
        if 'admin_settings' in admin_tabs:
            assert 'admin_settings' not in supervisor_tabs
            assert 'admin_settings' not in operator_tabs


class TestOMF2ComponentsIntegration:
    """Integration tests for OMF2 components"""
    
    @patch('streamlit.session_state', {})
    def test_session_state_initialization(self):
        """Test session state initialization"""
        from omf2.ui.user_manager import UserManager
        
        # Mock streamlit session_state
        mock_session_state = {}
        
        with patch('streamlit.session_state', mock_session_state):
            user_manager = UserManager()
            
            # Check default values are set
            assert user_manager.get_available_roles() is not None
            assert len(user_manager.get_available_roles()) > 0
    
    def test_client_factory_config_loading(self):
        """Test client factory configuration loading"""
        from omf2.factory.client_factory import ClientFactory
        
        factory = ClientFactory()
        
        # Should have default config even if no config file exists
        assert factory._config is not None
        # The config structure may vary, just check it's not empty
        assert len(factory._config) > 0
    
    def test_logger_functionality(self):
        """Test logging functionality"""
        from omf2.common.logger import get_logger
        
        logger = get_logger("test_logger")
        
        # Should return a logger instance
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        
        # Test logging (should not raise errors)
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")


@pytest.fixture
def mock_streamlit():
    """Mock streamlit for testing"""
    with patch('streamlit.set_page_config'), \
         patch('streamlit.session_state', {}), \
         patch('streamlit.header'), \
         patch('streamlit.markdown'), \
         patch('streamlit.tabs'), \
         patch('streamlit.columns'):
        yield


class TestOMF2UI:
    """UI component tests"""
    
    def test_main_dashboard_creation(self, mock_streamlit):
        """Test main dashboard can be created"""
        from omf2.ui.main_dashboard import MainDashboard
        
        dashboard = MainDashboard()
        assert dashboard is not None
        assert hasattr(dashboard, 'render')
        assert hasattr(dashboard, 'user_manager')
    
    def test_user_manager_permissions(self):
        """Test user manager permission system"""
        from omf2.ui.user_manager import UserManager
        
        user_manager = UserManager()
        
        # Test administrator permissions
        user_manager.set_user_role('administrator')
        assert user_manager.has_permission('admin:read')
        assert user_manager.has_permission('admin:write')
        assert user_manager.can_access_component('admin_settings')
        
        # Test supervisor permissions
        user_manager.set_user_role('supervisor')
        assert user_manager.has_permission('control:read')
        assert user_manager.has_permission('control:write')
        assert not user_manager.can_access_component('admin_settings')
        
        # Test operator permissions
        user_manager.set_user_role('operator')
        assert user_manager.has_permission('dashboard:read')
        assert not user_manager.has_permission('admin:read')
        assert not user_manager.can_access_component('admin_settings')