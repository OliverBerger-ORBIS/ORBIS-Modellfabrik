# UC-02: Analyse und Implementierungsplan

**Erstellt:** 2026-02-11  
**Ziel:** UC-02 wie UC-01 auf Basis der Draw.io-Vorlagen implementieren, Verknüpfung über Use-Case "Data Aggregation", Detail-View mit optionaler Animation.

---

## 1. Verknüpfung Data Aggregation ↔ UC-02

### Inhaltliche Prüfung

| Aspekt | DSP Use Case "Data Aggregation" (dsp-use-cases) | UC-02 (3 Datentöpfe) |
|--------|-------------------------------------------------|----------------------|
| **Titel** | Data Aggregation | Data Aggregation: Three Data Pools for Reliable KPIs |
| **Kernkonzept** | "Harmonize business, shopfloor, and sensor data for a single contextual production view" | Drei Datenwelten → gemeinsames Kontextmodell → KPIs |
| **Business** | ERP order streams, MES execution events | Orders, Plan, Material, PO/Supplier |
| **Shopfloor** | Machine telemetry, events, states | Events, FTS, Quality (AIQS), Warehouse |
| **Environment** | Temperature, humidity, air quality | Energy, Temp, Vibration (optional) |
| **Outcome** | OEE, process optimization | OEE, KPIs, RCA, Analytics/AI |
| **DSP-Rolle** | Normalize, Enrich, Correlate | Normalize, Enrich, Correlate |

**Fazit:** Die Verknüpfung passt inhaltlich. "Data Aggregation" und UC-02 sind konzeptionell identisch. Die DSP Use-Case-Kachel "Data Aggregation" ist der geeignete Einstiegspunkt für die UC-02 Detail-View.

### Empfehlung

- **Keine Änderung** an der inhaltlichen Zuordnung nötig.
- **Optional:** Die Beschreibung in `dsp-use-cases.component.ts` könnte explizit "3 Datentöpfe" erwähnen, um den Bezug zu UC-02 zu verdeutlichen (z.B. im SmartFactory-Punkt "Drei Datenwelten werden zu einem Kontextmodell verbunden" – ist bereits implizit vorhanden).

---

## 2. Draw.io-Vorlagen (Assets)

### Visual 1: Concept View (`UC-02_3-Data-Pools_Concept.drawio`)

**Layout:** Links → Mitte → Rechts

| Element-ID | Typ | Beschreibung | Koordinaten (Draw.io) |
|------------|-----|--------------|------------------------|
| `src_business` | cylinder3 | Business Data (ERP, Order, Material) | x=40, y=70, w=120, h=80 |
| `src_shopfloor` | cylinder3 | Shopfloor Data (Events, FTS, Quality) | x=40, y=179, w=120, h=80 |
| `src_env` | cylinder3 | Environment Data (Energy, Temp, Vibration) | x=40, y=280, w=120, h=80 |
| `container_dsp` | rounded rect | DSP Context Model & Mediation | x=240, y=40, w=320, h=360 |
| `7FmbLH8HXP0n9YStC2Ty-4` | step | 1. Normalize (Units, Formats) | x=300, y=80, w=200, h=80 |
| `7FmbLH8HXP0n9YStC2Ty-6` | step | 2. Enrich (Add Content) | x=300, y=190, w=200, h=80 |
| `7FmbLH8HXP0n9YStC2Ty-7` | step | 3. Correlate (Link Data) | x=300, y=300, w=200, h=80 |
| `note_enrich` | note | Order ↔ Werkstück-ID ↔ Station | x=520, y=23, w=100, h=50 |
| `tgt_a` | rounded rect | Analytics & AI App | x=640, y=73, w=140, h=80 |
| `tgt_b` | cloud | BI / Data Lake | x=640, y=179, w=140, h=90 |
| `tgt_c` | rounded rect | Closed Loop / ERP | x=640, y=300, w=140, h=80 |
| `edge_feedback` | edge | Feedback (dashed) | tgt_c → src_business |

**Hinweis:** Im Draw.io ist ein Schritt als "2. Correlate" beschriftet (sollte "3. Correlate" sein). Bei der Implementierung korrekt als 3. Correlate darstellen.

