# Sprint 14 – Use-Case-Bibliothek & Blog-Serie Umsetzung

**Zeitraum:** 22.01.2026 - 04.02.2026 (2 Wochen)  
**Status:** ✅ Abgeschlossen  
**Stakeholder-Update:** Fokus auf Umsetzung der Use-Case-Bibliothek und schrittweise Blog-Serie-Implementierung. Use-Cases werden als separate Route `dsp/use-case/xyz` implementiert (analog zu track-trace).

---

## 🎯 Ziele

### Use-Case-Bibliothek Implementierung
- [x] **UC-06:** Interoperability Event-to-Process Map - Route `dsp/use-case/interoperability` implementieren
  - ✅ SVG-Animation implementiert (Steps-Definition vorhanden)
  - ✅ Dynamische SVG-Generierung aus Struktur-Konfiguration
  - ✅ I18n-Unterstützung (DE/EN/FR)
  - ✅ Step-Animation mit Controls (Prev/Next, Auto-Play, Loop, Step-Dots, Zoom)
- [ ] **UC-01:** Track & Trace Genealogy - Route `dsp/use-case/track-trace-genealogy` implementieren
  - 🔄 In Arbeit: SVG-Generator-Service erstellt, Diagramm-Umarbeitung in Planung
- [ ] **UC-02:** 3 Datentöpfe - Route `dsp/use-case/three-data-pools` implementieren
- [ ] **UC-03:** AI Lifecycle - Route `dsp/use-case/ai-lifecycle` implementieren
- [ ] **UC-04:** Closed Loop Quality - Route `dsp/use-case/closed-loop-quality` implementieren
- [ ] **UC-05:** Predictive Maintenance - Route `dsp/use-case/predictive-maintenance` implementieren

### Blog-Serie Umsetzung (Schritt für Schritt)
- [x] **A1:** Interoperabilität als Fundament - Review & Finalisierung
  - ✅ Draft erstellt (`docs/assets/articles/a1-DE.md`)
  - ✅ Review durch externes Team
- [ ] **A2:** Track & Trace Genealogie - Review & Finalisierung
  - 🔄 In Arbeit: Draft erstellt (`docs/assets/articles/a2-DE.md`)
- [ ] **A3:** Drei Datentöpfe für KPIs - Review & Finalisierung
- [ ] **A4:** Closed Loops für Qualität & Maintenance - Review & Finalisierung

### Weitere Aufgaben
- [ ] Azure DevOps Migration & Docker-Setup (Hilcher-Box/RPi) - Fortsetzung
- [ ] Projekt-Phasenabschlussbericht finalisieren
- [ ] Projektantrag für neue Phase Q1/Q2 2026 finalisieren

## 📊 Fortschritt
- **Abgeschlossen:** 2/10 Aufgaben (UC-06, Artikel-01)
- **In Arbeit:** UC-01, Artikel-02
- **Übernommen in Sprint 15:** UC-01, Artikel-02, UC-02-05, Artikel-03-04
- **Blockiert:** Keine Blocker

## 🔗 Wichtige Entscheidungen
- **Routing:** Use-Cases werden unter `dsp/use-case/xyz` erreichbar sein (analog zu `dsp/use-case/track-trace`)
- **Aufgabenteilung:** Jeder Use-Case und jeder Artikel wird als separater Task umgesetzt
- **Zeitplan:** Blog-Serie und Use-Case-Bibliothek werden schrittweise über mehrere Sprints umgesetzt
- **Konsistenz DSP-Tab ↔ Direct-Access:** 
  - **Option 2 umgesetzt:** Direct-Access-Page (`dsp/use-case`) verwendet `DspUseCasesComponent` direkt (Wiederverwendung statt Duplizierung)
  - **Navigation:** 
    - **Einfacher Klick:** Use-Case highlighten und Details anzeigen
    - **Doppelklick:** Zu Detail-Seite navigieren (nur für implementierte Use-Cases: Track & Trace, Interoperability)
    - **"View Details" Button:** Im Detail-Bereich für implementierte Use-Cases
  - **Vorteile:** Single Source of Truth, keine Duplizierung, einfache Wartung, konsistente Datenquelle

## 📈 Stakeholder-Impact
- **Technisch:** Use-Case-Bibliothek schafft wiederverwendbare Komponenten für DSP-Demonstrationen
- **Business:** Blog-Serie unterstützt Marketing und Kundenkommunikation
- **Risiken:** Umfangreiche Aufgaben erfordern sorgfältige Priorisierung

---

## 📝 Use-Case-Bibliothek Details

