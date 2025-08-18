#!/usr/bin/env python3
"""
Test für Streamlit Dashboard Startup
Prüft, ob das Dashboard ohne Fehler startet
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_streamlit_startup():
    """Test: Dashboard kann mit Streamlit gestartet werden"""
    print("🧪 Testing Streamlit Dashboard Startup...")
    print("=" * 50)
    
    dashboard_path = project_root / "src_orbis" / "mqtt" / "dashboard" / "aps_dashboard.py"
    test_port = 8520  # Use different port for testing
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False
    
    print(f"📁 Dashboard path: {dashboard_path}")
    print(f"🌐 Test port: {test_port}")
    
    try:
        # Start Streamlit in background
        print("🚀 Starting Streamlit...")
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path), 
            "--server.port", str(test_port),
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        print("⏳ Waiting for startup...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
        
        # Test HTTP connection
        print("🔍 Testing HTTP connection...")
        try:
            response = requests.get(f"http://localhost:{test_port}", timeout=10)
            if response.status_code == 200:
                print("✅ HTTP connection successful")
                success = True
            else:
                print(f"❌ HTTP connection failed: {response.status_code}")
                success = False
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP connection error: {e}")
            success = False
        
        # Cleanup
        print("🧹 Cleaning up...")
        process.terminate()
        process.wait(timeout=5)
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_import_validation():
    """Test: Alle Imports funktionieren"""
    print("\n🔍 Testing Import Validation...")
    print("=" * 50)
    
    try:
        # Test basic imports
        from src_orbis.mqtt.dashboard.config.settings import APS_MODULES_EXTENDED
        print("✅ Config settings import: OK")
        
        from src_orbis.mqtt.dashboard.utils.data_handling import extract_module_info
        print("✅ Utils import: OK")
        
        from src_orbis.mqtt.dashboard.components.filters import create_filters
        print("✅ Components import: OK")
        
        from src_orbis.mqtt.tools.mqtt_message_library import MQTTMessageLibrary
        print("✅ MQTT library import: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 ORBIS Dashboard Test Suite")
    print("=" * 60)
    
    # Test 1: Import validation
    import_success = test_import_validation()
    
    # Test 2: Streamlit startup (only if imports work)
    if import_success:
        startup_success = test_streamlit_startup()
    else:
        print("⏭️ Skipping Streamlit test due to import failures")
        startup_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   Import Validation: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Streamlit Startup: {'✅ PASS' if startup_success else '❌ FAIL'}")
    
    if import_success and startup_success:
        print("\n🎉 ALL TESTS PASSED! Dashboard is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print("=" * 60)
