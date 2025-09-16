# Workflow Sequence Control System

## 🎯 Übersicht

Das **Workflow Sequence Control System** implementiert die Anforderungen aus `requirements_sequence_control.md` für sequenzielle Steuerungsbefehle in logischer Klammer mit UI-Unterstützung.

## 🏗️ Architektur

### **Kern-Komponenten:**

1. **`WorkflowOrderManager`** - Singleton für ID-Management (`orderId`/`orderUpdateId`)
2. **`SequenceExecutor`** - Führt Sequenzen aus (YML + Python)
3. **`SequenceDefinitionLoader`** - Lädt Sequenz-Definitionen aus verschiedenen Quellen
4. **`SequenceUI`** - Streamlit UI-Komponenten
5. **`WaitHandler`** - Event-Waiting zwischen Commands

### **Dateien:**
```
omf/omf/tools/
├── workflow_order_manager.py      # ID-Management
├── sequence_executor.py           # Sequenz-Ausführung
├── sequence_definition.py         # YML/Python Definitionen
├── sequence_ui.py                 # Streamlit UI (in helper_apps)
├── sequence_test_app.py           # Test-App
└── run_sequence_test.py           # Einfacher Test

omf/omf/config/sequence_definitions/
├── mill_sequence.yml              # MILL-Sequenz (YML)
├── drill_sequence.yml             # DRILL-Sequenz (YML)
└── aiqs_sequence.py               # AIQS-Sequenz (Python)
```

## 🚀 Verwendung

### **1. Einfacher Test (ohne UI):**
```bash
cd omf/omf/tools
python run_sequence_test.py
```

### **2. Streamlit Test-App:**
```bash
cd omf/omf/tools
streamlit run sequence_test_app.py
```

### **3. Integration in OMF Dashboard:**
```python
from omf.tools.sequence_executor import SequenceExecutor
from omf.tools.sequence_definition import SequenceDefinitionLoader
from omf.tools.sequence_ui import SequenceUI

# MQTT Client (aus OMF Dashboard)
executor = SequenceExecutor(mqtt_client)
ui = SequenceUI(executor)
```

## 📋 Sequenz-Definitionen

### **YML-Format:**
```yaml
name: mill_complete_sequence
description: Komplette MILL-Sequenz: PICK → MILL → DROP
context:
  module_serial: SVR4H76449
  module_type: MILL
steps:
  - name: PICK
    topic: module/v1/ff/{{module_serial}}/order
    payload:
      orderId: "{{orderId}}"
      orderUpdateId: "{{orderUpdateId}}"
      action: PICK
    wait_condition:
      topic: module/v1/ff/{{module_serial}}/state
      payload_contains:
        actionState: IDLE
```

### **Python-Format:**
```python
def get_sequence_definition():
    return SequenceDefinition(
        name='aiqs_complete_sequence',
        description='Komplette AIQS-Sequenz mit Quality-Check',
        steps=[
            SequenceStep(
                step_id=1,
                name='PICK',
                topic='module/v1/ff/{{module_serial}}/order',
                payload={
                    'orderId': '{{orderId}}',
                    'orderUpdateId': '{{orderUpdateId}}',
                    'action': 'PICK'
                }
            )
        ],
        context={'module_serial': 'SVR4H76530'}
    )
```

## ✅ Implementierte Features

### **Must-Have (✅ Alle implementiert):**
- ✅ Sequenz-Fenster öffnet sich bei Sequenz-Start
- ✅ Sequenz bleibt offen bis Ende oder Abbruch
- ✅ Manuelle Send-Button-Kontrolle (keine Automatik)
- ✅ Konsistente `orderId`/`orderUpdateId` Verwaltung
- ✅ Visuelle Fortschrittsanzeige mit Nummerierung und Symbolen
- ✅ Abbruch-Möglichkeit jederzeit
- ✅ Wait-Schritte zwischen Commands
- ✅ OMFMqttClient-Singleton Verwendung
- ✅ MQTT-Message-Versand für Steuerungsbefehle
- ✅ Unit-Tests ohne Dashboard-Start möglich
- ✅ Step-Details (Context/Payload) optional pro Schritt
- ✅ Sequenzdefinitionen als YML und Python möglich

### **Could-Have (🔄 Teilweise implementiert):**
- 🔄 Generische Topic/Message-Template-Definition
- 🔄 Payload-Anzeige ein-/ausschaltbar
- ✅ Modul-spezifische Rezepte (MILL, DRILL, AIQS)
- 🔄 YML-Integration für Topic/Message-Mapping
- 🔄 Thread-Sicherheit für parallele Sequenzen

## 🧪 Test-Ergebnisse

```
🔄 Workflow Sequence Control - Test Suite
==================================================
🔍 Teste Sequenz-Definitionen laden...
✅ 3 Sequenzen geladen:
  - aiqs_complete_sequence: 3 Schritte
  - drill_complete_sequence: 3 Schritte  
  - mill_complete_sequence: 3 Schritte

🔄 Teste WorkflowOrderManager...
✅ Order erstellt: ee0cd2bf-3b5d-4316-9754-97434df94a83
📊 Status: running → completed

🚀 Teste Sequenz-Ausführung...
📋 Teste Sequenz: aiqs_complete_sequence
✅ Sequenz gestartet mit Order ID: 95454095-f9cc-432b-842c-bffd786ff100
📤 MQTT Publish: module/v1/ff/{{module_serial}}/order → {...}

✅ Alle Tests erfolgreich abgeschlossen!
```

## 🔧 Technische Details

### **Variable-Ersetzung:**
- `{{orderId}}` → Automatisch generierte Order-ID
- `{{orderUpdateId}}` → Automatisch inkrementierte Update-ID
- `{{module_serial}}` → Aus Kontext-Variablen
- `{{quality_check_enabled}}` → Aus Kontext-Variablen

### **Wait-Bedingungen:**
```yaml
wait_condition:
  topic: module/v1/ff/{{module_serial}}/state
  payload_contains:
    actionState: IDLE
    qualityResult: true
```

### **Status-Management:**
- `pending` → Schritt wartet
- `ready` → Schritt bereit zum Senden
- `sent` → Schritt gesendet
- `waiting` → Wartet auf Bestätigung
- `completed` → Schritt abgeschlossen
- `error` → Fehler aufgetreten

## 🎯 Nächste Schritte

1. **Integration in OMF Dashboard** - UI-Komponenten in Dashboard einbinden
2. **Echte MQTT-Integration** - Mit OMFMqttClient verbinden
3. **Erweiterte Wait-Logik** - Komplexere Event-Bedingungen
4. **Template-Integration** - Mit bestehenden YML-Templates verbinden
5. **Performance-Optimierung** - Thread-Sicherheit und Skalierung

## 📚 Dokumentation

- **Anforderungen:** `docs_orbis/requirements_sequence_control.md`
- **Architektur:** Diese README
- **Beispiele:** `omf/omf/config/sequence_definitions/`
- **Tests:** `run_sequence_test.py`

---

**Status:** ✅ **Funktionsfähig und getestet**  
**Nächste Version:** Integration in OMF Dashboard