### Routing-Struktur
- Basis-Route: `dsp/use-case/`
- Einzelne Use-Cases:
  - `dsp/use-case/track-trace-genealogy` (UC-01)
  - `dsp/use-case/three-data-pools` (UC-02)
  - `dsp/use-case/ai-lifecycle` (UC-03)
  - `dsp/use-case/closed-loop-quality` (UC-04)
  - `dsp/use-case/predictive-maintenance` (UC-05)
  - `dsp/use-case/interoperability` (UC-06)

### Assets vorhanden
- **UC-01:** Schema, Screenshots DE/EN
- **UC-02:** Diagramm DE v2
- **UC-03:** Layered Diagram DE/EN, Animation-Steps
- **UC-04:** Diagramm
- **UC-05:** 2 Varianten
- **UC-06:** SVG DE/EN, Animation-Steps JSON (`uc-06-event-to-process-map.steps.json`)

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
- **A1-DE.md:** Interoperabilität als Fundament (`docs/assets/articles/a1-DE.md`)
- **A2-DE.md:** Track & Trace Genealogie (`docs/assets/articles/a2-DE.md`)
- **A3-DE.md:** Drei Datentöpfe für KPIs (`docs/assets/articles/a3-DE.md`)
- **A4-DE.md:** Closed Loops für Qualität & Maintenance (`docs/assets/articles/a4-DE.md`)

### Review-Schritte (pro Artikel)
- [x] **Artikel-01:** Review durch externes Team abgeschlossen
- [ ] **Artikel-02:** Review durch externes Team (in Arbeit)
- [ ] Tech Reviewer Review
- [ ] MES-ERP Reviewer Review
- [ ] Redaktion Review
- [ ] CTA-Optionen finalisieren
- [ ] OSF Proof Screenshots auswählen und croppen (DE/EN)
- [ ] SAP-Beispiele konsistent prüfen
- [ ] Finale Links zu ADO Wiki Use-Cases eintragen

---

---

## ✅ Abgeschlossene Aufgaben (Sprint 14)

### Use-Case-Bibliothek Konsistenz (Option 2)
- [x] **DspUseCasesComponent erweitert:** Router, LanguageService, Doppelklick-Navigation, "View Details" Button
- [x] **use-case-selector-page.component.ts angepasst:** Verwendet jetzt `DspUseCasesComponent` direkt (Wiederverwendung)
- [x] **I18n-Keys hinzugefügt:** `dspUseCaseViewDetails`, `dspUseCaseDoubleClickHint`
- [x] **Dokumentation aktualisiert:** Option 2 in `sprint_14.md` dokumentiert

**Ergebnis:** Konsistenz zwischen DSP-Tab Section "Use Cases" und Direct-Access-Page `dsp/use-case` durch Wiederverwendung der gleichen Komponente. Keine Duplizierung, Single Source of Truth.

### UC-06: Interoperability Event-to-Process Map
- [x] **Route implementiert:** `dsp/use-case/interoperability`
- [x] **Komponente erstellt:** `InteroperabilityUseCaseComponent`
- [x] **SVG-Generator-Service:** Dynamische SVG-Generierung aus Struktur-Konfiguration
- [x] **I18n-Service:** UC-spezifische Texte (DE/EN/FR)
- [x] **Step-Animation:** Vollständige Animation mit Controls (Prev/Next, Auto-Play, Loop, Step-Dots, Zoom)
- [x] **Assets:** SVG-Dateien, Steps-JSON, Dokumentation vorhanden

**Ergebnis:** UC-06 vollständig implementiert und produktionsreif. Dynamische SVG-Generierung ermöglicht einfache Wartung und I18n-Unterstützung.

### Artikel-01: Interoperabilität als Fundament
- [x] **Draft erstellt:** `docs/assets/articles/a1-DE.md`
- [x] **Review durch externes Team:** Abgeschlossen

**Ergebnis:** Artikel-01 bereit für finale Review-Schritte (Tech Reviewer, MES-ERP Reviewer, Redaktion).

---

---

## 📦 Assets erstellt (Sprint 14)

### Use-Case Assets
- **UC-06:**
  - `uc-06-event-to-process-map-DE.svg` / `-EN.svg` (SVG-Dateien)
  - `uc-06-event-to-process-map.steps.json` (Animation-Steps)
  - `UC-06-SVG-Template-DE.png` / `-EN.png` (Templates)
  - `UC-06-Interoperability-Shopfloor-first.png` / `-Business-first.png` (Screenshots)
  - `uc-06-interoperability.md` (Dokumentation)
  - `UC-06-IMPLEMENTATION-STATUS.txt` (Status-Dokumentation)

### Artikel Assets
- **Artikel-01:** `a1-DE.md` (Draft, Review abgeschlossen)
- **Artikel-02:** `a2-DE.md` (Draft, in Arbeit)

---

*Letzte Aktualisierung: 04.02.2026*
