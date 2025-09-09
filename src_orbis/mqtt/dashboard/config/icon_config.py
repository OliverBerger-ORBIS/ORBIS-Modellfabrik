"""
Icon configuration module for MQTT dashboard
Imports icons and functions from OMF dashboard components
"""

# Placeholder for STATUS_ICONS if not present in overview_module_status

# Modul-Icons als Emoji
MODULE_ICONS = {
    "DPS": "🔧",
    "HBW": "🧰",
    "MILL": "⚙️",
    "DRILL": "🛠️",
    "AIQS": "🔬",
    "FTS": "🚗",
}

# Status-Icons als Emoji
STATUS_ICONS = {
    "online": "🟢",
    "available": "🟢",
    "busy": "🟡",
    "error": "🔴",
    "idle": "⚫",
    "offline": "⚫",
    "unknown": "❓",
}


def get_module_icon(module: str) -> str:
    """Gibt das Icon für ein Modul zurück."""
    return MODULE_ICONS.get(module, "❓")


def get_status_icon(status: str) -> str:
    """Gibt das Icon für einen Status zurück."""
    return STATUS_ICONS.get(status, "❓")
