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

---

**"Registry ist die Quelle der Wahrheit - Templates sind topic-frei, Mappings sind priorisiert, Versionierung ist semantisch."**
