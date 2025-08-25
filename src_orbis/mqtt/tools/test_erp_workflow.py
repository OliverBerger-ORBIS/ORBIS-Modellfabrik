#!/usr/bin/env python3
"""
Vollständiger ERP Workflow Test

Testet die vollständige Integration von ERP Order-IDs in das APS System.
"""

import json
import time
import uuid
import paho.mqtt.client as mqtt
from datetime import datetime

class ERPWorkflowTest:
    def __init__(self):
        self.client = mqtt.Client()
        self.connected = False
        self.erp_orders = {}
        self.test_results = []
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT Verbindung erfolgreich")
            self.connected = True
        else:
            print(f"❌ MQTT Verbindung fehlgeschlagen: {rc}")
    
    def on_message(self, client, userdata, msg):
        print(f"📨 {msg.topic}")
        try:
            payload = json.loads(msg.payload.decode())
            
            # ERP Order-ID in Response suchen
            if 'erpOrderId' in payload or 'externalOrderId' in payload:
                erp_id = payload.get('erpOrderId') or payload.get('externalOrderId')
                print(f"   ✅ ERP Order-ID gefunden: {erp_id}")
            
            self.test_results.append({
                'topic': msg.topic,
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            })
        except:
            pass
    
    def connect_to_aps(self):
        """Verbindung zum APS System herstellen"""
        print("🔌 Verbinde zum APS System...")
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect("192.168.0.100", 1883, 60)
            self.client.loop_start()
            time.sleep(3)
            return self.connected
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")
            return False
    
    def test_wareneingang_with_erp_id(self):
        """Test: Wareneingang mit ERP Order-ID"""
        print("\n📥 Test: Wareneingang mit ERP Order-ID")
        print("=" * 50)
        
        erp_order_id = f"ERP-STORAGE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "orderType": "STORAGE",
            "type": "BLUE",
            "workpieceId": "047389ca341291",
            "erpOrderId": erp_order_id,
            "externalOrderId": erp_order_id,
            "source": "ERP_SYSTEM"
        }
        
        print(f"📤 Wareneingang Request:")
        print(f"   ERP Order-ID: {erp_order_id}")
        print(f"   Werkstück: 047389ca341291 (BLUE)")
        
        result = self.client.publish("ccu/order/request", json.dumps(payload))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ Wareneingang Request gesendet")
            self.erp_orders[erp_order_id] = {
                'type': 'STORAGE',
                'status': 'SENT',
                'timestamp': datetime.now().isoformat()
            }
            time.sleep(5)
            return True
        else:
            print(f"❌ Fehler: {result.rc}")
            return False
    
    def test_production_with_erp_id(self):
        """Test: Produktionsauftrag mit ERP Order-ID"""
        print("\n🏭 Test: Produktionsauftrag mit ERP Order-ID")
        print("=" * 50)
        
        erp_order_id = f"ERP-PRODUCTION-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "orderType": "PRODUCTION",
            "type": "BLUE",
            "workpieceId": "047389ca341291",
            "erpOrderId": erp_order_id,
            "externalOrderId": erp_order_id,
            "source": "ERP_SYSTEM",
            "productionSteps": [
                "PICK(DRILL)",
                "DRILL(DRILL)",
                "DROP(DRILL)",
                "PICK(MILL)",
                "MILL(MILL)",
                "DROP(MILL)"
            ]
        }
        
        print(f"📤 Produktionsauftrag Request:")
        print(f"   ERP Order-ID: {erp_order_id}")
        print(f"   Produktionsschritte: {len(payload['productionSteps'])}")
        
        result = self.client.publish("ccu/order/request", json.dumps(payload))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ Produktionsauftrag Request gesendet")
            self.erp_orders[erp_order_id] = {
                'type': 'PRODUCTION',
                'status': 'SENT',
                'timestamp': datetime.now().isoformat()
            }
            time.sleep(5)
            return True
        else:
            print(f"❌ Fehler: {result.rc}")
            return False
    
    def test_direct_module_commands(self):
        """Test: Direkte Modul Commands mit ERP Order-ID"""
        print("\n🔧 Test: Direkte Modul Commands")
        print("=" * 50)
        
        erp_order_id = f"ERP-DIRECT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # HBW PICK Command
        hbw_payload = {
            "serialNumber": "SVR3QA0022",
            "orderId": erp_order_id,
            "orderUpdateId": 1,
            "erpOrderId": erp_order_id,
            "action": {
                "id": str(uuid.uuid4()),
                "command": "PICK",
                "metadata": {
                    "type": "BLUE",
                    "erpOrderId": erp_order_id,
                    "priority": "HIGH"
                }
            }
        }
        
        print(f"📤 HBW PICK Command:")
        print(f"   ERP Order-ID: {erp_order_id}")
        print(f"   Modul: HBW (SVR3QA0022)")
        
        result = self.client.publish("module/v1/ff/SVR3QA0022/order", json.dumps(hbw_payload))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ HBW PICK Command gesendet")
            time.sleep(3)
            
            # DRILL Command
            drill_payload = {
                "serialNumber": "SVR4H76449",
                "orderId": erp_order_id,
                "orderUpdateId": 2,
                "erpOrderId": erp_order_id,
                "action": {
                    "id": str(uuid.uuid4()),
                    "command": "DRILL",
                    "metadata": {
                        "type": "BLUE",
                        "erpOrderId": erp_order_id
                    }
                }
            }
            
            print(f"📤 DRILL Command:")
            print(f"   ERP Order-ID: {erp_order_id}")
            print(f"   Modul: DRILL (SVR4H76449)")
            
            result = self.client.publish("module/v1/ff/SVR4H76449/order", json.dumps(drill_payload))
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("✅ DRILL Command gesendet")
                time.sleep(3)
                return True
            else:
                print(f"❌ DRILL Command Fehler: {result.rc}")
                return False
        else:
            print(f"❌ HBW Command Fehler: {result.rc}")
            return False
    
    def print_summary(self):
        """Zusammenfassung ausgeben"""
        print("\n📊 Test-Zusammenfassung")
        print("=" * 50)
        
        print(f"📋 ERP Orders gesendet: {len(self.erp_orders)}")
        for erp_id, info in self.erp_orders.items():
            print(f"   - {erp_id}: {info['type']} ({info['status']})")
        
        print(f"\n📨 Responses empfangen: {len(self.test_results)}")
        for result in self.test_results:
            print(f"   - {result['topic']}: {result['timestamp']}")
        
        # ERP Order-ID Erfolg prüfen
        erp_success = 0
        for result in self.test_results:
            payload = result['payload']
            if 'erpOrderId' in payload or 'externalOrderId' in payload:
                erp_success += 1
        
        print(f"\n✅ ERP Order-ID Erfolg: {erp_success}/{len(self.test_results)} Responses")
        
        if erp_success > 0:
            print("🎉 ERP Order-ID Integration funktioniert!")
        else:
            print("❌ ERP Order-ID Integration nicht erfolgreich")
    
    def cleanup(self):
        """Aufräumen"""
        print("\n🧹 Aufräumen...")
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
        print("✅ Test beendet")

def main():
    """Hauptfunktion"""
    print("🚀 Vollständiger ERP Workflow Test")
    print("=" * 50)
    
    test = ERPWorkflowTest()
    
    try:
        if not test.connect_to_aps():
            print("❌ Test abgebrochen - Keine Verbindung")
            return
        
        # 1. Wareneingang Test
        test.test_wareneingang_with_erp_id()
        
        # 2. Produktionsauftrag Test
        test.test_production_with_erp_id()
        
        # 3. Direkte Modul Commands Test
        test.test_direct_module_commands()
        
        # 4. Zusammenfassung
        test.print_summary()
        
    except KeyboardInterrupt:
        print("\n⚠️ Test durch Benutzer abgebrochen")
    except Exception as e:
        print(f"\n❌ Test-Fehler: {e}")
    finally:
        test.cleanup()

if __name__ == "__main__":
    main()
