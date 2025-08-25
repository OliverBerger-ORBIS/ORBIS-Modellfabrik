#!/usr/bin/env python3
"""
ERP Order-ID Integration Test

Testet die Integration von ERP Order-IDs in das APS System.
"""

import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

class ERPIntegrationTest:
    def __init__(self):
        self.client = mqtt.Client()
        self.connected = False
        self.test_results = []
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT Verbindung erfolgreich")
            self.connected = True
        else:
            print(f"❌ MQTT Verbindung fehlgeschlagen: {rc}")
    
    def on_message(self, client, userdata, msg):
        print(f"📨 Nachricht empfangen: {msg.topic}")
        try:
            payload = json.loads(msg.payload.decode())
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            
            # Test-Ergebnis speichern
            self.test_results.append({
                'topic': msg.topic,
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            })
        except:
            print(f"   Raw: {msg.payload.decode()}")
    
    def connect_to_aps(self):
        """Verbindung zum APS System herstellen"""
        print("🔌 Verbinde zum APS System...")
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect("192.168.0.100", 1883, 60)
            self.client.loop_start()
            
            # Warten auf Verbindung
            time.sleep(3)
            
            if self.connected:
                print("✅ Verbindung zum APS System hergestellt")
                return True
            else:
                print("❌ Verbindung zum APS System fehlgeschlagen")
                return False
                
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")
            return False
    
    def test_erp_order_injection(self):
        """Test: ERP Order-ID in CCU injizieren"""
        print("\n🎯 Test 1: ERP Order-ID Injection")
        print("=" * 50)
        
        if not self.connected:
            print("❌ Keine MQTT Verbindung")
            return False
        
        # ERP Order-ID definieren
        erp_order_id = "ERP-TEST-2024-001"
        
        # CCU Order Request mit ERP Order-ID
        payload = {
            "timestamp": datetime.now().isoformat(),
            "orderType": "STORAGE",
            "type": "BLUE",
            "workpieceId": "047389ca341291",
            "erpOrderId": erp_order_id,
            "externalOrderId": erp_order_id,
            "source": "ERP_SYSTEM"
        }
        
        print(f"📤 Sende ERP Order Request:")
        print(f"   Topic: ccu/order/request")
        print(f"   ERP Order-ID: {erp_order_id}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        # Message senden
        result = self.client.publish("ccu/order/request", json.dumps(payload))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ ERP Order Request gesendet")
            
            # 10 Sekunden warten auf Response
            print("⏳ Warte auf CCU Response (10 Sekunden)...")
            time.sleep(10)
            
            return True
        else:
            print(f"❌ Fehler beim Senden: {result.rc}")
            return False
    
    def test_module_command_with_erp_id(self):
        """Test: Modul Command mit ERP Order-ID"""
        print("\n🎯 Test 2: Modul Command mit ERP Order-ID")
        print("=" * 50)
        
        if not self.connected:
            print("❌ Keine MQTT Verbindung")
            return False
        
        # ERP Order-ID verwenden
        erp_order_id = "ERP-TEST-2024-001"
        
        # HBW PICK Command mit ERP Order-ID
        payload = {
            "serialNumber": "SVR3QA0022",
            "orderId": erp_order_id,
            "orderUpdateId": 1,
            "erpOrderId": erp_order_id,
            "action": {
                "id": "test-action-001",
                "command": "PICK",
                "metadata": {
                    "type": "BLUE",
                    "erpOrderId": erp_order_id,
                    "priority": "HIGH"
                }
            }
        }
        
        print(f"📤 Sende Modul Command:")
        print(f"   Topic: module/v1/ff/SVR3QA0022/order")
        print(f"   ERP Order-ID: {erp_order_id}")
        print(f"   Command: PICK")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        # Message senden
        result = self.client.publish("module/v1/ff/SVR3QA0022/order", json.dumps(payload))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ Modul Command gesendet")
            
            # 10 Sekunden warten auf Response
            print("⏳ Warte auf Modul Response (10 Sekunden)...")
            time.sleep(10)
            
            return True
        else:
            print(f"❌ Fehler beim Senden: {result.rc}")
            return False
    
    def print_test_results(self):
        """Test-Ergebnisse ausgeben"""
        print("\n📊 Test-Ergebnisse")
        print("=" * 50)
        
        if not self.test_results:
            print("❌ Keine Responses empfangen")
            return
        
        for i, result in enumerate(self.test_results, 1):
            print(f"\n{i}. Response:")
            print(f"   Topic: {result['topic']}")
            print(f"   Zeit: {result['timestamp']}")
            print(f"   Payload: {json.dumps(result['payload'], indent=2)}")
    
    def cleanup(self):
        """Aufräumen"""
        print("\n🧹 Aufräumen...")
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
        print("✅ Test beendet")

def main():
    """Hauptfunktion"""
    print("🚀 ERP Order-ID Integration Test")
    print("=" * 50)
    
    # Test-Instanz erstellen
    test = ERPIntegrationTest()
    
    try:
        # 1. Verbindung herstellen
        if not test.connect_to_aps():
            print("❌ Test abgebrochen - Keine Verbindung")
            return
        
        # 2. ERP Order-ID Injection Test
        test.test_erp_order_injection()
        
        # 3. Modul Command Test
        test.test_module_command_with_erp_id()
        
        # 4. Ergebnisse ausgeben
        test.print_test_results()
        
    except KeyboardInterrupt:
        print("\n⚠️ Test durch Benutzer abgebrochen")
    except Exception as e:
        print(f"\n❌ Test-Fehler: {e}")
    finally:
        test.cleanup()

if __name__ == "__main__":
    main()
