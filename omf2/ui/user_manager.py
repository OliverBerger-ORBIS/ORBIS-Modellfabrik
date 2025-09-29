"""
User and Role Management for OMF2 Dashboard
Manages user roles, permissions, and UI access based on omf2/config/user_roles.yml
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml
import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

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
                'administrator': {
                    'name': 'Administrator',
                    'permissions': ['*'],
                    'ui_components': ['ccu_dashboard', 'ccu_orders', 'ccu_process', 'ccu_configuration', 'ccu_modules', 'nodered_overview', 'nodered_processes', 'message_center', 'generic_steering', 'system_logs', 'admin_settings'],
                    'color': '#FF4B4B',
                    'description': 'Full system access - sees all tabs'
                },
                'supervisor': {
                    'name': 'Supervisor', 
                    'permissions': ['read', 'control', 'manage_workflows'],
                    'ui_components': ['ccu_dashboard', 'ccu_orders', 'ccu_process', 'ccu_configuration', 'ccu_modules', 'nodered_overview', 'nodered_processes'],
                    'color': '#FF8C00',
                    'description': 'CCU and Node-RED tabs access'
                },
                'operator': {
                    'name': 'Operator',
                    'permissions': ['read', 'control'],
                    'ui_components': ['ccu_dashboard', 'ccu_orders', 'ccu_process', 'ccu_configuration', 'ccu_modules'],
                    'color': '#1f77b4',
                    'description': 'CCU tabs only'
                }
            },
            'default_role': 'operator'
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
            default_role = self._roles_config.get('default_role', 'operator')
            st.session_state['user_role'] = default_role
        
        # Check if current role is still valid (in case viewer was removed)
        current_role = st.session_state['user_role']
        if current_role not in self.get_available_roles():
            # Reset to default role if current role is no longer available
            st.session_state['user_role'] = self._roles_config.get('default_role', 'operator')
            logger.info(f"🔄 Reset invalid role '{current_role}' to default role")
        
        # Force cleanup of viewer role if it still exists
        if current_role == 'viewer':
            st.session_state['user_role'] = 'operator'
            logger.info("🧹 Forced cleanup of viewer role - reset to operator")
        
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
            request_refresh()
        
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
        
        logger.info(f"👤 Current role: {current_role}")
        logger.info(f"📋 UI components for {current_role}: {ui_components}")
        
        # Define tab configuration with icons and display names
        all_tabs = {
            'ccu_dashboard': {
                'icon': '🏭',
                'name': 'CCU Dashboard',
                'module': 'omf2.ui.ccu.ccu_overview.ccu_overview_tab',
                'function': 'render_ccu_overview_tab'
            },
            'ccu_orders': {
                'icon': '📦',
                'name': 'CCU Orders',
                'module': 'omf2.ui.ccu.ccu_orders.ccu_orders_tab',
                'function': 'render_ccu_orders_tab'
            },
            'ccu_process': {
                'icon': '⚙️',
                'name': 'CCU Process',
                'module': 'omf2.ui.ccu.ccu_process.ccu_process_tab',
                'function': 'render_ccu_process_tab'
            },
            'ccu_configuration': {
                'icon': '⚙️',
                'name': 'CCU Configuration',
                'module': 'omf2.ui.ccu.ccu_configuration.ccu_configuration_tab',
                'function': 'render_ccu_configuration_tab'
            },
            'ccu_modules': {
                'icon': '🔧',
                'name': 'CCU Modules',
                'module': 'omf2.ui.ccu.ccu_modules.ccu_modules_tab',
                'function': 'render_ccu_modules_tab'
            },
            'nodered_overview': {
                'icon': '🔄',
                'name': 'Node-RED Overview',
                'module': 'omf2.ui.nodered.nodered_overview.nodered_overview_tab',
                'function': 'render_nodered_overview_tab'
            },
            'nodered_processes': {
                'icon': '⚙️',
                'name': 'Node-RED Processes',
                'module': 'omf2.ui.nodered.nodered_processes.nodered_processes_tab',
                'function': 'render_nodered_processes_tab'
            },
            'message_center': {
                'icon': '📨',
                'name': 'Message Center',
                'module': 'omf2.ui.admin.message_center.message_center_tab',
                'function': 'render_message_center_tab'
            },
            'generic_steering': {
                'icon': '🎛️',
                'name': 'Factory Control',
                'module': 'omf2.ui.admin.generic_steering.generic_steering_tab',
                'function': 'render_generic_steering_tab'
            },
            'system_logs': {
                'icon': '📋',
                'name': 'System Logs',
                'module': 'omf2.ui.admin.logs.logs_tab',
                'function': 'render_logs_tab'
            },
            'admin_settings': {
                'icon': '⚙️',
                'name': 'Admin Settings',
                'module': 'omf2.ui.admin.admin_settings.admin_settings_tab',
                'function': 'render_admin_settings_tab'
            },
        }
        
        # Filter tabs based on role permissions
        available_tabs = {}
        for tab_key, tab_config in all_tabs.items():
            if tab_key in ui_components:
                available_tabs[tab_key] = tab_config
                logger.info(f"✅ Tab '{tab_key}' available for {current_role}")
            else:
                logger.info(f"❌ Tab '{tab_key}' not available for {current_role}")
        
        logger.info(f"📋 Final available tabs: {list(available_tabs.keys())}")
        return available_tabs