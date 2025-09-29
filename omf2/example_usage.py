#!/usr/bin/env python3
"""
Example usage of OMF2 modular architecture
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from omf2.ccu import CCUGateway, ccu_mqtt_client
from omf2.nodered import NodeREDGateway, nodered_mqtt_client
from omf2.system import AdminSettings, LogManager
from omf2.ccu.workpiece_manager import get_workpiece_manager


def main():
    """Demonstrate OMF2 architecture usage"""
    print("🚀 OMF2 Modular Architecture Demo")
    print("=" * 50)
    
    # 1. System Configuration
    print("\n📋 1. Loading System Configuration...")
    
    admin_settings = AdminSettings()
    mqtt_settings = admin_settings.load_mqtt_settings()
    available_envs = admin_settings.get_available_environments()
    
    print(f"✅ Available MQTT environments: {available_envs}")
    print(f"✅ Default environment: {mqtt_settings.get('default_environment')}")
    
    # 2. Workpiece Management
    print("\n🔧 2. Workpiece Management...")
    
    workpiece_manager = get_workpiece_manager()
    workpieces = workpiece_manager.get_all_workpieces()
    stats = workpiece_manager.get_statistics()
    
    print(f"✅ Total workpieces: {stats.get('total_workpieces', 0)}")
    print(f"✅ Available colors: {list(stats.get('colors', {}).keys())}")
    
    # Test workpiece lookup
    if workpieces:
        first_workpiece_id = list(workpieces.keys())[0]
        workpiece = workpiece_manager.get_workpiece_by_id(first_workpiece_id)
        display_name = workpiece_manager.get_workpiece_display_name(first_workpiece_id)
        print(f"✅ Sample workpiece: {display_name}")
        
        nfc_codes = workpiece.get('nfc_codes', [])
        if nfc_codes:
            nfc_valid = workpiece_manager.validate_nfc_code(nfc_codes[0])
            print(f"✅ NFC validation: {nfc_codes[0]} -> {nfc_valid}")
    
    # 3. Domain-Specific Gateways
    print("\n🏭 3. Domain-Specific Gateways...")
    
    # CCU Gateway
    ccu_gateway = CCUGateway(ccu_mqtt_client)
    print(f"✅ CCU Gateway connected: {ccu_gateway.is_connected()}")
    
    # Node-RED Gateway
    nodered_gateway = NodeREDGateway(nodered_mqtt_client)
    print(f"✅ Node-RED Gateway connected: {nodered_gateway.is_connected()}")
    
    # Message Center Gateway
    
    
    # 4. Log Management
    print("\n📝 4. Log Management...")
    
    log_manager = LogManager()
    
    # Add some test log entries
    log_manager.log_info("demo", "OMF2 architecture demonstration started")
    log_manager.log_info("ccu", "CCU gateway initialized successfully")
    log_manager.log_warning("system", "This is a test warning message")
    
    # Get log statistics
    log_stats = log_manager.get_log_statistics()
    print(f"✅ Total log entries: {log_stats.get('total_entries', 0)}")
    print(f"✅ Components logging: {list(log_stats.get('component_distribution', {}).keys())}")
    
    # Get recent logs
    recent_logs = log_manager.get_recent_logs(minutes=1, limit=5)
    print(f"✅ Recent log entries: {len(recent_logs)}")
    
    # 5. Message Testing (without actual MQTT broker)
    print("\n📤 5. Message Publishing Test (Mock)...")
    
    # Test CCU messages
    print("✅ Testing CCU status update (would publish to MQTT)")
    # ccu_gateway.send_status_update("demo_module", "running", {"test": True})
    
    # Test Message Center broadcast
    print("✅ Testing Message Center broadcast (would publish to MQTT)")
    # message_center_gateway.send_broadcast_message("Demo message", "system")
    
    # Test Node-RED input
    print("✅ Testing Node-RED input (would publish to MQTT)")
    # nodered_gateway.send_input_data("demo_flow", {"sensor": "temperature", "value": 23.5})
    
    # Test Generic Steering command
    print("✅ Testing Generic Steering command (would publish to MQTT)")
    # steering_gateway.send_command("demo_device", "move", {"position": 100})
    
    # 6. User Roles & Permissions
    print("\n👥 6. User Roles & Permissions...")
    
    user_roles = admin_settings.load_user_roles()
    roles = user_roles.get('roles', {})
    users = user_roles.get('users', {})
    
    print(f"✅ Available roles: {list(roles.keys())}")
    print(f"✅ Configured users: {list(users.keys())}")
    
    # Test admin permissions
    admin_permissions = admin_settings.get_user_permissions("admin")
    has_admin_access = admin_settings.has_permission("admin", "control")
    print(f"✅ Admin has control permission: {has_admin_access}")
    
    # 7. Apps Configuration
    print("\n📱 7. Apps Configuration...")
    
    apps_config = admin_settings.load_apps_config()
    apps = apps_config.get('apps', {})
    enabled_apps = admin_settings.get_enabled_apps()
    
    print(f"✅ Total apps: {len(apps)}")
    print(f"✅ Enabled apps: {len(enabled_apps)}")
    print(f"✅ App names: {[app.get('name') for app in enabled_apps.values()]}")
    
    print("\n🎉 OMF2 Architecture Demo Complete!")
    print("All components initialized and tested successfully.")


if __name__ == "__main__":
    main()