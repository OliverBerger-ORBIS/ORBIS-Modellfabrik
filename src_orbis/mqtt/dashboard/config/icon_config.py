"""
Icon Configuration for APS Dashboard
Defines icons and visual elements for the dashboard
"""
import os

# Module Icons (Emoji placeholders for testing)
MODULE_ICONS = {
    "AIQS": "🤖",  # Robot for AI Quality System
    "MILL": "⚙️",  # Gear for milling (deine Wahl)
    "DRILL": "🔩",  # Nut&Bolt for drilling (deine Wahl)
    "DPS": "📦",   # Package for Disposal & Pickup Station (Warenein- und -ausgang)
    "HBW": "🏬",   # Department Store for high-bay warehouse (deine Wahl)
    "FTS": "🚗",   # Car for transport system
    "CHRG": "🔋",  # Battery for charger
    "OVEN": "🔥",  # Fire for oven (optional)
    "CCU": "🎛️",  # Control panel for CCU
}

# System Icons (for additional components)
SYSTEM_ICONS = {
    "RPI": "🖥️",      # Raspberry Pi
    "RPI1": "🖥️",     # Raspberry Pi 1
    "MOSQUITTO": "📡", # MQTT Broker
    "MACHINE": "⚙️",   # Machine
    "TXT": "🎮",       # TXT Controller
    "PLATINE": "🔌",   # Circuit Board
    "ROUTER": "🌐",    # Router
    "PC_TABLET": "💻", # PC/Tablet
}

# Alternative System Icons for Modules (if needed)
ALTERNATIVE_MODULE_ICONS = {
    "MILL": "🔧",      # Wrench (alternative to mill_icon.png)
    "DRILL": "⚙️",     # Gear (alternative to drill_icon.png)
    "HBW": "🏗️",       # Construction (alternative to hbw_icon.png)
    "AIQS": "🔍",      # Magnifying glass (alternative to aiqs_icon.png)
    "DPS": "📦",       # Package (alternative to dps_icon.png)
    "FTS": "🚚",       # Truck (alternative to fts_icon.jpeg)
    "CHRG": "⚡",      # Lightning (alternative to chrg_icon.png)
}

# Module Icon Names (for future PNG files)
MODULE_ICON_FILES = {
    "AIQS": "aiqs_icon.png",
    "MILL": "mill_icon.png", 
    "DRILL": "drill_icon.png",
    "DPS": "dps_icon.png",
    "HBW": "hbw_icon.png",
    "FTS": "fts_icon.jpeg",  # Note: JPEG format
    "CHRG": "chrg_icon.png",
    "OVEN": "oven_icon.png",
    "CCU": "ccu_icon.png",
}

# System Icon Names (for additional components)
SYSTEM_ICON_FILES = {
    "RPI": "rpi_icon.png",
    "RPI1": "rpi1_icon.png",
    "MOSQUITTO": "mosquitto_icon.png",
    "MACHINE": "machine_icon.png",
    "TXT": "txt_icon.png",
    "PLATINE": "platine_icon.png",
    "ROUTER": "router_icon.png",
    "PC_TABLET": "pc-tablet_icon.png",
}

# Logo configuration
LOGO_CONFIG = {
    "file": "orbis_logo.png",
    "sidebar_width": 200,
    "header_width": 150,
}

# Icon sizes
ICON_SIZES = {
    "small": 16,
    "medium": 24, 
    "large": 32,
    "sidebar": 48,
}

# Status Icons for different states
STATUS_ICONS = {
    "available": "✅",
    "busy": "⚠️", 
    "blocked": "❌",
    "error": "🚨",
    "offline": "⚫",
    "charging": "⚡",
    "battery": "🔋",
    "transport": "🚗",
    "processing": "⚙️",
    "idle": "😴",
    "maintenance": "🔧",
    "ready": "🎯"
}

