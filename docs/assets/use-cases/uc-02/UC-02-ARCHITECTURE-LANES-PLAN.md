# UC-02: Architecture Lanes — Analyse und Implementierungsplan

**Erstellt:** 2026-02-11  
**Vorlage:** `UC-02_3-Data-Pools_Architecture_Lanes.drawio`  
**Ziel:** Alternative Detail-View mit horizontalen Lanes (analog DSP-Architecture), ggf. als Variante/Toggle zur Concept-View.

---

## 1. Warum Architecture Lanes?

Die **Architecture Lanes**-Variante entspricht der Struktur des **DSP-Architecture**-Diagramms:

- **3 horizontale Lanes** (oben → unten): Analytics → DSP → Data
- **Mittlere Lane = DSP-Layer** (Context Model & Mediation) — wie im DSP-Architecture der `layer-dsp`
- Nutzer, die das DSP-Architecture-Diagramm bereits kennen, erkennen die gleiche **Lane-Struktur** wieder
- Intuitiv: „Oben = Wertschöpfung, Mitte = Vermittlung, unten = Datenquellen“

### Vergleich Concept vs. Architecture Lanes

| Aspekt           | Concept View                         | Architecture Lanes                               |
|------------------|--------------------------------------|--------------------------------------------------|
| Layout           | Links → Mitte → Rechts (Columns)     | Oben → Mitte → Unten (Lanes)                     |
| DSP-Position     | Mitte, vertikal (Sources\|DSP\|Targets) | Mittlere Lane (horizontal)                       |
| Parallele zu     | UC-06 (Interoperability)             | DSP-Architecture (Functional/Component View)      |
| Datenfluss       | Explizit horizontal (→)              | Vertikal (↓ Data → DSP, ↑ DSP → Analytics)       |
| Stärke           | Klarer sequentieller Fluss           | Architektur-Perspektive, Konsistenz mit DSP-Tab  |

---

## 2. Draw.io-Struktur (Architecture Lanes)

### Lane 1: Analytics & Value Layer (oben)

| Element-ID         | Typ          | Beschreibung        | Koordinaten (Draw.io)   |
|--------------------|--------------|---------------------|-------------------------|
| `9oTQZn78OOP3f05FhnRS-11` | rounded rect | Lane Container       | x=34, y=50, w=760, h=160 |
| `9oTQZn78OOP3f05FhnRS-12` | rounded rect | Analytics & AI App   | x=134, y=100, w=140, h=80 |
| `9oTQZn78OOP3f05FhnRS-14` | cloud        | BI / Data Lake       | x=334, y=95, w=140, h=90 |
| `9oTQZn78OOP3f05FhnRS-15` | rounded rect | Closed Loop / ERP    | x=540, y=100, w=140, h=80 |

**Farben:** Fill #ffe6cc, Stroke #d79b00 (`diagram.targetAnalyticsFill/Stroke`)

### Lane 2: DSP Context Model & Mediation (mitte)

| Element-ID         | Typ     | Beschreibung   | Koordinaten (Draw.io)     |
|--------------------|---------|----------------|---------------------------|
| `9oTQZn78OOP3f05FhnRS-1`  | rounded | Lane Container | x=40, y=230, w=760, h=160 |
| `9oTQZn78OOP3f05FhnRS-2`  | step    | 1. Normalize   | x=130, y=284, w=160, h=60  |
| `9oTQZn78OOP3f05FhnRS-3`  | step    | 2. Enrich      | x=330, y=284, w=160, h=60 |
| `9oTQZn78OOP3f05FhnRS-4`  | step    | 3. Correlate   | x=530, y=284, w=160, h=60 |
| `9oTQZn78OOP3f05FhnRS-25` | note    | Order ↔ Werkstück-ID ↔ Station | x=690, y=240, w=100, h=50 |

**Farben:** Fill #dae8fc, Stroke #6c8ebf (`diagram.laneTraceFill/Stroke`)

### Lane 3: Data Layer (unten)

| Element-ID         | Typ          | Beschreibung     | Koordinaten (Draw.io)   |
|--------------------|--------------|------------------|-------------------------|
| `9oTQZn78OOP3f05FhnRS-7`  | rounded rect | Lane Container   | x=40, y=411, w=760, h=160 |
| `9oTQZn78OOP3f05FhnRS-9`  | cylinder3    | Shopfloor Data   | x=150, y=461, w=120, h=80 |
| `9oTQZn78OOP3f05FhnRS-8`  | cylinder3    | Business Data    | x=350, y=461, w=120, h=80 |
| `9oTQZn78OOP3f05FhnRS-10` | cylinder3    | Environment Data | x=550, y=456, w=120, h=80 |

**Farben:** Shopfloor #f5f5f5/#666666, Business #d5e8d4/#82b366, Environment #e1d5e7/#9673a6

### Connections

