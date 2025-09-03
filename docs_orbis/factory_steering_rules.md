# Factory Steering Regeln

## Übersicht

Dieses Dokument beschreibt die aktuellen Regeln für die `factory_steering.py` Komponente im OMF Dashboard. Diese Regeln stellen sicher, dass alle MQTT-Nachrichten den korrekten Standards entsprechen.

## Wichtige Prinzipien

### 1. Historische Tests bleiben unverändert
- **Unit-Tests aus Commit 807c29a** sind **historische Referenzen**
- Sie dokumentieren, was in diesem Commit funktioniert hat
- Sie werden **NICHT angepasst** oder geändert

### 2. Neue Tests für aktuelle Regeln
- **Neue Unit-Tests** validieren die **aktuellen Implementierungen**
- Sie testen Topic + Message + Regeln in Kombination
- Sie stellen sicher, dass die Regeln eingehalten werden

## MQTT Topic Regeln

### Modul-Topics
Alle Modul-Befehle verwenden das folgende Topic-Pattern:
```
module/v1/ff/{serial_number}/order
```

**Spezifische Topics:**
- **DRILL**: `module/v1/ff/SVR4H76449/order`
- **MILL**: `module/v1/ff/SVR3QA2098/order`
- **AIQS**: `module/v1/ff/SVR4H76530/order`

### FTS-Topics
FTS-Befehle verwenden:
```
fts/v1/ff/5iO4/order
```

### CCU-Topics
Factory-Reset verwendet:
```
ccu/set/reset
```

## Message-Struktur Regeln

### Pflichtfelder
Jede Modul-Nachricht muss folgende Felder enthalten:
```json
{
  "serialNumber": "string",
  "orderId": "uuid-v4",
  "orderUpdateId": "integer",
  "action": {
    "id": "uuid-v4",
    "command": "string",
    "metadata": {
      "priority": "string",
      "timeout": "integer",
      "type": "string"
    }
  }
}
```

### UUID-Regeln
- **`orderId`**: Muss ein gültiger UUID-v4 sein
- **`action.id`**: Muss ein gültiger UUID-v4 sein (für jeden Befehl neu)
- **Generierung**: `str(uuid.uuid4())`

### orderUpdateId-Regeln
- **Sequenz**: Muss hochzählen (1, 2, 3, ...)
- **Konstanz**: `orderId` bleibt in einer Sequenz konstant
- **Verwaltung**: Über `st.session_state["order_update_counter"]`

## Sequenz-Regeln

### Modul-Sequenzen
**DRILL**: `PICK → DRILL → DROP`
**MILL**: `PICK → MILL → DROP`
**AIQS**: `PICK → CHECK_QUALITY → DROP`

### Sequenz-Validierung
1. **orderId**: Bleibt konstant für die gesamte Sequenz
2. **orderUpdateId**: Zählt hoch (1→2→3)
3. **action.id**: Neuer UUID für jeden Befehl
4. **Topic**: Bleibt konstant für alle Schritte

## FTS-Befehle

### Verfügbare Commands
- **`findInitialDockPosition`**: FTS fährt zum Wareneingang
- **`startCharging`**: FTS fährt zur Ladestation
- **`stopCharging`**: FTS stoppt das Laden
- **`factsheetRequest`**: FTS-Status abfragen
- **`STOP`**: FTS stoppen

### FTS-Message-Struktur
```json
{
  "serialNumber": "5iO4",
  "orderId": "uuid-v4",
  "orderUpdateId": "integer",
  "action": {
    "id": "uuid-v4",
    "command": "string",
    "metadata": {}
  },
  "timestamp": "iso-8601"
}
```

## Unit-Test-Strategie

### Neue Test-Dateien
- **`test_factory_steering_rules.py`**: Testet aktuelle Regeln
- **Nicht**: `test_working_sequences_commit_807c29a.py` (historisch!)

### Test-Kategorien
1. **Topic-Konformität**: Korrekte MQTT-Topics
2. **Message-Struktur**: UUIDs, Pflichtfelder, etc.
3. **Sequenz-Regeln**: orderId-Konstanz, orderUpdateId-Inkrementierung
4. **Kombinierte Tests**: Topic + Message + Regeln zusammen

### Mock-Strategie
- **`st.session_state`** wird gemockt für Tests
- **Keine echten MQTT-Verbindungen** in Tests
- **Isolierte Komponenten-Tests**

## Implementierungsdetails

### UUID-Generierung
```python
import uuid

# orderId generieren
order_id = str(uuid.uuid4())

# action.id generieren
action_id = str(uuid.uuid4())
```

### orderUpdateId-Verwaltung
```python
# In session_state hochzählen
if "order_update_counter" not in st.session_state:
    st.session_state["order_update_counter"] = 1
else:
    st.session_state["order_update_counter"] += 1
```

### Topic-Generierung
```python
# Modul-spezifische Topics
topic = f"module/v1/ff/{serial_number}/order"

# FTS-Topic
topic = "fts/v1/ff/5iO4/order"
```

## Validierung

### Automatische Tests
Alle Regeln werden durch Unit-Tests validiert:
- **Topic-Konformität**: Korrekte MQTT-Topics
- **UUID-Validierung**: Gültige UUID-v4 Strings
- **Struktur-Validierung**: Alle Pflichtfelder vorhanden
- **Sequenz-Validierung**: orderId-Konstanz, orderUpdateId-Inkrementierung

### Manuelle Tests
Dashboard-Funktionalität testen:
1. **Modul-Sequenzen** starten
2. **FTS-Befehle** senden
3. **Factory Reset** ausführen
4. **Nachrichten-Zentrale** prüfen

## Wartung

### Regeln aktualisieren
1. **Dokumentation** in dieser Datei aktualisieren
2. **Unit-Tests** entsprechend anpassen
3. **Implementierung** in `factory_steering.py` korrigieren

### Neue Module hinzufügen
1. **Serial Number** in `module_serials` Dictionary hinzufügen
2. **Topic-Pattern** folgt dem Standard
3. **Unit-Tests** für neues Modul erstellen

### Neue FTS-Commands hinzufügen
1. **Command** in `_show_fts_commands_section()` hinzufügen
2. **Button** mit korrektem Icon und Text erstellen
3. **Unit-Tests** für neuen Command erstellen

## Zusammenfassung

Die Factory Steering Regeln stellen sicher, dass:
- ✅ **Alle MQTT-Topics** dem korrekten Pattern folgen
- ✅ **Alle Nachrichten** gültige UUIDs verwenden
- ✅ **Alle Sequenzen** die orderId-Konstanz-Regel befolgen
- ✅ **Alle Tests** die aktuellen Regeln validieren
- ✅ **Historische Tests** unverändert bleiben

Diese Regeln werden durch umfassende Unit-Tests validiert und sind in der Implementierung strikt umgesetzt.
