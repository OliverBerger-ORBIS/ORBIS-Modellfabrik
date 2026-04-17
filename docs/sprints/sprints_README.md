# Sprint Documentation Index

Version: 0.5  
Letzte Aktualisierung: 2026-04-17  

---

## 📑 Übersicht

Dieses Verzeichnis enthält die Sprint-Dokumentationen des OSF-Projekts.  
Jeder Sprint dokumentiert Ziele, Fortschritt (Checkliste) und offene Punkte.

---

## 🔄 Dokumenten-Workflow (Aktualität sicherstellen)

### Sprint-Dokument (sprint_XX.md)
- **Wird erfasst:** Ziele, Tasks (Checkliste), Backlog (optional) für „Später“-Items
- **Aktualisierung:** Quasi täglich – Checkboxen abhaken, Status anpassen
- **Bei Anlage eines neuen Sprints:** Siehe „Sprint-Abschluss“ unten

### PROJECT_STATUS.md
- **Tabelle:** Jeder Sprint eine Zeile (Zeitraum, ORBIS-Projekt, OSF-Phase, Externe Events)
- **Aktualisierung:** Bei Sprint-Abschluss – neue Zeile für nächsten Sprint, Events ergänzen
- **Keine separate Sprint-Übersicht** – die Tabelle ist die Übersicht

### Strategy & Roadmap (01-strategy/)
- **Aktualisierung:** Seltener; bei Sprint-Abschluss als impliziter Check: Sind Phasen/Daten noch stimmig?

### Sprint-Abschluss (Pflicht vor Neuanlage nächster Sprint)
Diese Aufgaben sind **Teil des laufenden Sprints** und müssen erledigt sein, **bevor** der neue Sprint gestartet wird.

1. **Sprint-Dokument:** Status → „Abgeschlossen“, Abschlussdatum setzen.
2. **Neuer Sprint:** Aus Template anlegen (`sprint_XX.md`), offene `[ ]` aus dem alten Sprint übernehmen.
3. **PROJECT_STATUS:** Neue Tabellenzeile für nächsten Sprint anlegen, Externe Events eintragen.
4. **Roadmap prüfen:** Sind Phasen/Versionen/Daten noch aktuell? (bei Bedarf anpassen).

*Hinweis: Der neue Sprint enthält dann wieder einen eigenen "Sprint-Abschluss"-Block für den darauf folgenden Wechsel.*

---

## 📐 Sprint-Dokumentation (Neuanlage / Überarbeitung)

**Eine Checkliste unter `## Aufgaben (thematisch, mit Haken)`:** Unter **`### Thema`** (z. B. OSF-UI, Hardware, Organisation) stehen **gemischt** `- [ ]` und `- [x]`. **Nicht** zwei Kapitel „Offen“ und „Erledigt“.

| Element | Inhalt |
|---------|--------|
| **Aufgaben** | Nur Checkbox-Zeilen; **Gruppierung nach Thema**, nicht nach Erledigt-Status |
| **Releases** | Optional kurze Tabelle im Kopf; Details → [CHANGELOG.md](../../CHANGELOG.md) |
| **Backlog** | Optional Abschnitt **ohne** Checkboxen, wenn noch keine klaren Tasks |
| **Externe Events** | Optional **`## Externe Termine`** (Tabelle) + zugehörige Tasks unter einem Thema (z. B. Presentation); bei Sprint-Abschluss Zeile **PROJECT_STATUS** → Spalte **Externe Events** pflegen |
| **Sprint-Wechsel** | Checkboxen am Ende von „Aufgaben“ oder eigene Thema-Überschrift |

Template: [sprint_template.md](sprint_template.md) · Beispiele: [sprint_18.md](sprint_18.md), [sprint_19.md](sprint_19.md)

---

