# 🔧 DRILL Station Manual Control Guide - Pick-Drill-Drop Sequence

## 🎯 Ziel
Manuelle Ansteuerung der Bohrstation (DRILL) mit der Sequenz **Pick-Drill-Drop** für Werkstück **W1** (Weiß).

## 📋 Voraussetzungen

### 1. **Werkstück W1 verfügbar**
- **NFC Code:** `04798eca341290` (aus NFC-Mapping)
- **Farbe:** Weiß
- **Position:** Muss in HBW oder FTS verfügbar sein

### 2. **MQTT-Verbindung**
- **Broker:** `192.168.0.100`
- **Credentials:** `default` / `default`
- **DRILL Module:** `SVR4H76449` (192.168.0.50)

## 🏭 DRILL Station Konfiguration

| Parameter | Wert |
|-----------|------|
| **Module Name** | DRILL |
| **Serial Number** | SVR4H76449 |
| **IP Address** | 192.168.0.50 |
| **MQTT Topic** | `module/v1/ff/SVR4H76449/order` |
| **Working Commands** | PICK, DRILL, DROP |

## 🔄 Sequenz: Pick → Drill → Drop

### **Schritt 1: PICK (Werkstück aufnehmen)**

**Template:** `DRILL_PICK_WHITE`

**MQTT Message:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 1,
  "action": {
    "id": "5f5f2fe2-1bdd-4f0e-84c6-33c44d75f07e",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Ausführung:**
```bash
# Option 1: Template verwenden
python src_orbis/mqtt/tools/aps_enhanced_controller.py --template DRILL_PICK_WHITE

# Option 2: Direkter Befehl
python src_orbis/mqtt/tools/aps_enhanced_controller.py --order DRILL PICK

# Option 3: Remote Client
python src_orbis/mqtt/tools/remote_mqtt_client.py --broker 192.168.0.100 --template DRILL_PICK_WHITE
```

**Erwartete Antwort:** `Status: RUNNING`

---

### **Schritt 2: DRILL (Bohren)**

**Template:** `DRILL_PROCESS_WHITE`

**MQTT Message:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 2,
  "action": {
    "id": "6f6f3ff3-2cee-5f1f-95d7-44d55e86g18f",
    "command": "DRILL",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE",
      "duration": 30
    }
  }
}
```

**Ausführung:**
```bash
# Option 1: Template verwenden
python src_orbis/mqtt/tools/aps_enhanced_controller.py --template DRILL_PROCESS_WHITE

# Option 2: Direkter Befehl
python src_orbis/mqtt/tools/aps_enhanced_controller.py --order DRILL DRILL

# Option 3: Remote Client
python src_orbis/mqtt/tools/remote_mqtt_client.py --broker 192.168.0.100 --template DRILL_PROCESS_WHITE
```

**Erwartete Antwort:** `Status: RUNNING` (Dauer: ~30 Sekunden)

---

### **Schritt 3: DROP (Werkstück ablegen)**

**Template:** `DRILL_DROP_WHITE`

**MQTT Message:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 3,
  "action": {
    "id": "7g7g4gg4-3dff-6g2g-a6e8-55e66f97h29g",
    "command": "DROP",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Ausführung:**
```bash
# Option 1: Template verwenden
python src_orbis/mqtt/tools/aps_enhanced_controller.py --template DRILL_DROP_WHITE

# Option 2: Direkter Befehl
python src_orbis/mqtt/tools/aps_enhanced_controller.py --order DRILL DROP

# Option 3: Remote Client
python src_orbis/mqtt/tools/remote_mqtt_client.py --broker 192.168.0.100 --template DRILL_DROP_WHITE
```

**Erwartete Antwort:** `Status: RUNNING`

---

## 🛠️ Empfohlene Ausführung über Dashboard

### **Option 1: Dashboard Template Control (EMPFOHLEN)**
1. **Dashboard öffnen:** `http://localhost:8501`
2. **Hauptmenü:** "🎮 MQTT Module Control" wählen
3. **Steuerungsmethode:** "Template Message" auswählen
4. **Tab:** "🧪 Template Testing" wählen
5. **Session Logger starten** (falls nicht aktiv)
6. **Sequenz ausführen:**
   - **DRILL_PICK_WHITE** → Senden
   - **DRILL_PROCESS_WHITE** → Senden (nach PICK abgeschlossen)
   - **DRILL_DROP_WHITE** → Senden (nach DRILL abgeschlossen)
