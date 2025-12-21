# Task 14: Dokumentation Cleanup - Vollständige Inventarisierung

**Datum:** 2025-12-21  
**Status:** 🔄 Inventarisierung abgeschlossen, Teil 1 (SVG-Diagramme) erledigt, Cleanup folgt später  
**Ziel:** Alle Dokumente im Projekt-Root Schritt-für-Schritt prüfen, anpassen oder löschen

**Erledigt (21.12.2025):**
- ✅ DSP-Architektur-Diagramme erstellt (4 SVG-Diagramme)
- ✅ SVG-Inventory erstellt und nach `docs/02-architecture/` verschoben
- ✅ Objects Reference aktualisiert (Business Applications, SVG-Tiles)
- ✅ HOWTO_ADD_CUSTOMER.md aktualisiert

**Folgt später:**
- ⏳ Schritt-für-Schritt Dokumentation Cleanup

---

## 📋 Cleanup-Strategie

### Schritt-für-Schritt Vorgehen
1. **Ein Dokument nach dem anderen** prüfen
2. **Entscheidung treffen:** Behalten (ggf. anpassen), Löschen, Archivieren
3. **Voice-Control kompatibel:** Kurze, klare Tasks pro Dokument

### Entscheidungskriterien
- **Behalten:** Aktuell relevant, wird verwendet, referenziert in anderen Dokumenten
- **Anpassen:** Inhalt teilweise veraltet, aber Dokument noch relevant
- **Löschen:** Veraltet, abgeschlossen, nicht mehr benötigt
- **Archivieren:** Historisch relevant, aber nicht mehr aktiv

---

## 📁 Kategorisierte Dokumenten-Liste

### 🎯 PRIORITÄT 1: Root-Level Dokumente

#### ✅ Aktive Dokumente (wahrscheinlich behalten)
1. **`README.md`** - Haupt-Dokumentation, zentrale Referenz
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen auf Aktualität, Links prüfen

2. **`CHANGELOG.md`** - Versions-Historie
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen ob aktuell, Format prüfen

---

### 📂 PRIORITÄT 2: docs/ Verzeichnis (Root-Level)

#### Status-/Plan-Dokumente
3. **`docs/PROJECT_STATUS.md`** - Aktueller Projekt-Status
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen auf Aktualität, veraltete Inhalte entfernen

4. **`docs/TASK13_STATUS_CHECK.md`** - Task 13 Status
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen ob Task 13 abgeschlossen, ggf. löschen

5. **`docs/TASK14_DOCUMENTATION_CLEANUP_PLAN.md`** - Aktueller Cleanup-Plan
   - **Status:** ✅ Aktuell (wird gerade bearbeitet)
   - **Aktion:** Nach Abschluss von Task 14 löschen

6. **`docs/TASK14_DOCUMENTATION_CLEANUP_INVENTORY.md`** - Diese Datei
   - **Status:** ✅ Aktuell (wird gerade erstellt)
   - **Aktion:** Nach Abschluss von Task 14 löschen

#### Sonstige Root-Dokumente
7. **`docs/credentials.md`** - Credentials
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen ob noch benötigt, ggf. in .gitignore

8. **`docs/deployment-alternatives.md`** - Deployment-Alternativen
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen ob noch relevant, ggf. löschen (laut documentation-importance-analysis.md veraltet)

9. **`docs/README.md`** - Dokumentations-Übersicht
   - **Status:** ⏳ Zu prüfen
   - **Aktion:** Prüfen auf Aktualität, Links prüfen

10. **`docs/99-glossary.md`** - Glossar
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität, Begriffe prüfen

11. **`docs/svg-inventory.md`** - SVG-Inventar
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch verwendet, ggf. aktualisieren

12. **`docs/svg-inventory.html`** - SVG-Inventar HTML
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch verwendet, ggf. löschen wenn veraltet

---

### 📂 PRIORITÄT 3: docs/sprints/ - Sprint-Dokumentation

#### Sprint-Dokumente (13 Dateien)
13. **`docs/sprints/sprints_README.md`** - Sprint-Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

14. **`docs/sprints/sprint_template.md`** - Sprint-Template
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch verwendet

15. **`docs/sprints/sprint_aktuell.md`** - Aktueller Sprint
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität, ggf. mit PROJECT_STATUS.md abgleichen

