# Task 14: Dokumentation Cleanup - Plan

**Datum:** 21.12.2025  
**Status:** 🔄 Teilweise erledigt (Teil 1 abgeschlossen, Teil 2 folgt später)  
**Ziel:** Dokumentation aufräumen, DSP-Architektur-Diagramme erstellen

## 📋 Übersicht

Task 14 beinhaltet zwei Hauptaufgaben:
1. ✅ **DSP-Architektur-Diagramme erstellen**: 4 neue SVG-Diagramme erstellt (functional-view, edge-mc-functions, component-view, deployment-view) und in Objects Reference eingebettet **(Erledigt: 21.12.2025)**
2. ⏳ **Dokumentation aufräumen**: Veraltete Planungsdokumente identifizieren und entfernen/archivieren **(Folgt später)**

---

## 🎯 Teil 1: SVG-Diagramm Aktualisierung

### Aktuelle Situation

**Datei:** `osf/apps/osf-ui/src/app/components/dsp-animation/configs/assets/dsp-architecture-step19-diagram.svg`

**Probleme:**
- ❌ Enthält SVG-Icons statt Key-Namen
- ❌ Zeigt nicht alle Objekte, die in der functional-view-mode Animation verwendet werden
- ❌ Connections sind nicht in L-Form wie im Original
- ❌ Positionen/Struktur entspricht nicht genau dem functional-view-mode

### Alle Container aus Functional View Mode

Das SVG soll **alle Container** zeigen, die in der functional-view-mode Animation verwendet werden (aus allen Steps, nicht nur Step 19). Basierend auf `layout.shared.config.ts` und `layout.functional.config.ts`:

**Container-IDs (komplette Liste aller verwendeten Container):**

⚠️ **KONSISTENZ-PROBLEM IDENTIFIZIERT:**
- **Default Config:** Systems haben semantische Namen (`sf-system-any`, `sf-system-fts`, `sf-system-warehouse`, `sf-system-factory`)
- **FMF Config:** Systems haben abstrakte IDs (`sf-system-1`, `sf-system-2`)
- **Devices:** Beide verwenden die gleichen semantischen Namen (`sf-device-mill`, etc.)

**Frage:** Welche IDs sollen im SVG-Diagramm verwendet werden?

**✅ ENTSCHEIDUNG: Option B - Default Config (semantische Namen)**

- **Shopfloor Systems:** `sf-system-any`, `sf-system-fts` (semantisch)
- **Shopfloor Devices:** `sf-device-mill`, `sf-device-drill`, `sf-device-aiqs`, `sf-device-hbw`, `sf-device-dps`, `sf-device-chrg` (semantisch)
- → **Konsistent** (beide semantisch)

**Überlegung zur Default Config:**
- Im DSP-Tab wird immer Customer=FMF verwendet (OK)
- **Frage:** Brauchen wir überhaupt noch eine Default Config?
- **Antwort:** Default Config als Fallback/Referenz behalten, aber neue Customers sollten semantische Namen verwenden
- **Bei neuen Customers:** bp-layer und sf-layer Komponenten mit **semantischen Namen** anlegen (nicht abstrakt wie `sf-system-1`, `sf-system-2`)
- **Beispiel semantischer Namen:** `sf-system-agv`, `sf-system-warehouse`, `sf-system-factory` statt `sf-system-1`, `sf-system-2`
- **Vorteil:** Konsistenz gewährleistet, SVG-Diagramm kann Default Config verwenden

**Alle Container-IDs (für Planung):**
- **Layers:** `layer-bp`, `layer-dsp`, `layer-sf`
- **Business Processes:** `bp-erp`, `bp-mes`, `bp-cloud`, `bp-analytics`, `bp-data-lake`
- **DSP Containers:** `dsp-ux`, `dsp-edge`, `dsp-mc`
- **Shopfloor Groups:** `sf-systems-group`, `sf-devices-group`
- **Shopfloor Systems:** ✅ `sf-system-any`, `sf-system-fts` (semantisch, aus Default Config)
- **Shopfloor Devices:** `sf-device-mill`, `sf-device-drill`, `sf-device-aiqs`, `sf-device-hbw`, `sf-device-dps`, `sf-device-chrg` (semantisch)

**Anmerkung zu Connections:**
- Connections werden als L-Form-Pfade dargestellt
- **KEINE Beschriftung der Connections** erforderlich, da sie dem Pattern `conn_<from>_<to>` folgen und daher selbsterklärend sind

### Anforderungen für neue SVG

