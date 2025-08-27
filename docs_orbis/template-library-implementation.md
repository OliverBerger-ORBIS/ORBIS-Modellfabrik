# 📚 Template Library Implementation

## 🎯 Übersicht

Die **Template Library** löst das Problem der wiederholten MQTT-Template-Analyse durch persistente Speicherung der Analyse-Ergebnisse. Templates werden einmal analysiert und dann in einer SQLite-Datenbank gespeichert, zusammen mit Dokumentation und Metadaten.

## 🏗️ Architektur

### **📁 Dateistruktur:**
```
mqtt-data/
└── template_library/
    └── template_library.db    # SQLite-Datenbank für Templates
```

### **🗄️ Datenbank-Schema:**

#### **Templates Tabelle:**
```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT UNIQUE NOT NULL,      -- Eindeutiger Template-Name
    topic TEXT NOT NULL,                     -- MQTT Topic
    template_data TEXT NOT NULL,             -- JSON: Template, Variable Fields, Examples
    analysis_data TEXT NOT NULL,             -- JSON: Message Count, Sessions, etc.
    documentation TEXT,                      -- JSON: Beschreibung, Verwendung, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    template_type TEXT NOT NULL,             -- 'txt' oder 'ccu'
    message_count INTEGER DEFAULT 0,
    sessions_count INTEGER DEFAULT 0
);
```

#### **Analysis Sessions Tabelle:**
```sql
CREATE TABLE analysis_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,              -- Name der Analyse-Session
    analysis_type TEXT NOT NULL,             -- 'txt' oder 'ccu'
    topics_count INTEGER DEFAULT 0,          -- Anzahl gefundener Topics
    messages_count INTEGER DEFAULT 0,        -- Gesamtanzahl Nachrichten
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed'
);
```

## 🔧 Template Library Manager

### **Hauptfunktionen:**

#### **1. Template Speichern:**
```python
# TXT Templates speichern
session_name = template_library.save_txt_analysis(analysis_results)

# CCU Templates speichern
session_name = template_library.save_ccu_analysis(ccu_results)
```

#### **2. Template Abrufen:**
```python
# Alle Templates
all_templates = template_library.get_all_templates()

# Nach Typ filtern
txt_templates = template_library.get_all_templates('txt')
ccu_templates = template_library.get_all_templates('ccu')

# Spezifisches Template
template = template_library.get_template_by_name('TXT_j1_txt_1_f_i_stock')
```

#### **3. Dokumentation verwalten:**
```python
# Dokumentation aktualisieren
template_library.update_template_documentation(
    template_name='TXT_j1_txt_1_f_i_stock',
    documentation={
        'description': 'Stock-Status für Workpieces',
        'usage': 'Verwendung für Lagerverwaltung',
        'critical_for': ['HBW', 'DPS'],
        'workflow_step': 'Wareneingang'
    }
)
```

#### **4. Statistiken abrufen:**
```python
stats = template_library.get_library_stats()
# Returns: {'template_counts': [...], 'total_messages': 1234, 'latest_analysis': {...}}
```

## 🎨 Dashboard Integration

### **📋 MQTT Templates Tab:**

#### **1. Template Library Übersicht:**
- **📋 Templates:** Gesamtanzahl gespeicherter Templates
- **📨 Nachrichten:** Gesamtanzahl analysierter Nachrichten
- **🔍 TXT Templates:** Anzahl TXT Controller Templates
- **🏭 CCU Templates:** Anzahl CCU Templates

#### **2. Analyse-Historie:**
- **Letzte 3 Analysen** mit Details (Typ, Topics, Nachrichten, Datum)
- **Session-Namen** für Nachverfolgung

#### **3. Template-Analyse (nur bei Bedarf):**
- **🔄 TXT Templates analysieren:** Nur wenn neue Daten vorhanden
- **🏭 CCU Templates analysieren:** Nur wenn neue Daten vorhanden
- **Automatisches Speichern** in Template Library

#### **4. Template Library Anzeige:**
- **Filter-Optionen:** Nach Typ (TXT/CCU) und Suchbegriff
- **Template-Details:** Topic, Typ, Nachrichten, Sessions
- **Template-Daten:** JSON-Format mit Struktur
- **Variable Felder:** Identifizierte dynamische Felder
- **Beispiele:** Echte Nachrichten-Beispiele (ohne Platzhalter)

