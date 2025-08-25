#!/usr/bin/env python3
"""
ORBIS Dashboard - Complete Test Suite
Führt alle Tests aus und gibt einen Überblick
"""

import sys
import subprocess
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_file(test_file):
    """Führt einen einzelnen Test aus"""
    print(f"🧪 Running {test_file}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Test passed!")
            return True
        else:
            print("❌ Test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def main():
    """Hauptfunktion für Test-Suite"""
    print("🧪 ORBIS Dashboard - Complete Test Suite")
    print("=" * 60)
    
    # Test files to run
    test_files = [
        "tests_orbis/test_dashboard_imports.py",
        "tests_orbis/test_streamlit_startup.py",
        "tests_orbis/test_dashboard_functionality.py",
        "tests_orbis/test_dashboard_runtime.py",
        "tests_orbis/test_default_session.py",
        "tests_orbis/test_database_structure.py",
        "tests_orbis/test_template_message_manager.py",  # NEUER TEMPLATE MANAGER TEST
        "tests_orbis/test_icon_configuration.py",  # NEUER ICON CONFIG TEST
        "tests_orbis/test_template_control_dashboard.py",  # NEUER TEMPLATE CONTROL TEST
        "tests_orbis/test_filter_improvements.py",  # NEUER FILTER IMPROVEMENTS TEST
        "tests_orbis/test_filter_integration.py",  # NEUER FILTER INTEGRATION TEST
    
    ]
    
    results = []
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_test_file(test_file)
            results.append((test_file, success))
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results.append((test_file, False))
    
    # Summary
    print("=" * 60)
    print("📊 FINAL TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_file, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_file}: {status}")
        if success:
            passed += 1
    
    print("=" * 60)
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! Dashboard is ready for production.")
    else:
        print(f"⚠️  {passed}/{len(results)} tests passed. Some issues need attention.")
    print("=" * 60)


if __name__ == "__main__":
    main()
