# Sprint 15 – Use-Case-Bibliothek & Blog-Serie Fortsetzung

**Zeitraum:** 05.02.2026 - 18.02.2026 (2 Wochen)  
**Status:** Laufend  
**Stakeholder-Update:** 
- **Fokus im Repo:** Use-Case-Darstellungen und Animationen; UC-01 bis UC-06 haben OSF-Implementierung.
- **Stand:** In Sprint 15 wurden UC-01 bis UC-05 vollständig erstellt – jeweils mit Step-Animation.

---

## 🎯 Ziele

### Use-Case-Bibliothek (Konzept & Assets)
- [x] **UC-01** Track & Trace Genealogy – ✅ Implementiert
- [x] **UC-02** 3 Datentöpfe – ✅ Implementiert
- [x] **UC-03** AI Lifecycle – ✅ Implementiert
- [x] **UC-04** Closed Loop Quality – ✅ Implementiert
- [x] **UC-05** Predictive Maintenance – ✅ Implementiert
  - Details: [Use-Case Bibliothek](../02-architecture/use-case-library.md)
- [ ] **UC-02:** Entscheidung Layout Finalisierung (Vertical Concept vs. Horizontal Lanes)

### Blog-Serie (Drafts & Visuals)
- [x] **A2:** Track & Trace Genealogie - Draft & Visuals fertig
  - ✅ Draft finalisiert (`docs/assets/articles/a2-DE.md`)
  - ✅ Visual 1 (Partitur) erstellt
  - ✅ Visual 3 (Object Mesh) erstellt
  - [ ] Start Review-Prozess (extern/redaktionell)
- [x] **A3:** Drei Datentöpfe für KPIs - Draft & Visuals fertig
  - ✅ Draft harmonisiert (`docs/assets/articles/a3-DE.md`)
  - ✅ Visuals referenziert (PNGs vorhanden)
  - [ ] Start Review-Prozess (extern/redaktionell)
- [ ] **A4:** Closed Loops für Qualität & Maintenance - Review & Finalisierung
  - [ ] Draft erstellen


### Events / Demos
- [ ] **Kunde Glaston:** OSF-Präsentation am 10.02.2026
  - ✅ Zielsetzung und Fokus abstimmen
  - ✅  Drehbuch festlegen und OSF-UI ggf anpassen
  - ✅  Demo-Umgebung (Shadow-Mode) checken

### Weitere Aufgaben (aus Sprint 14 übernommen)
- [ ] Azure DevOps Migration & Docker-Setup (Hilcher-Box/RPi) - Fortsetzung
- [ ] Projekt-Phasenabschlussbericht finalisieren
- [ ] Projektantrag für neue Phase Q1/Q2 2026 finalisieren

### Modellfabrik Erweiterung (Hardware)
- [ ] **Vibrationsüberwachung:** Setup mit Arduino & Signalampel
  - ✅ Grobplanung & Komponentenbestellung
  - ✅ Projektplan erstellt: [arduino-vibrationssensor.md](../05-hardware/arduino-vibrationssensor.md)
  - [ ] Aufbau & Test (siehe Projektplan)

## 📊 Fortschritt
- **Abgeschlossen:** UC-01 bis UC-05 (jeweils mit Step-Animation), UC-02 Konzept, Artikel A2/A3, AIQS Quality-Check (Klassifikation & Beschreibung in MQTT + OSF-Anzeige)
- **In Arbeit:** UC-01 Diagramm-Umarbeitung (optional), Artikel A4
- **Geplant:** Review-Prozesse
- **Blockiert:** Keine Blocker

## 🔗 Wichtige Entscheidungen
- **Routing:** Use-Cases werden unter `dsp/use-case/xyz` erreichbar sein (analog zu `dsp/use-case/track-trace`)
- **Aufgabenteilung:** Jeder Use-Case und jeder Artikel wird als separater Task umgesetzt
- **Zeitplan:** Blog-Serie und Use-Case-Bibliothek werden schrittweise über mehrere Sprints umgesetzt
- **Review-Prozess:** Externes Team führt Reviews durch (Tech Reviewer, MES-ERP Reviewer, Redaktion)

