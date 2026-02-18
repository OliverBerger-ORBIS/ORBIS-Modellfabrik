# UC-07: Process Optimization – Analyse und Layout-Vorschlag

**Erstellt:** 18.02.2026  
**Status:** Vorschlag zur Freigabe

---

## 1. Executive Summary

UC-07 Process Optimization ist als **Meta-Use-Case** positioniert: Er baut auf UC-02 (Data Aggregation/3 Datentöpfe), UC-06 (Interoperability/Event-to-Process) sowie UC-04/05 (Closed Loops) auf und zeigt, wie aus **KPI-Transparenz und Prozessdaten** **kontinuierliche Optimierung** wird. Er füllt die Lücke zwischen „Beobachten“ und „Orchestrieren“ und passt in **Phase 4 (Automation & Orchestration)** des ORBIS-Vorgehensmodells (A1).

**Empfohlenes Layout:** **Horizontale Prozess-Spirale** (Optimization Loop) analog UC-04/05 – mit eigenem Fokus auf Observe → Analyze → Recommend → Simulate → Execute → Feedback. DSP bleibt in der Mitte als Vermittler.

---

## 2. Analyse der bestehenden Use-Cases

### 2.1 Übersicht und thematische Zuordnung

| UC | Name | Fokus | Layout-Typ | Blog-Artikel |
|----|------|-------|------------|--------------|
| UC-01 | Track & Trace Genealogie | Objekt-Historie, Plan vs. Ist | Partitur (Lanes) | A2 |
| UC-02 | Three Data Pools | Datenaggregation, KPIs | 3 Columns (Sources→DSP→Targets) | A3 |
| UC-03 | AI Lifecycle | ML-Training, Rollout, Feedback | 3 Layers (Process→DSP→Shopfloor) | A4 (Visual 1) |
| UC-04 | Closed Loop Quality | Detect→Decide→Act→Feedback | Process Loop + DSP + Shopfloor | A4 |
| UC-05 | Predictive Maintenance | Sensor→Alarm→(optional) Aktion | Process Loop + DSP + Shopfloor | A4 |
| UC-06 | Interoperability | Event-to-Process, Kontext | 3 Columns (Sources→DSP→Targets) | A1 |

### 2.2 Lücke, die UC-07 füllt

- **UC-02:** Liefert KPIs, Kontextmodell, OEE, Durchlaufzeit – aber keine **Folgeaktion** aus den KPIs.
- **UC-04/05:** Zeigen **reaktive** Closed Loops (Qualitätsereignis, Alarm).
- **UC-07:** Zeigt **proaktive, kontinuierliche** Optimierung: KPIs und Prozessdaten führen zu **Empfehlungen**, **Simulationen** und **ausgeführten Verbesserungen**.

**Kernmessage UC-07:**  
„KPI-Transparenz wird wirksam, wenn daraus **Systematische Optimierung** entsteht – Bottleneck-Analyse, AI-Empfehlungen, What-if-Simulation, DSP- und MES-Execution.“

---

## 3. Analyse der Use-Case-Asset-Beschreibungen

### 3.1 UC-Asset-Struktur (Referenz UC-04, UC-05)

Die bestehenden UC-Assets haben ein einheitliches Muster:

- **Titel / One-liner**
- **Kundennutzen (3)** – Pain Points (3)
- **Datenquellen** – Business, Shopfloor, optional Umwelt
- **KPI/Outcome-Bezug**
- **Orchestrierung / Systeminteraktion** – Layer-Logik
- **Demonstrator vs. produktive Lösung**
- **CTA**
- **Visuals / Screen Spec**

### 3.2 Inhalte aus `dsp-use-cases.component.ts` (UC-07)

| Kategorie | Inhalt |
|-----------|--------|
| **Actions** | Event-driven process control, Dynamic production planning, Autonomous system responses, Continuous process improvement |
| **Smart Factory** | Bottleneck/cycle-time analysis (DRILL, MILL, AIQS, FTS, HBW); Optimization of utilization, takt, conveyor flow; Energy/resource optimization; AI recommendations (feed rate, spindle speed); What-if simulation; Closed-loop improvements via DSP executors and MES/DSP workflows |

### 3.3 Ableitung für UC-07-Asset (Vorschlag)

**One-liner (DE):**  
Prozessoptimierung wird erst wirksam, wenn **KPIs und Prozessdaten** zu **analysierten Engpässen**, **AI-Empfehlungen** und **simulierten Maßnahmen** führen – mit optionaler Ausführung über DSP und MES.

