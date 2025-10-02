"""
OMF2 UI Symbol Definitions
Centralized symbol management for consistent UI across all components
"""

from typing import Dict, Optional


class UISymbols:
    """Centralized symbol definitions for OMF2 UI"""
    
    # Tab Navigation Icons - FINALE ENTSCHEIDUNGEN
    TAB_ICONS: Dict[str, str] = {
        # CCU Module
        'ccu_dashboard': '🏭',      # Factory/Overview
        'ccu_orders': '📝',         # Orders/Workpieces (FINAL: 📝)
        'ccu_process': '🔄',        # Process Control (FINAL: 🔄)
        'ccu_configuration': '⚙️',  # Configuration
        'ccu_modules': '🏗️',       # Module Control (FINAL: 🏗️)
        
        # Node-RED Integration
        'nodered_overview': '🔄',   # Process Overview
        'nodered_processes': '⚙️',  # Process Management
        
        # Admin Functions
        'message_center': '📨',     # Message Center (FINAL: 📨)
        'generic_steering': '🎮',   # Generic Steering
        'admin_settings': '⚙️',    # Admin Settings
        
        # Legacy Support (omf/dashboard compatibility)
        'aps_overview': '🏭',       # APS Overview
        'aps_orders': '📝',         # APS Orders (FINAL: 📝)
        'aps_processes': '🔄',      # APS Processes (FINAL: 🔄)
        'aps_configuration': '⚙️',  # APS Configuration
        'aps_modules': '🏗️',        # APS Modules (FINAL: 🏗️)
        'wl_module_control': '🛠️',  # Werkstückleiter Module Control (FINAL: 🛠️)
        'wl_system_control': '🎛️',  # Werkstückleiter System Control (FINAL: 🎛️)
        'steering': '🎮',           # Steering
        'logs': '📋',               # Logs (FINAL: 📋)
        'settings': '⚙️',           # Settings
    }
    
    # Status Feedback Icons - FINALE ENTSCHEIDUNGEN
    STATUS_ICONS: Dict[str, str] = {
        'success': '✅',            # Erfolgreiche Aktionen
        'error': '❌',              # Fehler und Fehlschläge
        'warning': '⚠️',            # Warnungen
        'info': 'ℹ️',               # Informationen
        'tip': '💡',                # Tipps und Hinweise
        'loading': '⏳',            # Ladevorgänge (FINAL: ⏳)
        'refresh': '🔄',            # Aktualisieren
        'send': '📤',               # Nachrichten senden
        'receive': '📥',            # Nachrichten empfangen (FINAL: 📥)
        'debug': '🔍',              # Debug/Inspection
        'history': '📚',            # History/Logs
    }
    
    # Functional Icons - FINALE ENTSCHEIDUNGEN
    FUNCTIONAL_ICONS: Dict[str, str] = {
        # Factory Operations
        'factory_reset': '🏭',      # Factory Reset
        'emergency_stop': '🚨',     # Emergency Stop
        'module_control': '🛠️',     # Module Control (FINAL: 🛠️)
        
        # Communication
        'topic_driven': '📡',       # Topic-driven Commands
        'schema_driven': '🧩',      # Schema-driven Commands (FINAL: 🧩)
        'mqtt_connect': '🔌',       # MQTT Connection (FINAL: 🔌)
        
        # Process States
        'running': '▶️',            # Running/Active (FINAL: ▶️)
        'stopped': '⏹️',            # Stopped/Error (FINAL: ⏹️)
        'unknown': '⚪',             # Unknown/Neutral
        'pending': '⏳',             # Pending/Waiting (FINAL: ⏳)
        'completed': '✅',          # Completed
        'cancelled': '❌',          # Cancelled
        
        # Navigation & Control
        'settings': '⚙️',           # Settings/Configuration
        'control': '🎮',            # Control/Steering
        'target': '🎯',             # Target/Goal
        'search': '🔍',             # Search/Find
        'filter': '🔍',             # Filter/Search
        'sort': '🔄',               # Sort/Order
        'add': '➕',                # Add/Create
        'remove': '➖',              # Remove/Delete
        'edit': '✏️',               # Edit/Modify
        'save': '💾',               # Save/Store
        'load': '📁',               # Load/Open
        'export': '📤',             # Export/Send
        'import': '📥',             # Import/Receive
        
        # Admin Settings specific icons
        'dashboard': '📊',          # Dashboard Settings
        'stations': '🏢',            # Stations (FINAL: 🏢)
        'txt_controllers': '🕹️',    # TXT Controllers (FINAL: 🕹️)
        'workpieces': '🔵⚪🔴',      # Workpieces (FINAL: 🔵⚪🔴)
    }
    
    @classmethod
    def get_tab_icon(cls, tab_key: str) -> str:
        """Get icon for tab navigation"""
        return cls.TAB_ICONS.get(tab_key, '📋')
    
    @classmethod
    def get_status_icon(cls, status: str) -> str:
        """Get icon for status feedback"""
        return cls.STATUS_ICONS.get(status, 'ℹ️')
    
    @classmethod
    def get_functional_icon(cls, function: str) -> str:
        """Get icon for functional elements"""
        return cls.FUNCTIONAL_ICONS.get(function, '⚙️')
    
    @classmethod
    def get_all_tab_icons(cls) -> Dict[str, str]:
        """Get all available tab icons"""
        return cls.TAB_ICONS.copy()
    
    @classmethod
    def get_all_status_icons(cls) -> Dict[str, str]:
        """Get all available status icons"""
        return cls.STATUS_ICONS.copy()
    
    @classmethod
    def get_all_functional_icons(cls) -> Dict[str, str]:
        """Get all available functional icons"""
        return cls.FUNCTIONAL_ICONS.copy()
    
    @classmethod
    def add_tab_icon(cls, key: str, icon: str) -> None:
        """Add new tab icon"""
        cls.TAB_ICONS[key] = icon
    
    @classmethod
    def add_status_icon(cls, key: str, icon: str) -> None:
        """Add new status icon"""
        cls.STATUS_ICONS[key] = icon
    
    @classmethod
    def add_functional_icon(cls, key: str, icon: str) -> None:
        """Add new functional icon"""
        cls.FUNCTIONAL_ICONS[key] = icon


# Convenience functions for easy access
def get_tab_icon(tab_key: str) -> str:
    """Convenience function to get tab icon"""
    return UISymbols.get_tab_icon(tab_key)


def get_status_icon(status: str) -> str:
    """Convenience function to get status icon"""
    return UISymbols.get_status_icon(status)


def get_functional_icon(function: str) -> str:
    """Convenience function to get functional icon"""
    return UISymbols.get_functional_icon(function)
