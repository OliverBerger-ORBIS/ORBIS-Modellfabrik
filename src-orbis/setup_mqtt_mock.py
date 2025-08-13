#!/usr/bin/env python3
"""
Setup Script für MQTT Mock System
Orbis Development - Quick Setup
"""

import subprocess
import sys
import time
import os

def check_mqtt_broker():
    """Check if MQTT broker is running"""
    try:
        import paho.mqtt.client as mqtt
        client = mqtt.Client()
        client.connect("localhost", 1883, 5)
        client.disconnect()
        return True
    except:
        return False

def start_mqtt_broker():
    """Start MQTT broker if not running"""
    print("🔍 Checking MQTT broker...")
    
    if check_mqtt_broker():
        print("✅ MQTT broker is already running")
        return True
    
    print("⚠️  MQTT broker not found. Starting...")
    
    # Try to start mosquitto
    try:
        # Check if mosquitto is installed
        result = subprocess.run(["which", "mosquitto"], capture_output=True, text=True)
        if result.returncode == 0:
            print("🚀 Starting mosquitto...")
            subprocess.Popen(["mosquitto", "-p", "1883"])
            time.sleep(2)
            
            if check_mqtt_broker():
                print("✅ MQTT broker started successfully")
                return True
            else:
                print("❌ Failed to start MQTT broker")
                return False
        else:
            print("❌ mosquitto not found. Please install it first:")
            print("   brew install mosquitto")
            return False
            
    except Exception as e:
        print(f"❌ Error starting MQTT broker: {e}")
        return False

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "paho-mqtt>=1.6.1"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MQTT Mock System Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start MQTT broker
    if not start_mqtt_broker():
        print("\n📋 Manual Setup Required:")
        print("1. Install mosquitto: brew install mosquitto")
        print("2. Start mosquitto: mosquitto -p 1883")
        print("3. Run this script again")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Start mock system: python mqtt_mock.py")
    print("2. Start test client: python mqtt_test_client.py")
    print("3. Or run demo: python setup_mqtt_mock.py --demo")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run demo
        print("🎬 Starting MQTT Demo...")
        
        # Start mock system in background
        mock_process = subprocess.Popen([sys.executable, "mqtt_mock.py"])
        
        # Wait for startup
        time.sleep(3)
        
        # Run test client
        test_process = subprocess.Popen([sys.executable, "mqtt_test_client.py"])
        
        try:
            test_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping demo...")
            mock_process.terminate()
            test_process.terminate()
    else:
        main()
