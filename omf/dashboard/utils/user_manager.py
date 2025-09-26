"""
User Management für OMF Dashboard
Verwaltet Benutzerrollen und Session State
"""

import streamlit as st
from enum import Enum
from typing import Dict, List, Optional


class UserRole(Enum):
    """Benutzerrollen im OMF Dashboard"""
    OPERATOR = "operator"      # APS-Business-User
    SUPERVISOR = "supervisor"  # Werksleiter/DSP-User
    ADMIN = "admin"           # System-Admin


class UserManager:
    """Manager für Benutzerrollen und Berechtigung"""
    
    # Definition der Tabs pro Rolle
    ROLE_TABS = {
        UserRole.OPERATOR: [
            "aps_overview",
            "aps_orders", 
            "aps_processes",
            "aps_configuration",
            "aps_modules"
        ],
        UserRole.SUPERVISOR: [
            "aps_overview",
            "aps_orders",
            "aps_processes", 
            "aps_configuration",
            "aps_modules",
            "wl_module_control",
            "wl_system_control"
        ],
        UserRole.ADMIN: [
            "aps_overview",
            "aps_orders",
            "aps_processes",
            "aps_configuration", 
            "aps_modules",
            "wl_module_control",
            "wl_system_control",
            "steering",
            "message_center",
            "logs",
            "settings"
        ]
    }
    
    # Tab-Namen und Icons
    TAB_NAMES = {
        "aps_overview": {"icon": "🏭", "key": "aps_overview"},
        "aps_orders": {"icon": "📋", "key": "aps_orders"},
        "aps_processes": {"icon": "🔄", "key": "aps_processes"},
        "aps_configuration": {"icon": "⚙️", "key": "aps_configuration"},
        "aps_modules": {"icon": "🏭", "key": "aps_modules"},
        "wl_module_control": {"icon": "🔧", "key": "wl_module_control", "component": "wl_module_state_control"},
        "wl_system_control": {"icon": "⚙️", "key": "wl_system_control", "component": "aps_control"},
        "steering": {"icon": "🎮", "key": "steering"},
        "message_center": {"icon": "📡", "key": "message_center"},
        "logs": {"icon": "📋", "key": "logs"},
        "settings": {"icon": "⚙️", "key": "settings"}
    }
    
    @staticmethod
    def get_current_user_role() -> UserRole:
        """Holt die aktuelle Benutzerrolle aus Session State"""
        if "user_role" not in st.session_state:
            st.session_state["user_role"] = UserRole.OPERATOR.value
        
        return UserRole(st.session_state["user_role"])
    
    @staticmethod
    def set_user_role(role: UserRole):
        """Setzt die Benutzerrolle in Session State"""
        st.session_state["user_role"] = role.value
    
    @staticmethod
    def get_allowed_tabs(role: UserRole) -> List[str]:
        """Gibt die erlaubten Tabs für eine Rolle zurück"""
        return UserManager.ROLE_TABS.get(role, [])
    
    @staticmethod
    def is_tab_allowed(tab_name: str, role: UserRole) -> bool:
        """Prüft ob ein Tab für eine Rolle erlaubt ist"""
        return tab_name in UserManager.get_allowed_tabs(role)
    
    @staticmethod
    def get_role_display_name(role: UserRole, language: str = "de") -> str:
        """Gibt den Anzeigenamen für eine Rolle zurück"""
        role_names = {
            "de": {
                UserRole.OPERATOR: "Operator (APS-Benutzer)",
                UserRole.SUPERVISOR: "Supervisor (Werksleiter)",
                UserRole.ADMIN: "Administrator (System)"
            },
            "en": {
                UserRole.OPERATOR: "Operator (APS User)",
                UserRole.SUPERVISOR: "Supervisor (Plant Manager)",
                UserRole.ADMIN: "Administrator (System)"
            },
            "fr": {
                UserRole.OPERATOR: "Opérateur (Utilisateur APS)",
                UserRole.SUPERVISOR: "Superviseur (Chef d'usine)",
                UserRole.ADMIN: "Administrateur (Système)"
            }
        }
        return role_names.get(language, role_names["de"]).get(role, str(role.value))
    
    @staticmethod
    def show_role_selector():
        """Zeigt einen Rolle-Wähler in der Sidebar"""
        current_role = UserManager.get_current_user_role()
        
        # Sprache aus Config holen
        from omf.config.omf_config import OmfConfig
        config = OmfConfig()
        language = config.get("dashboard.language", "de")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Benutzerrolle" if language == "de" else 
                           "👤 User Role" if language == "en" else 
                           "👤 Rôle utilisateur")
        
        role_options = [
            (UserRole.OPERATOR, UserManager.get_role_display_name(UserRole.OPERATOR, language)),
            (UserRole.SUPERVISOR, UserManager.get_role_display_name(UserRole.SUPERVISOR, language)),
            (UserRole.ADMIN, UserManager.get_role_display_name(UserRole.ADMIN, language))
        ]
        
        selected_role_name = st.sidebar.selectbox(
            "Rolle wählen:" if language == "de" else 
            "Select Role:" if language == "en" else 
            "Choisir le rôle:",
            options=[name for _, name in role_options],
            index=[role for role, _ in role_options].index(current_role)
        )
        
        # Neue Rolle finden und setzen
        for role, name in role_options:
            if name == selected_role_name:
                if role != current_role:
                    UserManager.set_user_role(role)
                    st.rerun()
                break
        
        # Info über aktuelle Rolle
        tab_count = len(UserManager.get_allowed_tabs(current_role))
        st.sidebar.info(
            f"📊 {tab_count} Tabs verfügbar" if language == "de" else
            f"📊 {tab_count} tabs available" if language == "en" else
            f"📊 {tab_count} onglets disponibles"
        )