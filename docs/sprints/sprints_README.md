# Sprint Documentation Index

Version: 0.4  
Letzte Aktualisierung: 2026-02-18  

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

### Sprint-Abschluss (Pflicht ab Sprint 16)
1. **Sprint-Dokument:** Status → „Abgeschlossen“, Abschlussdatum setzen
2. **Neuer Sprint:** Aus Template anlegen (`sprint_XX.md`), offene `[ ]` übernehmen
3. **PROJECT_STATUS:** Neue Tabellenzeile für nächsten Sprint, Externe Events eintragen
4. **Roadmap prüfen:** Sind Phasen/Versionen/Daten noch aktuell? (bei Bedarf anpassen)

---

## 📐 Sprint-Dokumentation Vorgehen (ab Sprint 15)

**Grundprinzip:** Eine Checkliste als einzige Quelle – keine Doppelung von Fortschritt/Abgeschlossen.

| Element | Inhalt | Vermeiden |
|---------|--------|-----------|
| **Ziele** | Flache Checkliste `[x]` / `[ ]`, eine Zeile pro Task | Keine nested Sub-Checkboxen, kein "✅ Implementiert" zusätzlich zu `[x]` |
| **Backlog (optional)** | Tasks bei Gelegenheit (z.B. Session-Log-Analyse, Doku-Lücken) | Kein separates Backlog-System |
| **Übernommen** | Offene Tasks explizit in nächsten Sprint übernehmen | Kein separater "Fortschritt"-Block (redundant zur Checkliste) |
| **Abgeschlossen** | Status auf "Abgeschlossen", Abschlussdatum, Verweis auf Nachfolge-Sprint | Kein eigener "Abgeschlossene Aufgaben"-Block (Checkboxen zeigen Status) |

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
- [Sprint 16](sprint_16.md) – Vibration-Sensor, Doku-Check, Marketing-Konsistenz (19.02 - 04.03.2026) ⏳ **AKTUELL**

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