#### **5. Dokumentation-Editor:**
- **💡 Beschreibung:** Template-Zweck und Funktion
- **🎯 Verwendung:** Anwendungsfälle und Kontext
- **⚠️ Kritisch für:** Abhängige Module/Prozesse
- **🔄 Workflow-Schritt:** Position im Fertigungsprozess
- **💾 Speichern:** Persistente Dokumentation

## 🔄 Workflow

### **1. Erste Analyse:**
```
1. Dashboard öffnen → ⚙️ Einstellungen → 📋 MQTT Templates
2. 🔄 TXT Templates analysieren (klicken)
3. Analyse läuft → Ergebnisse werden automatisch gespeichert
4. Template Library wird mit neuen Templates gefüllt
5. Dokumentation kann bearbeitet werden
```

### **2. Nachfolgende Nutzung:**
```
1. Dashboard öffnen → Template Library ist sofort verfügbar
2. Templates sind persistent gespeichert
3. Dokumentation ist editierbar
4. Neue Analyse nur bei Bedarf (neue Session-Daten)
```

### **3. Template-Verwaltung:**
```
1. Filter nach Typ oder Suchbegriff
2. Template-Details anzeigen
3. Dokumentation bearbeiten und speichern
4. Beispiele und Struktur einsehen
```

## 📊 Vorteile

### **✅ Performance:**
- **Keine wiederholte Analyse** - Templates werden einmal erstellt
- **Schnelle Anzeige** - Daten sind sofort verfügbar
- **Reduzierte CPU-Last** - Keine aufwändigen Berechnungen

### **✅ Persistenz:**
- **Dokumentation bleibt erhalten** - Auch nach Dashboard-Neustart
- **Analyse-Historie** - Nachverfolgung der Template-Entwicklung
- **Versionierung** - Änderungen werden protokolliert

### **✅ Benutzerfreundlichkeit:**
- **Sofortige Verfügbarkeit** - Keine Wartezeiten
- **Editierbare Dokumentation** - Direkt im Dashboard
- **Filter und Suche** - Einfache Navigation
- **Strukturierte Anzeige** - Übersichtliche Darstellung

## 🔧 Technische Details

### **Template-Namen-Konvention:**
```
TXT_j1_txt_1_f_i_stock    # TXT Controller Input Stock
TXT_j1_txt_1_f_o_order    # TXT Controller Output Order
CCU_ccu_order_request     # CCU Order Request
CCU_ccu_state_config      # CCU State Configuration
```

### **JSON-Strukturen:**

#### **Template Data:**
```json
{
    "topic": "/j1/txt/1/f/i/stock",
    "template": {
        "nfcCode": "<nfcCode>",
        "workpieceType": "<workpieceType: RED, WHITE, BLUE>",
        "state": "<state: RAW>",
        "location": "<location: A1, A2, A3, B1, B2, B3, C1, C2, C3>"
    },
    "variable_fields": ["nfcCode", "workpieceType", "state", "location"],
    "enum_fields": {
        "workpieceType": ["RED", "WHITE", "BLUE"],
        "state": ["RAW"],
        "location": ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    },
    "examples": [
        {"nfcCode": "123456", "workpieceType": "RED", "state": "RAW", "location": "A1"},
        {"nfcCode": "789012", "workpieceType": "BLUE", "state": "RAW", "location": "B2"}
    ]
}
```

#### **Documentation:**
```json
{
    "description": "Stock-Status für Workpieces im Lager",
    "usage": "Verwendung für Lagerverwaltung und Workpiece-Tracking",
    "critical_for": ["HBW", "DPS", "Wareneingang"],
    "workflow_step": "Wareneingang"
}
```

## 🚀 Nächste Schritte

### **Geplante Erweiterungen:**
1. **Template-Versionierung** - Mehrere Versionen pro Template
2. **Export/Import** - Template-Bibliothek teilen
3. **Template-Validierung** - Automatische Prüfung der Struktur
4. **Template-Tests** - Automatisierte Tests für Templates
5. **Template-Statistiken** - Detaillierte Nutzungsanalysen

### **Integration mit anderen Systemen:**
1. **Node-RED Integration** - Templates in Node-RED verwenden
2. **MQTT Explorer** - Templates in MQTT Explorer anzeigen
3. **API-Export** - REST-API für Template-Zugriff
4. **Backup/Restore** - Template-Bibliothek sichern

## 🔗 Verwandte Dokumentation

- **[Template Analysis Improvement](template-analysis-improvement.md)**
- **[CCU Analysis Integration](ccu-analysis-integration.md)**
- **[MQTT Control Dashboard](mqtt-control-summary.md)**
- **[Template Message Manager](template-message-manager-implementation.md)**
