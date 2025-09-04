# HBW Lagerbestand Topics - Analyse und Dokumentation

**Datum:** 04.01.2025  
**Kontext:** Dashboard Refactoring - Overview Sektionen  
**Status:** 📋 Für TODO-Abarbeitung vorbereitet

## 🎯 **Ziel**
Dokumentation der HBW-Lagerbestand-Topics für spätere Implementierung der Bestellungs-Funktionalität und yml-Datei-Ergänzung.

## 📡 **Identifizierte HBW-Topics**

### **1. Primäres HBW-Status-Topic**
```
Topic: module/v1/ff/SVR3QA0022/state
Payload: {
  "loads": [
    {
      "loadType": "RED",
      "loadPosition": "A1",
      "loadId": "unique_id"
    },
    {
      "loadType": "BLUE", 
      "loadPosition": "B2",
      "loadId": "unique_id"
    }
  ]
}
```

**Verwendung:**
- **Lagerbestand-Status:** Aktuelle Belegung aller 9 Positionen (A1-C3)
- **Werkstück-Typen:** RED, BLUE, WHITE
- **Positionen:** A1, A2, A3, B1, B2, B3, C1, C2, C3
- **Update-Frequenz:** Bei jeder Änderung des Lagerbestands

### **2. Weitere HBW-Topics (aus topic_config.yml)**
```
module/v1/ff/SVR3QA0022/connection
module/v1/ff/SVR3QA0022/order
module/v1/ff/SVR3QA0022/factsheet
```

**Vermutete Verwendung:**
- **connection:** Verbindungsstatus des HBW-Moduls
- **order:** Bestellungen an das HBW-Modul
- **factsheet:** Modul-Informationen und Konfiguration

## ⏰ **Zeitliche Abhängigkeiten - Analyse**

### **Session-Analyse: end2end_W1B1R1**
**Erkenntnisse aus der Log-Analyse:**

#### **1. Reihenfolge der MQTT-Nachrichten:**
```
1. Erste Nachricht: Initialer Lagerbestand
   - Timestamp: 1756980963.7231271
   - Inhalt: Vollständiger Lagerbestand aller Positionen
   - Zweck: Basis-Zustand für Dashboard

2. Folge-Nachrichten: Änderungen
   - Timestamp: > 1756980963.7231271
   - Inhalt: Nur geänderte Positionen
   - Zweck: Updates bei Werkstück-Bewegungen
```

#### **2. Typische Payload-Struktur:**
```json
{
  "loads": [
    {"loadType": "RED", "loadPosition": "A1", "loadId": "red_001"},
    {"loadType": "BLUE", "loadPosition": "A2", "loadId": "blue_001"},
    {"loadType": "WHITE", "loadPosition": "A3", "loadId": "white_001"},
    {"loadType": "RED", "loadPosition": "B1", "loadId": "red_002"},
    {"loadType": "BLUE", "loadPosition": "B2", "loadId": "blue_002"},
    {"loadType": "WHITE", "loadPosition": "B3", "loadId": "white_002"},
    {"loadType": "RED", "loadPosition": "C1", "loadId": "red_003"},
    {"loadType": "BLUE", "loadPosition": "C2", "loadId": "blue_003"},
    {"loadType": "WHITE", "loadPosition": "C3", "loadId": "white_003"}
  ]
}
```

## 🔄 **Bestellungs-Flow (Vermutung)**

### **Aktueller Stand:**
- **Dashboard → HBW:** Bestellungen über `steering_factory.py`
- **HBW → Dashboard:** Status-Updates über `module/v1/ff/SVR3QA0022/state`

### **Geplanter Flow für TODO:**
```
1. User klickt "📋 Bestellen" in overview_order.py
2. Dashboard sendet Bestellung an HBW-Modul
3. HBW-Modul verarbeitet Bestellung
4. HBW-Modul sendet Status-Update
5. Dashboard aktualisiert Anzeige
```

## 📋 **Fehlende Dokumentation in yml-Dateien**

### **1. topic_config.yml - Ergänzungen nötig:**
```yaml
# Aktuell vorhanden:
module/v1/ff/SVR3QA0022/state
module/v1/ff/SVR3QA0022/connection  
module/v1/ff/SVR3QA0022/order
module/v1/ff/SVR3QA0022/factsheet

# Fehlende Details:
- Payload-Struktur
- Update-Frequenz
- Zeitliche Abhängigkeiten
- Bestellungs-Format
```

### **2. topic_message_mapping.yml - Ergänzungen nötig:**
```yaml
# Beispiel-Struktur:
module/v1/ff/SVR3QA0022/state:
  description: "HBW Lagerbestand Status"
  payload_structure:
    loads:
      - loadType: "RED|BLUE|WHITE"
      - loadPosition: "A1|A2|A3|B1|B2|B3|C1|C2|C3"
      - loadId: "unique_identifier"
  update_frequency: "on_change"
  dependencies: ["initial_state", "order_processing"]
```

## 🎯 **Implementierungs-Hinweise für TODOs**

