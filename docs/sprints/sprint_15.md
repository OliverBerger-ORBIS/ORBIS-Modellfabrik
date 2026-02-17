# Sprint 15 – Use-Case-Bibliothek & Blog-Serie Fortsetzung

**Zeitraum:** 05.02.2026 - 18.02.2026 (2 Wochen)  
**Status:** Laufend  
**Stakeholder-Update:** 
- **Fokus im Repo:** Use-Case-Darstellungen und Animationen; UC-01 bis UC-06 haben OSF-Implementierung.
- **Stand:** In Sprint 15 wurden UC-01 bis UC-05 vollständig erstellt – jeweils mit Step-Animation.

---

## 🎯 Ziele

### Use-Case-Bibliothek (Konzept & Assets)
- [x] **UC-01:** Track & Trace Genealogy - Konzept & Visuals
  - ✅ Diagramm-Struktur finalisiert (Partitur vs. Snapshot)
  - ✅ Domain-Model (Object Mesh) erstellt
  - ✅ OSF-Darstellung und Step-Animation implementiert
  - ✅ Wiki-Doku aktualisiert (`UC-01_Track_Trace-genealogy.md`)
- [x] **UC-02:** 3 Datentöpfe - Konzept & Visuals
  - ✅ Textsynchronisation mit Artikel A3 (Begriffe harmonisiert)
  - ✅ Visuelle Assets erstellt (Concept.drawio & Architecture.drawio)
  - [ ] **Entscheidung:** Finalisierung Layout (Vertical Concept vs. Horizontal Lanes)
  - ✅ Status auf "Konzept Finalisiert" gesetzt
- [x] **UC-03:** AI Lifecycle - Konzept & Visuals
  - ✅ Layered Diagram DE/EN, Animation-Steps
  - ✅ OSF-Darstellung und Animation implementiert
- [x] **UC-04:** Closed Loop Quality - Konzept & Visuals
  - ✅ Eigenständiges UC-04-Template erstellt (unabhängig von UC-05)
  - ✅ OSF-Darstellung: 3 Lanes (Process Detect→Decide→Act→Feedback | Mixed DSP Edge | Quality-Event | Target | Shopfloor Production Order + AIQS | Systems & Devices)
  - ✅ 7-Step-Animation, I18n, Route `dsp/use-case/closed-loop-quality`, DSP Use Cases Link
- [x] **UC-05:** Predictive Maintenance - Konzept & Visuals
  - ✅ Diagramm-Struktur (Process, Mixed, Shopfloor), Icons (Alarm, Bell-Alarm, Vibration/Tilt-Sensor)
  - ✅ OSF-Darstellung und 7-Step-Animation implementiert

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
  - [ ] Review durch externes Team
  - [ ] Tech Reviewer Review
  - [ ] MES-ERP Reviewer Review
  - [ ] Redaktion Review
  - [ ] CTA-Optionen finalisieren
  - [ ] OSF Proof Screenshots auswählen und croppen (DE/EN)
  - [ ] SAP-Beispiele konsistent prüfen
  - [ ] Finale Links zu ADO Wiki Use-Cases eintragen

### Events / Demos
- [ ] **Kunde Glaston:** OSF-Präsentation am 10.02.2026
  - ✅ Zielsetzung und Fokus abstimmen
  - ✅  Drehbuch festlegen und OSF-UI ggf anpassen
  - ✅  Demo-Umgebung (Shadow-Mode) checken

### Weitere Aufgaben (aus Sprint 14 übernommen)
- [ ] Azure DevOps Migration & Docker-Setup (Hilcher-Box/RPi) - Fortsetzung
- [ ] Projekt-Phasenabschlussbericht finalisieren
- [ ] Projektantrag für neue Phase Q1/Q2 2026 finalisieren

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

### Routing-Struktur
- Basis-Route: `dsp/use-case/`
- Einzelne Use-Cases:
  - `dsp/use-case/track-trace-genealogy` (UC-01) - ✅ Darstellung + Step-Animation
  - `dsp/use-case/three-data-pools` (UC-02) - ✅ Darstellung + Animation
  - `dsp/use-case/ai-lifecycle` (UC-03) - ✅ Darstellung + Animation
  - `dsp/use-case/closed-loop-quality` (UC-04) - ✅ Darstellung + 7-Step-Animation
  - `dsp/use-case/predictive-maintenance` (UC-05) - ✅ Darstellung + 7-Step-Animation
  - `dsp/use-case/interoperability` (UC-06) - ✅ Abgeschlossen (Sprint 14)

### UC-Darstellung und Animationen (Status)
- **UC-01:** ✅ Track & Trace – SVG-Generator, I18n, Komponente, Animation
- **UC-02:** ✅ 3 Datentöpfe – Komponente, Animation
- **UC-03:** ✅ AI Lifecycle – Layered Diagram DE/EN, Animation-Steps
- **UC-04:** ✅ Closed Loop Quality – SVG-Generator, Icons (Production Order, AIQS), 7-Step-Animation, Quality-Event-Box
- **UC-05:** ✅ Predictive Maintenance – SVG-Generator, Icons (Alarm, Bell-Alarm, Vibration/Tilt-Sensor), 7-Step-Animation, globale Styles
- **UC-06:** ✅ Interoperabilität – vollständig (Sprint 14)

