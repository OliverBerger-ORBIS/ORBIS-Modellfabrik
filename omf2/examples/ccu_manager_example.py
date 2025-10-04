#!/usr/bin/env python3
"""
Example: Using CCU Manager State-Holder Pattern
"""

from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.ccu.module_manager import get_ccu_module_manager


def example_sensor_manager():
    """Example: Using SensorManager for sensor data access"""
    print("=" * 60)
    print("Example 1: SensorManager State-Holder Pattern")
    print("=" * 60)
    
    sensor_manager = get_ccu_sensor_manager()
    
    # Simulate MQTT message
    topic = "/j1/txt/1/i/bme680"
    payload = {"t": 25.5, "h": 45.2, "p": 1013.25, "iaq": 50.0}
    
    sensor_manager.process_sensor_message(topic, payload)
    print(f"✅ Processed sensor message for topic: {topic}")
    
    # UI Access
    sensor_data = sensor_manager.get_sensor_data(topic)
    print(f"\n📊 Temperature: {sensor_data.get('temperature', 0):.1f}°C")
    print()


def example_module_manager():
    """Example: Using ModuleManager for module status access"""
    print("=" * 60)
    print("Example 2: ModuleManager State-Holder Pattern")
    print("=" * 60)
    
    module_manager = get_ccu_module_manager()
    
    # Simulate MQTT messages
    module_manager.process_module_message(
        "module/v1/ff/HBW/connection",
        {"connectionState": "connected"}
    )
    module_manager.process_module_message(
        "module/v1/ff/HBW/state",
        {"available": "READY"}
    )
    
    # UI Access
    status = module_manager.get_module_status("HBW")
    print(f"✅ Module HBW Status:")
    print(f"  - Connected: {status.get('connected')}")
    print(f"  - Available: {status.get('available')}")
    print()


if __name__ == "__main__":
    print("\nCCU Manager State-Holder Pattern Examples\n")
    example_sensor_manager()
    example_module_manager()
    print("✅ All examples completed!")
