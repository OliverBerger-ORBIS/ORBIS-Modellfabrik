# Analyse: scripts/ und tools/ – Veraltete Elemente

**Stand:** 2025-02  
**Status:** Abgeschlossen

## Zusammenfassung

| Bereich | Befund | Aktion |
|---------|--------|--------|
| **tools/** registry-Tools | `registry/` existiert nicht (OMF2 entfernt) | Veraltet dokumentiert, Makefile-Targets deaktiviert |
| **tools/node_red_analysis** | Pfad `node_red/` statt `APS-NodeRED/` | Pfade angepasst |
| **Makefile** | `integrations/node_red/`, `omf/scripts` | Pfade auf APS-NodeRED, validate-development-rules entfernt |
| **integrations/APS-NodeRED** | Scripts/Docs nutzen `node_red/` | Einheitlich auf APS-NodeRED umgestellt |
| **.pre-commit-config.yaml** | OMF3-Bezeichnungen | Auf OSF aktualisiert |
| **validate_mermaid_diagrams.py** | OMF in Docstrings | Auf OSF aktualisiert |

---

## 1. tools/ – Registry-bezogene Scripts (VERALTET)

### Betroffene Dateien
- `tools/validate_registry.py`
- `tools/validate_mapping.py`
- `tools/check_mapping_collisions.py`
- `tools/common.py`

### Problem
- Alle lesen aus `registry/` (modules.yml, enums.yml, mapping.yml, Schemas)
- Verzeichnis `registry/` existiert nicht mehr (mit OMF2 entfernt)
- `make validate-registry`, `make validate-mapping`, `make check-mapping-collisions` würden fehlschlagen

### Abhängige Tools (ebenfalls veraltet)
- `tools/check_templates_no_topics.py` – nutzt `common.py` → registry
- `tools/render_template.py` – nutzt `common.py` → registry
- `tools/validate_observations.py` – prüfen ob registry-Abhängigkeit

### Entscheidung
- Tools bleiben im Repo (für Dokumentation/evtl. Revival)
- `tools/OBSOLETE_REGISTRY_README.md` erstellt
- Makefile-Targets für registry-Tools entfernt oder mit Hinweis versehen

---

## 2. tools/node_red_analysis – Pfad-Fehler

### Problem
- `aps_analysis.py` Zeile 757: `integrations/node_red/backups/...` 
- Tatsächlicher Pfad: `integrations/APS-NodeRED/backups/...`
- README referenziert `integrations/node_red/backups/`

### Aktion
- Pfad auf `integrations/APS-NodeRED/backups/` geändert
- README angepasst

---

## 3. Makefile – Veraltete Referenzen

### 3.1 Node-RED Pfade
- Zeilen 48–59: `./integrations/node_red/scripts/`  
- **Korrektur:** `./integrations/APS-NodeRED/scripts/`
- Usage-Beispiele: `integrations/node_red/backups/` → `integrations/APS-NodeRED/backups/`

### 3.2 validate-development-rules
- Zeile 67: `$(PY) omf/scripts/validate_development_rules.py`
- Verzeichnis `omf/` existiert nicht
- **Aktion:** Target entfernt (oder auf existierendes Script umstellen)

---

## 4. integrations/APS-NodeRED – Konsistenz

### Scripts (Backup/Restore)
- `nodered_backup_ssh.sh`: DEST=`integrations/node_red/backups` → `integrations/APS-NodeRED/backups`
- `nodered_backup_adminapi.sh`: gleiche Anpassung
- `nodered_restore_ssh.sh`, `nodered_restore_adminapi.sh`: Pfad-Hinweise anpassen

### Docs
- README.md, SSH_SETUP.md: `node_red` → `APS-NodeRED`

---

## 5. .pre-commit-config.yaml

- Kommentar: "OMF3 (Angular)" → "OSF (Angular)"
- Hook-Namen/Beschreibungen: "OMF3 Tests", "OMF3 Lint" → "OSF Tests", "OSF Lint"

---

## 6. tools/validate_mermaid_diagrams.py

- Docstring: "OMF Projekt", "OMF-Standards", "OMF-Palette" → "OSF Projekt", "OSF-Standards", "OSF-Palette"

---

## Durchgeführte Änderungen

1. `tools/OBSOLETE_REGISTRY_README.md` – Dokumentation veralteter Registry-Tools
2. Makefile – Node-RED-Pfade, registry-Targets bereinigt, validate-development-rules entfernt
3. tools/node_red_analysis – Pfade, README
4. integrations/APS-NodeRED – Scripts, README, SSH_SETUP
5. .pre-commit-config.yaml – OMF3 → OSF
6. validate_mermaid_diagrams.py – OMF → OSF
7. docs/04-howto/setup/project-setup.md – node_red → APS-NodeRED (falls referenziert)