### Assets vorhanden
- **UC-01:** Schema, Screenshots DE/EN, Dokumentation (Umarbeitung in Planung)
- **UC-02:** Diagramm DE v2, OSF-Darstellung
- **UC-03:** Layered Diagram DE/EN, Animation-Steps, OSF-Darstellung
- **UC-04:** Diagramm, OSF-Darstellung mit 7-Step-Animation
- **UC-05:** 2 Varianten, OSF-Darstellung mit 7-Step-Animation
- **UC-06:** ✅ Vollständig implementiert (Sprint 14)

### Implementierungs-Ansatz
- Jeder Use-Case wird als separate Angular-Komponente implementiert
- SVG-Animationen werden pro Use-Case umgesetzt (wenn Steps-Definition vorhanden)
- Routing wird in `app.routes.ts` ergänzt (analog zu track-trace)
- **Konsistenz:** `DspUseCasesComponent` wird sowohl im DSP-Tab als auch auf der Direct-Access-Page (`dsp/use-case`) verwendet
  - `enableNavigation` Input steuert, ob Navigation aktiviert ist (nur auf Direct-Access-Page)
  - Use-Cases mit `detailRoute` können zu Detail-Seiten navigieren

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

### Aktueller Status
- ✅ SVG-Generator-Service erstellt (`uc-01-svg-generator.service.ts`)
- ✅ I18n-Service erstellt (`uc-01-i18n.service.ts`)
- ✅ Komponente erstellt (`track-trace-genealogy-use-case.component.ts`)
- ✅ Route implementiert (`dsp/use-case/track-trace-genealogy`)
- 🔄 Diagramm-Umarbeitung in Planung (basierend auf ChatGPT-Analyse)

### Geplante Verbesserungen (aus ChatGPT-Analyse)
1. **Plan vs. Ist:** Separate Darstellung von Plan und Ist-Pfad
2. **Join-Key:** Klarere Darstellung der Korrelation zwischen Plan und Ist
3. **Zwei Visuals:** Object Mesh + Event Flow als separate Visuals
4. **UI-Verbesserungen:** Bessere Timeline-Sichtbarkeit, klarere Farben
5. **Datenmodell:** Schärfung des Datenmodells
6. **Terminologie:** Glättung der Terminologie

### Dokumentation
- `docs/assets/use-cases/uc-01/UC-01_Track_Trace-genealogy.md` - Hauptdokumentation
- `docs/assets/use-cases/uc-01/UC-01-IMPROVEMENTS-CHECKLIST.md` - Verbesserungs-Checkliste
- `docs/assets/use-cases/uc-01/UC-01-TIMELINE-PLANNING.md` - Timeline-Planung

---

## ✅ Abgeschlossene Aufgaben (Sprint 15)

**AIQS Quality-Check (Klassifikation & Beschreibung):**
- **TXT Controller AIQS:** Überträgt Ergebnisse der Qualitätsprüfung mit Klassifikation (ML-Label, z.B. BOHO, MIPO2) und Beschreibung (lesbar, z.B. „2x milled pocket“) via MQTT auf `/j1/txt/1/i/quality_check` – Vorbereitung für Rückmeldung an zentrales QS-System (MES, ERP, …)
- **OSF-Anzeige:** Klassifikation, Beschreibung, Farbe (White/Red/Blue) und Ergebnis (passed/failed) werden in den Device-Details bei AIQS im Bereich „Last Image“ angezeigt
- **I18n:** Alle neuen Labels und Werte in DE und FR übersetzt
- **Dokumentation:** How-To `aiqs-quality-check-enumeration.md` mit RoboPro-Workflow (Blockly, kein Python-Edit, retain für UI)

**UC-01 bis UC-05:** Alle Use-Cases in diesem Sprint erstellt – jeweils mit Step-Animation.

- **UC-01 Track & Trace Genealogy:** SVG-Generator, I18n, Komponente, Step-Animation
- **UC-02 3 Datentöpfe:** Komponente, Step-Animation
- **UC-03 AI Lifecycle:** Layered Diagram DE/EN, Step-Animation
- **UC-04 Closed Loop Quality (erste Version):** Eigenständiges Template
  - Structure Config: 4 Process-Steps (Detect→Decide→Act→Feedback), Mixed (DSP Edge | Quality-Event | Target), Shopfloor (Production Order + AIQS | Systems & Devices)
  - SVG-Generator mit uc04_ IDs, Mixed-Lane-Positionen/größen wie UC-05
  - Connection Quality Event→Act: vertikal nach oben bis Mitte, dann rechts, dann nach oben zum Act-Step
  - I18n-Service, Closed-Loop-Quality-Komponente, Route, Steps JSON, globale Styles, DSP Use Cases Eintrag

- **UC-05 Predictive Maintenance:** Vollständige OSF-Implementierung
  - SVG-Generator mit Process-, Mixed- und Shopfloor-Lane
  - Icons: Alarm, Bell-Alarm, Vibration-Sensor, Tilt-Sensor (icon.registry + dsp-svg-inventory)
  - Target-Subboxen (MES/ERP/Analytics), Alarm-Box (quadratisch), DSP-Edge-Icon
  - Connections: Vibration-Sensor→DSP (up-right-up), Alarm→Process nur gepunktet
  - 7-Step-Animation (Übersicht → Trigger/Sensor → DSP/Evaluate → Alarm → Act → Alarm Event → Feedback)
  - Globale Styles für Animation (hl, dim, dim-conn, hidden) in styles.scss
  - Opacity-Kaskade-Fix: Vorfahren von Highlight-Elementen werden nicht mehr gedimmt

---

*Letzte Aktualisierung: 18.02.2026*
