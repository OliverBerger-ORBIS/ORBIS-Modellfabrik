# Veraltete Registry-Tools (OMF2)

Die folgenden Tools referenzieren das Verzeichnis `registry/`, das mit der Migration von OMF2 zu OSF entfernt wurde:

- `validate_registry.py` – Validierung von modules/enums/workpieces gegen Schemas
- `validate_mapping.py` – Validierung von mapping.yml gegen Schema
- `check_mapping_collisions.py` – Prüfung auf Topic-Kollisionen
- `common.py` – Gemeinsame Hilfsfunktionen

**Status:** Ohne `registry/` sind diese Tools nicht ausführbar. Sie wurden aus dem Makefile entfernt.

Falls eine Registry-Struktur für OSF wieder eingeführt wird, können diese Scripts als Referenz dienen.
