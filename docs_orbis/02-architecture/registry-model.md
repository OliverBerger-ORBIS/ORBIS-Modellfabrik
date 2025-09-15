# Registry Model - 5 Kernprinzipien

## 🎯 Registry als Single Source of Truth

Das `registry/model/v1/` Verzeichnis ist die **einzige Quelle der Wahrheit** für alle MQTT-Nachrichtenstrukturen, Topic-Mappings und System-Konfigurationen.

## 📋 5 Kernprinzipien

### 1. Topic-freie Templates
**Prinzip:** Templates enthalten keine Topic-Strings, nur Nachrichtenstrukturen.

**Warum:** Wiederverwendung, kein Drift zwischen Topic und Template.

**Beispiel:**
```yaml
# ✅ Richtig: Template ohne Topic
templates:
  module.state.drill:
    structure:
      actionState: "<object>"
      timestamp: "<datetime>"

# ❌ Falsch: Topic im Template
templates:
  module/v1/ff/SVR4H76449/state:
    structure: ...
```

**CI-Guard:** `make check-templates-no-topics`

### 2. Exact Mappings vor Patterns
**Prinzip:** Spezifische Serial-Number-Mappings haben Priorität vor generischen Patterns.

**Warum:** Subtype-Spezifika (HBW Inventory vs. generisches module/state).

**Beispiel:**
```yaml
# ✅ Richtig: Exact vor Pattern
mappings:
  - { topic: "module/v1/ff/SVR3QA0022/state", template: "module.state.hbw_inventory" }
  - { pattern: "module/v1/ff/{module_id}/state", template: "module.state" }
```

**Konsequenz:** Klarer Pfad für spezialisierte Parser & UI.

### 3. Semantische Template-Keys
**Prinzip:** Template-Keys folgen dem Schema `domain.object.variant`.

**Beispiele:**
- `module.state.drill` - Modul-Status für DRILL
- `ccu.state.pairing` - CCU-Status für Pairing
- `fts.order.navigation` - FTS-Order für Navigation

**Vermeide:** Topic-Strings in Template-Namen (`module/v1/ff/...`)

### 4. Registry-Versionierung ≠ App-Versionierung
**Prinzip:** Registry hat eigene Semantische Versionierung, unabhängig von App-Versionen.

**Registry-Version:** `registry/model/v1/` (Major.Minor.Patch)
**App-Version:** `src_orbis/` (eigene Versionierung)

**Kompatibilität:** OMF-Dashboard prüft `MODEL_VERSION` beim Start.

### 5. Automatisierte Validierung
**Prinzip:** CI validiert Mapping/Schema-Konsistenz und verlinkt Doku-Abschnitte.

**Checks:**
- `make validate-mapping` - Topic-Template-Mappings
- `make validate-registry` - Schema-Konsistenz
- `make check-mapping-collisions` - Duplikate vermeiden
- `make check-templates-no-topics` - Topic-freie Templates

## 🏗️ Registry-Struktur

```
registry/model/v1/
├── manifest.yml              # Version, Owner, Kompatibilität
├── mappings/
│   └── topic_template.yml    # Alle Topic→Template Mappings
├── templates/
│   ├── module.state.*.yml    # Modul-Status-Templates
│   ├── module.connection.*.yml # Modul-Verbindungs-Templates
│   ├── module.order.*.yml    # Modul-Befehl-Templates
│   ├── ccu.state.*.yml       # CCU-Status-Templates
│   └── fts.*.yml             # FTS-Templates
├── entities/
│   ├── modules.yml           # Modul-Definitionen (Serial, Commands)
│   ├── workpieces.yml        # NFC-Codes, Workpiece-Types
│   └── enums.yml             # Zentrale Listen (Availability, Action)
└── schemas/
    └── *.json                # JSON-Schemas für Validierung
```

## 🔄 Versionierung & Kompatibilität

### Registry-Versionen

Das Registry-System unterstützt mehrere Versionen parallel:

- **`v0`**: Aktuelle stabile Version (saubere Basis)
- **`v1`**: Stable Registry (bestehend, unveränderlich)
- **`v2+`**: Development/Test-Versionen (für Experimente)

### Version Test Workflow

**Zweck:** Testen von Änderungen ohne Beeinträchtigung der stabilen Versionen.

**Durchführung:**
1. Alle Template Analyzer auf v2 konfigurieren
2. Vollständige Analyse mit aktueller Session-Datenbasis
3. Vergleich v0 vs v2 (Diff-Analyse)
4. Bei Erfolg: v2 → v0 verschieben

**Beispiel-Ergebnis (2025-09-15):**
```
Registry v0: 59 Templates (ursprünglich)
Registry v2: 59 Templates (ohne OMF Dashboard Session)

Hinzugefügt in v2:
+ bme680..c.bme680.yml    # Spezialisierte BME680 Templates
+ bme680..i.bme680.yml
+ cam..c.cam.yml          # Spezialisierte CAM Templates  
+ cam..i.cam.yml

Entfernt in v2:
- txt..c.bme680.yml       # Generische TXT Templates entfernt
- txt..c.cam.yml
- txt..i.bme680.yml
- txt..i.cam.yml
```