def get_module_icon(module_name, size="medium"):
    """
    Get icon for a module
    
    Args:
        module_name (str): Module name (e.g., 'AIQS', 'MILL')
        size (str): Icon size ('small', 'medium', 'large', 'sidebar')
    
    Returns:
        str: Icon (emoji or file path)
    """
    module_upper = module_name.upper()
    
    # For now, always use emoji icons to avoid path issues
    # TODO: Implement PNG icons when assets are available
    if module_upper in MODULE_ICONS:
        return MODULE_ICONS[module_upper]
    
    # Default icon if module not found
    return "❓"

def get_system_icon(system_name, size="medium"):
    """
    Get icon for a system component
    
    Args:
        system_name (str): System name (e.g., 'RPI', 'MOSQUITTO')
        size (str): Icon size ('small', 'medium', 'large', 'sidebar')
    
    Returns:
        str: Icon (emoji or file path)
    """
    system_upper = system_name.upper()
    
    # Try to get PNG icon first
    icon_path = get_system_icon_path(system_name)
    if icon_path and os.path.exists(icon_path):
        return icon_path
    
    # Fallback to emoji if PNG not available
    if system_upper in SYSTEM_ICONS:
        return SYSTEM_ICONS[system_upper]
    
    # Default icon if system not found
    return "❓"

def get_alternative_module_icon(module_name, size="medium"):
    """
    Get alternative icon for a module (emoji-based)
    
    Args:
        module_name (str): Module name (e.g., 'MILL', 'DRILL')
        size (str): Icon size ('small', 'medium', 'large', 'sidebar')
    
    Returns:
        str: Alternative emoji icon
    """
    module_upper = module_name.upper()
    
    if module_upper in ALTERNATIVE_MODULE_ICONS:
        return ALTERNATIVE_MODULE_ICONS[module_upper]
    
    # Fallback to standard module icon
    if module_upper in MODULE_ICONS:
        return MODULE_ICONS[module_upper]
    
    # Default icon if module not found
    return "❓"

def get_status_icon(status_text, size="medium"):
    """
    Get appropriate status icon based on status text
    
    Args:
        status_text (str): Status text (e.g., 'Available', 'Charging', 'Busy')
        size (str): Icon size (ignored for emoji)
    
    Returns:
        str: Status emoji icon
    """
    status_lower = status_text.lower()
    
    # Direct matches
    if status_lower in STATUS_ICONS:
        return STATUS_ICONS[status_lower]
    
    # Pattern matching
    if "available" in status_lower or "online" in status_lower:
        return STATUS_ICONS["available"]
    elif "busy" in status_lower or "processing" in status_lower:
        return STATUS_ICONS["busy"]
    elif "blocked" in status_lower or "error" in status_lower:
        return STATUS_ICONS["blocked"]
    elif "charging" in status_lower or "⚡" in status_text:
        return STATUS_ICONS["charging"]
    elif "battery" in status_lower or "🔋" in status_text:
        return STATUS_ICONS["battery"]
    elif "transport" in status_lower or "🚗" in status_text:
        return STATUS_ICONS["transport"]
    elif "idle" in status_lower or "waiting" in status_lower:
        return STATUS_ICONS["idle"]
    elif "maintenance" in status_lower or "🔧" in status_text:
        return STATUS_ICONS["maintenance"]
    elif "ready" in status_lower:
        return STATUS_ICONS["ready"]
    
    # Default status icon
    return "❓"

def get_logo_path():
    """Get the path to the ORBIS logo"""
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), "../assets")
    return os.path.join(assets_dir, LOGO_CONFIG["file"])

def get_module_icon_path(module_name):
    """Get the path to a module icon file"""
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), "../assets")
    module_upper = module_name.upper()
    
    if module_upper in MODULE_ICON_FILES:
        return os.path.join(assets_dir, MODULE_ICON_FILES[module_upper])
    
    return None

def get_system_icon_path(system_name):
    """Get the path to a system icon file"""
    import os
    assets_dir = os.path.join(os.path.dirname(__file__), "../assets")
    system_upper = system_name.upper()
    
    if system_upper in SYSTEM_ICON_FILES:
        return os.path.join(assets_dir, SYSTEM_ICON_FILES[system_upper])
    
    return None
