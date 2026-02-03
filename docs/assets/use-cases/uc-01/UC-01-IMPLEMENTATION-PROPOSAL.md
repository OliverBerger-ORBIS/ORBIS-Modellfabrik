# UC-01 Track & Trace Genealogy - Implementierungsvorschlag

**Erstellt:** 29.01.2026  
**Basis:** UC-06 Implementierungs-Pattern + UC-01-Track-Trace-Schema.png

---

## 🎯 Zielsetzung

**Unterschied zur Live-Demo (`dsp/use-case/track-trace`):**
- Live-Demo: Zeigt aktuelle Systeminformationen (Live/Replay)
- UC-01 Schema: Zeigt das **Konzept** der Korrelation und Genealogie-Bildung
- Fokus: **Visuelle Erklärung** des Join-Key-Prinzips (NFC-Tag) und der Event-Korrelation

---

## 📐 Column-Struktur (basierend auf Schema)

### Column 1: "Business Events" (Links)
**Zweck:** Zeigt Business-Kontext, der zum Werkstück führt

**Lanes:**
1. **Supplier Order** (oben)
   - Purchase Order mit Supplier-Info
   - Material/Batch-Informationen
   - ERP-ID, Supplier-ID

2. **Storage Order** (Mitte)
   - Verknüpfung: Supplier Order → Storage Order
   - Warehouse-Zuordnung
   - Material-Eingang

3. **Customer Order** (unten)
   - Customer Order mit Customer-Info
   - Produktionsauftrag (Production Order)
   - ERP-ID, Customer-ID

**Visuelle Elemente:**
- Pfeile zwischen Lanes (Supplier Order → Storage Order → Warehouse)
- Pfeil von Customer Order → Production Order
- Icons: Supplier, Warehouse, Customer, Production Order

---

### Column 2: "Production Plan" (Mitte-Links)
**Zweck:** Zeigt den **theoretischen Plan** (Soll-Prozess)

**Lanes:**
1. **Plan Definition**
   - Sequenz: Warehouse → DRILL → Quality-Station → DPS
   - Als Timeline/Sequenz dargestellt
   - Icons für Stationen

**Visuelle Elemente:**
- Timeline mit Stationen
- Sequenzielle Pfeile
- "Plan" Badge/Label

---

### Column 3: "Actual Path" (Mitte-Rechts)
**Zweck:** Zeigt den **tatsächlichen Weg** des Werkstücks (Ist-Prozess)

**Lanes:**
1. **FTS Route**
   - Tatsächliche FTS-Bewegungen
   - Stationen, die angefahren wurden
   - Kann Stationen enthalten, die NICHT im Plan sind

**Visuelle Elemente:**
- Timeline mit tatsächlichen Events
- Pfeile zwischen Stationen
- Hervorhebung von Abweichungen (Stationen außerhalb des Plans)
- Timestamps (optional)

---

### Column 4: "Correlated Timeline" (Rechts)
**Zweck:** Zeigt die **korrelierte Genealogie** (Join über NFC-Tag)

**Lanes:**
1. **NFC/Workpiece ID** (oben)
   - Zentrales Element: NFC-Tag als Join-Key
   - Beispiel-ID: "A5873A2-A4525"
   - Visuell hervorgehoben (grüner Rahmen, größer)

2. **Event Timeline** (Mitte)
   - Korrelierte Events aus allen Quellen
   - Nummerierte Timeline (1, 2, 3, ...)
   - Kombiniert: Business-Events + Shopfloor-Events + Quality-Events
   - Timestamps

3. **Order Context** (unten)
   - Production Order Details
   - Customer Order Details
   - Material/Batch-Info
   - ERP-IDs

**Visuelle Elemente:**
- Verbindungslinien (gestrichelt) von NFC-Tag zu Events
- Verbindungslinien von Events zu Order Context
- Farbcodierung: Business (blau), Shopfloor (grün), Quality (orange)

---

## 🔗 Verbindungen zwischen Columns

### Verbindungslinien (gestrichelt):
1. **Business Events → NFC-Tag:**
   - Supplier Order → NFC-Tag
   - Customer Order → NFC-Tag
   - Storage Order → NFC-Tag

2. **Production Plan → Actual Path:**
   - Plan-Stationen → Tatsächliche Stationen (wenn übereinstimmend)
   - Abweichungen visuell markiert

3. **Actual Path → Correlated Timeline:**
   - FTS-Events → Timeline-Events
   - Station-Events → Timeline-Events

4. **NFC-Tag → Correlated Timeline:**
   - Zentraler Join-Punkt
   - Alle Events werden über NFC-Tag korreliert

---

## 🎬 Animation-Steps (Vorschlag)

### Step 0: Overview
- Alle Columns sichtbar
- Keine Hervorhebung
- Subtitle: "Track & Trace entsteht durch Korrelation von Events entlang einer eindeutigen Werkstück-ID"