## 🔗 Sprint Links
- [Sprint 01](sprint_01.md) – Projekt-Initialisierung und Know-How Aufbau (24.07 - 06.08.2025)
- [Sprint 02](sprint_02.md) – Aufbau und Inbetriebnahme der Modellfabrik (07.08 - 22.08.2025)
- [Sprint 03](sprint_03.md) – MQTT-Schnittstelle und ORBIS Dashboard (23.08 - 03.09.2025)
- [Sprint 04](sprint_04.md) – Daten sammeln und Projektstruktur (04.09 - 17.09.2025)
- [Sprint 05](sprint_05.md) – Track & Trace und Fit Gap Analyse (18.09 - 01.10.2025)
- [Sprint 06](sprint_06.md) – OMF2-Refactoring und Architektur-Migration (02.10 - 15.10.2025)
- [Sprint 07](sprint_07.md) – CCU Messe-Readiness und UI-Polish (16.10 - 29.10.2025)
- [Sprint 08](sprint_08.md) – Asset-Management Refactoring und OMF3 Start (30.10 - 12.11.2025)
- [Sprint 09](sprint_09.md) – OMF3 Integration und UI-Polish (13.11 - 27.11.2025)
- [Sprint 10](sprint_10.md) – DSP-Kundentag & Responsive Mockup (28.11 - 11.12.2025)
- [Sprint 11](sprint_11.md) – Shopfloor UX Refresh & DSP-Links (12.12 - 24.12.2025)
- [Sprint 12](sprint_12.md) – OBS-Video, AIQS-Kamera & Deployment (25.12.2025 - 07.01.2026)
- [Sprint 13](sprint_13.md) – Projektabschluss & Ausblick Q1/Q2 2026 (08.01 - 21.01.2026)
- [Sprint 14](sprint_14.md) – Use-Case-Bibliothek & Blog-Serie Umsetzung (22.01 - 04.02.2026)
- [Sprint 15](sprint_15.md) – Use-Case-Bibliothek & Blog-Serie Fortsetzung (05.02 - 18.02.2026) ✅
- [Sprint 16](sprint_16.md) – Vibration-Sensor, Doku-Check, Marketing-Konsistenz (19.02 - 04.03.2026) ✅
- [Sprint 17](sprint_17.md) – MES/Integration & LogiMAT Vorbereitung (05.03 - 18.03.2026) ✅
- [Sprint 18](sprint_18.md) – LogiMAT-Messe Durchführung (19.03 - 01.04.2026) ✅
- [Sprint 19](sprint_19.md) – Sensor-Station, Backend/Grafana & Hannover-Vorbereitung (02.04 - 17.04.2026) ✅
- [Sprint 20](sprint_20.md) – Hannover Messe & Customer Connect (v1.1.x) (16.04 - 29.04.2026) ⏳ **AKTUELL**

## 📊 Berichte
- [ORBIS-Projekt-Abschlussbericht Sprints 1-12](ORBIS-Projekt-Abschlussbericht_sprints_01-12.md) – Erstes ORBIS-Projekt (ORBIS-Modellfabrik)
- [Sprint 01-04 Report](stakeholder_report_sprints_01-04.md) – Umfassender Bericht für Management
- [Sprint 05-06 Report](stakeholder_report_sprints_05-06.md) – OMF2-Migration und Architektur-Refactoring

---

## 📌 Hinweise
- **Schlanke Dokumentation:** Minimaler Overhead, fokussiert auf Stakeholder-Reporting
- **2-Wochen-Zyklen:** Regelmäßige Fortschrittsdokumentation
- **Templates:** `sprint_template.md` für neue Sprints, `stakeholder_report_template.md` für externe Berichte
- **Decision Records:** Wichtige Entscheidungen in `docs/03-decision-records/`

## 📋 Templates
- **[Sprint Template](sprint_template.md)** - Für neue Sprints
- **[Stakeholder Report Template](stakeholder_report_template.md)** - Für externe Berichte
- **[Decision Record Template](../03-decision-records/decision_template.md)** - Für wichtige Entscheidungen
