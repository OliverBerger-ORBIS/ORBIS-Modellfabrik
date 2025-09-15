# Registry Observations

## Zweck

Das `registry/observations/` Verzeichnis ist das Arbeitsverzeichnis für Entwickler zur Sammlung von Beobachtungen aus dem Live-System. Hier werden Payloads, Strukturen und Vorschläge abgelegt, die bei Analysen oder im Betrieb auffallen.

## Struktur

```
registry/observations/
├── templates/          # Template-Vorschläge und -Erweiterungen
├── schemas/           # Schema-Vorschläge und -Validierungen
├── payloads/          # Beispiele und neue Payload-Strukturen
├── issues/            # Fehlerfälle und Problembeispiele
├── archive/           # Geschlossene/abgeschlossene Observations
├── observation.schema.json  # JSON Schema für Observation-Validierung
└── README.md          # Diese Datei
```

## Workflow

### Initiale Phase (aktuell)
1. **Neue Beobachtung erfassen**  
   Ein neues Beispiel oder ein Vorschlag wird als YAML/JSON-Datei abgelegt.  
   → Namensschema: `<datum>_<topic>_<kurzbeschreibung>.yml`

2. **Direkte Migration**  
   Observation wird direkt in Registry übernommen (Review-Prozess abgekürzt):
   - Template/Schema wird entsprechend angepasst
   - Observation wird geschlossen (Status: `migrated`)

### Spätere Phase (nach Registry v1.0)
1. **Neue Beobachtung erfassen**  
   Ein neues Beispiel oder ein Vorschlag wird als YAML/JSON-Datei abgelegt.

2. **Review & Analyse**  
   Beobachtungen werden durch das Team bewertet:
   - Ist es ein valider neuer Anwendungsfall?
   - Muss ein bestehendes Template erweitert werden?
   - Oder handelt es sich um einen Ausreißer / Fehler?

3. **Migration in Registry**  
   - Wenn relevant → Anpassung des passenden Templates/Schemas.  
   - Observation wird geschlossen (z. B. ins Archiv verschoben oder im Commit-History dokumentiert).

## Observation-Format

Jede Observation-Datei folgt dem Schema in `observation.schema.json`:

```yaml
metadata:
  date: "2025-09-15"
  author: "Template Analyzer"
  source: "analysis"
  topic: "ccu/order/request"
  related_template: "ccu.order.request"
  status: "open"

observation:
  description: "Auto-analyzed CCU topic with 76 messages"
  payload_example: {...}

analysis:
  initial_assessment: "Template structure generated with 2 variable fields"
  open_questions:
    - "Soll diese Template-Struktur in die Registry übernommen werden?"

proposed_action:
  - "Template 'ccu/order/request' in Registry v1 übernehmen"

tags: ["ccu", "auto-generated", "template"]
priority: "medium"
```

## Wichtige Regeln

- **Namenskonvention**: `<datum>_<kategorie>_<kurzbeschreibung>.yml`
- **Status-Workflow**: `open` → `reviewed` → `migrated`/`discarded`
- **Datum-Format**: `YYYY-MM-DD`
- **Encoding**: UTF-8
- **Dateiformat**: YAML (`.yml`)

## Registry-Integration

- **Templates**: Observations werden zu `registry/model/v0/templates/` migriert
- **Schemas**: Validierungsregeln werden zu `registry/model/v1/schemas/` hinzugefügt
- **Mapping**: Topic-Mappings werden in `registry/model/v1/topic_template.yml` aktualisiert

## Validierung

```bash
# Alle Observations validieren
make validate-observations

# Einzelne Observation validieren
python tools/validate_observations.py
```