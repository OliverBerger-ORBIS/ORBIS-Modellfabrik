# Sprint 15 – Use-Case-Bibliothek & Blog-Serie Fortsetzung

**Zeitraum:** 05.02.2026 - 18.02.2026 (2 Wochen)  
**Status:** In Planung  
**Stakeholder-Update:** Fortsetzung der Use-Case-Bibliothek und Blog-Serie. UC-01 und Artikel-02 wurden in Sprint 14 begonnen und werden hier fortgesetzt.

---

## 🎯 Ziele

### Use-Case-Bibliothek Implementierung (Fortsetzung)
- [ ] **UC-01:** Track & Trace Genealogy - Route `dsp/use-case/track-trace-genealogy` implementieren
  - 🔄 In Arbeit: SVG-Generator-Service erstellt, Diagramm-Umarbeitung in Planung
  - [ ] Diagramm-Struktur finalisieren (basierend auf ChatGPT-Analyse)
  - [ ] Timeline-Synchronisation implementieren
  - [ ] I18n-Integration vervollständigen
- [ ] **UC-02:** 3 Datentöpfe - Route `dsp/use-case/three-data-pools` implementieren
- [ ] **UC-03:** AI Lifecycle - Route `dsp/use-case/ai-lifecycle` implementieren
- [ ] **UC-04:** Closed Loop Quality - Route `dsp/use-case/closed-loop-quality` implementieren
- [ ] **UC-05:** Predictive Maintenance - Route `dsp/use-case/predictive-maintenance` implementieren

### Blog-Serie Umsetzung (Fortsetzung)
- [ ] **A2:** Track & Trace Genealogie - Review & Finalisierung
  - 🔄 In Arbeit: Draft erstellt (`docs/assets/articles/a2-DE.md`)
  - [ ] Review durch externes Team
  - [ ] Tech Reviewer Review
  - [ ] MES-ERP Reviewer Review
  - [ ] Redaktion Review
  - [ ] CTA-Optionen finalisieren
  - [ ] OSF Proof Screenshots auswählen und croppen (DE/EN)
  - [ ] SAP-Beispiele konsistent prüfen
  - [ ] Finale Links zu ADO Wiki Use-Cases eintragen
- [ ] **A3:** Drei Datentöpfe für KPIs - Review & Finalisierung
  - [ ] Draft erstellen
  - [ ] Review durch externes Team
  - [ ] Tech Reviewer Review
  - [ ] MES-ERP Reviewer Review
  - [ ] Redaktion Review
  - [ ] CTA-Optionen finalisieren
  - [ ] OSF Proof Screenshots auswählen und croppen (DE/EN)
  - [ ] SAP-Beispiele konsistent prüfen
  - [ ] Finale Links zu ADO Wiki Use-Cases eintragen
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

### Weitere Aufgaben (aus Sprint 14 übernommen)
- [ ] Azure DevOps Migration & Docker-Setup (Hilcher-Box/RPi) - Fortsetzung
- [ ] Projekt-Phasenabschlussbericht finalisieren
- [ ] Projektantrag für neue Phase Q1/Q2 2026 finalisieren

## 📊 Fortschritt
- **Abgeschlossen:** 0/X Aufgaben
- **In Arbeit:** UC-01, Artikel-02
- **Geplant:** UC-02-05, Artikel-03-04
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
  - `dsp/use-case/track-trace-genealogy` (UC-01) - 🔄 In Arbeit
  - `dsp/use-case/three-data-pools` (UC-02)
  - `dsp/use-case/ai-lifecycle` (UC-03)
  - `dsp/use-case/closed-loop-quality` (UC-04)
  - `dsp/use-case/predictive-maintenance` (UC-05)
  - `dsp/use-case/interoperability` (UC-06) - ✅ Abgeschlossen (Sprint 14)

### Assets vorhanden
- **UC-01:** Schema, Screenshots DE/EN, Dokumentation (Umarbeitung in Planung)
- **UC-02:** Diagramm DE v2
- **UC-03:** Layered Diagram DE/EN, Animation-Steps
- **UC-04:** Diagramm
- **UC-05:** 2 Varianten
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

*Wird während des Sprints aktualisiert*

---

*Letzte Aktualisierung: 04.02.2026*
