# ERP Order-ID Integration Guide

## 🎯 Übersicht

Diese Anleitung beschreibt, wie man das APS System so manipulieren kann, dass eigene Order-IDs von einem ERP-System verwendet werden, anstelle der automatisch generierten CCU Order-IDs.

## 🔍 Aktuelle System-Architektur

### **Standard Order-ID Vergabe:**
```
Browser Trigger → CCU → CCU generiert Order-ID → Module Commands
```

### **ERP Order-ID Integration:**
```
ERP System → ERP Order-ID → CCU → CCU verwendet ERP Order-ID → Module Commands
```

## 🛠️ Manipulations-Methoden

### **1. CCU Order Request Manipulation**

#### **Standard CCU Order Request:**
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "timestamp": "2024-01-20T10:30:00Z",
    "orderType": "PRODUCTION",
    "type": "BLUE",
    "workpieceId": "047389ca341291"
  }
}
```

#### **Manipulierter CCU Order Request mit ERP Order-ID:**
```json
{
  "topic": "ccu/order/request",
  "payload": {
    "timestamp": "2024-01-20T10:30:00Z",
    "orderType": "PRODUCTION",
    "type": "BLUE",
    "workpieceId": "047389ca341291",
    "erpOrderId": "ERP-PRODUCTION-2024-001",
    "externalOrderId": "ERP-PRODUCTION-2024-001",
    "source": "ERP_SYSTEM"
  }
}
```

### **2. Modul Command Manipulation**

#### **Standard Modul Command:**
```json
{
  "topic": "module/v1/ff/SVR3QA0022/order",
  "payload": {
    "serialNumber": "SVR3QA0022",
    "orderId": "ccu-generated-uuid",
    "orderUpdateId": 1,
    "action": {
      "id": "action-uuid",
      "command": "PICK",
      "metadata": {
        "type": "BLUE"
      }
    }
  }
}
```

#### **Manipulierter Modul Command mit ERP Order-ID:**
```json
{
  "topic": "module/v1/ff/SVR3QA0022/order",
  "payload": {
    "serialNumber": "SVR3QA0022",
    "orderId": "ERP-PRODUCTION-2024-001",
    "orderUpdateId": 1,
    "erpOrderId": "ERP-PRODUCTION-2024-001",
    "action": {
      "id": "action-uuid",
      "command": "PICK",
      "metadata": {
        "type": "BLUE",
        "erpOrderId": "ERP-PRODUCTION-2024-001",
        "priority": "HIGH"
      }
    }
  }
}
```

## 🔧 Implementierungs-Strategien

### **Strategie 1: CCU Request Interception**

#### **Schritt 1: ERP Order-ID in CCU Request injizieren**
```python
def inject_erp_order_id_in_ccu_request(erp_order_id: str, order_type: str, 
                                     workpiece_id: str, color: str):
    payload = {
        "timestamp": datetime.now().isoformat(),
        "orderType": order_type,
        "type": color,
        "workpieceId": workpiece_id,
        "erpOrderId": erp_order_id,  # ERP Order-ID hinzufügen
        "externalOrderId": erp_order_id,  # Alternative Feld
        "source": "ERP_SYSTEM"
    }
    
    # MQTT Message senden
    topic = "ccu/order/request"
    mqtt_client.publish(topic, json.dumps(payload))
```

#### **Schritt 2: CCU Response verarbeiten**
```python
def handle_ccu_response(topic: str, payload: dict):
    if topic == "ccu/order/active":
        for order in payload:
            erp_order_id = order.get('erpOrderId')
            ccu_order_id = order.get('orderId')
            
            if erp_order_id:
                # ERP Order-ID wurde akzeptiert
                print(f"✅ ERP Order {erp_order_id} → CCU Order {ccu_order_id}")