16-24. **`docs/sprints/sprint_01.md` bis `docs/sprints/sprint_08.md`** (8 Dateien)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob archiviert werden sollten

25. **`docs/sprints/stakeholder_report_sprints_01-04.md`** - Stakeholder Report
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob historisch relevant, ggf. archivieren

26. **`docs/sprints/stakeholder_report_template.md`** - Stakeholder Report Template
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch verwendet

---

### 📂 PRIORITÄT 4: docs/01-strategy/ - Strategische Dokumentation

27. **`docs/01-strategy/README.md`** - Strategy-Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

28. **`docs/01-strategy/vision.md`** - Vision
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

29. **`docs/01-strategy/roadmap.md`** - Roadmap
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität, mit PROJECT_STATUS.md abgleichen

30. **`docs/01-strategy/project-overview.md`** - Projekt-Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität, Links prüfen

31. **`docs/01-strategy/development-phases.md`** - Entwicklungsphasen
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

---

### 📂 PRIORITÄT 5: docs/02-architecture/ - Architektur-Dokumentation

32. **`docs/02-architecture/README.md`** - Architecture-Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

33. **`docs/02-architecture/project-structure.md`** - Projekt-Struktur
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität (referenziert in README.md)

34. **`docs/02-architecture/naming-conventions.md`** - Namenskonventionen
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität (referenziert in README.md)

35. **`docs/02-architecture/aps-data-flow.md`** - APS Data Flow
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität (referenziert in README.md)

36. **`docs/02-architecture/dsp-architecture-component-spec.md`** - DSP Architecture Spec
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch relevant (alte Spezifikation?)

37. **`docs/02-architecture/message-processing-pattern.md`** - Message Processing Pattern
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

38. **`docs/02-architecture/message-sending-architecture.md`** - Message Sending Architecture
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

39. **`docs/02-architecture/multiple_client_per_role.md`** - Multiple Client per Role
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

40. **`docs/02-architecture/omf2-architecture.md`** - OMF2 Architecture (Legacy)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch relevant (OMF2 ist Legacy)

41. **`docs/02-architecture/omf2-registry-system.md`** - OMF2 Registry System (Legacy)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch relevant (OMF2 ist Legacy)

42. **`docs/02-architecture/shopfloor-mapping-service.md`** - Shopfloor Mapping Service
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

43. **`docs/02-architecture/shopfloor-route-calculation.md`** - Shopfloor Route Calculation
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

---

### 📂 PRIORITÄT 6: docs/03-decision-records/ - Entscheidungs-Dokumente

44. **`docs/03-decision-records/README.md`** - Decision Records Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

45-52. **`docs/03-decision-records/*.md`** (8 Decision Records)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jeden Record einzeln prüfen, ob noch relevant

---

### 📂 PRIORITÄT 7: docs/04-howto/ - How-To Guides

53. **`docs/04-howto/README.md`** - How-To Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

54-87. **`docs/04-howto/*.md`** (34 How-To Guides in verschiedenen Unterordnern)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jeden Guide einzeln prüfen, ob noch relevant

---

### 📂 PRIORITÄT 8: docs/06-integrations/ - Integrations-Dokumentation

88. **`docs/06-integrations/00-REFERENCE/README.md`** - Reference-Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

89-97. **`docs/06-integrations/**/*.md`** (10 Integrations-Dokumente)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jedes Dokument einzeln prüfen, ob noch relevant

---

### 📂 PRIORITÄT 9: docs/07-analysis/ - Analyse-Dokumente

98-107. **`docs/07-analysis/*.md`** (10 Analysis-Dokumente)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jedes Dokument einzeln prüfen, ob noch relevant oder veraltet

---

### 📂 PRIORITÄT 10: docs/analysis/ - Code Quality Analysis

108. **`docs/analysis/README.md`** - Analysis Übersicht
    - **Status:** ✅ Bereits aktualisiert (2025-12-21)
    - **Aktion:** Keine weitere Aktion

109. **`docs/analysis/test-coverage-status.md`** - Test Coverage Status
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

110. **`docs/analysis/test-coverage-summary.md`** - Test Coverage Summary
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

111. **`docs/analysis/build-commands-guide.md`** - Build Commands Guide
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

112. **`docs/analysis/fixture-system-analysis.md`** - Fixture System Analysis
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

