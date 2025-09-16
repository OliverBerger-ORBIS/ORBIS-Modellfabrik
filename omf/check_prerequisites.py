#!/usr/bin/env python3
"""
Prerequisites Check für MQTT Mock System
Orbis Development - System Requirements Check
"""

import importlib
import socket
import subprocess
import sys


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Too old (need 3.7+)")
        return False


def check_python_packages():
    """Check required Python packages"""
    print("\n📦 Checking Python packages...")

    required_packages = [
        ("paho-mqtt", "paho.mqtt.client"),
        ("json", "json"),
        ("datetime", "datetime"),
        ("logging", "logging"),
        ("threading", "threading"),
    ]

    all_ok = True

    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} - OK")
        except ImportError:
            print(f"❌ {package_name} - Missing")
            all_ok = False

    return all_ok


def check_mqtt_broker():
    """Check if MQTT broker is running"""
    print("\n🔌 Checking MQTT broker...")

    # Check if port 1883 is open
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", 1883))
        sock.close()

        if result == 0:
            print("✅ MQTT broker is running on localhost:1883")
            return True
        else:
            print("❌ MQTT broker not running on localhost:1883")
            return False
    except Exception as e:
        print(f"❌ Error checking MQTT broker: {e}")
        return False


def check_mosquitto_installation():
    """Check if mosquitto is installed"""
    print("\n📋 Checking mosquitto installation...")

    import platform

    try:
        system = platform.system()
        if system == "Windows":
            cmd = ["where", "mosquitto"]
        else:
            cmd = ["which", "mosquitto"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ mosquitto is installed")
            # Check version
            version_result = subprocess.run(["mosquitto", "-h"], capture_output=True, text=True)
            if version_result.returncode == 0:
                print("✅ mosquitto is working")
                return True
            else:
                print("❌ mosquitto is installed but not working")
                return False
        else:
            print("❌ mosquitto is not installed")
            return False
    except Exception as e:
        print(f"❌ Error checking mosquitto: {e}")
        return False


def check_network_connectivity():
    """Check network connectivity"""
    print("\n🌐 Checking network connectivity...")

    try:
        # Test localhost connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("localhost", 1883))
        sock.close()

        if result == 0:
            print("✅ Local network connectivity - OK")
            return True
        else:
            print("❌ Cannot connect to localhost:1883")
            return False
    except Exception as e:
        print(f"❌ Network connectivity error: {e}")
        return False


def test_mqtt_connection():
    """Test actual MQTT connection"""
    print("\n🔍 Testing MQTT connection...")

    try:
        import paho.mqtt.client as mqtt

        client = mqtt.Client()
        client.connect("localhost", 1883, 5)
        client.disconnect()

        print("✅ MQTT connection test successful")
        return True
    except Exception as e:
        print(f"❌ MQTT connection test failed: {e}")
        return False


def main():
    """Main check function"""
    print("🔍 MQTT Mock System - Prerequisites Check")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_python_packages),
        ("Mosquitto Installation", check_mosquitto_installation),
        ("Network Connectivity", check_network_connectivity),
        ("MQTT Broker", check_mqtt_broker),
        ("MQTT Connection", test_mqtt_connection),
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 CHECK SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All prerequisites are met! You can run the MQTT mock system.")
        print("\n🚀 Next steps:")
        print("1. python setup_mqtt_mock.py --demo")
        print("2. Or manually: python mqtt_mock.py")
    else:
        print("\n⚠️  Some prerequisites are missing. Please fix the issues above.")
        print("\n📋 Common solutions:")
        print("1. Install mosquitto: brew install mosquitto")
        print("2. Start mosquitto: mosquitto -p 1883")
        print("3. Install Python packages: pip install paho-mqtt")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
