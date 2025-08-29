# **ORBIS Modellfabrik (OMF) - Architektur-Dokumentation**

## **Übersicht**
Diese Dokumentation beschreibt die neue Architektur für das ORBIS Modellfabrik Dashboard (OMF) und die zugehörigen Datenstrukturen.

## **📁 Verzeichnisstruktur**

### **Source Code (`src_orbis/`)**
```
src_orbis/
├── omf/                          # ORBIS Modellfabrik (Hauptmodul)
│   ├── __init__.py
│   ├── dashboard/                 # Dashboard-Komponenten
│   │   ├── __init__.py
│   │   ├── omf_dashboard.py      # Haupt-Dashboard (neu)
│   │   ├── components/           # UI-Komponenten
│   │   │   ├── __init__.py
│   │   │   ├── overview.py       # Overview Tab
│   │   │   ├── orders.py         # Aufträge Tab
│   │   │   ├── message_monitor.py # Messages-Monitor
│   │   │   ├── message_controls.py # Message-Controls
│   │   │   └── settings.py       # Settings Tab
│   │   ├── utils/                # Hilfsfunktionen
│   │   │   ├── __init__.py
│   │   │   ├── data_handling.py
│   │   │   └── mqtt_utils.py
│   │   └── config/               # Dashboard-Konfiguration
│   │       ├── __init__.py
│   │       ├── settings.py
│   │       └── i18n.py          # Zweisprachigkeit (DE/EN)
│   ├── tools/                    # Produktiv-Tools
│   │   ├── __init__.py
│   │   ├── message_template_manager.py
│   │   ├── module_manager.py
│   │   └── order_manager.py
│   └── config/                   # OMF-Konfiguration
│       ├── __init__.py
│       └── omf_config.py
├── analysis/                     # SEPARAT: Analysis-Tools
│   ├── __init__.py
│   ├── session_analyzer.py       # Session Analyse
│   ├── template_analyzer.py      # Template-Analyse
│   └── replay_tool.py           # Replay-Tool
└── mqtt/                         # Bestehende MQTT-Tools (behalten)
    └── ... (bestehende Struktur)
```

### **Daten (`omf-data/`)**
```
omf-data/
├── sessions/                     # Session-Daten
│   ├── production/               # Produktions-Sessions
│   ├── development/              # Entwicklungs-Sessions
│   └── archived/                 # Archivierte Sessions
├── templates/                    # Template-Daten
│   ├── message_templates.yaml
│   └── analysis_results/
├── logs/                        # Log-Dateien
│   ├── dashboard/
│   └── system/
└── exports/                     # Export-Dateien
    ├── reports/
    └── analytics/
```

## **🎯 Dashboard-Tab-Struktur**

### **Produktiv-Dashboard (OMF)**
- **Overview**
  - Modul-Status (Modul Info mit aktuellem Status)
  - Bestellung
  - Bestellung-Rohware
  - Lagerbestand
- **Aufträge (Orders)**
  - Auftragsverwaltung (Mapping omf-id aus ERP auf aps-ID)
  - Laufende Aufträge (Ongoing Orders mit Production Steps)
- **Messages-Monitor**
  - Anzeige der MQTT-Messages (empfangen/gesendet)
- **Message-Controls**
  - Steuerung der Fabrik, Module durch MQTT-Messages
- **Settings**
  - Dashboard-Settings
  - Modul-Config
  - NFC-Config
  - Topic-Config
  - Messages-Templates

### **Analysis-Tools (Separate Anwendung)**
- **Session Analyse**
  - Auswertung von Session.db und Logs
- **Template-Analyse**
  - Analyse der Nachrichten zur Erstellung von MessageTemplates
- **Replay**
  - Abspielen von aufgenommenen Sessions

## **🌐 Zweisprachigkeit**

### **Konzept**
- **Source-Namen:** Englisch (technisch konsistent)
- **UI-Namen:** Deutsch (benutzerfreundlich)
- **Konfiguration:** Über Settings umschaltbar

### **Implementierung**
```python
# src_orbis/omf/dashboard/config/i18n.py
SUPPORTED_LANGUAGES = ['de', 'en']
DEFAULT_LANGUAGE = 'de'

TRANSLATIONS = {
    'de': {
        'overview': 'Übersicht',
        'orders': 'Aufträge',
        'message_monitor': 'Nachrichten-Monitor',
        # ...
    },
    'en': {
        'overview': 'Overview',
        'orders': 'Orders',
        'message_monitor': 'Message Monitor',
        # ...
    }
}
```

## **🔧 Migration-Strategie**

### **Phase 1: Grundgerüst**
1. Neue Verzeichnisstruktur erstellen ✅
2. Grundgerüst für Dashboard-Komponenten
3. Konfiguration und Zweisprachigkeit

### **Phase 2: Komponenten-Migration**
1. Module Status aus V2.0.0 übernehmen
2. MessageTemplate Manager integrieren
3. MQTT-Integration

### **Phase 3: Neue Features**
1. Order Management
2. Session Management
3. Analysis-Tools

### **Phase 4: Daten-Migration**
1. Wichtige Sessions migrieren
2. Template-Daten übertragen
3. Konfiguration anpassen

## **🧪 Test-Strategie**

### **Nach jeder Änderung:**
```bash
python -m py_compile src_orbis/omf/dashboard/omf_dashboard.py
python test_dashboard_before_commit.py
streamlit run src_orbis/omf/dashboard/omf_dashboard.py --server.port=8506
```

### **Commit-Strategie**
- Häufige Commits nach jedem erfolgreichen Schritt
- Immer einen funktionierenden Stand haben
- Rollback bei Fehlern möglich

## **📋 Nächste Schritte**

1. **Grundgerüst für Dashboard-Komponenten erstellen**
2. **Konfiguration und Zweisprachigkeit implementieren**
3. **Erste UI-Komponenten entwickeln**
4. **Tests nach jedem Schritt**

---

**Status:** ✅ Verzeichnisstruktur erstellt
**Nächster Schritt:** Dashboard-Grundgerüst erstellen
