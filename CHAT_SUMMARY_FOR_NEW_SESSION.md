# Chat-Zusammenfassung für neue Session

## 🎯 Aktueller Projektstand (September 2025)

### ✅ Abgeschlossene Arbeiten
1. **Dashboard v3.3.0 Entwicklung** - Neue Produktionsplanung-Features implementiert
2. **Shopfloor 3x4-Grid System** - Vollständig implementiert mit Intersection1-4 IDs
3. **FTS Route Generator** - YAML → MQTT Message Generator für Fahrerloses Transport System
4. **Produktkatalog** - Blau, Weiß, Rot Produkte mit Fertigungsaufträgen
5. **MessageGenerator Integration** - Alle neuen Features nutzen das zentrale Konzept
6. **Umfassende Tests** - Unit Tests für alle neuen Komponenten

### 🔧 Aktuelles Problem: Windows allUppercase Dateinamen
- **Problem**: Auf Windows System wurden Dateien in allUppercase abgelegt
- **Lokale Dateien**: Alle in lowercase (connection.yml, state.yml, etc.)
- **Windows Dateien**: Vermutlich CONNECTION.YML, STATE.YML, etc.
- **Auswirkung**: Mögliche Kompatibilitätsprobleme bei der Übertragung

### 📁 Wichtige Dateien und Strukturen
```
src_orbis/omf/config/
├── message_templates/templates/
│   ├── ccu/ (control.yml, state.yml, pairing.yml, etc.)
│   ├── fts/ (navigation_template.yml, order.yml, etc.)
│   ├── module/ (connection.yml, state.yml, order.yml, etc.)
│   ├── node_red/ (connection.yml, state.yml, etc.)
│   └── txt/ (control.yml, input.yml, output.yml, etc.)
├── products/product_catalog.yml
├── shopfloor/layout.yml, routes.yml
└── module_config.yml
```

### 🎯 Nächste Schritte
1. **Windows allUppercase Problem** - Dateinamen-Konventionen zwischen Systemen harmonisieren
2. **Sequenz-Systeme konsolidieren** - Doppelte Implementierungen vereinheitlichen
3. **Helper-Apps Struktur** - Klare Trennung zu aktiven Sourcen optimieren
4. **Architektur-Dokumentation** - Integriert in `docs_orbis/README.md`

### 💾 Wichtige Erinnerungen
- **Zentrales Konzept**: MessageGenerator als Herzstück verwenden [[memory:8530341]]
- **Konfiguration**: YAML-basierte Konfiguration bevorzugen [[memory:8528125]]
- **Tests**: Umfassende Tests für alle neuen Funktionen [[memory:8528084]]
- **Pre-commit**: Black (120 Zeilen), Ruff, pytest [[memory:7599139]]
- **Intersection IDs**: Intern Intersection1-4, MQTT nur 1-4 [[memory:8528077]]

### 🔄 Git Status
- **Branch**: debug/steering-b6e579b
- **Letzter Merge**: Erfolgreich von wfm-sequence-cursor2 zu main
- **Version**: Dashboard v3.3.0

### 🚀 Bereit für neue Session
Alle wichtigen Informationen sind in dieser Zusammenfassung enthalten. Die Entwicklung kann nahtlos fortgesetzt werden.
