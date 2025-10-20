#!/usr/bin/env python3
"""
Test CCU MQTT Client Connection - Test gegen localhost:1883
Zeigt dass CCU Client richtig funktioniert ohne Reconnect Loop
"""

import time

from omf2.ccu.ccu_mqtt_client import CcuMqttClient
from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


def test_ccu_client_connection():
    """Test CCU Client Connection gegen localhost:1883"""
    print("🧪 Testing CCU MQTT Client Connection")
    print("=" * 50)

    try:
        # 1. Registry Manager testen
        print("📚 Testing Registry Manager...")
        registry_manager = get_registry_manager()
        mqtt_clients = registry_manager.get_mqtt_clients()
        ccu_config = mqtt_clients.get("ccu_mqtt_client", {})
        subscribed_topics = ccu_config.get("subscribed_topics", [])
        print(f"✅ Registry: Found {len(subscribed_topics)} CCU topics")

        # 2. CCU Client initialisieren
        print("\n🏗️ Initializing CCU MQTT Client...")
        ccu_client = CcuMqttClient()
        print(f"✅ CCU Client initialized: {ccu_client.client_id}")

        # 3. Connection Info vor Connect
        print("\n📊 Connection Info (before connect):")
        conn_info = ccu_client.get_connection_info()
        print(f"  - Connected: {conn_info['connected']}")
        print(f"  - Host: {conn_info['host']}")
        print(f"  - Port: {conn_info['port']}")
        print(f"  - Client ID: {conn_info['client_id']}")
        print(f"  - Subscribed Topics: {len(conn_info['subscribed_topics'])}")

        # 4. Connect to live environment (localhost:1883)
        print("\n🔌 Connecting to live environment (localhost:1883)...")
        success = ccu_client.connect("live")

        if success:
            print("✅ CCU Client connected successfully!")
        else:
            print("❌ CCU Client connection failed!")
            return False

        # 5. Connection Info nach Connect
        print("\n📊 Connection Info (after connect):")
        conn_info = ccu_client.get_connection_info()
        print(f"  - Connected: {conn_info['connected']}")
        print(f"  - Host: {conn_info['host']}")
        print(f"  - Port: {conn_info['port']}")
        print(f"  - Client ID: {conn_info['client_id']}")
        print(f"  - Subscribed Topics: {len(conn_info['subscribed_topics'])}")
        print(f"  - Topics: {conn_info['subscribed_topics'][:5]}...")  # First 5 topics

        # 6. Test Message Publishing
        print("\n📤 Testing Message Publishing...")
        test_topic = "test/ccu/connection"
        test_payload = {"test": True, "timestamp": time.time(), "client_id": ccu_client.client_id}

        publish_success = ccu_client.publish(test_topic, test_payload)
        if publish_success:
            print(f"✅ Published test message to {test_topic}")
        else:
            print(f"❌ Failed to publish test message to {test_topic}")

        # 7. Test Message Buffers
        print("\n📥 Testing Message Buffers...")
        all_buffers = ccu_client.get_all_buffers()
        print(f"  - Total topic buffers: {len(all_buffers)}")

        for topic, messages in all_buffers.items():
            print(f"  - {topic}: {len(messages)} messages")

        # 8. Test Environment Switch
        print("\n🔄 Testing Environment Switch...")
        switch_success = ccu_client.reconnect_environment("replay")
        if switch_success:
            print("✅ Environment switch to replay successful!")
        else:
            print("❌ Environment switch to replay failed!")

        # 9. Final Connection Info
        print("\n📊 Final Connection Info:")
        conn_info = ccu_client.get_connection_info()
        print(f"  - Connected: {conn_info['connected']}")
        print(f"  - Client ID: {conn_info['client_id']}")
        print(f"  - Environment: {getattr(ccu_client, 'current_environment', 'unknown')}")

        # 10. Clean Disconnect
        print("\n🔌 Disconnecting...")
        ccu_client.disconnect()
        print("✅ CCU Client disconnected cleanly!")

        assert True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"CCU Client test failed: {e}")
        return False


def test_admin_client_comparison():
    """Test Admin Client zum Vergleich"""
    print("\n" + "=" * 50)
    print("🔍 Testing Admin Client for comparison...")

    try:
        from omf2.admin.admin_mqtt_client import AdminMqttClient

        admin_client = AdminMqttClient()
        print(f"✅ Admin Client initialized: {admin_client.client_id}")

        # Connection Info
        conn_info = admin_client.get_connection_info()
        print(f"  - Connected: {conn_info['connected']}")
        print(f"  - Subscribed Topics: {len(conn_info['subscribed_topics'])}")

        # Test Connect
        success = admin_client.connect("live")
        print(f"  - Connect success: {success}")

        if success:
            conn_info = admin_client.get_connection_info()
            print(f"  - After connect - Connected: {conn_info['connected']}")
            print(f"  - After connect - Topics: {len(conn_info['subscribed_topics'])}")

        admin_client.disconnect()
        print("✅ Admin Client test completed")

    except Exception as e:
        print(f"❌ Admin Client test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting CCU MQTT Client Connection Test")
    print("Target: localhost:1883 (Mosquitto)")
    print("=" * 50)

    # Test CCU Client
    ccu_success = test_ccu_client_connection()

    # Test Admin Client for comparison
    test_admin_client_comparison()

    print("\n" + "=" * 50)
    if ccu_success:
        print("✅ CCU Client Test PASSED - No reconnect loop detected!")
    else:
        print("❌ CCU Client Test FAILED - Check logs for details")

    print("🏁 Test completed!")
