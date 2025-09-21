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
    style B fill:#90caf9,stroke:#1976d2,stroke-width:3px
    style C fill:#bbdefb
    style D fill:#bbdefb
    style E fill:#bbdefb
    style F fill:#e3f2fd
    style G fill:#e3f2fd
    style H fill:#e3f2fd
    style I fill:#e3f2fd
    style J fill:#e3f2fd
    style K fill:#f5f5f5
    style L fill:#f5f5f5
    style M fill:#f5f5f5
```

### **Farbnuancen-Erklärung:**
- **🔵 Dunkelblau (`#90caf9`):** Zentrale Komponente "Session Analysis" - **Hauptfunktion**
- **🔵 Mittelblau (`#bbdefb`):** Kern-Komponenten (Timeline, Graph, Statistics) - **Direkte Analysen**
- **🔵 Hellblau (`#e3f2fd`):** UI-Komponenten und Ergebnisse - **Darstellung**
- **⚪ Grau (`#f5f5f5`):** Externe/Input-Komponenten - **Eingaben**

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
