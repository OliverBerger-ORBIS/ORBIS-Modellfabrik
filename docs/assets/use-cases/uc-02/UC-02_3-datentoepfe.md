# UC-02 — 3 Datentöpfe (A3)

## Status
- Owner: @<Oliver Berger>
- Scope: OSF-BLOG-2026
- Messe-Tag: LOGIMAT
- Referenziert in: A3 (DE/EN Draft) #69081
- Feature: #69068
- **STATUS: KONZEPT FINALISIERT** (Stand: 2026-02-06)
  - Konzept und Artikel A3 sind synchronisiert.
  - Visuals liegen bereit (PNG).

---

## DE

**Titel:** Datenaggregation: 3 Datentöpfe für belastbare KPIs  
**One-liner:** Business + Shopfloor + Umwelt: erst die Kombination macht KPIs erklärbar und steuerbar.

**Kundennutzen (3):**
- Verlässliche KPI-Transparenz (OEE, Qualität, Durchsatz, Energie)
- Kontextbasierte Ursachenanalyse statt isolierter Messwerte
- Grundlage für skalierbare Analytics/AI ohne Insellösungen

**Pain Points (3):**
- KPI-Diskussionen ohne gemeinsame Datenbasis („Welche Zahl stimmt?“)
- OT-Daten ohne Business-Kontext (Order/Material/Plan) → KPIs nicht erklärbar
- Umwelt-/Sensordaten werden nicht genutzt oder nicht korreliert → blinde Flecken

**Datenquellen:**
- **Business:** Kundenaufträge, Produktionspläne, Material/Chargen, Stammdaten, Supplier/PO-Entities
- **Shopfloor:** Events, Zustände, Parameter, Qualitätsresultate (AIQS), FTS-Transfers, Lagerbewegungen
- **Umwelt/Sensorik:** Temperatur/Feuchte/Luftqualität/Energie (optional: Vibration)

**KPI/Outcome-Bezug:** OEE, Stillstandsgründe, FPY, Energie pro Werkstück/Los, Durchlaufzeit/WIP, Traceability Coverage (als Enabler)  
**Orchestrierung / Systeminteraktion (DSP):**  
- **Normalize:** Semantik und Formate harmonisieren  
- **Enrich:** Kontext anreichern (Order, Werkstück/NFC, Station, Zeit)  
- **Correlate:** Events zu Prozessschritten verbinden  
DSP stellt die Daten zielsystemoffen für BI/Analytics/AI bereit (Best-of-Breed; SAP als Beispiel) und ermöglicht optional Rückkopplungen (Closed Loop).  
**Demonstrator vs produktive Lösung (Pflicht):**  
„Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. Die dargestellten Use Cases sind konzeptionell und werden je nach Systemlandschaft (ERP/MES/Analytics) kundenspezifisch umgesetzt.“  
**CTA:** KPI Readiness Check (Workshop)  
**Caption:** Drei Datenwelten werden zu einem gemeinsamen Kontextmodell verbunden – als Grundlage für KPIs, Analytik und AI.  
**Alt-Text:** Diagramm, das Business-, Shopfloor- und Umweltdaten in ein gemeinsames Kontextmodell und KPI/Analytics-Ergebnisse zusammenführt.

---

## EN

**Title:** Data Aggregation: Three Data Pools for Reliable KPIs  
**One-liner:** Business + shopfloor + environment: only the combination makes KPIs explainable and actionable.

**Benefits (3):**
- Reliable KPI transparency (OEE, quality, throughput, energy)
- Context-based root-cause analysis instead of isolated readings
- Foundation for scalable analytics/AI without one-off integrations

**Pain points (3):**
- KPI debates without a shared data foundation (“Which number is correct?”)
- OT data without business context (order/material/plan) → KPIs are not explainable
- Environment/sensor data is unused or not correlated → blind spots remain

**Data sources:**
- **Business:** customer & production orders, plans, material/batch, master data, supplier/PO entities
- **Shopfloor:** events, states, parameters, quality results (AIQS), transfers (AGV/AMR), warehouse moves
- **Environment/Sensors:** temperature/humidity/air quality/energy (optional: vibration)

**KPI/Outcome:** OEE, downtime reasons, FPY, energy per unit/batch, lead time/WIP, traceability coverage (as enabler)  
**Orchestration / interaction (DSP):**  
- **Normalize:** harmonize semantics and formats  
- **Enrich:** add context (order, workpiece/NFC, station, time)  
- **Correlate:** link events to process steps  
DSP provisions data to BI/analytics/AI (best-of-breed; SAP as an example) and optionally enables feedback (closed loop).  
**Disclaimer (required):**  
“The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual and are implemented customer-specifically depending on the target landscape (ERP/MES/analytics).”  
**CTA:** KPI readiness check (workshop)  
**Caption:** Three data worlds are unified into one context model—enabling KPIs, analytics, and AI.  
**Alt text:** Diagram combining business, shopfloor, and environment data into a shared context model and KPI/analytics outcomes.

