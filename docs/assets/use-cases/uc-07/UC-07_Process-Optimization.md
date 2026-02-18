# UC-07 — Process Optimization: KPI-to-Action Loop (A3)

## Status
- Owner: @<Oliver Berger>
- Scope-Tag: OSF-BLOG-2026
- Messe-Tag: LOGIMAT
- Referenziert in: A3 (DE/EN Draft) #69081
- Feature: #69068
- Implementiert: OSF Use-Case-Bibliothek (18.02.2026)

---

## DE

### Titel
Process Optimization: Von KPIs zu kontinuierlicher Prozessverbesserung

### One-liner
Prozessoptimierung wird erst wirksam, wenn **KPIs und Prozessdaten** zu **analysierten Engpässen**, **AI-Empfehlungen** und **simulierten Maßnahmen** führen – mit optionaler Ausführung über DSP und MES.

### Kundennutzen (3)
- **Systematische Engpass-Analyse** statt Einzelmaßnahmen (Bottleneck, Zykluszeit, Takt)
- **AI-gestützte Empfehlungen** für Parameter, Reihenfolge und Nutzung
- **What-if-Simulation** vor physischen Änderungen – risikoarm optimieren

### Pain Points (3)
- KPIs sind sichtbar, aber **ohne Folgeaktion** (Daten bleiben Zahlen)
- Engpässe werden **manuell** identifiziert – keine systematische RCA
- Änderungen erfolgen **ohne Vorab-Simulation** – Risiko von Fehlentscheidungen

### Datenquellen
- **Business-Kontext:** Produktionsaufträge, Pläne, Material, Kundenaufträge
- **Shopfloor:** Zykluszeiten, Maschinenstatus, DRILL/MILL/AIQS/FTS/HBW-Events, Qualitätsdaten
- **Optional:** Umwelt-/Sensordaten (Energie, Vibration) aus UC-02/UC-05

### KPI/Outcome-Bezug
OEE, Durchlaufzeit, WIP, Taktstabilität, Maschinenauslastung, Energie pro Werkstück, FPY

### Orchestrierung / Systeminteraktion (Optimization Loop)
**Obere Ebene – Prozess (Optimization Loop):**
1) **Observe:** KPIs, Zykluszeiten, Maschinennutzung (aus UC-02/UC-06)
2) **Analyze:** Bottleneck-Analyse, Engpassindikatoren, Root-Cause-Indikatoren
3) **Recommend:** AI-Empfehlungen (Parameter, Reihenfolge, Takt)
4) **Simulate:** What-if-Szenarien vor physischer Umsetzung
5) **Execute:** DSP Executors, MES-Workflows, Parameter-Anpassung
6) **Feedback:** Verbesserte KPIs → erneuter Observe-Schritt (geschlossener Kreis)

**Zentrale Ebene – DSP:**
- Analytics-Engine, Bottleneck-Analyse, Kontextanreicherung
- Recommendation-Service (AI-gestützt)
- Simulation-Orchestrierung
- Execution-Governance

**Untere Ebene – Shopfloor & Zielsysteme:**
- **Quellen:** DRILL, MILL, AIQS, FTS, HBW (Events, Zykluszeiten, Status)
- **Ziele:** MES, ERP, Planning (Best-of-Breed)

**Kernmessage (muss sichtbar sein):**
„KPI-Transparenz wird wirksam, wenn daraus systematische Optimierung entsteht – Observe → Analyze → Recommend → Simulate → Execute → Feedback“

### Demonstrator vs produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. UC-07 zeigt das Prinzip des KPI-to-Action-Loops; produktive Implementierungen erfolgen kundenspezifisch (Analytics-Plattform, MES/ERP, Simulation-Tools).

### CTA
KPI-to-Action Workshop (Priorisierte KPIs, Kontext-Keys, Maßnahmenableitung, Closed Loops)

### Visuals (Einbindung)
#### Visual 1: UC-07 Konzept-Diagramm (SVG-Animation in OSF)
- Datei/Link: OSF Use-Case-Bibliothek → `dsp/use-case/process-optimization`
- Caption DE: Process Optimization verbindet KPIs, Analyse, Empfehlung, Simulation und Ausführung in einem geschlossenen Regelkreis.
- Alt-Text DE: Diagramm zeigt Observe → Analyze → Recommend → Simulate → Execute → Feedback mit DSP und Shopfloor-Quellen/Zielen.

### Screen Spec / Implementation Notes (OSF)
- UC-07 ist in der **Use-Case-Bibliothek** implementiert (Step-Animation, DE/EN)
- Layout: Prozess-Loop analog UC-04/05 (6 Schritte horizontal)
- Export: `node scripts/export-use-case-svgs.js` für statische SVGs

---

## EN

### Title
Process Optimization: KPI-to-Action Loop

### One-liner
Process optimization becomes effective when **KPIs and process data** lead to **bottleneck analysis**, **AI recommendations**, and **simulated actions**—with optional execution via DSP and MES.

### Benefits (3)
- **Systematic bottleneck analysis** instead of ad-hoc measures (cycle time, takt, utilization)
- **AI-backed recommendations** for parameters, sequence, and utilization
- **What-if simulation** before physical changes—optimize with reduced risk

### Pain points (3)
- KPIs are visible but **no follow-up action** (data remains numbers)
- Bottlenecks are identified **manually**—no systematic RCA
- Changes are made **without prior simulation**—risk of poor decisions

### Data sources
- **Business context:** production orders, plans, material, customer orders
- **Shopfloor:** cycle times, machine states, DRILL/MILL/AIQS/FTS/HBW events, quality data
- **Optional:** environment/sensor data (energy, vibration) from UC-02/UC-05

### KPI/Outcome
OEE, lead time, WIP, takt stability, machine utilization, energy per unit, FPY

### Orchestration / interaction (Optimization Loop)
**Top layer — Process (optimization loop):**
1) **Observe:** KPIs, cycle times, machine utilization (from UC-02/UC-06)
2) **Analyze:** bottleneck analysis, constraint indicators, root-cause indicators
3) **Recommend:** AI recommendations (parameters, sequence, takt)
4) **Simulate:** what-if scenarios before physical changes
5) **Execute:** DSP executors, MES workflows, parameter updates
6) **Feedback:** improved KPIs → back to Observe (closed loop)

**Middle layer — DSP:**
- Analytics engine, bottleneck analysis, context enrichment
- Recommendation service (AI-backed)
- Simulation orchestration
- Execution governance

**Bottom layer — Shopfloor & targets:**
- **Sources:** DRILL, MILL, AIQS, FTS, HBW (events, cycle times, status)
- **Targets:** MES, ERP, Planning (best-of-breed)

**Core message (must be explicit):**
"KPI transparency becomes effective when systematic optimization follows—Observe → Analyze → Recommend → Simulate → Execute → Feedback"

### Demonstrator vs productive solution (mandatory)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. UC-07 illustrates the KPI-to-action loop; productive implementations are customer-specific (analytics platform, MES/ERP, simulation tools).

### CTA
KPI-to-Action Workshop (prioritized KPIs, context keys, action derivation, closed loops)

### Visuals
#### Visual 1: UC-07 concept diagram (SVG animation in OSF)
- File/Link: OSF Use-Case Library → `dsp/use-case/process-optimization`
- Caption EN: Process optimization connects KPIs, analysis, recommendation, simulation, and execution in a closed loop.
- Alt text EN: Diagram showing Observe → Analyze → Recommend → Simulate → Execute → Feedback with DSP and shopfloor sources/targets.
