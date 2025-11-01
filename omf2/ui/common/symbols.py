"""
OMF2 UI Symbol Definitions
Centralized symbol management for consistent UI across all components
"""

import re
from pathlib import Path
from typing import Dict, Optional


class UISymbols:
    """Centralized symbol definitions for OMF2 UI"""

    # Tab Navigation Icons - FINAL
    # Ordering encodes hierarchy exactly like main_dashboard: TOP-Level → SUB-TAB → THIRD-Level
    TAB_ICONS: Dict[str, str] = {
        # === TOP-LEVEL: CCU Overview ===
        "ccu_dashboard": "🏭",  # TOP-LEVEL: Overview (Dashboard)
        # SUB-TAB (Overview)
        "product_catalog": "📋",  # SUB-TAB: Product Catalog
        "inventory": "📚",  # SUB-TAB: Inventory / Stock Grid
        "sensor_data": "🌡️",  # SUB-TAB: Sensor Data
        # === TOP-LEVEL: Orders ===
        "ccu_orders": "📝",  # TOP-LEVEL: Orders/Workpieces
        # SUB-TAB (Orders)
        "production_orders": "🏭",  # SUB-TAB: Production Orders
        "storage_orders": "📦",  # SUB-TAB: Storage Orders
        # === TOP-LEVEL: Process ===
        "ccu_process": "🔄",  # TOP-LEVEL: Process Control
        # SUB-TAB (Process)
        "production_plan": "📋",  # SUB-TAB: Production Plan
        # removed: production_monitoring
        # === TOP-LEVEL: Configuration ===
        "ccu_configuration": "⚙️",  # TOP-LEVEL: Configuration
        # SUB-TAB (Configuration)
        "factory": "🏭",  # SUB-TAB: Factory Configuration
        "parameter": "⚙️",  # SUB-TAB: Parameter Configuration
        "business_functions": "🧩",  # SUB-TAB: Business Functions
        "workflow": "🔄",  # SUB-TAB: Workflow / Process Flow
        # === TOP-LEVEL: Modules ===
        "ccu_modules": "🧩",  # TOP-LEVEL: Module Control
        # === TOP-LEVEL: Message Center ===
        "message_center": "📨",  # TOP-LEVEL: Message Center
        # SECOND-LEVEL (Message Center)
        "message_monitor": "🔍",  # SECOND-LEVEL: Message Monitor
        "topic_monitor": "🏷️",  # SECOND-LEVEL: Topic Monitor
        "send_test_message": "📤",  # SECOND-LEVEL: Send Test Message
        # === TOP-LEVEL: Generic Steering ===
        "generic_steering": "🎮",  # TOP-LEVEL: Generic Steering
        # SECOND-LEVEL (Generic Steering)
        "factory_steering": "🎛️",  # SECOND-LEVEL: Factory Steering
        "topic_steering": "🏷️",  # SECOND-LEVEL: Topic Steering
        # === TOP-LEVEL: System Logs ===
        "system_logs": "🧾",  # TOP-LEVEL: System Logs
        # SECOND-LEVEL (System Logs)
        "log_history": "📚",  # SECOND-LEVEL: Log History
        "log_search": "🔍",  # SECOND-LEVEL: Log Search
        "log_analytics": "📊",  # SECOND-LEVEL: Log Analytics
        "log_management": "⚙️",  # SECOND-LEVEL: Log Management
        "log_errors_warnings": "🚨",  # SECOND-LEVEL: Error & Warnings
        # === TOP-LEVEL: Admin Settings ===
        "admin_settings": "⚙️",  # TOP-LEVEL: Admin Settings
        # SUB-TAB (Admin Settings)
        "admin_dashboard": "📊",  # SUB-TAB: Dashboard
        "mqtt_clients": "🔌",  # SUB-TAB: MQTT Clients
        "gateway": "🔀",  # SUB-TAB: Gateway
        "topics": "🏷️",  # SUB-TAB: Topics
        "schemas": "{}",  # SUB-TAB: Schemas
        "admin_modules": "🧩",  # SUB-TAB: Modules
        "stations": "🏢",  # SUB-TAB: Stations
        "txt_controllers": "🕹️",  # SUB-TAB: TXT Controllers
        "workpieces": "📦",  # SUB-TAB: Workpieces
        # === Legacy / Optional ===
        # Node-RED Integration (keine TOP-Navigation im Messe-Setup)
        "nodered_overview": "🔄",  # LEGACY: Node-RED Overview
        "nodered_processes": "⚙️",  # LEGACY: Node-RED Processes
        # Weitere Legacy-Kompatibilität (omf/dashboard)
        "ccu_overview": "🏭",  # LEGACY alias for ccu_dashboard
        "aps_overview": "🏭",
        "aps_orders": "📝",
        "aps_processes": "🔄",
        "aps_configuration": "⚙️",
        "aps_modules": "🏗️",
        "wl_module_control": "🛠️",
        "wl_system_control": "🎛️",
        "steering": "🎮",
        "logs": "🧾",
        "settings": "⚙️",
    }

    # Status Feedback Icons - FINALE ENTSCHEIDUNGEN
    STATUS_ICONS: Dict[str, str] = {
        "success": "✅",  # Erfolgreiche Aktionen
        "error": "❌",  # Fehler und Fehlschläge
        "warning": "⚠️",  # Warnungen
        "info": "ℹ️",  # Informationen
        "tip": "💡",  # Tipps und Hinweise
        "loading": "⏳",  # Ladevorgänge (FINAL: ⏳)
        "refresh": "🔄",  # Aktualisieren
        "send": "📤",  # Nachrichten senden
        "receive": "📥",  # Nachrichten empfangen (FINAL: 📥)
        "debug": "🔍",  # Debug/Inspection
        "history": "📚",  # History/Logs
        "overview": "📋",  # Overview/Summary
        "stats": "📊",  # Statistics/Analytics
        "save": "💾",  # Save/Store
        "load": "📂",  # Load/Open
        "start": "▶️",  # Start/Begin
        "stop": "⏹️",  # Stop/End
        "pause": "⏸️",  # Pause/Suspend
        "add": "➕",  # Add/Create
        # Connection Status Icons
        "connected": "📶",  # Connected/Online (WiFi symbol)
        "disconnected": "🚫",  # Disconnected/Offline (Crossed out symbol)
        "connecting": "🟡",  # Connecting/In Progress
        # Production Process Step Icons
        "step_in_progress": "🟠",  # Production Step In Progress (ORANGE CIRCLE - wie aktive Station)
        "step_finished": "✅",  # Production Step Finished
        "step_enqueued": "⏳",  # Production Step Enqueued
        "step_pending": "⚪",  # Production Step Pending
        "step_failed": "❌",  # Production Step Failed
        # Availability Status Icons
        "available": "🟢",  # Available/Ready
        "busy": "🟠",  # Busy/Processing (🟠 - avoid conflict with pending)
        "blocked": "🔴",  # Blocked (🔴 - red circle like in aps_modules.py)
        "charging": "⚡",  # Charging
        "transport": "🚗",  # Transport/Moving
        "maintenance": "🔧",  # Maintenance
        "idle": "😴",  # Idle/Waiting
        "unknown": "⚫",  # Unknown/Undefined (⚫ - avoid conflict with workpieces)
        # Configuration Status Icons
        "configured": "📋",  # Configured (Factsheet symbol)
        "not_configured": "❌",  # Not Configured
    }

    # Functional Icons - FINALE ENTSCHEIDUNGEN
    FUNCTIONAL_ICONS: Dict[str, str] = {
        # Factory Operations
        "factory_reset": "🏭🔄",  # Factory Reset (Factory + Refresh)
        "emergency_stop": "🚨",  # Emergency Stop
        "module_control": "🛠️",  # Module Control (FINAL: 🛠️)
        # Communication
        "topic_driven": "📡",  # Topic-driven Commands
        "schema_driven": "🧩",  # Schema-driven Commands (FINAL: 🧩)
        "mqtt_connect": "🔌",  # MQTT Connection (FINAL: 🔌)
        # Process States
        "running": "▶️",  # Running/Active (FINAL: ▶️)
        "stopped": "⏹️",  # Stopped/Error (FINAL: ⏹️)
        "unknown": "⚪",  # Unknown/Neutral
        "pending": "🟡",  # Pending/Waiting (FINAL: 🟡 - avoid conflict with loading)
        "completed": "✔️",  # Completed (FINAL: ✔️ - avoid conflict with success)
        "cancelled": "✖️",  # Cancelled (FINAL: ✖️ - avoid conflict with error)
        # Navigation & Control
        "settings": "⚙️",  # Settings/Configuration
        "control": "🎮",  # Control/Steering
        "target": "🎯",  # Target/Goal
        "search": "🔍",  # Search/Find
        "filter": "🔍",  # Filter/Search
        "sort": "🔄",  # Sort/Order
        "add": "➕",  # Add/Create
        "remove": "➖",  # Remove/Delete
        "edit": "✏️",  # Edit/Modify
        "save": "💾",  # Save/Store
        "load": "📁",  # Load/Open
        "export": "📤",  # Export/Send
        "import": "📥",  # Import/Receive
        # Admin Settings specific icons
        "dashboard": "📊",  # Dashboard Settings
        "stations": "🏢",  # Stations (FINAL: 🏢)
        "txt_controllers": "🕹️",  # TXT Controllers (FINAL: 🕹️)
        "workpieces": None,  # Workpieces (loaded from Registry)
        # CCU Overview specific icons
        "product_catalog": "📋",  # Product Catalog
        "customer_order": "🛒",  # Customer Orders
        "purchase_order": "📦",  # Purchase Orders
        "inventory": "📚",  # Inventory
        "sensor_data": "📊",  # Sensor Data
    }

    @classmethod
    def get_tab_icon(cls, tab_key: str) -> str:
        """Get icon for tab navigation"""
        return cls.TAB_ICONS.get(tab_key, "📋")

    @classmethod
    def get_status_icon(cls, status: str) -> str:
        """Get icon for status feedback"""
        return cls.STATUS_ICONS.get(status, "ℹ️")

    @classmethod
    def get_functional_icon(cls, function: str) -> str:
        """Get icon for functional elements"""
        return cls.FUNCTIONAL_ICONS.get(function, "⚙️")

    @classmethod
    def get_workpiece_icon(cls, color: str = None) -> str:
        """Get workpiece icon by color or general workpiece icon"""
        try:
            from omf2.common.workpiece_manager import get_workpiece_manager

            workpiece_manager = get_workpiece_manager()

            # Special case for all_workpieces
            if color == "all_workpieces":
                return workpiece_manager.get_all_workpieces_icon()
            elif color:
                return workpiece_manager.get_workpiece_icon(color)
            else:
                return workpiece_manager.get_all_workpieces_icon()
        except Exception:
            # Fallback to hardcoded icons if Registry is not available
            if color == "all_workpieces":
                return "🔵⚪🔴"
            elif color:
                color_lower = color.lower()
                if color_lower == "blue":
                    return "🔵"
                elif color_lower == "white":
                    return "⚪"
                elif color_lower == "red":
                    return "🔴"
                else:
                    return "📦"
            else:
                return "🔵⚪🔴"

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