---

## Visuals / Assets

### Visual 1: UC-02 Diagram (Concept View)
- Datei: [UC-02_3-Data-Pools_Concept.drawio](diagrams/UC-02_3-Data-Pools_Concept.drawio)
- Caption DE: Drei Datenwelten werden zu einem gemeinsamen Kontextmodell verbunden – als Grundlage für KPIs, Analytik und AI.
- Alt-Text DE: Diagramm, das Business-, Shopfloor- und Umweltdaten in ein gemeinsames Kontextmodell und KPI/Analytics-Ergebnisse zusammenführt.

### Visual 2: UC-02 Diagram (Architecture View - Lanes)
- Datei: [UC-02_3-Data-Pools_Architecture_Lanes.drawio](diagrams/UC-02_3-Data-Pools_Architecture_Lanes.drawio)
- Beschreibung: Technische Sicht in 3 Lanes.
  - Bottom: Data Pools (Sources)
  - Center: DSP Mediation (Normalize -> Enrich -> Correlate)
  - Top: Analytics & Value Targets

### Optional: OSF Proof Screenshot(s)
Hinweis: In OSF existieren bereits passende Einstiegspunkte (z. B. Orders/Environment Data/Message Monitor). Sensor-Korrelation ist für UC-02 optional und kann später ergänzt werden.
- Datei/Link DE: <optional>
- Datei/Link EN: <optional>

---

## Screen Spec / Implementation Notes (OSF-Logik: statisch jetzt, später optional SVG-Animation)

### Ziel
UC-02 visualisiert **das Konzept** „3 Datentöpfe → Kontextmodell → KPI/Analytics“, unabhängig davon, ob die vollständige Datenpipeline bereits produktiv integriert ist.

### UI-Platzierung (Empfehlung)
1) **DSP Tab → Use Cases (statische Kachel + Detailbereich)**: UC-02 als zusätzlicher Use Case wie die bestehenden Kacheln.  
2) **Use-Case Library (Wiki/Docs)**: UC-02 als Vorlage/Spec inkl. Assets.  
*(Optional später)*: In OSF unter `/use-cases/uc-02` eine dedizierte Detailansicht mit identischem Layout.

### Inhalte / Elemente (statisch modelliert)
- **Datenpool 1 (Business)**: Order/Customer/Material/Plan (inkl. PO/Supplier Entities)
- **Datenpool 2 (Shopfloor)**: Station Events, FTS Transfers, Quality (AIQS), Warehouse moves
- **Datenpool 3 (Umwelt/Sensorik)**: Temperature/Humidity/Energy (optional Vibration)
- **Shared Context Model**: Verknüpfung über IDs + Zeit + Semantik (Order ↔ Werkstück-ID (NFC) ↔ Station ↔ Time)
- **Outcomes**: KPIs, RCA, Analytics/AI enablement, optional closed loop to MES/ERP

### Farb-/Icon-Konventionen (für Konsistenz)
- Business: konsistente Farbe (wie in anderen Diagrammen)
- Shopfloor: konsistente Farbe
- Environment/Sensors: konsistente Farbe
- **AGV/Transfer** innerhalb Shopfloor immer **dieselbe Akzentfarbe** (nicht pro Screen variieren)
- Icons: vorhandene ORBIS/DSP SVG Icons wiederverwenden (keine neuen Stile einführen)

### Internationalisierung
- Alle Labels über i18n (`messages.de.json` / `messages.en.json`)
- Bild-Assets **sprachspezifisch** (DE/EN), da Labels im Bild enthalten sind

### Optional: SVG-Animation (wie DSP-Architecture Steps)
Wenn später animiert:
- **Step 0**: Alles „neutral“ (ohne Hervorhebung)
- **Step 1**: Highlight Business Pool (Quelle: Orders/Plan/Material)
- **Step 2**: Highlight Shopfloor Pool (Events/AGV/AIQS)
- **Step 3**: Highlight Environment Pool (Energy/Temp/…)
- **Step 4**: Highlight „Shared Context Model“ (Linking/Correlation)
- **Step 5**: Highlight Outcomes (KPIs/RCA/Analytics/AI)
- **Step 6 (optional)**: Highlight „Closed Loop“ (Feedback to MES/ERP)

### Done-Kriterien (für Implementierungsauftrag)
- UC-02 erscheint als statischer Use Case im DSP Tab (DE/EN)
- Assets/Diagramm sind konsistent zum ORBIS CI und übrigen Use-Case Screens
- i18n vollständig, keine Hardcodings im SVG/Text
- (Optional später) Animation Steps gemäß obigem Schema implementiert