### Step 1: Business Events
- **Highlight:** Column 1 (Business Events)
- **Dim:** Column 2, 3, 4
- **Beschreibung:** "Business-Events (Supplier Order, Customer Order) werden mit Material/Batch-Informationen verknüpft"

### Step 2: NFC-Tag als Join-Key
- **Highlight:** NFC-Tag in Column 4
- **Highlight:** Verbindungslinien von Business Events → NFC-Tag
- **Dim:** Production Plan, Actual Path
- **Beschreibung:** "Der NFC-Tag des Werkstücks dient als Join-Key zur Korrelation aller Events"

### Step 3: Production Plan
- **Highlight:** Column 2 (Production Plan)
- **Highlight:** Plan-Sequenz (Warehouse → DRILL → Quality → DPS)
- **Dim:** Actual Path
- **Beschreibung:** "Der Produktionsplan definiert die theoretische Sequenz der Stationen"

### Step 4: Actual Path
- **Highlight:** Column 3 (Actual Path)
- **Highlight:** Tatsächliche FTS-Route
- **Highlight:** Abweichungen vom Plan (wenn vorhanden)
- **Dim:** Production Plan
- **Beschreibung:** "Der tatsächliche Weg des Werkstücks kann vom Plan abweichen"

### Step 5: Correlation
- **Highlight:** Verbindungslinien von Actual Path → Correlated Timeline
- **Highlight:** Timeline-Events in Column 4
- **Dim:** Business Events, Production Plan
- **Beschreibung:** "Shopfloor-Events werden über den NFC-Tag korreliert"

### Step 6: Complete Genealogy
- **Highlight:** Gesamte Correlated Timeline
- **Highlight:** Order Context
- **Beschreibung:** "Die vollständige Genealogie kombiniert Business-Kontext, Plan, tatsächlichen Weg und korrelierte Events"

### Step 7: Target Systems
- **Highlight:** Order Context
- **Highlight:** ERP/MES/Analytics Icons (optional, unten)
- **Beschreibung:** "Die Genealogie wird in Zielsysteme (ERP, MES, Analytics) integriert"

---

## 🏗️ Implementierungs-Ansatz

### 1. Struktur-Datei: `uc-01-structure.config.ts`

**Columns:**
```typescript
columns: {
  businessEvents: {
    id: 'business-events',
    x: 80,
    y: 300,
    width: 400,
    height: 900,
    lanes: [
      { id: 'supplier-order', ... },
      { id: 'storage-order', ... },
      { id: 'customer-order', ... }
    ]
  },
  productionPlan: {
    id: 'production-plan',
    x: 520,
    y: 300,
    width: 400,
    height: 400,
    lanes: [
      { id: 'plan-sequence', ... }
    ]
  },
  actualPath: {
    id: 'actual-path',
    x: 960,
    y: 300,
    width: 400,
    height: 400,
    lanes: [
      { id: 'fts-route', ... }
    ]
  },
  correlatedTimeline: {
    id: 'correlated-timeline',
    x: 1400,
    y: 300,
    width: 480,
    height: 900,
    lanes: [
      { id: 'nfc-tag', ... },
      { id: 'event-timeline', ... },
      { id: 'order-context', ... }
    ]
  }
}
```

### 2. SVG-Generator: `uc-01-svg-generator.service.ts`

**Features:**
- Dynamische Generierung aus Struktur
- Verbindungslinien zwischen Columns (gestrichelt)
- Timeline-Rendering mit Nummerierung
- Event-Icons aus Icon-Registry
- Farbcodierung: Business (blau), Shopfloor (grün), Quality (orange), Plan (grau)

### 3. I18n-Service: `uc-01-i18n.service.ts`

**Keys:**
- `uc01.title`
- `uc01.subtitle`
- `uc01.column.business_events`
- `uc01.column.production_plan`
- `uc01.column.actual_path`
- `uc01.column.correlated_timeline`
- `uc01.lane.supplier_order`
- `uc01.lane.storage_order`
- `uc01.lane.customer_order`
- `uc01.lane.plan_sequence`
- `uc01.lane.fts_route`
- `uc01.lane.nfc_tag`
- `uc01.lane.event_timeline`
- `uc01.lane.order_context`
- `uc01.chip.purchase_order`
- `uc01.chip.material_batch`
- `uc01.chip.production_order`
- etc.

### 4. Component: `track-trace-genealogy-use-case.component.ts`

**Features:**
- Step-Animation (analog UC-06)
- Zoom-Funktionalität
- Auto-Play, Loop
- Controls: Prev/Next, Step-Dots, Zoom

### 5. Steps-Definition: `uc-01-track-trace-genealogy.steps.json`

