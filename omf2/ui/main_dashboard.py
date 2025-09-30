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
            # Environment status removed - shown in sidebar instead
            pass
    
    def _render_environment_selector(self):
        """Render environment selector with radio buttons - EXACT like old dashboard"""
        current_env = st.session_state.get('current_environment', 'mock')
        
        # Environment options - EXACT like old dashboard
        env_options = ["live", "replay", "mock"]
        
        # Radio buttons - EXACT like old dashboard
        new_env = st.sidebar.radio(
            "Umgebung",  # EXACT German label like old dashboard
            env_options, 
            index=env_options.index(current_env) if current_env in env_options else 0,
            horizontal=True
        )
        
        # Handle environment switch - EXACT like old dashboard
        if new_env != current_env:
            self._handle_environment_switch(current_env, new_env)
    
    def _handle_environment_switch(self, old_env, new_env):
        """Handle environment switching - EXACT like old dashboard"""
        logger.info(f"🔄 ENV-SWITCH: Environment-Wechsel erkannt: '{old_env}' -> '{new_env}'")
        
        # Update session state - EXACT like old dashboard
        st.session_state['current_environment'] = new_env
        
        # Reconnect admin MQTT client with new environment using improved method
        if 'admin_mqtt_client' in st.session_state:
            admin_client = st.session_state['admin_mqtt_client']
            
            # Use the new reconnect_environment method for clean switching
            success = admin_client.reconnect_environment(new_env)
            
            if success:
                logger.info(f"✅ Admin MQTT Client reconnected to {new_env}")
            else:
                logger.warning(f"⚠️ Admin MQTT Client reconnection to {new_env} had issues, continuing anyway")
        
        # Clear cache - EXACT like old dashboard
        st.cache_resource.clear()
        logger.info(f"🔄 ENV-SWITCH: Cache geleert, Environment aktualisiert")
        
        # Use request_refresh instead of potential st.rerun calls
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
    
    def _render_sidebar(self):
        """Render sidebar with controls and status"""
        st.sidebar.title("🏭 OMF2 Control")
        
        # Environment selector (moved to sidebar)
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌍 Environment")
        self._render_environment_selector()
        
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
        """Render connection status in sidebar as collapsible element"""
        st.sidebar.markdown("---")
        
        # Check admin MQTT client status first to determine expander color
        admin_client = st.session_state.get('admin_mqtt_client')
        current_env = st.session_state.get('current_environment', 'mock')
        
        # Determine expander color based on connection status
        if admin_client:
            conn_info = admin_client.get_connection_info()
            if conn_info['connected']:
                expander_color = "🟢"  # Green for connected
            else:
                expander_color = "🔴"  # Red for disconnected
        else:
            expander_color = "🔴"  # Red for not initialized
        
        # Collapsible Connection Status with color-coded icon
        with st.sidebar.expander(f"{expander_color} Connection Status", expanded=False):
            if admin_client:
                # Get detailed connection info - UI liest IMMER aus session_state
                conn_info = admin_client.get_connection_info()
                
                # NO AUTO-CONNECT in UI - prevents connection loops
                # Connection is handled by main dashboard initialization
                
                # Display connection status with consistent formatting
                if conn_info['connected']:
                    if conn_info['mock_mode']:
                        status_icon = "🧪"
                        status_text = f"Mock Mode ({current_env})"
                        st.info(f"{status_icon} **Admin MQTT**: {status_text}")
                    else:
                        status_icon = "🟢"
                        status_text = f"Connected ({current_env})"
                        st.success(f"{status_icon} **Admin MQTT**: {status_text}")
                else:
                    status_icon = "🔴"
                    status_text = f"Disconnected ({current_env})"
                    st.error(f"{status_icon} **Admin MQTT**: {status_text}")
                
                # Show Broker and Client ID with same formatting as MQTT status
                host_port = f"{conn_info['host']}:{conn_info['port']}"
                st.info(f"🌐 **Broker**: `{host_port}`")
                
                client_id = conn_info.get('client_id', f'omf_{current_env}')
                st.info(f"🆔 **Client ID**: `{client_id}`")
                
            else:
                st.warning("Admin MQTT client not initialized")
                st.info("🆔 **Client ID**: Noch nicht initialisiert")
                
            # Show environment-specific info
            if current_env == 'mock':
                st.info("🧪 Mock mode - No real MQTT connection")
            elif current_env == 'live':
                st.success("🟢 Live mode - Real MQTT connection")
            elif current_env == 'replay':
                st.warning("🔄 Replay mode - Historical data")
    
    def _render_main_content(self):
        """Render main content area with tabs"""
        # Get tab configuration based on user role
        tab_config = self.user_manager.get_tab_config()
        
        # Log tab configuration only once per session
        if "tab_config_logged" not in st.session_state:
            logger.info(f"📋 Tab configuration: {tab_config}")
            logger.info(f"📋 Available tabs: {list(tab_config.keys()) if tab_config else 'None'}")
            st.session_state["tab_config_logged"] = True
        
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
        if "tabs_created" not in st.session_state:
            logger.info(f"📑 Creating {len(tab_keys)} tabs: {tab_keys}")
            st.session_state["tabs_created"] = True
        tabs = st.tabs(tab_labels)
        
        # Render tab content
        for i, tab_key in enumerate(tab_keys):
            with tabs[i]:
                # Only log tab rendering on first render
                if f"tab_{tab_key}_rendered" not in st.session_state:
                    logger.info(f"📋 Rendering tab {i+1}/{len(tab_keys)}: {tab_key}")
                    st.session_state[f"tab_{tab_key}_rendered"] = True
                self._render_tab_content(tab_key, tab_config[tab_key])
    
    def _render_tab_content(self, tab_key: str, tab_config: Dict[str, Any]):
        """Render content for a specific tab"""
        try:
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
                    # Only log component loading once
                    if f"component_{tab_key}_loaded" not in st.session_state:
                        logger.info(f"✅ Loaded component: {tab_key}")
                        st.session_state[f"component_{tab_key}_loaded"] = True
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