**Orchestrierung (Layer-Logik):**

- **Obere Ebene – Prozess (Optimization Loop):**
  1. **Observe:** KPIs, Zykluszeiten, Maschinennutzung (aus UC-02/UC-06)
  2. **Analyze:** Bottleneck-Analyse, Engpassindikatoren, RCA
  3. **Recommend:** AI-Empfehlungen (Parameter, Reihenfolge, Takt)
  4. **Simulate:** What-if-Szenarien vor physischer Umsetzung
  5. **Execute:** DSP Executors, MES-Workflows, Parameter-Anpassung
  6. **Feedback:** Verbesserte KPIs → erneuter Observe-Schritt (geschlossener Kreis)

- **Mitte – DSP:** Analytics-Engine, Recommendation-Service, Simulation-Orchestration, Execution-Governance  
- **Unten – Shopfloor & Zielsysteme:** DRILL, MILL, AIQS, FTS, HBW; MES/ERP für Planung und Rückmeldung

---

## 4. Einordnung in die Blog-Serie

### 4.1 Aktuelle Artikel-Zuordnung

| Artikel | Use-Cases | Fokus |
|---------|-----------|-------|
| A1 | UC-06 | Interoperabilität als Fundament |
| A2 | UC-01 | Track & Trace Genealogie |
| A3 | UC-02 | 3 Datentöpfe für KPIs |
| A4 | UC-03, UC-04, UC-05 | Closed Loops Qualität & Maintenance |

### 4.2 Wo passt UC-07 rein?

**Option A: Eigenständiger Artikel A5**  
- „Von KPIs zu Wirkung: Prozessoptimierung als kontinuierlicher Regelkreis“  
- Eigenständiger Artikel für Phase 4 des Vorgehensmodells

**Option B: Erweiterung von A4**  
- A4 behandelt Closed Loops – UC-07 ist ein **weiterer Closed Loop** (Optimization Loop)  
- Erweiterung um Abschnitt „6. Process Optimization: KPI-zu-Aktion als Regelkreis“

**Option C: Erweiterung von A3**  
- A3 endet mit „KPI-to-Action Workshop“ – UC-07 zeigt genau das  
- Ergänzung um Visual/Verweis: „UC-07 Process Optimization visualisiert den KPI-to-Action-Flow“

**Empfehlung:**  
- **Kurzfristig:** Option C – UC-07 als visuelle Ergänzung zu A3 (KPIs → Aktion). A3 CTA „KPI-to-Action Workshop“ passt 1:1.  
- **Mittelfristig:** Option A – A5 als eigenständiger Artikel, sobald UC-07 implementiert und der Use-Case-Bibliothek etabliert ist.

---

## 5. Layout-Vorschlag für UC-07

### 5.1 Layout-Varianten im Vergleich

| Variante | Beschreibung | Pro | Contra |
|----------|--------------|-----|--------|
| **A: 3-Column** (wie UC-02/06) | Sources (KPIs) → DSP (Analyze/Recommend/Simulate) → Targets (Executors) | Konsistent mit UC-02/06, gute Wiederverwendbarkeit | Zeigt den **Regelkreis** weniger deutlich |
| **B: Prozess-Loop** (wie UC-04/05) | Horizontaler Loop: Observe→Analyze→Recommend→Simulate→Execute→Feedback | Regelkreis klar sichtbar, „kontinuierliche Verbesserung“ | Etwas komplexer durch 6 Schritte |
| **C: Layer-View** (wie UC-03) | Oben: Loop; Mitte: DSP; Unten: Quellen + Ziele | Klar getrennte Ebenen | Kann überladen wirken |

### 5.2 Empfehlung: **Variante B – Prozess-Loop (Optimization Loop)**

**Begründung:**

1. **UC-07 ist ein Closed Loop** – wie UC-04 und UC-05. Das Loop-Pattern ist konzeptionell passend.
2. **„Kontinuierliche Optimierung“** wird durch den Feedback-Pfeil zum Observe-Schritt visuell erkennbar.
3. **Bestehende Implementierungsmuster** (UC-04, UC-05) können wiederverwendet werden (Process Layer, DSP Layer, Shopfloor Layer).
4. **Step-Animation:** Jeder Prozessschritt kann als eigener Step hervorgehoben werden – gut für die Use-Case-Bibliothek.

