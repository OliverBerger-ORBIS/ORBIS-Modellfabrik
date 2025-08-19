"""
Dashboard Configuration
"""

# APS Module Serial Numbers mapping
APS_MODULES = {
    'MILL': 'SVR3QA2098',
    'DRILL': 'SVR4H76449',
    'AIQS': 'SVR4H76530',
    'HBW': 'SVR3QA0022',
    'DPS': 'SVR4H73275'
}

# Extended APS Modules with additional info
APS_MODULES_EXTENDED = {
    'MILL': {
        'id': 'SVR3QA2098',
        'name': 'MILL',
        'icon': '⚙️',
        'type': 'Processing',
        'commands': ['PICK', 'MILL', 'DROP'],
        'ip': '192.168.0.40'
    },
    'DRILL': {
        'id': 'SVR4H76449',
        'name': 'DRILL',
        'icon': '🔧',
        'type': 'Processing',
        'commands': ['PICK', 'DRILL', 'DROP'],
        'ip': '192.168.0.50'
    },
    'AIQS': {
        'id': 'SVR4H76530',
        'name': 'AIQS',
        'icon': '🔍',
        'type': 'Quality Control',
        'commands': ['PICK', 'DROP', 'CHECK_QUALITY'],
        'ip': '192.168.0.70'
    },
    'HBW': {
        'id': 'SVR3QA0022',
        'name': 'HBW',
        'icon': '📦',
        'type': 'Storage',
        'commands': ['PICK', 'DROP', 'STORE'],
        'ip': '192.168.0.80'
    },
    'DPS': {
        'id': 'SVR4H73275',
        'name': 'DPS',
        'icon': '🏭',
        'type': 'Distribution',
        'commands': ['PICK', 'DROP', 'INPUT_RGB', 'RGB_NFC'],
        'ip': '192.168.0.90'
    },
    'FTS': {
        'id': '5iO4',
        'name': 'FTS (Fahrerloses Transportsystem)',
        'icon': '🚗',
        'type': 'Transport',
        'commands': ['finish_charging', 'dock_to_dps', 'charge'],
        'ip': '192.168.0.60'
    },
    'CHRG': {
        'id': 'CHRG0',
        'name': 'Charging Station',
        'icon': '🔋',
        'type': 'Charging',
        'commands': ['start_charging', 'stop_charging', 'get_status'],
        'ip': '192.168.0.65'
    }
}

# MQTT Configuration
MQTT_BROKER = "192.168.0.100"
MQTT_PORT = 1883
MQTT_USERNAME = "default"
MQTT_PASSWORD = "default"
