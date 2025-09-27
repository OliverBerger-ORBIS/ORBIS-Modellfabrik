"""
User and Role Management for OMF2 Dashboard
Manages user roles, permissions, and UI access based on omf2/config/user_roles.yml
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml
import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)


class UserManager:
    """Manages user roles and permissions for OMF2 Dashboard"""
    
    def __init__(self):
        self._roles_config = self._load_roles_config()
        self._current_user = None
    
    def _load_roles_config(self) -> Dict:
        """Load user roles configuration from YAML"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "user_roles.yml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    logger.info("✅ User roles configuration loaded")
                    return config
            else:
                logger.warning(f"⚠️ Roles config file not found: {config_path}")
                return self._get_default_roles_config()
        except Exception as e:
            logger.error(f"❌ Failed to load roles config: {e}")
            return self._get_default_roles_config()
    
    def _get_default_roles_config(self) -> Dict:
        """Get default roles configuration"""
        return {
            'roles': {
                'admin': {
                    'name': 'Administrator',
                    'permissions': ['*'],
                    'ui_components': ['ccu_dashboard', 'message_center', 'system_logs', 'admin_settings', 'steering_factory'],
                    'color': '#FF4B4B'
                },
                'supervisor': {
                    'name': 'Supervisor', 
                    'permissions': ['read', 'control', 'manage_workflows'],
                    'ui_components': ['ccu_dashboard', 'message_center', 'system_logs', 'steering_factory'],
                    'color': '#FF8C00'
                },
                'operator': {
                    'name': 'Operator',
                    'permissions': ['read', 'control'],
                    'ui_components': ['ccu_dashboard', 'message_center'],
                    'color': '#1f77b4'
                },
                'viewer': {
                    'name': 'Viewer',
                    'permissions': ['read'],
                    'ui_components': ['ccu_dashboard'],
                    'color': '#2ca02c'
                }
            },
            'default_role': 'viewer'
        }
    
    def get_available_roles(self) -> List[str]:
        """Get list of available user roles"""
        return list(self._roles_config.get('roles', {}).keys())
    
    def get_role_info(self, role: str) -> Dict:
        """Get information about a specific role"""
        return self._roles_config.get('roles', {}).get(role, {})
    
    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role"""
        role_info = self.get_role_info(role)
        return role_info.get('permissions', [])
    
    def get_role_ui_components(self, role: str) -> List[str]:
        """Get UI components accessible by a role"""
        role_info = self.get_role_info(role)
        return role_info.get('ui_components', [])
    
    def get_current_user_role(self) -> str:
        """Get current user role from session state"""
        if 'user_role' not in st.session_state:
            default_role = self._roles_config.get('default_role', 'viewer')
            st.session_state['user_role'] = default_role
        
        return st.session_state['user_role']
    
    def set_user_role(self, role: str) -> bool:
        """Set user role in session state"""
        if role in self.get_available_roles():
            st.session_state['user_role'] = role
            logger.info(f"👤 User role set to: {role}")
            return True
        else:
            logger.warning(f"⚠️ Invalid role: {role}")
            return False
    
    def has_permission(self, permission: str, role: Optional[str] = None) -> bool:
        """Check if role has a specific permission"""
        if role is None:
            role = self.get_current_user_role()
        
        permissions = self.get_role_permissions(role)
        
        # Wildcard permission grants all access
        if '*' in permissions:
            return True
        
        return permission in permissions
    
    def can_access_component(self, component: str, role: Optional[str] = None) -> bool:
        """Check if role can access a UI component"""
        if role is None:
            role = self.get_current_user_role()
        
        ui_components = self.get_role_ui_components(role)
        return component in ui_components
    
    def render_role_selector(self):
        """Render role selector in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 User Settings")
        
        current_role = self.get_current_user_role()
        available_roles = self.get_available_roles()
        
        # Role selector
        role_index = available_roles.index(current_role) if current_role in available_roles else 0
        
        new_role = st.sidebar.selectbox(
            "Select Role:",
            available_roles,
            index=role_index,
            format_func=lambda x: f"{self.get_role_info(x).get('name', x).title()}"
        )
        
        if new_role != current_role:
            self.set_user_role(new_role)
            st.rerun()
        
        # Role information
        role_info = self.get_role_info(current_role)
        role_color = role_info.get('color', '#333333')
        
        st.sidebar.markdown(
            f"<div style='padding: 10px; background-color: {role_color}20; border-left: 4px solid {role_color}; margin: 10px 0;'>"
            f"<strong>Current Role:</strong> {role_info.get('name', current_role)}<br>"
            f"<small>{role_info.get('description', 'No description available')}</small>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        # Show accessible components
        ui_components = self.get_role_ui_components(current_role)
        st.sidebar.caption(f"📊 {len(ui_components)} components available")
    
    def render_permissions_info(self):
        """Render permissions information for current role"""
        current_role = self.get_current_user_role()
        permissions = self.get_role_permissions(current_role)
        
        with st.expander("🔐 Role Permissions", expanded=False):
            st.write(f"**Role:** {self.get_role_info(current_role).get('name', current_role)}")
            
            if '*' in permissions:
                st.success("✅ Full system access (Administrator)")
            else:
                st.write("**Permissions:**")
                for perm in permissions:
                    st.write(f"• {perm}")
    
    def get_tab_config(self) -> Dict[str, Dict]:
        """Get tab configuration based on current user role"""
        current_role = self.get_current_user_role()
        ui_components = self.get_role_ui_components(current_role)
        
        # Define tab configuration with icons and display names
        all_tabs = {
            'ccu_dashboard': {
                'icon': '🏭',
                'name': 'CCU Dashboard',
                'module': 'omf2.ui.ccu.overview_tab',
                'function': 'render_ccu_overview_tab'
            },
            'message_center': {
                'icon': '📨',
                'name': 'Message Center', 
                'module': 'omf2.ui.message_center_tab',
                'function': 'render_message_center_tab'
            },
            'system_logs': {
                'icon': '📋',
                'name': 'System Logs',
                'module': 'omf2.ui.system.logs_tab',
                'function': 'render_logs_tab'
            },
            'admin_settings': {
                'icon': '⚙️',
                'name': 'Settings',
                'module': 'omf2.ui.system.admin_settings_tab',
                'function': 'render_admin_settings_tab'
            },
            'steering_factory': {
                'icon': '🎛️',
                'name': 'Factory Control',
                'module': 'omf2.ui.admin.steering_tab',
                'function': 'render_steering_tab'
            }
        }
        
        # Filter tabs based on role permissions
        available_tabs = {}
        for tab_key, tab_config in all_tabs.items():
            if tab_key in ui_components:
                available_tabs[tab_key] = tab_config
        
        return available_tabs