1. **Keine SVG-Icons**: Stattdessen Text mit Key-Namen (z.B. `sf-device-mill`, `bp-erp`)
2. **Alle Objekte**: Alle Container, die in der functional-view-mode Animation verwendet werden (Union aller Container aus allen Steps)
3. **Key-Namen**: Container-IDs als Text anzeigen (wie in `customer.fmf` Config definiert - z.B. `sf-system-1`, `sf-system-2` für FMF)
4. **L-Form Connections**: Connections sollen L-Form haben (nicht direkt, sondern mit rechtwinkligen Umwegen)
5. **Connections ohne Labels**: Connections werden NICHT beschriftet, da sie dem Pattern `conn_<from>_<to>` folgen
6. **Positionen**: Exakte Positionen aus `layout.shared.config.ts` verwenden (createCustomerContainers mit FMF_CONFIG)
7. **Layer-Struktur**: Business Process Layer (oben), DSP Layer (Mitte), Shopfloor Layer (unten)

### Datenquellen für SVG-Generierung

**Container-Positionen:**
- `layout.shared.config.ts`: `LAYOUT` Constants und Container-Erstellung
- `createCustomerContainers(FMF_CONFIG)` - Verwendet FMF Config für Key-Namen
- Alle Container-Positionen (x, y, width, height) extrahieren

**Connection-Positionen:**
- `layout.shared.config.ts`: `createDefaultConnections(customerConfig)` mit FMF_CONFIG
- Anchors: `fromSide`, `toSide` für L-Form-Routing
- **Wichtig:** Connections werden gezeichnet, aber NICHT beschriftet (Pattern `conn_<from>_<to>` ist selbsterklärend)

**Config Referenz (für Key-Namen):**

✅ **Entscheidung: Default Config verwenden**

- **Default Config:** `layout.shared.config.ts` - `createDefaultContainers()`
  - Shopfloor Systems: `sf-system-any`, `sf-system-fts` (semantisch) ✅
  - Shopfloor Devices: `sf-device-mill`, `sf-device-drill`, `sf-device-aiqs`, `sf-device-hbw`, `sf-device-dps`, `sf-device-chrg` (semantisch) ✅
  - Business Processes: `bp-erp`, `bp-mes`, `bp-cloud`, `bp-analytics`, `bp-data-lake`
  - DSP Containers: `dsp-ux`, `dsp-edge`, `dsp-mc`

**Hinweis zu FMF Config:**
- FMF Config verwendet abstrakte System-IDs (`sf-system-1`, `sf-system-2`)
- Im DSP-Tab wird zwar FMF verwendet, aber für SVG-Diagramm verwenden wir Default Config (semantische Namen)
- **Bei neuen Customers:** Semantische Namen verwenden (nicht abstrakt), damit Konsistenz gewährleistet ist

### Vorgehen

1. **Analyse aller Container:**
   - `layout.shared.config.ts` durchgehen
   - ✅ **Entscheidung:** Default Config (`createDefaultContainers()`) verwenden (semantische Namen)
   - Alle Container-Positionen (x, y, width, height) extrahieren
   - Alle Container-IDs sammeln (Union aller Container aus allen functional-view Steps)

2. **Analyse der Connections:**
   - `createDefaultConnections(FMF_CONFIG)` analysieren
   - Alle Connection-Anchors identifizieren (fromSide, toSide)
   - L-Form-Routing verstehen

3. **SVG neu erstellen:**
   - ViewBox: `0 0 1200 1140` (aus aktueller SVG, oder VIEWBOX_WIDTH/HEIGHT aus layout.shared.config.ts)
   - Layer-Hintergründe (Business Process, DSP, Shopfloor)
   - Container als Rechtecke mit Container-ID als Text (Key-Name, z.B. `sf-system-1`, `sf-device-mill`)
   - Connections als L-Form-Pfade (rechtwinklige Umwege)
   - **KEINE Labels/Beschriftungen bei Connections** (Pattern `conn_<from>_<to>` ist selbsterklärend)
   - Keine Icons, nur Text-Labels für Container

4. **Validierung:**
   - Vergleich mit funktionaler Ansicht im Browser (verschiedene Steps durchgehen)
   - Key-Namen mit FMF_CONFIG abgleichen (`sf-system-1`, `sf-system-2` statt `sf-system-any`, `sf-system-fts`)
   - Positionen mit layout.shared.config.ts abgleichen
   - Alle Container vorhanden (Union aus allen Steps)

---

## 🗑️ Teil 2: Dokumentation Cleanup

### Identifizierte veraltete Dokumente

#### Plan-Dokumente (bereits umgesetzt)

1. **`docs/PLAN_MODULE_TAB_UNIFICATION.md`**
   - **Status:** ✅ Bereits umgesetzt (Tasks 1-4 in PROJECT_STATUS.md erledigt)
   - **Inhalt:** Plan für Module-Tab Vereinheitlichung
   - **Empfehlung:** ➡️ Nach `docs/archive/` verschieben oder löschen

