# 🔍 Template Analysis - Tab Dokumentation

## 🎯 Zweck

Die **Template Analysis** nutzt die bestehenden Template-Analyzer, um Message-Templates aus Session-Daten zu generieren. Diese Templates dienen als Basis für den MessageGenerator und ermöglichen die automatische Erkennung von Message-Strukturen.

## 🏗️ Architektur

```mermaid
graph TD
    A[Session Files] -->|Load| B[Template Analysis]
    B --> C[Template Analyzers]
    
    C --> D[CCU Analyzer]
    C --> E[Module Analyzer]
    C --> F[Node-RED Analyzer]
    C --> G[TXT Analyzer]
    C --> H[BME680 Analyzer]
    C --> I[Camera Analyzer]
    
    D --> J[CCU Templates]
    E --> K[Module Templates]
    F --> L[Node-RED Templates]
    G --> M[TXT Templates]
    H --> N[BME680 Templates]
    I --> O[Camera Templates]
    
    J --> P[Template Library]
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    Q[User Interface] --> B
    Q --> R[Session Selection]
    Q --> S[Analyzer Selection]
    Q --> T[Template Preview]
    
    style A fill:#fff8e1
    style B fill:#e8f5e8
    style C fill:#f3e5f5
    style D fill:#fff3e0
    style E fill:#fff3e0
    style F fill:#fff3e0
    style G fill:#fff3e0
    style H fill:#fff3e0
    style I fill:#fff3e0
    style J fill:#e1f5fe
    style K fill:#e1f5fe
    style L fill:#e1f5fe
    style M fill:#e1f5fe
    style N fill:#e1f5fe
    style O fill:#e1f5fe
    style P fill:#fff8e1
    style Q fill:#e1f5fe
    style R fill:#f3e5f5
    style S fill:#fff3e0
    style T fill:#fff8e1
```

## 🎮 Bedienung

### 1. **Session-Auswahl**
- **Verzeichnis:** `data/omf-data/sessions/`
- **Filter:** Regex-basierte Session-Suche
- **Formate:** SQLite (.db) Dateien
- **Auswahl:** Dropdown mit gefilterten Sessions

### 2. **Analyzer-Auswahl**
- **CCU Analyzer:** CCU-Nachrichten analysieren
- **Module Analyzer:** Modul-Nachrichten analysieren
- **Node-RED Analyzer:** Node-RED Nachrichten analysieren
- **TXT Analyzer:** TXT-Nachrichten analysieren
- **BME680 Analyzer:** BME680-Sensor-Nachrichten analysieren
- **Camera Analyzer:** Kamera-Nachrichten analysieren

### 3. **Template-Generierung**
- **Analyse:** Automatische Template-Erkennung
- **Validierung:** Template-Struktur prüfen
- **Export:** YAML-Templates für MessageGenerator
- **Vorschau:** Template-Inhalt anzeigen

### 4. **Template-Bibliothek**
- **Verwaltung:** Generierte Templates verwalten
- **Suche:** Templates nach Komponente filtern
- **Bearbeitung:** Templates manuell anpassen
- **Integration:** Templates in MessageGenerator integrieren

## 📊 Datenfluss

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Template Analysis UI
    participant A as Analysis Engine
    participant DB as SQLite DB
    participant T as Template Analyzers
    participant L as Template Library
    participant M as MessageGenerator
    
    U->>UI: Select Session
    UI->>DB: Load session data
    DB-->>A: Raw message data
    
    U->>UI: Select Analyzer
    UI->>T: Run specific analyzer
    T->>A: Process messages
    A-->>T: Analyzed message patterns
    T-->>UI: Generated templates
    
    UI->>L: Store templates
    L-->>UI: Template library updated
    
    U->>UI: Export templates
    UI->>M: Integrate templates
    M-->>UI: Templates ready for use
```

## 🔧 Technische Details

### **Template-Analyzer**
- **CCU Analyzer:** `ccu_template_analyzer.py`
- **Module Analyzer:** `module_template_analyzer.py`
- **Node-RED Analyzer:** `nodered_template_analyzer.py`
- **TXT Analyzer:** `txt_template_analyzer.py`
- **BME680 Analyzer:** `bme680_template_analyzer.py`
- **Camera Analyzer:** `cam_template_analyzer.py`

### **Template-Format**
- **YAML-Struktur:** Standardisiertes Template-Format
- **Schema-Validation:** JSON-Schema für Template-Validierung
- **Meta-Daten:** Beschreibung, Version, Autor
- **Beispiele:** Sample-Messages für Testing

### **Integration**
- **MessageGenerator:** Templates für Message-Generierung
- **Registry:** Templates in Registry-System integrieren
- **Validation:** Template-Struktur und -Inhalt prüfen
- **Export:** Templates für externe Nutzung exportieren

## 🎯 Sprint-Zuordnung

- **Sprint 4:** Integration der bestehenden Template-Analyzer
- **Sprint 5:** Template-Bibliothek und UI-Optimierung
- **Sprint 6:** MessageGenerator-Integration und Testing

## 🔗 Verwandte Komponenten

- [**Session Analysis**](session-analysis.md) - Basis für Template-Analyse
- [**MessageGenerator**](../../../02-architecture/message-template-system.md) - Nutzer der generierten Templates
- [**Registry System**](../../../02-architecture/registry-model.md) - Template-Speicherung und -Verwaltung
