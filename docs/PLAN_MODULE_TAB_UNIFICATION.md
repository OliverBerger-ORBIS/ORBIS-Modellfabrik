# Plan: Module-Tab Vereinheitlichung

**Datum:** 17.12.2025  
**Ziel:** Vereinheitlichung der Module-Sections (HBW/DRILL/MILL/DPS/AIQS) + Task 2 (Sequence Commands)

## 📊 Aktuelle Situation

### Unterschiede zwischen Module-Sections

#### HBW/DRILL/MILL (einheitlich)
- **CSS-Klasse:** `module-specific-section`
- **Header:** Einfaches `<h4>` ohne Icon
- **Details:** `module-specific-section__details` mit `detail-row` Struktur
- **History:** `module-specific-section__history` mit einfacher Liste (`history-list` + `history-item`)
- **Struktur:** 
  ```
  - Header (h4)
  - Details (detail-row)
  - History (h5 + history-list)
  ```

#### DPS/AIQS (unterschiedlich)
- **CSS-Klasse:** `dps-section` / `aiqs-section` (separate Klassen)
- **Header:** Icon (`<img>`) + `<h4>` mit Icon
- **Details:** `dps-section__status` / `aiqs-section__status` (andere Struktur)
- **History:** `<details>` mit Tabelle (`dps-history-table` / `aiqs-history-table`)
- **Zusätzliche Sections:**
  - DPS: `dps-section__workpiece` (Workpiece Information)
  - AIQS: `aiqs-section__quality` (Quality Results)
- **Struktur:**
  ```
  - Header (Icon + h4)
  - Status (status-item)
  - Workpiece/Quality (optional, nur DPS/AIQS)
  - History (details + table)
  ```

### Sequence Commands (Task 2)
- **Aktuell:** Direkt nach Module-Sections, nur für DRILL/MILL/AIQS
- **Ziel:** Gemeinsames Accordion am unteren Rand für alle Module mit Sequence Commands

## 🎯 Vereinheitlichungs-Plan

### Phase 1: DPS/AIQS an `module-specific-section` Pattern anpassen

#### 1.1 CSS-Klassen vereinheitlichen
- [ ] DPS/AIQS Sections auf `module-specific-section` umstellen
- [ ] Alte `dps-section` / `aiqs-section` Klassen entfernen oder als Aliase behalten
- [ ] Gemeinsame Styles in `module-specific-section` konsolidieren

#### 1.2 Header-Struktur vereinheitlichen
- [ ] **Option A:** Alle Sections bekommen Icon (konsistent)
- [ ] **Option B:** Alle Sections ohne Icon (wie HBW/DRILL/MILL)
- [ ] **Empfehlung:** Option A (Icons machen UI konsistenter)

#### 1.3 Details-Struktur vereinheitlichen
- [ ] DPS/AIQS `status` Sections in `module-specific-section__details` umwandeln
- [ ] `detail-row` Pattern für alle Module verwenden
- [ ] Bestehende `dps-status-item` / `aiqs-status-item` durch `detail-row` ersetzen

#### 1.4 History-Struktur vereinheitlichen
- [ ] **Entscheidung:** Liste oder Tabelle?
  - **Option A:** Alle als Liste (wie HBW/DRILL/MILL) - einfacher, weniger Info
  - **Option B:** Alle als Tabelle (wie DPS/AIQS) - mehr Info, besser lesbar
  - **Empfehlung:** Option B (Tabelle zeigt mehr Details: Command, State, Result, Timestamp)
- [ ] History für HBW/DRILL/MILL auf Tabellen-Format umstellen
- [ ] Gemeinsame `module-specific-section__history-table` Klasse erstellen

#### 1.5 Zusätzliche Sections (DPS/AIQS)
- [ ] `dps-section__workpiece` → `module-specific-section__workpiece` (optional, nur DPS)
- [ ] `aiqs-section__quality` → `module-specific-section__quality` (optional, nur AIQS)
- [ ] Als separate Sub-Sections innerhalb von `module-specific-section` belassen

### Phase 2: Sequence Commands bündeln (Task 2)

#### 2.1 Accordion-Komponente erstellen
- [ ] Sequence Commands in `<details>` Accordion verschieben
- [ ] Position: Am unteren Rand, nach allen Module-Sections
- [ ] Konsistente Beschriftung: "Sequence Commands" mit Modul-Name

#### 2.2 Module-Erweiterung
- [ ] Prüfen, welche Module Sequence Commands haben (aktuell: DRILL/MILL/AIQS)
- [ ] Ggf. auch für andere Module vorbereiten (HBW, DPS?)

#### 2.3 Layout-Anpassung
- [ ] Sequence Commands Section am Ende positionieren
- [ ] Styling anpassen (Abstand, Border, etc.)

### Phase 3: Namensgebung vereinheitlichen

#### 3.1 Section-Titel
- [ ] **HBW:** "Storage Information" → beibehalten
- [ ] **DRILL:** "Drilling Information" → beibehalten
- [ ] **MILL:** "Milling Information" → beibehalten
- [ ] **DPS:** "DPS Status" → "DPS Information" (konsistent)
- [ ] **AIQS:** "AIQS Status" → "AIQS Information" (konsistent)

#### 3.2 Sub-Section-Titel
- [ ] DPS: "Workpiece Information" → beibehalten
- [ ] AIQS: "Quality Results" → beibehalten
- [ ] History: "Command History" → einheitlich für alle

### Phase 4: Code-Cleanup

#### 4.1 TypeScript
- [ ] Interfaces vereinheitlichen (alle Module verwenden ähnliche Struktur)
- [ ] Helper-Methoden konsolidieren (z.B. `formatTimestamp` für alle)

#### 4.2 SCSS
- [ ] Alte `dps-section` / `aiqs-section` Styles entfernen
- [ ] Gemeinsame Styles in `module-specific-section` konsolidieren
- [ ] Redundanzen eliminieren

## 📋 Implementierungs-Reihenfolge

1. **History-Struktur vereinheitlichen** (Phase 1.4)
   - Entscheidung: Liste oder Tabelle?
   - Alle Module auf einheitliches Format umstellen

2. **Details-Struktur vereinheitlichen** (Phase 1.3)
   - DPS/AIQS auf `detail-row` Pattern umstellen

3. **CSS-Klassen vereinheitlichen** (Phase 1.1)
   - Alle Sections auf `module-specific-section` umstellen

4. **Header vereinheitlichen** (Phase 1.2)
   - Icons für alle Module hinzufügen (oder entfernen)

5. **Sequence Commands bündeln** (Phase 2)
   - Accordion erstellen und positionieren

6. **Namensgebung anpassen** (Phase 3)
   - Titel konsistent machen

7. **Code-Cleanup** (Phase 4)
   - Alte Styles/Methoden entfernen

## ❓ Offene Fragen

1. **History-Format:** Liste oder Tabelle? (Empfehlung: Tabelle)
2. **Icons:** Für alle Module oder keine? (Empfehlung: Alle)
3. **Sequence Commands:** Auch für HBW/DPS? (Aktuell nur DRILL/MILL/AIQS)
4. **Workpiece/Quality Sections:** Als separate Sub-Sections oder integriert?

## 📝 Stash-Status

**Aktueller Stash:**
- `stash@{0}: DPS/AIQS Module-Tab Integration (korrigierte Logik mit actionStates Array)`

**Status:** Stash wurde bereits angewendet (Änderungen sind im aktuellen Code). Stash kann gelöscht werden nach erfolgreicher Vereinheitlichung.