## 📈 Stakeholder-Impact
- **Technisch:** Use-Case-Bibliothek schafft wiederverwendbare Komponenten für DSP-Demonstrationen
- **Business:** Blog-Serie unterstützt Marketing und Kundenkommunikation
- **Risiken:** Umfangreiche Aufgaben erfordern sorgfältige Priorisierung

---

## 📝 Use-Case-Bibliothek Details

**Vollständige technische Doku:** [Use-Case Bibliothek](../02-architecture/use-case-library.md) (Routing, Dateien, Steps, Konsistenz)

- **UC-01 bis UC-06:** Alle implementiert mit Step-Animation
- **SVG-Export:** `node scripts/export-use-case-svgs.js` (Export nach `assets/svg/use-cases/`, Icons inlined als Data-URIs)
- **Inventar:** [use-case-inventory.md](../02-architecture/use-case-inventory.md) für grafische Übersicht (Overview/Step 0)

---

## 📝 Blog-Serie Details

### Artikel-Drafts v1 (Arbeitsversionen)
- **A1-DE.md:** Interoperabilität als Fundament (`docs/assets/articles/a1-DE.md`) - ✅ Review abgeschlossen (Sprint 14)
- **A2-DE.md:** Track & Trace Genealogie (`docs/assets/articles/a2-DE.md`) - 🔄 In Arbeit
- **A3-DE.md:** Drei Datentöpfe für KPIs (`docs/assets/articles/a3-DE.md`) - Geplant
- **A4-DE.md:** Closed Loops für Qualität & Maintenance (`docs/assets/articles/a4-DE.md`) - Geplant

### Review-Schritte (pro Artikel)
- [ ] Review durch externes Team
- [ ] Tech Reviewer Review
- [ ] MES-ERP Reviewer Review
- [ ] Redaktion Review
- [ ] CTA-Optionen finalisieren
- [ ] OSF Proof Screenshots auswählen und croppen (DE/EN)
- [ ] SAP-Beispiele konsistent prüfen
- [ ] Finale Links zu ADO Wiki Use-Cases eintragen

---

## 📝 UC-01: Track & Trace Genealogy (In Arbeit)

- ✅ Vollständig implementiert (siehe [Use-Case Bibliothek](../02-architecture/use-case-library.md))
- 🔄 Diagramm-Umarbeitung in Planung (Plan vs. Ist, Join-Key, UI-Verbesserungen)
- Doku: `docs/assets/use-cases/uc-01/`

---

## ✅ Abgeschlossene Aufgaben (Sprint 15)

**AIQS Quality-Check (Klassifikation & Beschreibung):**
- **TXT Controller AIQS:** Überträgt Ergebnisse der Qualitätsprüfung mit Klassifikation (ML-Label, z.B. BOHO, MIPO2) und Beschreibung (lesbar, z.B. „2x milled pocket“) via MQTT auf `/j1/txt/1/i/quality_check` – Vorbereitung für Rückmeldung an zentrales QS-System (MES, ERP, …)
- **OSF-Anzeige:** Klassifikation, Beschreibung, Farbe (White/Red/Blue) und Ergebnis (passed/failed) werden in den Device-Details bei AIQS im Bereich „Last Image“ angezeigt
- **I18n:** Alle neuen Labels und Werte in DE und FR übersetzt
- **Dokumentation:** How-To `aiqs-quality-check-enumeration.md` mit RoboPro-Workflow (Blockly, kein Python-Edit, retain für UI)

**UC-01 bis UC-05:** Alle Use-Cases in diesem Sprint erstellt – jeweils mit Step-Animation.

- **UC-01** Track & Trace Genealogy – ✅
- **UC-02** 3 Datentöpfe – ✅
- **UC-03** AI Lifecycle – ✅
- **UC-04** Closed Loop Quality – ✅
- **UC-05** Predictive Maintenance – ✅

Details: [Use-Case Bibliothek](../02-architecture/use-case-library.md)

---

*Letzte Aktualisierung: 18.02.2026*