2. **`docs/PLAN_OSF_REBRANDING.md`**
   - **Status:** ✅ Vollständig umgesetzt (Task 13 erledigt)
   - **Inhalt:** Plan für OSF Rebranding
   - **Empfehlung:** ➡️ Nach `docs/archive/` verschieben

3. **`docs/TASK13_PLAN_VS_STATUS.md`**
   - **Status:** ✅ Vergleichsdokument, Task 13 abgeschlossen
   - **Inhalt:** Plan vs. Status Vergleich für Task 13
   - **Empfehlung:** ➡️ Nach `docs/archive/` verschieben

#### Analysis-Dokumente (bereits bereinigt)

4. ~~**`docs/analysis/code-optimization-test-coverage-plan-status.md`**~~ ✅ **GELÖSCHT**
   - **Status:** Plan vollständig umgesetzt, Status-Update nicht mehr benötigt
   - **Aktion:** Gelöscht (2025-12-21)

5. ~~**`docs/analysis/code-optimization-test-coverage-plan.md`**~~ ✅ **BEREITS GELÖSCHT**
   - **Status:** Original-Plan existierte nicht mehr (nur Status-Update vorhanden)
   - **Hinweis:** Plan war vollständig umgesetzt

6. ~~**`docs/analysis/examples-status-analysis.md`**~~ ✅ **GELÖSCHT**
   - **Status:** Analyse abgeschlossen, alle Examples gelöscht (2025-12-13)
   - **Aktion:** Gelöscht (2025-12-21)

7. ~~**`docs/analysis/documentation-importance-analysis.md`**~~ ✅ **GELÖSCHT**
   - **Status:** Analyse veraltet (PROJECT_STATUS.md wird weiterhin verwendet)
   - **Aktion:** Gelöscht (2025-12-21)

8. **`docs/analysis/fts-integration-plan.md`**
   - **Status:** ⚠️ Prüfen ob noch relevant (FTS → AGV bereits umgesetzt)
   - **Empfehlung:** Prüfen und ggf. archivieren

9. **`docs/07-analysis/shopfloor-layout-refactoring-plan.md`**
   - **Status:** ⚠️ Prüfen ob noch relevant
   - **Empfehlung:** Prüfen, ob Plan bereits umgesetzt wurde

#### Sonstige Dokumente

10. ~~**`docs/ANALYSIS_OVERVIEW_TAB.md`**~~ ✅ **GELÖSCHT**
    - **Status:** Analyse abgeschlossen, Overview-Tab wurde entfernt (2025-12-20)
    - **Aktion:** Gelöscht (2025-12-21)

11. **`docs/deployment-alternatives.md`**
    - **Status:** ⚠️ Prüfen, ob noch relevant
    - **Empfehlung:** Prüfen, ob noch relevant, sonst löschen

### Cleanup-Strategie

#### Schritt 1: Plan-Dokumente archivieren
- Alle PLAN_*.md Dateien prüfen
- Wenn umgesetzt → Nach `docs/archive/plans/` verschieben
- README.md in archive/plans/ erstellen mit Erläuterung

#### Schritt 2: Analysis-Pläne prüfen
- Jeden Plan-Dokument prüfen
- Status mit aktueller Implementierung abgleichen
- Wenn umgesetzt → Archivieren
- Wenn noch relevant → Behalten

#### Schritt 3: Veraltete Dokumente entfernen
- Dokumente identifizieren, die nur noch Optionen enthalten (nach Umsetzung nicht mehr relevant)
- Diese entweder löschen oder stark bereinigen

#### Schritt 4: Dokumentation strukturieren
- Sicherstellen, dass `docs/archive/` für historische Dokumente verwendet wird
- Root-Level docs nur für aktuelle, relevante Dokumentation

### Vorgehen

1. **Dokumente durchgehen:**
   - Jede identifizierte Datei öffnen
   - Prüfen ob Inhalt noch relevant
   - Status mit PROJECT_STATUS.md abgleichen

2. **Archivierung:**
   - Neue Struktur: `docs/archive/plans/`
   - Dokumente verschieben (git mv)
   - README.md erstellen mit Erläuterung

3. **Löschung (nur nach Prüfung):**
   - Nur Dokumente löschen, die wirklich obsolet sind
   - Bei Unsicherheit: Archivieren statt löschen

---

## 📋 Checkliste für Umsetzung

### SVG-Diagramm Aktualisierung

- [ ] **Schritt 1: Analyse**
  - [ ] ✅ **Entscheidung getroffen:** Default Config verwenden (semantische Namen: `sf-system-any`, `sf-system-fts`)
  - [ ] `layout.shared.config.ts` durchgehen
  - [ ] `createDefaultContainers()` analysieren (alle Container-Positionen extrahieren)
  - [ ] Alle Connection-Anchors identifizieren
  - [ ] ViewBox-Dimensionen prüfen (VIEWBOX_WIDTH, VIEWBOX_HEIGHT)