### 5.3 Konkrete Layout-Spezifikation

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Process Layer (Highlight-Green) – Optimization Loop                                │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────┐│
│  │ Observe  │ → │ Analyze  │ → │ Recommend│ → │ Simulate │ → │ Execute  │ → │Feedb.││
│  └────┬─────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──┬──┘│
│       │                                                                        │    │
│       └────────────────────────────────────────────────────────────────────────┘    │
│                                    (Rückkopplung)                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  DSP Layer (Blau)                                                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                     │
│  │ Analytics /     │  │ Recommendation  │  │ Simulation &     │                     │
│  │ Bottleneck       │  │ Service (AI)   │  │ Execution Gov.   │                     │
│  │ Analysis         │  │                │  │                  │                     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  Shopfloor Layer (Grau) – Quellen & Ziele                                            │
│  DRILL | MILL | AIQS | FTS | HBW    ←→    MES | ERP | Planning                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Step-Animation (Vorschlag für steps.json)

| Step | ID | Titel (EN) | Beschreibung (Kern) |
|------|----|-----------|----------------------|
| 0 | uc07-00-overview | Overview | Optimization Loop, DSP, Shopfloor |
| 1 | uc07-01-observe | Observe | KPIs, cycle times, machine data from 3 Data Pools |
| 2 | uc07-02-analyze | Analyze | Bottleneck analysis, root-cause indicators |
| 3 | uc07-03-recommend | Recommend | AI recommendations (parameters, sequence, takt) |
| 4 | uc07-04-simulate | Simulate | What-if scenarios before physical changes |
| 5 | uc07-05-execute | Execute | DSP executors, MES workflows, parameter updates |
| 6 | uc07-06-feedback | Feedback | Improved KPIs feed back into Observe |

**Connection-IDs:** Analog UC-04/05 – Verbindungen zwischen Process-Schritten und DSP/Shopfloor für `dim-conn` bei Fokus auf einem Step.

---

## 6. Abgrenzung zu anderen Use-Cases

| Aspekt | UC-02 | UC-04/05 | UC-07 |
|--------|-------|----------|-------|
| **Fokus** | Daten aggregieren, KPIs berechnen | Reagieren auf Ereignis/Alarm | Proaktiv optimieren |
| **Trigger** | Kontinuierlich (Streams) | Einzelereignis (Quality/Alarm) | Kontinuierlich + Batch-Analyse |
| **Aktion** | Keine direkte Aktion | Sperre, Nacharbeit, Stop | Parameter-Anpassung, Plan-Update |
| **Feedback** | Optional (Closed Loop im UC-02-Step 6) | Explizit (MES/ERP) | KPIs → Observe (Loop) |

---

## 7. Implementierungs-Checkliste (Kurz)

1. **Ordner:** `osf/.../use-cases/process-optimization/`
2. **Dateien:** Component, `uc-07-structure.config.ts`, `uc-07-svg-generator.service.ts`, `uc-07-i18n.service.ts`
3. **Steps:** `assets/use-cases/uc-07/uc-07-process-optimization.steps.json`
4. **Routing:** `process-optimization` in `use-case.routes.ts`
5. **DspUseCasesComponent:** `detailRoute: '/dsp/use-case/process-optimization'` ergänzen
6. **UseCaseSelectorPageComponent:** Karte hinzufügen
7. **UC-Asset:** `docs/assets/use-cases/uc-07/UC-07_Process-Optimization.md` (analog UC-04)
8. **Inventory:** Zeile in use-case-inventory.md + Abschnitt UC-07

---

## 8. Zusammenfassung

| Frage | Antwort |
|-------|---------|
| **Wo passt UC-07 thematisch?** | Phase 4 (Automation & Orchestration); baut auf UC-02, UC-06, UC-04/05 auf. |
| **Wo in der Blog-Serie?** | Kurzfristig A3 (KPI-to-Action); mittelfristig A5 (eigenständig). |
| **Empfohlenes Layout** | **Prozess-Loop** (Observe→Analyze→Recommend→Simulate→Execute→Feedback) analog UC-04/05. |
| **Steps** | 7 Steps (Overview + 6 Prozessschritte). |
| **Connection-IDs** | Ja, analog UC-04/05 für dim-conn. |

---

*Referenzen: [use-case-inventory.md](../../02-architecture/use-case-inventory.md), [use-case-library.md](../../02-architecture/use-case-library.md), [UC-DIAGRAM-IMPLEMENTATION-GUIDE.md](../UC-DIAGRAM-IMPLEMENTATION-GUIDE.md)*