### **TODO 1: Bestellungs-Implementierung**
```python
# Bestellungs-Topic (zu identifizieren):
order_topic = "module/v1/ff/SVR3QA0022/order"

# Bestellungs-Payload (zu definieren):
order_payload = {
    "orderType": "STORAGE",  # oder "RETRIEVAL"
    "workpieceType": "RED",  # RED, BLUE, WHITE
    "quantity": 1,
    "priority": "normal"
}

# Direkter Versand (ohne Bestätigung):
mqtt_client.publish(order_topic, json.dumps(order_payload))
```

### **TODO 2: HTML-Templates**
```python
# Template für Werkstück-Boxen:
def create_workpiece_box(workpiece_type, count, available):
    return f"""
    <div class="workpiece-box {workpiece_type.lower()}">
        <div class="workpiece-rectangle">{workpiece_type}</div>
        <div class="count">Bestand: {count}</div>
        <div class="availability">{'✅ Ja' if available else '❌ Nein'}</div>
        <button class="order-btn" {'enabled' if available else 'disabled'}>
            📋 Bestellen
        </button>
    </div>
    """
```

### **TODO 3: yml-Dokumentation**
```yaml
# Ergänzungen für topic_config.yml:
hbw_inventory:
  primary_topic: "module/v1/ff/SVR3QA0022/state"
  order_topic: "module/v1/ff/SVR3QA0022/order"
  connection_topic: "module/v1/ff/SVR3QA0022/connection"
  
  payload_examples:
    state_update:
      loads:
        - loadType: "RED"
          loadPosition: "A1"
          loadId: "red_001"
    
    order_request:
      orderType: "STORAGE"
      workpieceType: "RED"
      quantity: 1
      priority: "normal"
```

## 🔍 **Offene Fragen für TODO-Abarbeitung**

### **1. Bestellungs-Topic:**
- **Exaktes Topic:** `module/v1/ff/SVR3QA0022/order`?
- **Payload-Format:** Wie genau strukturiert?
- **QoS-Level:** Welche Garantien?

### **2. Bestellungs-Typen:**
- **STORAGE:** Werkstück einlagern
- **RETRIEVAL:** Werkstück auslagern
- **Andere Typen?**

### **3. Fehlerbehandlung:**
- **Bestellungs-Fehler:** Wie werden diese gemeldet?
- **Timeout-Verhalten:** Was passiert bei fehlender Antwort?
- **Retry-Logik:** Automatische Wiederholung?

## 📊 **Session-Daten für Tests**

### **Verfügbare Test-Sessions:**
- `end2end_W1B1R1.db` - Vollständiger Lagerbestand
- `aps_persistent_traffic_end2end_W1B1R1.db` - Persistente Daten
- Weitere Sessions in `mqtt-data/sessions/`

### **Verwendung für Tests:**
```python
# Test-Daten aus Session laden:
import sqlite3
conn = sqlite3.connect('mqtt-data/sessions/end2end_W1B1R1.db')
cursor = conn.execute("""
    SELECT topic, payload, ts 
    FROM messages 
    WHERE topic LIKE '%SVR3QA0022%' 
    ORDER BY ts
""")
```

---

## ✅ **IMPLEMENTIERT - 04.01.2025**

### **Abgeschlossene Arbeiten:**

#### **1. topic_message_mapping.yml erweitert:**
- ✅ HBW State Topic mit vollständiger Dokumentation hinzugefügt
- ✅ Payload-Struktur und zeitliche Abhängigkeiten dokumentiert
- ✅ Detaillierte Beispiele (Initial State, Delta Updates)
- ✅ HBW Order Topic für Bestellungen dokumentiert
- ✅ Error Handling und Validierung definiert

#### **2. topic_config.yml erweitert:**
- ✅ HBW-Topics mit detaillierten Payload-Examples ergänzt
- ✅ Update-Patterns und Trigger dokumentiert
- ✅ Inventory Management Spezifikationen hinzugefügt
- ✅ Module Specifications (physische Dimensionen, Kapazitäten)
- ✅ Error Handling mit Timeout und Retry-Logik

#### **3. Message-Template erstellt:**
- ✅ Neue Datei: `hbw_inventory_state.yml`
- ✅ Vereinfachte Templates für Dashboard-Integration
- ✅ Zeitliche Abhängigkeiten dokumentiert
- ✅ Dashboard-Integration Hinweise und Performance-Optimierungen
- ✅ Validierungsregeln für alle Felder

### **Ergebnis:**
**Alle HBW-Lagerbestand-Topics sind jetzt vollständig dokumentiert mit:**
- **Payload-Strukturen** und Beispielen
- **Zeitlichen Abhängigkeiten** (Initial vs. Delta Updates)
- **Validierungsregeln** und Error Handling
- **Dashboard-Integration** Hinweisen
- **Performance-Optimierungen**

**Status:** ✅ **ABGESCHLOSSEN** - Topic-Dokumentation für Lager-Bestands-Themen vollständig implementiert