- [ ] **Schritt 2: SVG erstellen**
  - [ ] Layer-Hintergründe zeichnen
  - [ ] Container als Rechtecke mit Key-Namen (Container-IDs aus Default Config, z.B. `sf-system-any`, `sf-system-fts`, `sf-device-mill`)
  - [ ] Connections als L-Form-Pfade (rechtwinklige Umwege)
  - [ ] **KEINE Labels bei Connections** (Pattern `conn_<from>_<to>` ist selbsterklärend)
  - [ ] Keine Icons, nur Text für Container-IDs

- [ ] **Schritt 3: Validierung**
  - [ ] Vergleich mit Browser (verschiedene Steps, functional view mit Default Config)
  - [ ] Key-Namen mit Default Config abgleichen (`sf-system-any`, `sf-system-fts`, etc.)
  - [ ] Alle Container vorhanden (Union aus allen Steps)
  - [ ] Positionen verifizieren (aus `createDefaultContainers()`)
  - [ ] L-Form Connections prüfen (ohne Labels)

### Dokumentation Cleanup

- [ ] **Schritt 1: Plan-Dokumente**
  - [ ] `PLAN_MODULE_TAB_UNIFICATION.md` prüfen → archivieren/löschen
  - [ ] `PLAN_OSF_REBRANDING.md` prüfen → archivieren
  - [ ] `TASK13_PLAN_VS_STATUS.md` prüfen → archivieren

- [x] **Schritt 2: Analysis-Pläne**
  - [x] ✅ `code-optimization-test-coverage-plan-status.md` → **GELÖSCHT** (2025-12-21)
  - [x] ✅ `code-optimization-test-coverage-plan.md` → **BEREITS GELÖSCHT** (existierte nicht mehr)
  - [x] ✅ `examples-status-analysis.md` → **GELÖSCHT** (2025-12-21)
  - [x] ✅ `documentation-importance-analysis.md` → **GELÖSCHT** (2025-12-21)
  - [ ] `fts-integration-plan.md` prüfen
  - [ ] `shopfloor-layout-refactoring-plan.md` prüfen

- [x] **Schritt 3: Sonstige Dokumente**
  - [x] ✅ `ANALYSIS_OVERVIEW_TAB.md` → **GELÖSCHT** (2025-12-21)
  - [ ] `deployment-alternatives.md` prüfen → löschen/archivieren

- [ ] **Schritt 4: Strukturierung**
  - [ ] `docs/archive/plans/` Verzeichnis erstellen
  - [ ] README.md für archive/plans/ erstellen
  - [ ] Dokumente verschieben (git mv)

---

## 🎯 Erwartetes Ergebnis

### SVG-Diagramm
- ✅ Zeigt alle Container, die in der functional-view-mode Animation verwendet werden (Union aller Steps)
- ✅ Key-Namen statt Icons (Container-IDs als Text, aus Default Config)
- ✅ Connections in L-Form (ohne Labels, da Pattern `conn_<from>_<to>` selbsterklärend)
- ✅ Exakte Positionen aus layout.shared.config.ts (`createDefaultContainers()`)
- ✅ **Konsistenz:** Default Config mit semantischen Namen (`sf-system-any`, `sf-system-fts`, `sf-device-mill`, etc.)

### Dokumentation
- ✅ Plan-Dokumente archiviert (wenn umgesetzt)
- ✅ Veraltete Dokumente entfernt oder archiviert
- ✅ Klare Struktur: Aktuelle docs im Root, historische im archive/
- ✅ README.md in archive/plans/ erklärt die archivierten Pläne

---

## 📝 Notizen

- **SVG-Erstellung:** Kann manuell in Inkscape/Figma/Draw.io erfolgen oder programmatisch generiert werden
- **L-Form Connections:** Routing-Logik aus dsp-animation.component.ts kann als Referenz dienen
- **Positionen:** VIEWBOX_WIDTH und VIEWBOX_HEIGHT aus `layout.shared.config.ts` verwenden
- **Config-Entscheidung:** ✅ Default Config mit semantischen Namen (`sf-system-any`, `sf-system-fts`, etc.)
- **Alle Container:** Union aller Container aus allen functional-view Steps (nicht nur Step 19)
- **Connections:** Werden gezeichnet, aber NICHT beschriftet (Pattern `conn_<from>_<to>` ist selbsterklärend)
- **Hinweis:** Im DSP-Tab wird FMF verwendet, aber SVG-Diagramm zeigt Default Config (semantische Namen für Konsistenz)
- **Für neue Customers:** Semantische Namen verwenden (nicht abstrakt), damit Konsistenz gewährleistet ist

---

**Nächster Schritt:** Warten auf Freigabe, dann Umsetzung beginnen
