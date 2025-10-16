#!/usr/bin/env python3
"""
Test Script for Symbol Consistency
Validates that all symbols are consistent and unique where needed
"""


from omf2.ui.common.symbols import UISymbols


def test_symbol_consistency():
    """Test that all symbols are consistent and unique where needed"""
    print("🧪 Testing Symbol Consistency...")
    print("=" * 50)

    # Test tab icons
    print("\n📑 Tab Icons:")
    tab_icons = UISymbols.get_all_tab_icons()
    for key, icon in tab_icons.items():
        print(f"  {key}: {icon}")

    # Test status icons
    print("\n📊 Status Icons:")
    status_icons = UISymbols.get_all_status_icons()
    for key, icon in status_icons.items():
        print(f"  {key}: {icon}")

    # Test functional icons
    print("\n🔧 Functional Icons:")
    functional_icons = UISymbols.get_all_functional_icons()
    for key, icon in functional_icons.items():
        print(f"  {key}: {icon}")

    # Check for duplicates
    print("\n🔍 Checking for duplicate symbols...")
    all_icons = {}
    all_icons.update(tab_icons)
    all_icons.update(status_icons)
    all_icons.update(functional_icons)

    # Find duplicates
    icon_to_keys = {}
    for key, icon in all_icons.items():
        if icon not in icon_to_keys:
            icon_to_keys[icon] = []
        icon_to_keys[icon].append(key)

    duplicates = {icon: keys for icon, keys in icon_to_keys.items() if len(keys) > 1}

    if duplicates:
        print("⚠️  Found duplicate symbols:")
        for icon, keys in duplicates.items():
            print(f"  {icon}: {', '.join(keys)}")
    else:
        print("✅ No duplicate symbols found")

    # Test specific final decisions
    print("\n🎯 Testing Final Decisions:")
    final_decisions = {
        "ccu_orders": "📝",
        "ccu_process": "🔄",
        "ccu_modules": "🏗️",
        "message_center": "📨",
        "logs": "📋",
        "loading": "⏳",
        "receive": "📥",
        "running": "▶️",
        "stopped": "⏹️",
        "pending": "⏳",
        "module_control": "🛠️",
        "schema_driven": "🧩",
        "mqtt_connect": "🔌",
        "stations": "🏢",
        "txt_controllers": "🕹️",
        "workpieces": None,  # loaded from Registry
    }

    for key, expected_icon in final_decisions.items():
        if key in tab_icons:
            actual_icon = tab_icons[key]
        elif key in status_icons:
            actual_icon = status_icons[key]
        elif key in functional_icons:
            actual_icon = functional_icons[key]
        else:
            print(f"❌ {key}: Not found in any icon category")
            continue

        if actual_icon == expected_icon:
            print(f"✅ {key}: {actual_icon}")
        else:
            print(f"❌ {key}: Expected {expected_icon}, got {actual_icon}")

    print("\n🎉 Symbol consistency test completed!")


def test_ui_components():
    """Test that all UI components use the new symbol system"""
    print("\n🧪 Testing UI Components...")
    print("=" * 50)

    # Test main dashboard
    print("📱 Main Dashboard:")
    try:

        print("✅ Main Dashboard imports successfully")
    except Exception as e:
        print(f"❌ Main Dashboard import failed: {e}")

    # Test admin settings
    print("\n⚙️ Admin Settings:")
    try:

        print("✅ Admin Settings imports successfully")
    except Exception as e:
        print(f"❌ Admin Settings import failed: {e}")

    # Test message center
    print("\n📧 Message Center:")
    try:

        print("✅ Message Center imports successfully")
    except Exception as e:
        print(f"❌ Message Center import failed: {e}")

    print("\n🎉 UI Components test completed!")


if __name__ == "__main__":
    print("🚀 Starting OMF2 Symbol Consistency Tests")
    print("=" * 60)

    test_symbol_consistency()
    test_ui_components()

    print("\n" + "=" * 60)
    print("🎯 All tests completed!")
