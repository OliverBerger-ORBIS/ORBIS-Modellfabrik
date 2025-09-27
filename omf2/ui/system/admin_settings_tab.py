#!/usr/bin/env python3
"""
Admin Settings Tab - UI component for system administration
"""

import logging
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from omf2.system import AdminSettings

logger = logging.getLogger(__name__)


class AdminSettingsTab:
    """
    Admin Settings Tab - System administration interface
    """
    
    def __init__(self):
        self.admin_settings = AdminSettings()
        logger.info("⚙️ Admin Settings Tab initialized")
    
    def render(self):
        """Render the admin settings tab"""
        if not STREAMLIT_AVAILABLE:
            logger.error("Streamlit not available for UI rendering")
            return
        
        st.header("⚙️ Admin Settings")
        st.markdown("System administration and configuration management")
        
        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔌 MQTT Settings", 
            "👥 User Roles", 
            "📱 Apps Config",
            "📊 System Info"
        ])
        
        with tab1:
            self._render_mqtt_settings()
        
        with tab2:
            self._render_user_roles()
        
        with tab3:
            self._render_apps_config()
        
        with tab4:
            self._render_system_info()
    
    def _render_mqtt_settings(self):
        """Render MQTT settings configuration"""
        st.subheader("🔌 MQTT Configuration")
        
        mqtt_settings = self.admin_settings.load_mqtt_settings()
        
        # Environment selection
        st.write("**Environment Selection:**")
        environments = mqtt_settings.get("environments", {})
        available_envs = [env for env, config in environments.items() if config.get("enabled", True)]
        
        current_default = mqtt_settings.get("default_environment", "replay")
        
        default_env = st.selectbox(
            "Default Environment",
            available_envs,
            index=available_envs.index(current_default) if current_default in available_envs else 0
        )
        
        # Environment configuration
        st.write("**Environment Configurations:**")
        
        updated_environments = {}
        for env_name, env_config in environments.items():
            with st.expander(f"{env_name.title()} Environment"):
                col1, col2 = st.columns(2)
                
                with col1:
                    enabled = st.checkbox(
                        "Enabled",
                        value=env_config.get("enabled", True),
                        key=f"env_{env_name}_enabled"
                    )
                    host = st.text_input(
                        "Host",
                        value=env_config.get("host", "localhost"),
                        key=f"env_{env_name}_host"
                    )
                    port = st.number_input(
                        "Port",
                        value=env_config.get("port", 1883),
                        min_value=1,
                        max_value=65535,
                        key=f"env_{env_name}_port"
                    )
                
                with col2:
                    username = st.text_input(
                        "Username",
                        value=env_config.get("username", ""),
                        key=f"env_{env_name}_username"
                    )
                    password = st.text_input(
                        "Password",
                        value=env_config.get("password", ""),
                        type="password",
                        key=f"env_{env_name}_password"
                    )
                    client_id_prefix = st.text_input(
                        "Client ID Prefix",
                        value=env_config.get("client_id_prefix", f"omf2_{env_name}"),
                        key=f"env_{env_name}_client_id"
                    )
                
                updated_environments[env_name] = {
                    "enabled": enabled,
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                    "client_id_prefix": client_id_prefix,
                    "description": env_config.get("description", ""),
                    "tls": env_config.get("tls", False),
                    "keepalive": env_config.get("keepalive", 60),
                    "clean_session": env_config.get("clean_session", True)
                }
        
        # Global settings
        st.write("**Global Settings:**")
        col1, col2 = st.columns(2)
        
        with col1:
            connection_timeout = st.number_input(
                "Connection Timeout (seconds)",
                value=mqtt_settings.get("connection_timeout", 60),
                min_value=5,
                max_value=300
            )
            keepalive = st.number_input(
                "Keepalive (seconds)",
                value=mqtt_settings.get("keepalive", 60),
                min_value=10,
                max_value=300
            )
        
        with col2:
            qos_default = st.selectbox(
                "Default QoS",
                [0, 1, 2],
                index=mqtt_settings.get("qos_default", 1)
            )
            buffer_size = st.number_input(
                "Buffer Size",
                value=mqtt_settings.get("buffer_size", 1000),
                min_value=100,
                max_value=10000
            )
        
        # Save button
        if st.button("💾 Save MQTT Settings"):
            new_settings = {
                "environments": updated_environments,
                "default_environment": default_env,
                "connection_timeout": connection_timeout,
                "keepalive": keepalive,
                "qos_default": qos_default,
                "buffer_size": buffer_size
            }
            
            if self.admin_settings.save_mqtt_settings(new_settings):
                st.success("✅ MQTT settings saved successfully")
            else:
                st.error("❌ Failed to save MQTT settings")
    
    def _render_user_roles(self):
        """Render user roles configuration"""
        st.subheader("👥 User Roles & Permissions")
        
        user_roles = self.admin_settings.load_user_roles()
        
        # Roles configuration
        st.write("**Role Definitions:**")
        roles = user_roles.get("roles", {})
        
        for role_name, role_config in roles.items():
            with st.expander(f"{role_config.get('name', role_name)} ({role_name})"):
                st.write(f"**Description:** {role_config.get('description', 'No description')}")
                st.write(f"**Permissions:** {', '.join(role_config.get('permissions', []))}")
                
                ui_components = role_config.get('ui_components', [])
                if ui_components:
                    st.write(f"**UI Components:** {', '.join(ui_components)}")
        
        # Users configuration
        st.write("**User Assignments:**")
        users = user_roles.get("users", {})
        
        user_data = []
        for username, user_config in users.items():
            user_data.append({
                "Username": username,
                "Name": user_config.get("name", ""),
                "Role": user_config.get("role", ""),
                "Active": "✅" if user_config.get("active", False) else "❌",
                "Email": user_config.get("email", "")
            })
        
        if user_data:
            st.dataframe(user_data, use_container_width=True)
        else:
            st.info("No users configured")
        
        # Add new user
        with st.expander("➕ Add New User"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username")
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email")
            
            with col2:
                new_role = st.selectbox(
                    "Role",
                    list(roles.keys()),
                    key="new_user_role"
                )
                new_active = st.checkbox("Active", value=True)
            
            if st.button("➕ Add User") and new_username:
                users[new_username] = {
                    "name": new_name,
                    "email": new_email,
                    "role": new_role,
                    "active": new_active,
                    "created_at": st.session_state.get("current_time", "2024-01-01T00:00:00Z")
                }
                
                updated_config = user_roles.copy()
                updated_config["users"] = users
                
                if self.admin_settings.save_user_roles(updated_config):
                    st.success(f"✅ User {new_username} added successfully")
                    st.rerun()
                else:
                    st.error("❌ Failed to add user")
    
    def _render_apps_config(self):
        """Render apps configuration"""
        st.subheader("📱 Apps Configuration")
        
        apps_config = self.admin_settings.load_apps_config()
        apps = apps_config.get("apps", {})
        
        # Apps overview
        st.write("**Available Apps:**")
        
        for app_id, app_config in apps.items():
            with st.expander(f"{app_config.get('icon', '📱')} {app_config.get('name', app_id)}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Description:** {app_config.get('description', 'No description')}")
                    st.write(f"**Category:** {app_config.get('category', 'Unknown')}")
                    st.write(f"**Module:** `{app_config.get('module', 'Unknown')}`")
                
                with col2:
                    enabled = app_config.get("enabled", True)
                    status = "🟢 Enabled" if enabled else "🔴 Disabled"
                    st.write(f"**Status:** {status}")
                    
                    required_permissions = app_config.get("required_permissions", [])
                    if required_permissions:
                        st.write(f"**Required Permissions:** {', '.join(required_permissions)}")
                    
                    required_role = app_config.get("required_role")
                    if required_role:
                        st.write(f"**Required Role:** {required_role}")
        
        # Categories
        categories = apps_config.get("categories", {})
        if categories:
            st.write("**App Categories:**")
            for cat_id, cat_config in categories.items():
                st.write(f"• {cat_config.get('icon', '📁')} **{cat_config.get('name', cat_id)}**: {cat_config.get('description', '')}")
    
    def _render_system_info(self):
        """Render system information"""
        st.subheader("📊 System Information")
        
        # Environment info
        available_envs = self.admin_settings.get_available_environments()
        st.write(f"**Available Environments:** {', '.join(available_envs)}")
        
        # Statistics
        user_roles = self.admin_settings.load_user_roles()
        apps_config = self.admin_settings.load_apps_config()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(user_roles.get("users", {})))
        
        with col2:
            st.metric("Total Roles", len(user_roles.get("roles", {})))
        
        with col3:
            st.metric("Total Apps", len(apps_config.get("apps", {})))
        
        # Configuration files status
        st.write("**Configuration Files:**")
        config_files = [
            ("MQTT Settings", self.admin_settings.mqtt_settings_file),
            ("User Roles", self.admin_settings.user_roles_file),
            ("Apps Config", self.admin_settings.apps_file)
        ]
        
        for name, file_path in config_files:
            exists = file_path.exists()
            status = "✅ Exists" if exists else "❌ Missing"
            st.write(f"• **{name}**: {status} (`{file_path}`)")


def render_admin_settings_tab():
    """Convenience function to render admin settings tab"""
    tab = AdminSettingsTab()
    tab.render()