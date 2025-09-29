"""
Main Dashboard UI for OMF2
Central dashboard component that orchestrates the entire UI
"""

import streamlit as st
from typing import Dict, Any, Optional
import importlib

from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh
from omf2.ui.user_manager import UserManager

logger = get_logger(__name__)


class MainDashboard:
    """Main dashboard controller for OMF2"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self._loaded_components = {}
    
    def render(self):
        """Render the main dashboard"""
        try:
            # Render header
            self._render_header()
            
            # Render sidebar
            self._render_sidebar()
            
            # Render main content area with tabs
            self._render_main_content()
            
        except Exception as e:
            logger.error(f"❌ Dashboard rendering error: {e}")
            st.error(f"❌ Dashboard rendering failed: {e}")
    
    def _render_header(self):
        """Render dashboard header"""
        # Get i18n manager from session state
        i18n = st.session_state.get('i18n_manager')
        
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.markdown("# 🏭 OMF2 Dashboard")
        
        with col2:
            if i18n:
                subtitle = i18n.translate('dashboard.subtitle')
                st.markdown(f"## {subtitle}")
            else:
                st.markdown("## ORBIS Modellfabrik Control")
        
        with col3:
            self._render_environment_selector()
    
    def _render_environment_selector(self):
        """Render environment selector"""
        current_env = st.session_state.get('current_environment', 'mock')
        
        environments = ['live', 'replay', 'mock']
        env_descriptions = {
            'live': '🟢 Live - Real-time MQTT connection',
            'replay': '🔄 Replay - Historical data playback',
            'mock': '🧪 Mock - Simulated data for testing'
        }
        
        new_env = st.selectbox(
            "Environment:",
            environments,
            index=environments.index(current_env) if current_env in environments else 0,
            key="env_selector",
            format_func=lambda x: env_descriptions[x]
        )
        
        if new_env != current_env:
            st.session_state['current_environment'] = new_env
            logger.info(f"🌍 Environment changed to: {new_env}")
            request_refresh()
    
    def _render_sidebar(self):
        """Render sidebar with controls and status"""
        st.sidebar.title("🏭 OMF2 Control")
        
        # Language selector  
        self._render_language_selector()
        
        # User role management
        self.user_manager.render_role_selector()
        
        # Connection status
        self._render_connection_status()
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Dashboard"):
            request_refresh()
    
    def _render_language_selector(self):
        """Render language selector in sidebar"""
        i18n = st.session_state.get('i18n_manager')
        if not i18n:
            return
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌐 Language")
        
        current_lang = i18n.get_current_language()
        languages = i18n.get_supported_languages()
        
        # Language selector with display names
        lang_options = {lang: i18n.get_language_display_name(lang) for lang in languages}
        
        new_lang = st.sidebar.selectbox(
            "Select Language:",
            languages,
            index=languages.index(current_lang) if current_lang in languages else 0,
            format_func=lambda x: lang_options[x]
        )
        
        if new_lang != current_lang:
            i18n.set_language(new_lang)
            st.session_state['current_language'] = new_lang
            logger.info(f"🌐 Language changed to: {new_lang}")
            request_refresh()
    
    def _render_connection_status(self):
        """Render connection status in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 Connection Status")
        
        # Get client factory from session state
        client_factory = st.session_state.get('client_factory')
        
        if client_factory:
            client_status = client_factory.get_client_status()
            
            if client_status:
                for client_name, is_connected in client_status.items():
                    status_icon = "🟢" if is_connected else "🔴"
                    status_text = "Connected" if is_connected else "Disconnected"
                    st.sidebar.write(f"{status_icon} **{client_name}**: {status_text}")
            else:
                st.sidebar.info("No active clients")
        else:
            st.sidebar.warning("Client factory not initialized")
    
    def _render_main_content(self):
        """Render main content area with tabs"""
        # Get tab configuration based on user role
        tab_config = self.user_manager.get_tab_config()
        
        logger.info(f"📋 Tab configuration: {tab_config}")
        logger.info(f"📋 Available tabs: {list(tab_config.keys()) if tab_config else 'None'}")
        
        if not tab_config:
            st.warning("⚠️ No tabs available for your current role")
            self.user_manager.render_permissions_info()
            return
        
        # Create tab labels with icons
        tab_labels = []
        tab_keys = list(tab_config.keys())
        
        for tab_key in tab_keys:
            tab_info = tab_config[tab_key]
            icon = tab_info.get('icon', '📋')
            name = tab_info.get('name', tab_key)
            tab_labels.append(f"{icon} {name}")
        
        # Create tabs
        logger.info(f"📑 Creating {len(tab_keys)} tabs: {tab_keys}")
        tabs = st.tabs(tab_labels)
        
        # Render tab content
        for i, tab_key in enumerate(tab_keys):
            with tabs[i]:
                logger.info(f"📋 Rendering tab {i+1}/{len(tab_keys)}: {tab_key}")
                self._render_tab_content(tab_key, tab_config[tab_key])
    
    def _render_tab_content(self, tab_key: str, tab_config: Dict[str, Any]):
        """Render content for a specific tab"""
        try:
            # Log tab navigation
            logger.info(f"🔄 Rendering tab: {tab_key}")
            
            # Check if component is already loaded
            if tab_key not in self._loaded_components:
                module_name = tab_config.get('module')
                function_name = tab_config.get('function')
                
                if not module_name or not function_name:
                    self._render_dummy_tab(tab_key, "Configuration missing")
                    return
                
                # Try to import and load the component
                try:
                    module = importlib.import_module(module_name)
                    component_function = getattr(module, function_name)
                    self._loaded_components[tab_key] = component_function
                    logger.info(f"✅ Loaded component: {tab_key}")
                except (ImportError, AttributeError) as e:
                    logger.warning(f"⚠️ Failed to load component {tab_key}: {e}")
                    error_msg = str(e)
                    self._loaded_components[tab_key] = lambda: self._render_dummy_tab(tab_key, error_msg)
            
            # Render the component
            component_function = self._loaded_components[tab_key]
            component_function()
            
        except Exception as e:
            logger.error(f"❌ Error rendering tab {tab_key}: {e}")
            self._render_dummy_tab(tab_key, f"Rendering error: {e}")
    
    def _render_dummy_tab(self, tab_name: str, error_message: str = ""):
        """Render a dummy tab for unavailable components"""
        st.warning(f"⚠️ Component '{tab_name}' is not available")
        
        if error_message:
            with st.expander("Error Details", expanded=False):
                st.code(error_message)
        
        st.info("💡 This component is currently under development or not properly configured.")
        
        # Show some placeholder content
        st.markdown("### 🚧 Coming Soon")
        st.markdown(f"The **{tab_name}** component will be available in a future release.")
        
        # Add some example metrics for demonstration
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "Under Development", "⚠️")
        with col2:
            st.metric("Progress", "0%", "🔧")
        with col3:
            st.metric("ETA", "TBD", "📅")
    
    def get_user_manager(self) -> UserManager:
        """Get the user manager instance"""
        return self.user_manager