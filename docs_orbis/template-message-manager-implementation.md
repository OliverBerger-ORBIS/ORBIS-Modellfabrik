# Template Message Manager: Implementierung

## 📋 Übersicht

**Implementiert:** Template Message Manager für APS MQTT Control  
**Status:** Vorbereitet für Live-Test  
**Dateien:** 3 neue Dateien erstellt  

## 🗂️ Implementierte Dateien

### 1. **Template Message Manager** (`src_orbis/mqtt/tools/template_message_manager.py`)
- ✅ **Template Library** mit vordefinierten Templates
- ✅ **Parameter Validierung** für alle Templates
- ✅ **Order Tracking** System
- ✅ **MQTT Integration** (optional)
- ✅ **Statistiken** und Monitoring

### 2. **Dashboard Integration** (`src_orbis/mqtt/dashboard/template_control.py`)
- ✅ **Wareneingang Control Panel**
- ✅ **Order Tracking Dashboard**
- ✅ **Template Library Browser**
- ✅ **Template Testing Interface**
- ✅ **Benutzerdefinierte Template Creator**

### 3. **Test-Script** (`test_template_manager.py`)
- ✅ **Vollständiger Test** ohne MQTT-Verbindung
- ✅ **Error Handling Tests**
- ✅ **Order Tracking Simulation**

## 🎯 **Hauptfunktionen**

### **Template Message Manager:**
```python
# Template Manager erstellen
manager = TemplateMessageManager()

# Wareneingang-Trigger senden
success = manager.send_wareneingang_trigger("RED", "04798eca341290")

# CCU Response verarbeiten
manager.handle_ccu_response(order_id, color, workpiece_id, response_data)

# Order Progress verfolgen
manager.track_order_progress(order_id, message_data)

# Statistiken abrufen
stats = manager.get_statistics()
```

### **Dashboard Integration:**
```python
# Dashboard erstellen
dashboard = create_template_control_dashboard(manager)

# Widgets anzeigen
dashboard.show_wareneingang_control()
dashboard.show_order_tracking()
dashboard.show_template_library()
```

## 📊 **Template Library**

### **1. Wareneingang Trigger Template:**
```json
{
  "name": "wareneingang_trigger",
  "topic": "ccu/order/request",
  "payload": {
    "timestamp": "{{timestamp}}",
    "orderType": "STORAGE",
    "type": "{{color}}",
    "workpieceId": "{{workpieceId}}"
  },
  "parameters": {
    "color": ["RED", "WHITE", "BLUE"],
    "workpieceId": "string (NFC)",
    "timestamp": "ISO 8601"
  }
}
```

### **2. DPS DROP Template:**
```json
{
  "name": "dps_drop_template",
  "topic": "module/v1/ff/SVR4H73275/order",
  "payload": {
    "timestamp": "{{timestamp}}",
    "serialNumber": "SVR4H73275",
    "orderId": "{{orderId}}",
    "orderUpdateId": 1,
    "action": {
      "id": "{{actionId}}",
      "command": "DROP",
      "metadata": {
        "workpiece": {
          "workpieceId": "{{workpieceId}}",
          "type": "{{color}}",
          "history": [],
          "state": "PROCESSED"
        }
      }
    }
  }
}
```

### **3. HBW PICK Template:**
```json
{
  "name": "hbw_pick_template",
  "topic": "module/v1/ff/SVR3QA0022/order",
  "payload": {
    "timestamp": "{{timestamp}}",
    "serialNumber": "SVR3QA0022",
    "orderId": "{{orderId}}",
    "orderUpdateId": 3,
    "action": {
      "id": "{{actionId}}",
      "command": "PICK",
      "metadata": {
        "type": "{{color}}",
        "workpieceId": "{{workpieceId}}"
      }
    }
  }
}
```

## 🔄 **Order Tracking Workflow**

### **Phase 1: Wareneingang-Trigger**
```
Dashboard → send_wareneingang_trigger("RED", "04798eca341290")
↓
MQTT → ccu/order/request
↓
Tracking → pending_04798eca341290
```

### **Phase 2: CCU Response**
```
CCU → ccu/order/response
↓
Manager → handle_ccu_response(order_id, color, workpiece_id, response_data)
↓
Tracking → order_id (aktiv)
```