```

### **Strategie 2: Direkte Modul Command Manipulation**

#### **Schritt 1: Modul Commands mit ERP Order-ID senden**
```python
def send_module_command_with_erp_id(erp_order_id: str, module_serial: str, 
                                   command: str, color: str):
    payload = {
        "serialNumber": module_serial,
        "orderId": erp_order_id,  # Direkt ERP Order-ID verwenden
        "orderUpdateId": 1,
        "erpOrderId": erp_order_id,
        "action": {
            "id": str(uuid.uuid4()),
            "command": command,
            "metadata": {
                "type": color,
                "erpOrderId": erp_order_id
            }
        }
    }
    
    topic = f"module/v1/ff/{module_serial}/order"
    mqtt_client.publish(topic, json.dumps(payload))
```

### **Strategie 3: Node-RED Flow Manipulation**

#### **Schritt 1: Node-RED Flow anpassen**
```javascript
// In Node-RED Flow: ccu/order/request Handler
function handleOrderRequest(msg) {
    const payload = msg.payload;
    
    // ERP Order-ID extrahieren falls vorhanden
    const erpOrderId = payload.erpOrderId || payload.externalOrderId;
    
    if (erpOrderId) {
        // ERP Order-ID verwenden anstelle UUID generieren
        msg.orderId = erpOrderId;
        msg.source = "ERP_SYSTEM";
    } else {
        // Standard UUID generieren
        msg.orderId = generateUUID();
    }
    
    return msg;
}
```

## 🎯 Praktische Implementierung

### **1. ERP Integration Klasse**

```python
class ERPOrderIDIntegration:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.erp_orders = {}
        self.ccu_order_mapping = {}
    
    def inject_erp_order_id(self, erp_order_id: str, order_type: str, 
                           workpiece_id: str, color: str):
        # ERP Order registrieren
        self.erp_orders[erp_order_id] = {
            'erp_order_id': erp_order_id,
            'order_type': order_type,
            'workpiece_id': workpiece_id,
            'color': color,
            'status': 'INJECTED'
        }
        
        # CCU Order Request mit ERP Order-ID senden
        payload = {
            "timestamp": datetime.now().isoformat(),
            "orderType": order_type,
            "type": color,
            "workpieceId": workpiece_id,
            "erpOrderId": erp_order_id,
            "source": "ERP_SYSTEM"
        }
        
        topic = "ccu/order/request"
        self.mqtt_client.publish(topic, json.dumps(payload))
```

### **2. ERP Order Tracking**

```python
def track_erp_order_progress(self, erp_order_id: str):
    """Verfolgt den Fortschritt einer ERP Order"""
    if erp_order_id in self.erp_orders:
        order_info = self.erp_orders[erp_order_id]
        
        # Status abfragen
        ccu_order_id = order_info.get('ccu_order_id')
        if ccu_order_id:
            # CCU Order Status abfragen
            topic = "ccu/order/status"
            payload = {"orderId": ccu_order_id}
            self.mqtt_client.publish(topic, json.dumps(payload))
        
        return order_info
    return None
