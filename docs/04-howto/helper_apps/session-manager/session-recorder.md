# 📹 Session Recorder - Tab Dokumentation

**Navigation:** In der Sidebar **🎙️ Session Recorder** wählen. Broker, Zielverzeichnis und Aufnahme-Optionen liegen unter **⚙️ Einstellungen** (Tabs **Session Recorder** bzw. **Logging & Diagnose**).

## 🎯 Zweck

Der **Session Recorder** ermöglicht die Aufnahme von MQTT-Sessions der APS-Fabrik für zwei Hauptzwecke:

1. **🔍 Template Generierung** - Automatische Erkennung von Message-Templates
2. **🎬 Replay Station** - Sessions für reproduzierbare Tests des OSF-UI

**Aufgenommene Sessions** werden als SQLite-Datenbank und Log-Datei gespeichert und dienen als Basis für alle weiteren Analysen und Tests.


## 🏗️ Architektur

```mermaid
graph LR
    A[MQTT Broker] -->|Live Messages| B[Session Recorder]
    B --> C[SQLite DB]
    B --> D[Log File]
    B --> E[Session Metadata]
    
    F[User Interface] --> B
    F --> G[Start/Stop Controls]
    F --> H[Status Display]
    
    style A fill:#f5f5f5
    style B fill:#90caf9,stroke:#1976d2,stroke-width:3px
    style C fill:#fff8e1
    style D fill:#fff8e1
    style E fill:#fff8e1
    style F fill:#bbdefb
    style G fill:#f5f5f5
    style H fill:#e3f2fd
```

## 🎮 Bedienung

### 1. **MQTT-Verbindung**
- **Broker:** localhost:1883 (Standard MQTT Port)
- **Status:** Verbunden/Nicht verbunden anzeigen
- **Test:** Verbindung testen vor Aufnahme starten

### 2. **Session-Aufnahme**
- **Start:** Aufnahme einer neuen Session beginnen
- **Stop:** Aufnahme beenden und Session speichern
- **Live-Monitoring:** Aktuelle Nachrichten-Anzahl anzeigen

### 3. **Session-Management**
- **Session-Name:** Automatisch generiert mit Timestamp
- **Speicherort:** `data/osf-data/sessions/`
- **Formate:** SQLite (.db) + Log (.log) Dateien

## 📊 Datenfluss

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Session Recorder UI
    participant R as Recorder Component
    participant M as MQTT Broker
    participant DB as SQLite DB
    participant L as Log File
    
    U->>UI: Start Recording
    UI->>R: start_recording()
    R->>M: Subscribe to all topics
    M-->>R: Live MQTT Messages
    R->>DB: Store structured data
    R->>L: Store raw messages
    R->>UI: Update message count
    UI->>U: Show live status
    
    U->>UI: Stop Recording
    UI->>R: stop_recording()
    R->>M: Unsubscribe
    R->>DB: Finalize database
    R->>L: Close log file
    UI->>U: Session saved
```

## 🔧 Technische Details

### **MQTT-Integration**
- **Protokoll:** paho-mqtt Python Client
- **Topics:** Alle verfügbaren Topics abonnieren
- **QoS:** Level 1 für zuverlässige Übertragung
- **Retain:** Optional (Checkbox „Retained Messages am Start miterfassen“)

### **Topic-Aufnahme (DR-25)**

Im Tab **Session Recorder** (und unter **Einstellungen → Session Recorder → Recording**): **Topic-Aufnahme**

- **Alle Topics (unfiltered):** jede empfangene Message landet im `.log` (Baseline / volle Topic-Union).
- **Analyse: ohne Arduino / BME680 / Kamera / LDR:** Messages zu `osf/arduino/…`, TXT `…/i/cam`, `…/i/bme680`, `…/i/ldr` (u. a.) werden **nicht** geschrieben — `subscribe("#")` bleibt unverändert; nur der **Schreibpfad** filtert.

Persistenz: `session_manager_settings.json` → `session_recorder.recording.recording_exclusion_preset` (`none` | `analysis`).

### **Session-Meta (erste Zeile in der `.log`)**

Beim Speichern schreibt der Recorder optional eine **erste JSON-Zeile** mit `_kind: "session_meta"` (ohne `topic` / `payload` / `timestamp`). **Replay** und `load_log_session` ignorieren sie. Felder u. a.: `recordingStartedAt`, `recordingEndedAt`, `durationSec`, `recordingExclusionPreset`, `brokerHost`, `osfWorkspaceVersion` (aus Root-`package.json`), `ccuOrdersDescription`, `ccuOrderOutcome` (`ok` | `nok` | `mixed` | `unknown`), `note`.

Die **INVENTORY**-Tabelle unter `data/osf-data/sessions/INVENTORY.md` sollte bei neuen/gelöschten Sessions manuell mitgepflegt werden; Hilfe: `python scripts/check_session_inventory.py`.

### **⚠️ Kritische Paho-MQTT-Patterns (nicht ändern)**

| Pattern | Grund |
|---------|-------|
| **`subscribe("#")` in `on_connect`** | Paho erfordert Subscribe *nach* Verbindung. Subscribe vor/nach `connect()` bricht die Aufnahme (keine Nachrichten). |
| **Erneuter Start nach Stop:** `subscribe("#")` in `start_recording` | Nach `unsubscribe` bei Stop muss bei erneutem Start erneut subscribt werden (on_connect feuert nicht). |
| **`_recording_active`-Filter in `on_message_received`** | Nur während Aufnahme speichern; verhindert Akkumulation alter Messages. |
| **Topic-Ausschluss nur im Write-Pfad** | Kein Weglassen von `subscribe` — siehe [DR-25](../../../03-decision-records/25-session-log-topic-filters.md). |

### **Daten-Speicherung**
- **SQLite:** Strukturierte Nachrichten-Daten
- **Log-File:** Rohe MQTT-Nachrichten für Debugging
- **Metadata:** Session-Info, Start/End-Zeit, Message-Count

### **Performance**
- **Threading:** Background-Thread für MQTT-Callbacks
- **Memory:** Streaming-Ansatz für große Sessions
- **Error-Handling:** Graceful Fehlerbehandlung

## 🎯 Sprint-Zuordnung

- **Sprint 1:** Grundstruktur und MQTT-Integration
- **Sprint 2:** SQLite-Speicherung und UI-Optimierung
- **Sprint 3:** Performance-Optimierung und Error-Handling

## 🔗 Verwandte Komponenten

- [**Replay Station**](replay-station.md) - Wiedergabe der aufgenommenen Sessions
- [**Settings**](../../development/dashboard-components.md) - MQTT-Konfiguration