### Visual 2: Architecture Lanes (`UC-02_3-Data-Pools_Architecture_Lanes.drawio`)

**Layout:** 3 horizontale Lanes (oben → unten)

- **Lane 1 (oben):** Analytics & Value Layer — Analytics & AI App, BI / Data Lake, Closed Loop / ERP
- **Lane 2 (mitte):** DSP Context Model & Mediation — Normalize → Enrich → Correlate (horizontal)
- **Lane 3 (unten):** Data Layer — Business Data, Shopfloor Data, Environment Data (Cylinder)

**Empfehlung für Implementierung:** Concept View als Haupt-Diagramm (wie UC-06 Sources → DSP → Targets), da klarer Datenfluss und besser für Animation.

---

## 3. Farben (ORBIS_COLORS.diagram)

| Draw.io Farbe | Verwendung | ORBIS_COLORS Referenz |
|---------------|------------|------------------------|
| Business Fill #d5e8d4 | src_business | `diagram.laneBusinessFill` |
| Business Stroke #82b366 | src_business | `diagram.laneBusinessStroke` |
| Shopfloor Fill #f5f5f5 | src_shopfloor | `diagram.laneShopfloorFill` |
| Shopfloor Stroke #666666 | src_shopfloor | `diagram.laneShopfloorStroke` |
| Environment Fill #e1d5e7 | src_env | **Neu:** `diagram.laneEnvironmentFill` (ergänzen) |
| Environment Stroke #9673a6 | src_env | **Neu:** `diagram.laneEnvironmentStroke` (ergänzen) |
| DSP/Context Fill #dae8fc | container_dsp, steps | `diagram.laneTraceFill` |
| DSP Stroke #6c8ebf | container_dsp, steps | `diagram.laneTraceStroke` |
| Targets Fill #ffe6cc | tgt_a, tgt_b, tgt_c | **Neu:** `diagram.targetAnalyticsFill` oder SAP Orange |
| Targets Stroke #d79b00 | tgt_a, tgt_b, tgt_c | `statusWarning.strong` oder eigener Key |

**Ergänzung in `color-palette.ts`:**  
`laneEnvironmentFill`, `laneEnvironmentStroke` für Environment Data Pool.

---

## 4. Implementierungsvorgehen (analog UC-01 / UC-06)

### 4.1 Dateistruktur

```
osf/apps/osf-ui/src/app/pages/use-cases/
  three-data-pools/
    three-data-pools-use-case.component.ts
    three-data-pools-use-case.component.html
    three-data-pools-use-case.component.scss
    uc-02-structure.config.ts
    uc-02-svg-generator.service.ts
    uc-02-i18n.service.ts

osf/apps/osf-ui/public/assets/use-cases/
  uc-02/
    uc-02-three-data-pools.steps.json
```

### 4.2 Struktur-Konfiguration (uc-02-structure.config.ts)

Auf Basis des Concept Draw.io:

- **Sources** (links): src_business, src_shopfloor, src_env (Cylinder-ähnliche Darstellung oder Rechtecke mit ORBIS-Farben)
- **DSP** (mitte): container_dsp mit 3 Steps: Normalize, Enrich, Correlate
- **Targets** (rechts): tgt_a (Analytics & AI), tgt_b (BI / Data Lake), tgt_c (Closed Loop / ERP)
- **Note:** Order ↔ Werkstück-ID ↔ Station
- **Feedback-Connection:** gestrichelte Linie tgt_c → src_business

### 4.3 SVG-Generator (uc-02-svg-generator.service.ts)

- Generiert SVG aus `Uc02Structure` (analog `Uc06SvgGeneratorService`)
- Semantische IDs für Animation: `uc02_src_business`, `uc02_src_shopfloor`, `uc02_src_env`, `uc02_step_normalize`, `uc02_step_enrich`, `uc02_step_correlate`, `uc02_tgt_analytics`, `uc02_tgt_bi`, `uc02_tgt_closed_loop`, `uc02_note_context`, `uc02_container_dsp`

