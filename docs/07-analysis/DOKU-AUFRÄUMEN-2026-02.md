# Doku-Aufräumen 2026-02 – Obsolete Analysen

**Datum:** 2026-02-18  
**Kontext:** Fischertechnik-Doku und CCU-Source-Code sind vorhanden. Empirische Reverse-Engineering-Analysen sind größtenteils obsolet.

---

## 1. Befund

### 1.1 data/omf-data
- **Existiert nicht mehr** – Migration auf `data/osf-data` abgeschlossen.

### 1.2 data/osf-data – Veraltete Inhalte

| Datei/Ordner | Status | Empfehlung |
|--------------|--------|------------|
| **sessions/README.md** | Veraltet: .db, default_test_session, omf/mqtt, aps_persistent_traffic | **Aktualisieren** → .log-only, Session Manager |
| **MODULE_ANALYSIS_SUMMARY.md** | Empirische Stats aus Session-Logs | Optional behalten als Debug-Referenz; Fischertechnik-Doku ist Source of Truth |
| **\*-analysis/** (drill, mill, hbw, dps, aiqs, fts) | Script-Output, empirische Extraktion | Behalten – nützlich für Session-Debug; READMEs ggf. anpassen |

### 1.3 docs/07-analysis – Obsolete Analysen

| Datei | Inhalt | Bewertung |
|-------|--------|-----------|
| **registry-mosquitto-log-analysis.md** | Registry vs. Mosquitto-Log (empirisch), Status: ABGESCHLOSSEN | **Archivieren** – Fischertechnik hat Topic-Struktur |
| **production-order-analysis-results.md** | Order-Workflow, OSF Order Manager, Track & Trace | **Behalten** – wird von 13-track-trace referenziert, OSF-Implementierungsdetails |
| **session-manager-and-data-consolidation-analysis.md** | Migration omf→osf, Session Manager | **Archivieren** – erledigt |
| **registry-missing-topics-proposals.md** | Basiert auf Log-Analyse | **Archivieren** – mit registry-mosquitto |
| **TOPIC_SCHEMA_CORRELATION.md** | Schema↔Topic-Mapping (OSF-Registry) | Behalten – OSF-spezifisch, Test-Payload-Status |

### 1.4 Weiterhin relevant

| Bereich | Begründung |
|---------|------------|
| **00-REFERENCE/** | ORBIS-spezifisch: Modul-Serials, Hardware-Mapping, mit FT abgeglichen |
| **AS-IS-FISCHERTECHNIK-COMPARISON.md** | Abgleich unserer Doku mit Fischertechnik |
| **INTEGRATIONS-VENDOR-ANALYSIS.md** | integrations vs. vendor |
| **build-commands-guide.md**, **test-coverage-*.md** | Praktische Anleitungen |
| **publish-buttons-*.md** | OSF-spezifisch |

---

## 2. Durchgeführte Änderungen

- [x] `data/osf-data/sessions/README.md` – auf .log-only, Session Manager, ORBIS Smart-Factory aktualisiert
- [x] `docs/07-analysis/README.md` – Verweise auf archivierte Analysen angepasst, Archiv-Hinweis ergänzt
- [x] 3 obsolete Analysen nach `docs/archive/analysis-obsolete-2026/` verschoben (registry-mosquitto, session-manager-consolidation, registry-missing-topics)
- [x] `production-order-analysis-results.md` **nicht** archiviert – Obsolet-Check ergab: OSF-spezifisch, von Track & Trace referenziert
- [x] Links in `docs/03-decision-records/13-track-trace-architecture.md` → `docs/07-analysis/production-order-analysis-results.md`

---

## 3. Referenzen

- **Fischertechnik-Doku:** `docs/06-integrations/fischertechnik-official/`, `FISCHERTECHNIK-OFFICIAL.md`
- **ORBIS-Referenz:** `docs/06-integrations/00-REFERENCE/`
