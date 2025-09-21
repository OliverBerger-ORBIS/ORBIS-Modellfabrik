# 🎬 Replay Station - Tab Dokumentation

## 🎯 Zweck

Die **Replay Station** ermöglicht die Wiedergabe von aufgezeichneten MQTT-Sessions. Sessions werden mit originalem Timing und korrekten MQTT-Nachrichten an den lokalen Broker gesendet.

## 🏗️ Architektur

```mermaid
graph LR
    A[Session Files] -->|Load| B[Replay Station]
    B -->|Parse| C[Message Queue]
    C -->|Timing| D[Replay Engine]
    D -->|Publish| E[MQTT Broker]
    E -->|Forward| F[OMF Dashboard]
    
    G[User Interface] --> B
    G --> H[Play/Pause/Stop]
    G --> I[Speed Control]
    G --> J[Progress Bar]
    
    style A fill:#fff8e1
    style B fill:#e8f5e8
    style C fill:#f3e5f5
    style D fill:#fff3e0
    style E fill:#fff8e1
    style F fill:#e1f5fe
    style G fill:#e1f5fe
    style H fill:#f3e5f5
    style I fill:#fff3e0
    style J fill:#fff3e0
```

## 🎮 Bedienung

### 1. **Session-Auswahl**
- **Verzeichnis:** `data/omf-data/sessions/`
- **Filter:** Regex-basierte Session-Suche
- **Formate:** SQLite (.db) Dateien
- **Auswahl:** Dropdown mit gefilterten Sessions

### 2. **Replay-Kontrollen**
- **▶️ Play:** Session starten/fortsetzen
- **⏸️ Pause:** Session pausieren
- **⏹️ Stop:** Session stoppen
- **🔄 Reset:** Session zurücksetzen

### 3. **Geschwindigkeits-Kontrolle**
- **1x:** Original-Geschwindigkeit
- **2x:** Doppelte Geschwindigkeit
- **5x:** Fünffache Geschwindigkeit
- **10x:** Zehnfache Geschwindigkeit

### 4. **Fortschritts-Anzeige**
- **Progress Bar:** Visueller Fortschrittsbalken
- **Message Count:** Aktuelle/Gesamt Nachrichten
- **Status:** Aktiv/Pausiert/Beendet

## 📊 Datenfluss

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Replay Station UI
    participant R as Replay Engine
    participant DB as SQLite DB
    participant M as MQTT Broker
    participant D as OMF Dashboard
    
    U->>UI: Select Session
    UI->>DB: Load session data
    DB-->>UI: Session messages
    UI->>R: Initialize replay
    
    U->>UI: Start Playback
    UI->>R: start_replay()
    R->>DB: Read messages with timing
    DB-->>R: Message + timestamp
    R->>M: Publish MQTT message
    M-->>D: Forward to dashboard
    R->>UI: Update progress
    UI->>U: Show live progress
    
    U->>UI: Pause/Stop
    UI->>R: pause_replay()
    R->>M: Stop publishing
    UI->>U: Show paused status
```

## 🔧 Technische Details

### **Session-Format**
- **SQLite:** Strukturierte Nachrichten-Daten
- **Timestamps:** Originale Zeitstempel für Timing
- **Topics:** Vollständige MQTT-Topic-Struktur
- **Payloads:** JSON-Nachrichten-Inhalte

### **Replay-Engine**
- **Threading:** Background-Thread für non-blocking UI
- **Timing:** Präzise Zeitsteuerung basierend auf Original-Timestamps
- **Speed-Control:** Multiplikator für Replay-Geschwindigkeit
- **Error-Handling:** Graceful Fehlerbehandlung bei MQTT-Problemen

### **MQTT-Integration**
- **Broker:** localhost:1883 (Standard MQTT Port)
- **QoS:** Level 1 für zuverlässige Übertragung
- **Retain:** False (nur Live-Replay)
- **Timeout:** 5 Sekunden pro Nachricht

## 🎯 Sprint-Zuordnung

- **Sprint 2:** Grundstruktur und Session-Loading
- **Sprint 3:** Replay-Engine und Timing-Kontrolle
- **Sprint 4:** UI-Optimierung und Performance-Tuning

## 🔗 Verwandte Komponenten

- [**Session Recorder**](session-recorder.md) - Aufnahme der Sessions
- [**Session Analysis**](session-analysis.md) - Analyse der Session-Daten
- [**OMF Dashboard**](../../development/dashboard-components.md) - Empfänger der Replay-Nachrichten