**Struktur:**
```json
[
  {
    "id": "uc01-00-overview",
    "title": { "de": "Übersicht", "en": "Overview" },
    "description": { "de": "...", "en": "..." },
    "highlightIds": ["uc01_col_business_events", "uc01_col_production_plan", "uc01_col_actual_path", "uc01_col_correlated_timeline"],
    "dimIds": [],
    "showIds": [],
    "hideIds": []
  },
  {
    "id": "uc01-01-business-events",
    "title": { "de": "Business-Events", "en": "Business Events" },
    "description": { "de": "...", "en": "..." },
    "highlightIds": ["uc01_col_business_events", "uc01_lane_supplier_order", "uc01_lane_storage_order", "uc01_lane_customer_order"],
    "dimIds": ["uc01_col_production_plan", "uc01_col_actual_path", "uc01_col_correlated_timeline"],
    "showIds": [],
    "hideIds": []
  },
  // ... weitere Steps
]
```

---

## 🎨 Design-Überlegungen

### Farben (ORBIS-CI):
- **Business Events:** `--orbis-blue-strong` (blau)
- **Production Plan:** `--orbis-grey-medium` (grau, da theoretisch)
- **Actual Path:** `--highlight-green-strong` (grün, da real)
- **Correlated Timeline:** `--orbis-blue-light` (hellblau)
- **NFC-Tag:** `--highlight-green-strong` (grün, hervorgehoben)
- **Abweichungen:** `--microsoft-orange-medium` (orange, Warnung)

### Icons:
- Supplier: `supplier.svg` (falls vorhanden) oder `customer.svg`
- Warehouse: `hbw-station.svg`
- Customer: `customer.svg`
- Production Order: `heading-production.svg`
- Stationen: `drill-station.svg`, `aiqs-station.svg`, `dps-station.svg`
- FTS: `agv-vehicle.svg`
- NFC: `nfc-tag.svg` (falls vorhanden) oder `order-tracking.svg`

### Verbindungslinien:
- **Gestrichelt:** `stroke-dasharray="5,5"`
- **Farbe:** `--orbis-blue-light` (50% Opacity)
- **Dicke:** 2px

---

## 📋 Implementierungs-Checkliste

### Phase 1: Struktur & Basis
- [ ] `uc-01-structure.config.ts` erstellen
- [ ] Column-Definitionen (4 Columns)
- [ ] Lane-Definitionen pro Column
- [ ] Chip-Definitionen pro Lane
- [ ] Verbindungslinien-Definitionen

### Phase 2: SVG-Generator
- [ ] `uc-01-svg-generator.service.ts` erstellen
- [ ] Column-Rendering
- [ ] Lane-Rendering
- [ ] Chip-Rendering
- [ ] Verbindungslinien-Rendering
- [ ] Timeline-Rendering mit Nummerierung

### Phase 3: I18n
- [ ] `uc-01-i18n.service.ts` erstellen
- [ ] I18n-Keys in `messages.de.json` hinzufügen
- [ ] I18n-Keys in `messages.fr.json` hinzufügen
- [ ] Keys in `public/locale/` kopieren

### Phase 4: Component
- [ ] `track-trace-genealogy-use-case.component.ts` erstellen
- [ ] Template mit Header, Controls, SVG-Container
- [ ] Step-Animation-Logik
- [ ] Zoom-Funktionalität
- [ ] Auto-Play, Loop

### Phase 5: Steps-Definition
- [ ] `uc-01-track-trace-genealogy.steps.json` erstellen
- [ ] 7-8 Steps definieren
- [ ] Highlight/Dim-IDs pro Step
- [ ] DE/EN/FR Beschreibungen

### Phase 6: Routing & Integration
- [ ] Route `dsp/use-case/track-trace-genealogy` in `app.routes.ts`
- [ ] `detailRoute` in `DspUseCasesComponent` für `track-trace-genealogy`
- [ ] Settings-Tab Link (optional)

---

## 🔄 Unterschiede zu UC-06

### Ähnlichkeiten:
- ✅ Column-basierte Struktur
- ✅ Dynamische SVG-Generierung
- ✅ Step-Animation
- ✅ I18n-Support

### Unterschiede:
- ❌ **Keine DSP-Steps** (Normalize, Enrich, Correlate)
- ✅ **Verbindungslinien zwischen Columns** (gestrichelt)
- ✅ **Timeline mit Nummerierung** (1, 2, 3, ...)
- ✅ **Zwei parallele Pfade:** Plan vs. Actual
- ✅ **NFC-Tag als zentrales Element** (hervorgehoben)

---

## 📝 Nächste Schritte

1. **Bestätigung des Vorschlags** durch User
2. **Detaillierte Struktur-Definition** (Column-Positionen, Lane-Höhen, Chip-Positionen)
3. **Icon-Mapping** (welche Icons für welche Elemente)
4. **Steps-Definition finalisieren**
5. **Implementierung starten**

---

*Letzte Aktualisierung: 29.01.2026*