| Von            | Nach         | Beschreibung                         |
|----------------|-------------|--------------------------------------|
| Shopfloor Data | Normalize   | Vertikal (y: unten → oben)           |
| Business Data  | Enrich      | Vertikal                             |
| Environment    | Enrich + Correlate | Vertikal (geteilt)         |
| Correlate      | Analytics, BI, Closed Loop | Horizontal (oben)   |
| Closed Loop    | Business Data | Feedback (gestrichelt, rechts)       |

---

## 3. Semantische IDs für SVG (Architecture Lanes)

| Draw.io-ID        | Semantische ID          | Beschreibung                |
|-------------------|-------------------------|-----------------------------|
| Lane 1 Container  | `uc02_lanes_layer_analytics` | Analytics & Value Layer |
| Analytics & AI    | `uc02_tgt_analytics`    | (bereits Concept)          |
| BI / Data Lake    | `uc02_tgt_bi`           | (bereits Concept)          |
| Closed Loop / ERP | `uc02_tgt_closed_loop`  | (bereits Concept)          |
| Lane 2 Container  | `uc02_lanes_layer_dsp`  | DSP Context Model          |
| Step Normalize    | `uc02_step_normalize`   | (bereits Concept)          |
| Step Enrich       | `uc02_step_enrich`      | (bereits Concept)          |
| Step Correlate    | `uc02_step_correlate`   | (bereits Concept)          |
| Note Context     | `uc02_note_context`     | (bereits Concept)          |
| Lane 3 Container  | `uc02_lanes_layer_data` | Data Layer                 |
| Business Data     | `uc02_src_business`     | (bereits Concept)          |
| Shopfloor Data    | `uc02_src_shopfloor`    | (bereits Concept)          |
| Environment Data  | `uc02_src_env`          | (bereits Concept)          |
| Feedback          | `uc02_edge_feedback`    | (bereits Concept)          |

---

## 4. Implementierungsoptionen

### Option A: Toggle zwischen Concept und Architecture Lanes

- Zwei Views in derselben Detail-Page (z. B. Tabs oder Radio: „Concept“ | „Architecture“)
- Beide nutzen dieselbe Steps-Logik; nur die SVG-Generierung wechselt (`Uc02SvgGeneratorConceptService` vs. `Uc02SvgGeneratorLanesService`)
- I18n-Keys bleiben gleich

### Option B: Separate Route

- Route z. B. `dsp/use-case/three-data-pools/lanes`
- Eigenes Sub-Component oder gleiche Component mit Query-Param `?view=lanes`

### Option C: Architecture Lanes als Standard ersetzen

- Concept-View entfernen oder als „Alternative“ hinterlegen
- Architecture Lanes wird zur Standard-View (näher an DSP-Architecture)

**Empfehlung:** Option A (Toggle) — Nutzer können je nach Kontext zwischen Konzept-Fluss und Architektur-Perspektive wechseln.

---

## 5. Animation Steps (Architecture Lanes)

Steps können analog zur Concept-View bleiben, da dieselben semantischen IDs verwendet werden:

| Step | Titel                 | Highlight (Beispiele)                              |
|------|------------------------|----------------------------------------------------|
| 0    | Übersicht              | `uc02_lanes_layer_analytics`, `uc02_lanes_layer_dsp`, `uc02_lanes_layer_data` |
| 1    | Business-Daten         | `uc02_src_business`, Verbindung zu Enrich          |
| 2    | Shopfloor-Daten        | `uc02_src_shopfloor`, Verbindung zu Normalize     |
| 3    | Umwelt-Daten           | `uc02_src_env`, Verbindungen zu Enrich/Correlate  |
| 4    | Kontextmodell          | `uc02_lanes_layer_dsp`, `uc02_note_context`       |
| 5    | Outcomes               | `uc02_tgt_analytics`, `uc02_tgt_bi`, `uc02_tgt_closed_loop` |
| 6    | Closed Loop            | `uc02_edge_feedback`, `uc02_tgt_closed_loop`, `uc02_src_business` |

---

## 6. Koordinaten-Transformation (Draw.io → ViewBox 1920×1080)

Draw.io: 827×1169. Skalierung für 1920×1080:

- `scaleX = 1920 / 827 ≈ 2.32`
- `scaleY = 1080 / 1169 ≈ 0.92`

Alternativ: fixe Proportionen beibehalten und ViewBox an Draw.io anpassen (z. B. 827×1169), dann per CSS skalieren.

Oder: manuell angepasstes Layout für 1920×1080 (wie bei Concept-Implementierung).

---

## 7. Nächste Schritte (bei Umsetzung)

1. `uc-02-structure-lanes.config.ts` anlegen — Struktur für 3 Lanes
2. `Uc02SvgGeneratorLanesService` implementieren — SVG aus Lane-Struktur
3. Component um View-Toggle erweitern (Concept vs. Lanes)
4. Steps-JSON ggf. um `view: 'lanes'`-spezifische IDs ergänzen (falls abweichend)
5. Manueller Test beider Views

---

*Letzte Aktualisierung: 2026-02-11*