```

## 🔄 Workflow-Integration

### **1. Wareneingang mit ERP Order-ID**

```python
# ERP Wareneingang Order
erp_order_id = "ERP-STORAGE-2024-001"
erp_integration.inject_erp_order_id(
    erp_order_id=erp_order_id,
    order_type="STORAGE",
    workpiece_id="047389ca341291",
    color="BLUE"
)
```

### **2. Produktionsauftrag mit ERP Order-ID**

```python
# ERP Produktionsauftrag
erp_order_id = "ERP-PRODUCTION-2024-001"
erp_integration.inject_erp_order_id(
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
```

### **3. Direkte Modul Commands mit ERP Order-ID**

```python
# HBW PICK mit ERP Order-ID
erp_integration.inject_module_command_with_erp_id(
    erp_order_id="ERP-PRODUCTION-2024-001",
    module_serial="SVR3QA0022",  # HBW
    command="PICK",
    metadata={
        "type": "BLUE",
        "erpOrderId": "ERP-PRODUCTION-2024-001"
    }
)
```

## 🚨 Risiken und Einschränkungen

### **1. System-Kompatibilität**
- **CCU muss ERP Order-IDs akzeptieren** - nicht garantiert
- **Module müssen ERP Order-IDs verarbeiten** - möglicherweise nicht unterstützt
- **Node-RED Flows müssen angepasst werden** - erfordert Konfigurationsänderungen

### **2. Validierung und Sicherheit**
- **Order-ID Format** - muss CCU-Format entsprechen
- **Duplikate vermeiden** - ERP Order-IDs müssen eindeutig sein
- **Fehlerbehandlung** - bei Ablehnung durch CCU

### **3. Workflow-Komplexität**
- **Zusätzliche Tracking-Logik** - ERP ↔ CCU Mapping
- **Status-Synchronisation** - ERP und APS Status synchron halten
- **Fehler-Recovery** - bei Kommunikationsproblemen

## ✅ Erfolgs-Kriterien

### **1. CCU Akzeptanz**
- ✅ CCU akzeptiert ERP Order-IDs in `ccu/order/request`
- ✅ CCU verwendet ERP Order-IDs in Responses
- ✅ CCU generiert keine eigenen Order-IDs für ERP Orders

### **2. Modul Kompatibilität**
- ✅ Module akzeptieren ERP Order-IDs in Commands
- ✅ Module verwenden ERP Order-IDs in Responses
- ✅ Workflow-Sequenz funktioniert mit ERP Order-IDs

### **3. End-to-End Tracking**
- ✅ ERP Order-IDs durchgängig verfolgbar
- ✅ Status-Updates an ERP-System möglich
- ✅ Fehlerbehandlung funktioniert

## 🔧 Test-Strategie

### **1. Einfache Tests**
```python
# Test 1: ERP Order-ID in CCU Request
erp_order_id = "TEST-ERP-001"
success = inject_erp_order_id(erp_order_id, "STORAGE", "test-nfc", "BLUE")

# Test 2: CCU Response verarbeiten
ccu_response = handle_ccu_response("ccu/order/active", test_payload)

# Test 3: Modul Command mit ERP Order-ID
module_success = send_module_command_with_erp_id(erp_order_id, "SVR3QA0022", "PICK", "BLUE")
```

### **2. Integration Tests**
```python
# Vollständiger Workflow Test
def test_erp_workflow():
    # 1. ERP Order erstellen
    erp_order_id = "ERP-TEST-001"
    
    # 2. Wareneingang
    inject_erp_order_id(erp_order_id, "STORAGE", "test-nfc", "BLUE")
    
    # 3. Produktionsauftrag
    inject_erp_order_id(erp_order_id, "PRODUCTION", "test-nfc", "BLUE")
    
    # 4. Status verfolgen
    status = track_erp_order_progress(erp_order_id)
    
    return status
```

## 📋 Implementierungs-Checkliste

### **Phase 1: Analyse**
- [ ] CCU Order-ID Format analysieren
- [ ] Modul Command Format analysieren
- [ ] Node-RED Flow Struktur verstehen
- [ ] ERP Order-ID Format definieren

### **Phase 2: Prototyp**
- [ ] ERP Integration Klasse implementieren
- [ ] CCU Request Manipulation testen
- [ ] Modul Command Manipulation testen
- [ ] Response Handling implementieren

### **Phase 3: Integration**
- [ ] Node-RED Flows anpassen
- [ ] End-to-End Tests durchführen
- [ ] Fehlerbehandlung implementieren
- [ ] Dokumentation erstellen

### **Phase 4: Produktion**
- [ ] ERP-System Integration
- [ ] Monitoring implementieren
- [ ] Backup-Strategien definieren
- [ ] Rollback-Plan erstellen

---

**Status: 🚧 IN ENTWICKLUNG** - ERP Order-ID Integration ist möglich, erfordert aber sorgfältige Implementierung und Tests! 🚀✨