---

### 📂 PRIORITÄT 11: docs/archive/ - Archivierte Dokumente

113. **`docs/archive/README.md`** - Archiv-Übersicht
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

114-122. **`docs/archive/**/*.md`** (10 Archiv-Dokumente)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob wirklich archiviert, ggf. weiter bereinigen

---

### 📂 PRIORITÄT 12: Weitere Verzeichnisse

#### docs/registry/
123. **`docs/registry/business_functions.md`** - Business Functions
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

124. **`docs/registry/sensors_display.md`** - Sensors Display
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

#### docs/_shared/
125. **`docs/_shared/README.md`** - Shared Documentation
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

---

### 📂 PRIORITÄT 13: Weitere Root-Level Verzeichnisse

#### data/omf-data/
126-135. **`data/omf-data/**/*.md`** (10+ Markdown-Dateien)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen ob noch relevant (Daten-Analysen)

#### osf/ (Library-Dokumentation)
136-145. **`osf/**/README.md`** (10+ README-Dateien in Libraries)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jedes README einzeln prüfen

#### session_manager/
146. **`session_manager/README.md`** - Session Manager README
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

#### integrations/
147-155. **`integrations/**/README.md`** (8+ README-Dateien)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jedes README einzeln prüfen

#### tools/
156-160. **`tools/**/*.md`** (5+ Markdown-Dateien)
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Jedes Dokument einzeln prüfen

#### backend/
161. **`backend/metrics-service/README.md`** - Metrics Service README
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

#### deploy/
162. **`deploy/README.md`** - Deploy README
    - **Status:** ⏳ Zu prüfen
    - **Aktion:** Prüfen auf Aktualität

---

## 📊 Zusammenfassung

- **Gesamt:** ~162 Dokumente zu prüfen
- **Priorität 1-2:** 12 Dokumente (Root-Level, docs/ Root)
- **Priorität 3:** 13 Dokumente (Sprints)
- **Priorität 4:** 5 Dokumente (Strategy)
- **Priorität 5:** 12 Dokumente (Architecture)
- **Priorität 6:** 8 Dokumente (Decision Records)
- **Priorität 7:** 34 Dokumente (How-To Guides)
- **Priorität 8:** 10 Dokumente (Integrations)
- **Priorität 9:** 10 Dokumente (Analysis)
- **Priorität 10:** 4 Dokumente (Code Quality Analysis - teilweise bereits bereinigt)
- **Priorität 11:** 10 Dokumente (Archive)
- **Priorität 12-13:** ~34 Dokumente (Weitere Verzeichnisse)

---

## 🎯 Vorgehen

### Voice-Control kompatible Task-Beschreibungen

Für jedes Dokument kann eine kurze, klare Anweisung gegeben werden:

**Format:** `[Priorität] [Dateiname] - [Kurze Beschreibung] - [Aktion]`

**Beispiele:**
- `P1 README.md - Haupt-Dokumentation prüfen - Links prüfen, Aktualität checken`
- `P2 PROJECT_STATUS.md - Projekt-Status prüfen - Veraltete Inhalte entfernen`
- `P3 sprint_01.md - Sprint 1 Dokumentation prüfen - Archivieren oder löschen`

---

## ✅ Bereits erledigt (2025-12-21)

- ✅ `TASK5_PLAN.md` - **GELÖSCHT** (Task abgeschlossen)
- ✅ `docs/ANALYSIS_OVERVIEW_TAB.md` - **GELÖSCHT** (Analyse abgeschlossen)
- ✅ `docs/analysis/examples-status-analysis.md` - **GELÖSCHT** (Analyse abgeschlossen)
- ✅ `docs/analysis/documentation-importance-analysis.md` - **GELÖSCHT** (veraltet)
- ✅ `docs/analysis/code-optimization-test-coverage-plan-status.md` - **GELÖSCHT** (veraltet)
- ✅ `docs/analysis/README.md` - **AKTUALISIERT** (Referenzen bereinigt)

---

## 📝 Notizen

- Dokumente werden Schritt-für-Schritt geprüft
- Bei Unsicherheit: Archivieren statt löschen
- Referenzen zwischen Dokumenten prüfen
- Links prüfen und aktualisieren

---

**Nächster Schritt:** Mit Priorität 1 beginnen (Root-Level Dokumente)