### 4.4 Animation Steps (uc-02-three-data-pools.steps.json)

Gemäß UC-02 Spec:

| Step | Titel (DE) | Highlight | Dim |
|------|------------|-----------|-----|
| 0 | Übersicht | (alle) | — |
| 1 | Business Pool | uc02_src_business, Verbindungen zu Normalize | Rest |
| 2 | Shopfloor Pool | uc02_src_shopfloor, Verbindungen zu Enrich | Rest |
| 3 | Environment Pool | uc02_src_env, Verbindungen zu Correlate | Rest |
| 4 | Shared Context Model | uc02_container_dsp, uc02_step_*, uc02_note_context | Targets |
| 5 | Outcomes | uc02_tgt_analytics, uc02_tgt_bi, uc02_tgt_closed_loop | Sources, DSP |
| 6 | Closed Loop | uc02_tgt_closed_loop, uc02_edge_feedback, uc02_src_business | Rest |

### 4.5 Routen und Verknüpfung

- **Route:** `dsp/use-case/three-data-pools`
- **DSP Use Case "Data Aggregation":** `detailRoute: '/dsp/use-case/three-data-pools'` hinzufügen

---

## 5. Änderungen im Bestand

| Datei | Änderung |
|-------|----------|
| `app.routes.ts` | Route `dsp/use-case/three-data-pools` → `ThreeDataPoolsUseCaseComponent` |
| `dsp-use-cases.component.ts` | Use Case `data-aggregation`: `detailRoute: '/dsp/use-case/three-data-pools'` |
| `color-palette.ts` | `diagram.laneEnvironmentFill`, `diagram.laneEnvironmentStroke` ergänzen |
| `_color-palette.scss` | CSS-Variablen für Environment-Lane |

---

## 6. I18n-Keys (Beispiele)

- `uc02.title`: "Data Aggregation: Three Data Pools for Reliable KPIs"
- `uc02.subtitle`: "Business + Shopfloor + Environment: only the combination makes KPIs explainable."
- `uc02.src.business`: "Business Data"
- `uc02.src.business.sub`: "ERP, Order, Material"
- `uc02.src.shopfloor`: "Shopfloor Data"
- `uc02.src.shopfloor.sub`: "Events, FTS, Quality"
- `uc02.src.env`: "Environment Data"
- `uc02.src.env.sub`: "Energy, Temp, Vibration"
- `uc02.step.normalize`: "1. Normalize"
- `uc02.step.normalize.sub`: "Units, Formats"
- `uc02.step.enrich`: "2. Enrich"
- `uc02.step.enrich.sub`: "Add Content"
- `uc02.step.correlate`: "3. Correlate"
- `uc02.step.correlate.sub`: "Link Data"
- `uc02.note.context`: "Order ↔ Werkstück-ID ↔ Station"
- `uc02.tgt.analytics`: "Analytics & AI App"
- `uc02.tgt.bi`: "BI / Data Lake"
- `uc02.tgt.closed_loop`: "Closed Loop / ERP"
- `uc02.footer`: "OSF is a demonstrator …"

---

## 7. Nächste Schritte (Reihenfolge)

1. **color-palette** um Environment-Lane-Farben erweitern
2. **Route** und **Lazy-Load** für `three-data-pools` anlegen
3. **detailRoute** für `data-aggregation` setzen
4. **uc-02-structure.config.ts** aus Draw.io-Koordinaten ableiten
5. **uc-02-svg-generator.service.ts** implementieren (analog UC-06)
6. **uc-02-i18n.service.ts** und Locale-Keys ergänzen
7. **three-data-pools-use-case.component** anlegen (Klon von interoperability)
8. **uc-02-three-data-pools.steps.json** definieren
9. **Manueller Test** der Detail-View und Animation

---

## Status der Implementierung (2026-02-11)

- **Concept View:** ✅ Implementiert (Route `dsp/use-case/three-data-pools`, Detail-View mit Animation)
- **Architecture Lanes:** 📋 Plan erstellt — siehe `UC-02-ARCHITECTURE-LANES-PLAN.md`

---

*Letzte Aktualisierung: 2026-02-11*