def get_icon_html(key: str, size_px: Optional[int] = 24) -> str:
    """
    Get icon as HTML, preferring SVG over emoji fallback.

    This function implements a cascading lookup strategy:
    1. Try to load heading SVG via omf2.assets.heading_icons.get_svg_inline()
    2. Fall back to module icon via omf2.assets.asset_manager.get_module_icon_path()
    3. Final fallback to emoji from registry (TAB_ICONS, STATUS_ICONS, FUNCTIONAL_ICONS)

    Args:
        key: Icon key (e.g., "DASHBOARD_ADMIN", "HBW", "success", "ccu_dashboard")
        size_px: Size in pixels for the icon (default: 24)

    Returns:
        HTML string with either inline SVG or emoji in a span

    Examples:
        >>> get_icon_html("DASHBOARD_ADMIN", size_px=32)
        '<svg width="32"...>...</svg>'

        >>> get_icon_html("ccu_dashboard", size_px=24)
        '<span style="font-size: 24px;">🏭</span>'
    """
    # Step 1: Try heading icons first
    try:
        from omf2.assets.heading_icons import get_svg_inline

        svg_html = get_svg_inline(key, size_px=size_px)
        if svg_html:
            return svg_html
    except Exception:
        # heading_icons module not available or key not found
        pass

    # Step 2: Try module icons via asset_manager
    try:
        from omf2.assets.asset_manager import get_asset_manager, scope_svg_styles

        asset_manager = get_asset_manager()
        icon_path = asset_manager.get_module_icon_path(key.upper())

        if icon_path:
            icon_file = Path(icon_path)
            if icon_file.exists():
                # Read SVG content
                svg_content = icon_file.read_text(encoding="utf-8")

                # Apply CSS scoping to prevent class conflicts
                svg_content = scope_svg_styles(svg_content)

                # Remove existing width/height attributes
                svg_content = re.sub(r'\s+width="[^"]*"', "", svg_content)
                svg_content = re.sub(r'\s+height="[^"]*"', "", svg_content)

                # Inject new width for proportional scaling
                svg_content = re.sub(r"<svg\b", f'<svg width="{size_px}"', svg_content, count=1)

                return svg_content
    except Exception:
        # asset_manager not available or error loading SVG
        pass

    # Step 3: Fall back to emoji from registry
    emoji = None

    # Try TAB_ICONS first
    if key in UISymbols.TAB_ICONS:
        emoji = UISymbols.TAB_ICONS[key]
    # Try STATUS_ICONS
    elif key in UISymbols.STATUS_ICONS:
        emoji = UISymbols.STATUS_ICONS[key]
    # Try FUNCTIONAL_ICONS
    elif key in UISymbols.FUNCTIONAL_ICONS:
        emoji = UISymbols.FUNCTIONAL_ICONS[key]

    if emoji:
        return f'<span style="font-size: {size_px}px;">{emoji}</span>'

    # Ultimate fallback: return a placeholder
    return f'<span style="font-size: {size_px}px;">⚙️</span>'
