#!/usr/bin/env python3
"""
ERP Order-ID Integration

Ermöglicht die Verwendung von ERP Order-IDs anstelle der automatisch generierten CCU Order-IDs.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ERPOrderIDIntegration:
    """Integration von ERP Order-IDs in das APS System"""
    
    def __init__(self, mqtt_client=None):
        self.mqtt_client = mqtt_client
        self.erp_orders = {}  # Speichert ERP Order-IDs und deren Status
        self.ccu_order_mapping = {}  # Mapping zwischen ERP und CCU Order-IDs
        
    def inject_erp_order_id(self, erp_order_id: str, order_type: str, 
                           workpiece_id: str, color: str, 
                           production_steps: Optional[list] = None) -> bool:
        """
        Injiziert eine ERP Order-ID in das APS System
        
        Args:
            erp_order_id: Order-ID vom ERP-System
            order_type: STORAGE oder PRODUCTION
            workpiece_id: NFC-Code des Werkstücks
            color: Farbe (RED, WHITE, BLUE)
            production_steps: Optional - Produktionsschritte für PRODUCTION Orders
        """
        try:
            # 1. ERP Order registrieren
            self.erp_orders[erp_order_id] = {
                'erp_order_id': erp_order_id,
                'order_type': order_type,
                'workpiece_id': workpiece_id,
                'color': color,
                'production_steps': production_steps,
                'status': 'INJECTED',
                'timestamp': datetime.now().isoformat(),
                'ccu_order_id': None,
                'ccu_response': None
            }
            
            # 2. CCU Order Request mit ERP Order-ID senden
            success = self._send_ccu_order_request_with_erp_id(erp_order_id)
            
            if success:
                logger.info(f"✅ ERP Order-ID {erp_order_id} erfolgreich injiziert")
                return True
            else:
                logger.error(f"❌ Fehler beim Injizieren der ERP Order-ID {erp_order_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler bei ERP Order-ID Integration: {e}")
            return False
    
    def _send_ccu_order_request_with_erp_id(self, erp_order_id: str) -> bool:
        """Sendet CCU Order Request mit ERP Order-ID"""
        try:
            order_info = self.erp_orders[erp_order_id]
            
            # CCU Order Request Payload mit ERP Order-ID
            payload = {
                "timestamp": datetime.now().isoformat(),
                "orderType": order_info['order_type'],
                "type": order_info['color'],
                "workpieceId": order_info['workpiece_id'],
                "erpOrderId": erp_order_id,  # ERP Order-ID hinzufügen
                "externalOrderId": erp_order_id,  # Alternative Feld
                "source": "ERP_SYSTEM"  # Quelle kennzeichnen
            }
            
            # Produktionsschritte hinzufügen falls vorhanden
            if order_info['production_steps']:
                payload["productionSteps"] = order_info['production_steps']
            
            # MQTT Message senden
            if self.mqtt_client and self.mqtt_client.is_connected():
                topic = "ccu/order/request"
                message = json.dumps(payload)
                
                result = self.mqtt_client.publish(topic, message)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"📤 CCU Order Request gesendet: {erp_order_id}")
                    return True
                else:
                    logger.error(f"❌ MQTT Fehler: {result.rc}")
                    return False
            else:
                logger.error("❌ MQTT Client nicht verbunden")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Senden des CCU Order Requests: {e}")
            return False
    
    def handle_ccu_response(self, topic: str, payload: Dict[str, Any]) -> bool:
        """Behandelt CCU Responses und verknüpft mit ERP Order-IDs"""
        try:
            # CCU Order Response verarbeiten
            if topic == "ccu/order/active":
                return self._handle_ccu_order_active(payload)
            elif topic == "ccu/order/completed":
                return self._handle_ccu_order_completed(payload)
            elif topic == "ccu/order/failed":
                return self._handle_ccu_order_failed(payload)
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Verarbeiten der CCU Response: {e}")
            return False
    
    def _handle_ccu_order_active(self, payload: Dict[str, Any]) -> bool:
        """Behandelt ccu/order/active Response"""
        try:
            if isinstance(payload, list):
                for order in payload:
                    ccu_order_id = order.get('orderId')
                    erp_order_id = order.get('erpOrderId') or order.get('externalOrderId')
                    
                    if erp_order_id and erp_order_id in self.erp_orders:
                        # ERP Order mit CCU Order verknüpfen
                        self.erp_orders[erp_order_id]['ccu_order_id'] = ccu_order_id
                        self.erp_orders[erp_order_id]['status'] = 'ACTIVE'
                        self.erp_orders[erp_order_id]['ccu_response'] = order
                        
                        self.ccu_order_mapping[ccu_order_id] = erp_order_id
                        
                        logger.info(f"✅ ERP Order {erp_order_id} → CCU Order {ccu_order_id}")
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"❌ Fehler bei ccu/order/active: {e}")
            return False
    
    def _handle_ccu_order_completed(self, payload: Dict[str, Any]) -> bool:
        """Behandelt ccu/order/completed Response"""
        try:
            ccu_order_id = payload.get('orderId')
            erp_order_id = self.ccu_order_mapping.get(ccu_order_id)
            
            if erp_order_id and erp_order_id in self.erp_orders:
                self.erp_orders[erp_order_id]['status'] = 'COMPLETED'
                self.erp_orders[erp_order_id]['completion_time'] = datetime.now().isoformat()
                
                logger.info(f"✅ ERP Order {erp_order_id} abgeschlossen")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ Fehler bei ccu/order/completed: {e}")
            return False
    
    def _handle_ccu_order_failed(self, payload: Dict[str, Any]) -> bool:
        """Behandelt ccu/order/failed Response"""
        try:
            ccu_order_id = payload.get('orderId')
            erp_order_id = self.ccu_order_mapping.get(ccu_order_id)
            
            if erp_order_id and erp_order_id in self.erp_orders:
                self.erp_orders[erp_order_id]['status'] = 'FAILED'
                self.erp_orders[erp_order_id]['error'] = payload.get('error', 'Unknown error')
                
                logger.error(f"❌ ERP Order {erp_order_id} fehlgeschlagen")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ Fehler bei ccu/order/failed: {e}")
            return False
    
    def get_erp_order_status(self, erp_order_id: str) -> Optional[Dict[str, Any]]:
        """Gibt den Status einer ERP Order zurück"""
        return self.erp_orders.get(erp_order_id)
    
    def get_all_erp_orders(self) -> Dict[str, Dict[str, Any]]:
        """Gibt alle ERP Orders zurück"""
        return self.erp_orders.copy()
    
    def inject_module_command_with_erp_id(self, erp_order_id: str, module_serial: str, 
                                        command: str, metadata: Optional[Dict] = None) -> bool:
        """
        Injiziert ein Modul-Command mit ERP Order-ID
        
        Args:
            erp_order_id: ERP Order-ID
            module_serial: Modul Serial Number
            command: Command (PICK, DROP, etc.)
            metadata: Optional - Zusätzliche Metadaten
        """
        try:
            if erp_order_id not in self.erp_orders:
                logger.error(f"❌ ERP Order {erp_order_id} nicht gefunden")
                return False
            
            order_info = self.erp_orders[erp_order_id]
            
            # Modul Command mit ERP Order-ID
            payload = {
                "serialNumber": module_serial,
                "orderId": order_info.get('ccu_order_id', erp_order_id),  # CCU Order-ID oder ERP Order-ID
                "orderUpdateId": 1,
                "erpOrderId": erp_order_id,  # ERP Order-ID hinzufügen
                "action": {
                    "id": str(uuid.uuid4()),
                    "command": command,
                    "metadata": metadata or {
                        "priority": "NORMAL",
                        "timeout": 300,
                        "type": order_info['color'],
                        "erpOrderId": erp_order_id
                    }
                }
            }
            
            # MQTT Message senden
            if self.mqtt_client and self.mqtt_client.is_connected():
                topic = f"module/v1/ff/{module_serial}/order"
                message = json.dumps(payload)
                
                result = self.mqtt_client.publish(topic, message)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"📤 Modul Command gesendet: {module_serial} - {command} - {erp_order_id}")
                    return True
                else:
                    logger.error(f"❌ MQTT Fehler: {result.rc}")
                    return False
            else:
                logger.error("❌ MQTT Client nicht verbunden")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Senden des Modul Commands: {e}")
            return False

def create_erp_order_example():
    """Beispiel für ERP Order-ID Integration"""
    
    # MQTT Client erstellen
    client = mqtt.Client()
    
    # ERP Integration initialisieren
    erp_integration = ERPOrderIDIntegration(client)
    
    # Beispiel 1: Wareneingang mit ERP Order-ID
    erp_order_id = "ERP-STORAGE-2024-001"
    success = erp_integration.inject_erp_order_id(
        erp_order_id=erp_order_id,
        order_type="STORAGE",
        workpiece_id="047389ca341291",
        color="BLUE"
    )
    
    if success:
        print(f"✅ ERP Order {erp_order_id} injiziert")
    
    # Beispiel 2: Produktionsauftrag mit ERP Order-ID
    erp_order_id = "ERP-PRODUCTION-2024-001"
    success = erp_integration.inject_erp_order_id(
        erp_order_id=erp_order_id,
        order_type="PRODUCTION",
        workpiece_id="047389ca341291",
        color="BLUE",
        production_steps=[
            "PICK(DRILL)",
            "DRILL(DRILL)",
            "DROP(DRILL)",
            "PICK(MILL)",
            "MILL(MILL)",
            "DROP(MILL)"
        ]
    )
    
    if success:
        print(f"✅ ERP Order {erp_order_id} injiziert")
    
    # Beispiel 3: Direkter Modul Command mit ERP Order-ID
    success = erp_integration.inject_module_command_with_erp_id(
        erp_order_id="ERP-PRODUCTION-2024-001",
        module_serial="SVR3QA0022",  # HBW
        command="PICK",
        metadata={
            "type": "BLUE",
            "erpOrderId": "ERP-PRODUCTION-2024-001",
            "priority": "HIGH"
        }
    )
    
    if success:
        print("✅ Modul Command mit ERP Order-ID gesendet")

def main():
    """Hauptfunktion"""
    print("🚀 ERP Order-ID Integration Beispiel")
    print("=" * 50)
    
    create_erp_order_example()
    
    print("\n📋 Verfügbare Funktionen:")
    print("1. inject_erp_order_id() - ERP Order-ID in CCU injizieren")
    print("2. inject_module_command_with_erp_id() - Modul Command mit ERP Order-ID")
    print("3. get_erp_order_status() - Status einer ERP Order abfragen")
    print("4. get_all_erp_orders() - Alle ERP Orders anzeigen")

if __name__ == "__main__":
    main()
