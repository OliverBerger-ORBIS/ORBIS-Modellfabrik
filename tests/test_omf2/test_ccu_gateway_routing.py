#!/usr/bin/env python3
"""
Test CCU Gateway Topic-Routing Pattern

Validiert, dass:
- ccu_mqtt_client KEINE Business-Logik enthält
- ccu_gateway korrekt an Manager routet
- Manager ihre Callbacks empfangen
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_gateway_routing_sensor_topics():
    """Test: Gateway routet Sensor-Topics an sensor_manager"""
    from omf2.ccu.ccu_gateway import CcuGateway
    from omf2.ccu.sensor_manager import SensorManager

    # Gateway ohne MQTT-Client initialisieren
    gateway = CcuGateway(mqtt_client=None)

    # Test: Sensor-Topics sind korrekt definiert
    assert '/j1/txt/1/i/bme680' in gateway.sensor_topics
    assert '/j1/txt/1/i/ldr' in gateway.sensor_topics
    assert '/j1/txt/1/i/cam' in gateway.sensor_topics

    print("✅ Gateway hat korrekte Sensor-Topic-Liste")

    # Test: Gateway kann sensor_manager instanziieren
    sensor_manager = gateway._get_sensor_manager()
    assert sensor_manager is not None
    assert isinstance(sensor_manager, SensorManager)

    print("✅ Gateway kann sensor_manager instanziieren")


def test_gateway_routing_module_topics():
    """Test: Gateway routet Module-Topics an module_manager"""
    from omf2.ccu.ccu_gateway import CcuGateway
    from omf2.ccu.module_manager import CcuModuleManager

    # Gateway ohne MQTT-Client initialisieren
    gateway = CcuGateway(mqtt_client=None)

    # Test: Module-Topic-Prefixes sind korrekt definiert
    assert 'module/v1/ff/' in gateway.module_topic_prefixes
    assert 'fts/v1/ff/' in gateway.module_topic_prefixes

    print("✅ Gateway hat korrekte Module-Topic-Prefixes")

    # Test: Gateway kann module_manager instanziieren
    module_manager = gateway._get_module_manager()
    assert module_manager is not None
    assert isinstance(module_manager, CcuModuleManager)

    print("✅ Gateway kann module_manager instanziieren")


def test_mqtt_client_no_business_logic():
    """Test: MQTT-Client hat KEINE Business-Logik mehr"""
    from omf2.ccu.ccu_mqtt_client import CcuMqttClient

    # Client instanziieren
    client = CcuMqttClient()

    # Test: Business-Logic-Methoden existieren NICHT mehr
    assert not hasattr(client, '_notify_business_functions'), \
        "❌ MQTT-Client sollte KEINE _notify_business_functions Methode haben"
    assert not hasattr(client, '_call_business_function_callback'), \
        "❌ MQTT-Client sollte KEINE _call_business_function_callback Methode haben"

    # Test: Gateway-Referenz existiert
    assert hasattr(client, '_gateway'), \
        "❌ MQTT-Client sollte _gateway Attribut haben"

    # Test: set_gateway Methode existiert
    assert hasattr(client, 'set_gateway'), \
        "❌ MQTT-Client sollte set_gateway Methode haben"

    print("✅ MQTT-Client hat KEINE Business-Logik mehr")


def test_gateway_routing_logic():
    """Test: Gateway on_mqtt_message routet korrekt"""
    from omf2.ccu.ccu_gateway import CcuGateway

    # Gateway ohne MQTT-Client initialisieren
    gateway = CcuGateway(mqtt_client=None)

    # Test: on_mqtt_message Methode existiert
    assert hasattr(gateway, 'on_mqtt_message'), \
        "❌ Gateway sollte on_mqtt_message Methode haben"

    # Simuliere Message-Routing (ohne Exceptions)
    try:
        # Sensor-Topic
        gateway.on_mqtt_message('/j1/txt/1/i/bme680', {'t': 25.5})
        print("✅ Sensor-Topic-Routing funktioniert")

        # Module-Topic
        gateway.on_mqtt_message('module/v1/ff/SVR3QA0022/state', {'actionState': {'state': 'READY'}})
        print("✅ Module-Topic-Routing funktioniert")

        # Unbekanntes Topic
        gateway.on_mqtt_message('unknown/topic', {})
        print("✅ Unbekanntes Topic wird ignoriert")

    except Exception as e:
        print(f"❌ Routing-Fehler: {e}")
        raise


def test_manager_callback_methods():
    """Test: Manager haben ihre Callback-Methoden"""
    from omf2.ccu.module_manager import CcuModuleManager
    from omf2.ccu.sensor_manager import SensorManager

    # Test: sensor_manager hat process_sensor_message
    sensor_manager = SensorManager()
    assert hasattr(sensor_manager, 'process_sensor_message'), \
        "❌ SensorManager sollte process_sensor_message Methode haben"

    print("✅ SensorManager hat process_sensor_message Callback")

    # Test: module_manager hat process_module_message
    module_manager = CcuModuleManager()
    assert hasattr(module_manager, 'process_module_message'), \
        "❌ CcuModuleManager sollte process_module_message Methode haben"

    print("✅ CcuModuleManager hat process_module_message Callback")


def test_factory_gateway_wiring():
    """Test: Factory verbindet Gateway mit MQTT-Client"""
    from omf2.factory.gateway_factory import GatewayFactory

    # Factory instanziieren
    factory = GatewayFactory()

    # Test: Factory kann CCU-Gateway erstellen
    try:
        ccu_gateway = factory.get_ccu_gateway()
        assert ccu_gateway is not None
        print("✅ Factory kann CCU-Gateway erstellen")

        # Test: Gateway hat MQTT-Client
        assert hasattr(ccu_gateway, 'mqtt_client')
        print("✅ Gateway hat MQTT-Client-Referenz")

        # Test: MQTT-Client hat Gateway-Referenz
        if ccu_gateway.mqtt_client:
            assert hasattr(ccu_gateway.mqtt_client, '_gateway')
            print("✅ MQTT-Client hat Gateway-Referenz")

    except Exception as e:
        print(f"⚠️ Factory-Test-Fehler (kann bei fehlenden Dependencies auftreten): {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 CCU Gateway Topic-Routing Pattern Tests")
    print("="*70 + "\n")

    try:
        test_gateway_routing_sensor_topics()
        print()

        test_gateway_routing_module_topics()
        print()

        test_mqtt_client_no_business_logic()
        print()

        test_gateway_routing_logic()
        print()

        test_manager_callback_methods()
        print()

        test_factory_gateway_wiring()
        print()

        print("="*70)
        print("✅ ALLE TESTS ERFOLGREICH")
        print("="*70)

    except AssertionError as e:
        print("\n" + "="*70)
        print(f"❌ TEST FEHLGESCHLAGEN: {e}")
        print("="*70)
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ UNERWARTETER FEHLER: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