7. **MQTT Analysis** Tab für Monitoring verwenden

### **Option 2: Python Script**
```python
from src_orbis.mqtt.tools.mqtt_message_library import create_message_from_template
from src_orbis.mqtt.tools.aps_enhanced_controller import APSEnhancedController

controller = APSEnhancedController()

# Sequenz ausführen
templates = ["DRILL_PICK_WHITE", "DRILL_PROCESS_WHITE", "DRILL_DROP_WHITE"]

for template in templates:
    print(f"Sending {template}...")
    controller.send_template_message(template)
    time.sleep(35)  # Warten bis DRILL abgeschlossen
```

### **Option 3: Shell Script**
```bash
#!/bin/bash
echo "Starting DRILL sequence for W1..."

echo "Step 1: PICK"
python src_orbis/mqtt/tools/aps_enhanced_controller.py --template DRILL_PICK_WHITE
sleep 10

echo "Step 2: DRILL"
python src_orbis/mqtt/tools/aps_enhanced_controller.py --template DRILL_PROCESS_WHITE
sleep 35

echo "Step 3: DROP"
python src_orbis/mqtt/tools/aps_enhanced_controller.py --template DRILL_DROP_WHITE

echo "DRILL sequence completed!"
```

## 📊 Monitoring & Session Logging

### **Session Logger aktivieren:**
```bash
# Session Logger für DRILL-Test starten
python src_orbis/mqtt/loggers/aps_session_logger.py --session drill-test-w1
```

### **Dashboard Monitoring:**
1. **MQTT Analysis** Tab öffnen
2. **Session auswählen:** `drill-test-w1`
3. **Filter anwenden:**
   - **Module:** DRILL
   - **Topic:** `module/v1/ff/SVR4H76449/*`
   - **Zeitbereich:** Nach Bedarf eingrenzen

### **MQTT Topics für Monitoring:**
- **State:** `module/v1/ff/SVR4H76449/state`
- **Order:** `module/v1/ff/SVR4H76449/order`
- **Order Status:** Über Dashboard MQTT Analysis

### **Erwartete Status-Sequenz:**
1. **PICK:** `IDLE` → `RUNNING` → `IDLE`
2. **DRILL:** `IDLE` → `RUNNING` → `IDLE` (30s)
3. **DROP:** `IDLE` → `RUNNING` → `IDLE`

## ⚠️ Wichtige Hinweise

### **Reihenfolge beachten:**
- **PICK** muss vor **DRILL** ausgeführt werden
- **DRILL** benötigt ~30 Sekunden
- **DROP** kann erst nach **DRILL** erfolgen

### **Fehlerbehandlung:**
- Bei `Status: ERROR` → Modul-Status prüfen
- Bei Timeout → Werkstück-Position verifizieren
- Bei `Status: BUSY` → Warten bis `IDLE`

### **Werkstück-Verfügbarkeit:**
- W1 muss in HBW oder FTS verfügbar sein
- NFC-Code `04798eca341290` sollte lesbar sein
- FTS muss W1 zur DRILL-Station transportieren

## 🔍 Troubleshooting

### **Problem: "Module not responding"**
- MQTT-Verbindung prüfen
- DRILL-Modul IP `192.168.0.50` erreichbar?
- Credentials `default/default` korrekt?

### **Problem: "Status: ERROR"**
- Werkstück W1 verfügbar?
- DRILL-Station nicht blockiert?
- Vorherige Befehle abgeschlossen?

### **Problem: "Status: BUSY"**
- Warten bis Modul `IDLE` ist
- Keine anderen Befehle parallel senden
- Modul-Status über Dashboard prüfen

## 📈 Nächste Schritte

1. **Session Logger starten** für `drill-test-w1`
2. **Dashboard Template Control** verwenden
3. **Sequenz ausführen:** PICK → DRILL → DROP
4. **MQTT Analysis** für Monitoring nutzen
5. **Session analysieren** für Fehlerbehandlung
6. **Automatisierung** für andere Werkstücke
7. **Integration** in größere Workflows
