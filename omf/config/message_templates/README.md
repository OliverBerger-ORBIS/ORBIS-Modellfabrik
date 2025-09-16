# OMF Message Templates - Modulare Struktur

## **📋 Problem der alten Struktur:**
- **Monolithische YAML** (8669 Zeilen!) - schwer wartbar
- **Keine Versionierung** der Templates
- **Schwierige Updates** bei neuen Erkenntnissen
- **Keine Modularität** - alles in einer Datei

## **✅ Neue modulare Struktur:**

```
omf/omf/config/message_templates/
├── README.md
├── metadata.yml                    # Globale Metadaten
├── categories.yml                  # Kategorien und Sub-Kategorien
├── templates/
│   ├── ccu/                       # CCU Templates
│   │   ├── control.yml
│   │   ├── order.yml
│   │   ├── state.yml
│   │   └── wareneingang.yml
│   ├── module/                    # Module Templates
│   │   ├── connection.yml
│   │   ├── factsheet.yml
│   │   ├── instant_action.yml
│   │   ├── order.yml
│   │   └── state.yml
│   ├── txt/                       # TXT Controller Templates
│   │   ├── control.yml
│   │   ├── function_input.yml
│   │   ├── function_output.yml
│   │   ├── input.yml
│   │   └── output.yml
│   └── node_red/                  # Node-RED Templates
│       ├── connection.yml
│       ├── dashboard.yml
│       ├── flows.yml
│       ├── state.yml
│       └── ui.yml
├── examples/                      # Beispiel-Nachrichten
│   ├── ccu_examples.json
│   ├── module_examples.json
│   ├── txt_examples.json
│   └── node_red_examples.json
└── validation/                    # Validierungsregeln
    ├── common_rules.yml
    ├── ccu_rules.yml
    ├── module_rules.yml
    └── txt_rules.yml
```

## **🎯 Vorteile der neuen Struktur:**

### **✅ Modularität:**
- **Separate Dateien** für jede Kategorie/Sub-Kategorie
- **Einfache Wartung** einzelner Template-Gruppen
- **Klare Trennung** der Verantwortlichkeiten

### **✅ Versionierung:**
- **Git-basierte Versionskontrolle** für jedes Template
- **Change Tracking** pro Kategorie
- **Rollback-Möglichkeit** einzelner Templates

### **✅ Erweiterbarkeit:**
- **Neue Templates** einfach hinzufügen
- **Neue Kategorien** ohne große YAML zu ändern
- **Inkrementelle Updates** möglich

### **✅ Wartbarkeit:**
- **Kleine, fokussierte Dateien**
- **Klare Struktur** und Organisation
- **Einfache Suche** und Navigation

## **🔧 Migration-Strategie:**

### **Phase 1: Struktur erstellen**
1. **Verzeichnisstruktur** anlegen
2. **Metadata und Kategorien** extrahieren
3. **Basis-Templates** migrieren

### **Phase 2: Templates aufteilen**
1. **CCU Templates** in separate Dateien
2. **Module Templates** in separate Dateien
3. **TXT Templates** in separate Dateien
4. **Node-RED Templates** in separate Dateien

### **Phase 3: Beispiele und Validierung**
1. **Beispiel-Nachrichten** extrahieren
2. **Validierungsregeln** strukturieren
3. **Dokumentation** vervollständigen

### **Phase 4: Manager anpassen**
1. **OMF Message Template Manager** erstellen
2. **Modulare Ladefunktionen** implementieren
3. **Backward Compatibility** sicherstellen

## **📊 Template-Struktur pro Datei:**

```yaml
# templates/ccu/control.yml
metadata:
  version: "1.0"
  last_updated: "2025-08-29"
  description: "CCU Control Templates"

templates:
  ccu/control:
    description: "CCU Steuerungsbefehle"
    structure:
      command: <string>
      parameters: <object>
      timestamp: <datetime>
    examples:
      - command: "start"
        parameters: {"module": "hbw"}
        timestamp: "2025-08-29T10:00:00Z"
    validation_rules:
      - "command muss gültiger Befehl sein"
      - "timestamp muss ISO 8601 Format haben"
```

## **🚀 Nächste Schritte:**
1. **Verzeichnisstruktur** erstellen
2. **Erste Template-Dateien** migrieren
3. **OMF Message Template Manager** implementieren
4. **Dashboard-Integration** testen