**Vorteile:**
- ✅ Bessere Datenqualität durch spezialisierte Analyzer
- ✅ Saubere Trennung verschiedener Datentypen
- ✅ Sichere Entwicklung ohne Contract-Bruch

### Registry-Versionierung
```yaml
# manifest.yml
version: 1.2.0
model_version: "1.2"
compatibility:
  min_omf_version: "3.3.0"
  breaking_changes: []
```

### App-Integration
```python
# OMF Dashboard prüft Kompatibilität
def check_registry_compatibility():
    registry_version = load_manifest()["model_version"]
    if not is_compatible(registry_version, OMF_VERSION):
        show_error("Registry version mismatch", 
                  "See docs_orbis/04-howto/validate-and-release.md")
```

### Breaking Changes
- **Major:** Inkompatible Template-Änderungen
- **Minor:** Neue Templates, erweiterte Enums
- **Patch:** Bug-Fixes, Dokumentation

## 🛠️ Mapping-Priorität

### 1. Exact Mappings (höchste Priorität)
```yaml
- { topic: "module/v1/ff/SVR3QA0022/state", template: "module.state.hbw_inventory" }
- { topic: "ccu/state/pairing", template: "ccu.state.pairing" }
```

### 2. Pattern Mappings (Fallback)
```yaml
- { pattern: "module/v1/ff/{module_id}/state", template: "module.state" }
- { pattern: "module/v1/ff/{module_id}/connection", template: "module.connection" }
```

### 3. Collision-Detection
```bash
make check-mapping-collisions
# Prüft: Kein Topic wird mehrfach gemappt
```

## 📊 Template-Struktur

### Standard-Template-Schema
```yaml
metadata:
  category: MODULE
  sub_category: State
  description: "Template description"
  icon: "📊"
  version: "1.0.0"
  last_updated: "2025-01-15"

templates:
  template.key:
    category: MODULE
    sub_category: State
    description: "Specific template description"
    direction: inbound|outbound|bidirectional
    structure:
      field1: "<string>"
      field2: "<object>"
    examples:
      - field1: "example value"
        field2: { nested: "object" }
    validation:
      required_fields: ["field1"]
      field1_values: ["VALUE1", "VALUE2"]
    friendly_name: "Human readable name"
```

## 🔗 Integration mit Source Code

### Template-Loading
```python
# MessageTemplateManager lädt Registry
def load_templates():
    registry_path = "registry/model/v1/templates/"
    return load_all_templates(registry_path)
```

### Mapping-Resolution
```python
# TopicManager löst Topics auf
def resolve_topic(topic):
    exact_match = mappings.get(topic)
    if exact_match:
        return exact_match
    return pattern_match(topic)
```

### Validierung
```python
# Validator nutzt Registry-Schema
def validate_message(template_key, payload):
    template = registry.get_template(template_key)
    return validate_against_schema(payload, template.schema)
```

## Umgang mit Observations

Die Registry unterscheidet zwischen **stabilen Artefakten** und **laufenden Beobachtungen**:

- **`/schemas`**  
  Enthält validierende JSON/YAML-Schemas. Diese definieren die erwartete Struktur und Regeln für Templates.

- **`/templates`**  
  Enthält die freigegebenen und stabilen Templates, die vom OMF-Dashboard und anderen Komponenten verwendet werden.

- **`registry/observations/`**  
  Arbeitsverzeichnis für Entwickler (innerhalb der Registry). Hier werden Payloads oder Strukturen abgelegt, die im Betrieb oder bei Analysen auffallen:
  - Beispiele für neue Felder, die im Live-System auftauchen,
  - Vorschläge für Erweiterungen oder Anpassungen bestehender Templates,
  - Sonderfälle oder fehlerhafte Payloads, die noch bewertet werden müssen.

### Workflow

#### **Initiale Phase (aktuell):**
1. **Neue Beobachtung erfassen**  
   Ein neues Beispiel oder ein Vorschlag wird als YAML/JSON-Datei in `registry/observations/` abgelegt.  
   → Namensschema: `<datum>_<topic>_<kurzbeschreibung>.yml`

2. **Direkte Migration**  
   Observation wird direkt in Registry übernommen (Review-Prozess abgekürzt):
   - Template/Schema wird entsprechend angepasst
   - Observation wird geschlossen (Status: `migrated`)

#### **Spätere Phase (nach Registry v1.0):**
1. **Neue Beobachtung erfassen**  
   Ein neues Beispiel oder ein Vorschlag wird als YAML/JSON-Datei in `registry/observations/` abgelegt.

2. **Review & Analyse**  
   Beobachtungen werden durch das Team bewertet:
   - Ist es ein valider neuer Anwendungsfall?
   - Muss ein bestehendes Template erweitert werden?
   - Oder handelt es sich um einen Ausreißer / Fehler?

3. **Migration in Registry**  
   - Wenn relevant → Anpassung des passenden Templates/Schemas.  
   - Observation wird geschlossen (z. B. ins Archiv verschoben oder im Commit-History dokumentiert).

### Vorteile

- Stabilität im Kern (`/templates` & `/schemas`)  
- Transparente Nachvollziehbarkeit von Änderungen  
- Sammelstelle für neue Ideen & Betriebserkenntnisse

---

**"Registry ist die Quelle der Wahrheit - Templates sind topic-frei, Mappings sind priorisiert, Versionierung ist semantisch."**
