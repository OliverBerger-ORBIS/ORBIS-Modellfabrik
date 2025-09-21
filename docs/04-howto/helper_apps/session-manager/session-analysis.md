# 📊 Session Analysis - Tab Dokumentation

## 🎯 Zweck

Die **Session Analysis** ermöglicht die detaillierte Analyse von aufgezeichneten MQTT-Sessions. Sie bietet Timeline-Visualisierung, Message-Statistiken und Graph-basierte Darstellung von Message-Ketten.

## 🏗️ Architektur

```mermaid
graph TD
    A[Session Files] -->|Load| B[Session Analysis]
    B --> C[Timeline Visualizer]
    B --> D[Graph Analyzer]
    B --> E[Message Statistics]
    
    C --> F[Time-based Chart]
    D --> G[Message Chain Graph]
    E --> H[Topic Statistics]
    E --> I[Payload Analysis]
    
    J[User Interface] --> B
    J --> K[Session Selection]
    J --> L[Filter Controls]
    J --> M[Visualization Options]
    
    style A fill:#fff8e1
    style B fill:#e8f5e8
    style C fill:#f3e5f5
    style D fill:#fff3e0
    style E fill:#fff8e1
    style F fill:#e1f5fe
    style G fill:#e1f5fe
    style H fill:#f2f2f2
    style I fill:#f2f2f2
    style J fill:#e1f5fe
    style K fill:#f3e5f5
    style L fill:#fff3e0
    style M fill:#fff8e1
```

## 🎮 Bedienung

### 1. **Session-Auswahl**
- **Verzeichnis:** `data/omf-data/sessions/`
- **Filter:** Regex-basierte Session-Suche
- **Formate:** SQLite (.db) Dateien
- **Auswahl:** Dropdown mit gefilterten Sessions

### 2. **Timeline-Visualisierung**
- **Zeitachse:** X-Achse zeigt Zeitverlauf
- **Topics:** Y-Achse zeigt verschiedene Topics
- **Message-Points:** Jeder Punkt = eine MQTT-Nachricht
- **Interaktiv:** Zoom, Pan, Hover für Details

### 3. **Graph-Visualisierung**
- **Message-Ketten:** Verbindungen zwischen Messages
- **Meta-Daten:** orderID, workpieceId, nfcCode
- **Komponenten:** Welche Komponenten beteiligt sind
- **Abläufe:** Reihenfolge der Message-Verarbeitung

### 4. **Statistiken**
- **Topic-Count:** Anzahl Nachrichten pro Topic
- **Payload-Size:** Größe der Nachrichten
- **Time-Span:** Dauer der Session
- **Component-Activity:** Aktivität der verschiedenen Komponenten

## 📊 Datenfluss

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Session Analysis UI
    participant A as Analysis Engine
    participant DB as SQLite DB
    participant T as Timeline Visualizer
    participant G as Graph Analyzer
    participant S as Statistics Engine
    
    U->>UI: Select Session
    UI->>DB: Load session data
    DB-->>A: Raw message data
    A->>T: Process timeline data
    A->>G: Extract message chains
    A->>S: Calculate statistics
    
    T-->>UI: Timeline chart data
    G-->>UI: Graph structure data
    S-->>UI: Statistical data
    
    UI->>U: Display visualizations
    
    U->>UI: Apply filters
    UI->>A: Filter messages
    A->>T: Update timeline
    A->>G: Update graph
    A->>S: Update statistics
    UI->>U: Show filtered results
```

## 🔧 Technische Details

### **Timeline-Visualisierung**
- **Technologie:** Plotly für interaktive Charts
- **Daten:** Timestamp + Topic + Payload-Size
- **Performance:** Optimiert für große Sessions (10k+ Messages)
- **Interaktivität:** Zoom, Pan, Hover, Click für Details

### **Graph-Analyse**
- **Technologie:** NetworkX für Graph-Verarbeitung
- **Meta-Daten:** orderID, workpieceId, nfcCode, moduleId
- **Algorithmen:** Message-Chain-Erkennung und -Visualisierung
- **Layout:** Automatische Graph-Layout-Optimierung

### **Statistik-Engine**
- **Topics:** Häufigkeit und Verteilung
- **Payloads:** Größe und Struktur-Analyse
- **Timing:** Zeitliche Verteilung und Patterns
- **Components:** Aktivität der verschiedenen APS-Komponenten

## 🎯 Sprint-Zuordnung

- **Sprint 3:** Timeline-Visualisierung und Grundstatistiken
- **Sprint 4:** Graph-Analyse und Message-Chain-Erkennung
- **Sprint 5:** Performance-Optimierung und erweiterte Features

## 🔗 Verwandte Komponenten

- [**Template Analysis**](template-analysis.md) - Template-Erkennung basierend auf Session-Daten
- [**Session Recorder**](session-recorder.md) - Aufnahme der zu analysierenden Sessions
- [**Replay Station**](replay-station.md) - Wiedergabe der analysierten Sessions