### **Phase 3: Order Progress**
```
MQTT → module/state (mit order_id)
↓
Manager → track_order_progress(order_id, message_data)
↓
Status → COMPLETED/ERROR
↓
Historie → order_history
```

## 🎯 **Dashboard Widgets**

### **1. Wareneingang Control Panel:**
- **Farb-Auswahl:** RED, WHITE, BLUE
- **Werkstück-ID:** NFC oder manuell
- **Trigger Button:** Startet Wareneingang
- **Template Info:** Zeigt Parameter und Details

### **2. Order Tracking Dashboard:**
- **Statistiken:** Aktive, Abgeschlossen, Fehler, Gesamt
- **Farb-Verteilung:** Anzahl pro Farbe
- **Aktive Orders:** Expandable Details
- **Order Historie:** Filter nach Status

### **3. Template Library:**
- **Template Browser:** Alle verfügbaren Templates
- **Payload Preview:** JSON-Format
- **Parameter Details:** Typen und Werte

### **4. Template Testing:**
- **Parameter Validierung:** Live-Validierung
- **Test senden:** Nur für Wareneingang
- **Error Handling:** Ungültige Parameter

### **5. Custom Template Creator:**
- **Template Name:** Benutzerdefinierter Name
- **MQTT Topic:** Custom Topic
- **Payload JSON:** Template-Format
- **Parameter:** Typen und Werte

## 🧪 **Test-Script Features**

### **Vollständiger Test ohne MQTT:**
```bash
python test_template_manager.py
```

### **Getestete Funktionen:**
1. ✅ **Template Auflistung**
2. ✅ **Template Info Anzeige**
3. ✅ **Parameter Validierung**
4. ✅ **Ungültige Parameter Erkennung**
5. ✅ **Order Tracking Simulation**
6. ✅ **CCU Response Verarbeitung**
7. ✅ **Order Progress Tracking**
8. ✅ **Statistiken Berechnung**
9. ✅ **Order Info Abfrage**
10. ✅ **Benutzerdefinierte Templates**

## 🚀 **Nächste Schritte für Live-Test**

### **1. Dashboard Integration:**
```python
# In aps_dashboard.py hinzufügen:
from .template_control import create_template_control_dashboard

# Template Manager erstellen
template_manager = TemplateMessageManager()
template_manager.set_mqtt_client(mqtt_client)

# Dashboard erstellen
template_dashboard = create_template_control_dashboard(template_manager)

# Widgets anzeigen
template_dashboard.show_wareneingang_control()
template_dashboard.show_order_tracking()
```

### **2. MQTT Message Handler:**
```python
# CCU Response Handler
def on_ccu_response(topic, payload):
    data = json.loads(payload)
    if "orderId" in data:
        template_manager.handle_ccu_response(
            data["orderId"],
            data.get("type"),
            data.get("workpieceId"),
            data
        )

# Order Progress Handler
def on_order_progress(topic, payload):
    data = json.loads(payload)
    if "orderId" in data:
        template_manager.track_order_progress(data["orderId"], data)
```

### **3. Live-Test Checkliste:**
- [ ] **MQTT Client** verbinden
- [ ] **Template Manager** initialisieren
- [ ] **Dashboard Widgets** integrieren
- [ ] **Message Handler** registrieren
- [ ] **Wareneingang-Trigger** testen
- [ ] **Order Tracking** verifizieren
- [ ] **Error Handling** testen

## ✅ **Bereit für Live-Test**

### **Was funktioniert:**
- ✅ **Template Library** vollständig implementiert
- ✅ **Parameter Validierung** robust
- ✅ **Order Tracking** System funktional
- ✅ **Dashboard Widgets** bereit
- ✅ **Error Handling** implementiert
- ✅ **Test-Script** validiert

### **Was morgen getestet werden kann:**
- 🎯 **Live MQTT-Verbindung** zur APS
- 🎯 **Wareneingang-Trigger** senden
- 🎯 **CCU Response** empfangen
- 🎯 **Order Tracking** in Echtzeit
- 🎯 **Dashboard Integration** testen

**Der Template Message Manager ist vollständig implementiert und bereit für den Live-Test morgen!** 🚀✨
