# UC-02 — 3 Datentöpfe (A3)

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
- **Shopfloor:** Events, Zustände, Parameter, Qualitätsresultate (AIQS), Transfers (FTS/AGV), Lagerbewegungen
- **Umwelt/Sensorik:** Temperatur/Feuchte/Luftqualität/Energie (optional: Vibration)

**KPI/Outcome-Bezug:** OEE, Stillstandsgründe, FPY, Energie pro Werkstück/Los, Durchlaufzeit/WIP, Traceability Coverage (als Enabler)  
**Orchestrierung / Systeminteraktion:** DSP harmonisiert und kontextualisiert die Streams (Semantik + IDs + Zeit), stellt sie für BI/Analytics/AI bereit (Best-of-Breed; SAP als Beispiel) und ermöglicht optional Rückkopplungen in MES/ERP (Closed Loop).  
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
**Orchestration / interaction:** DSP harmonizes and contextualizes streams (semantics + IDs + time), provisions them to BI/analytics/AI (best-of-breed; SAP as an example) and optionally enables feedback to MES/ERP (closed loop).  
**Disclaimer (required):**  
“The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual and are implemented customer-specifically depending on the target landscape (ERP/MES/analytics).”  
**CTA:** KPI readiness check (workshop)  
**Caption:** Three data worlds are unified into one context model—enabling KPIs, analytics, and AI.  
**Alt text:** Diagram combining business, shopfloor, and environment data into a shared context model and KPI/analytics outcomes.

---

## Visuals / Assets

### Visual 1: UC-02 Diagram (DE)
- Datei/Link Vorschlag: ![UC-02-3-Data-Pools-DE.png](/.attachments/UC-02-3-Data-Pools-DE-174436e5-2ce4-4f5c-8ea5-a3eaf7319d21.png)
- potentielle Änderungen (Datentöpfe als Zylinder = Datenbank), potentiell: vermittelnde Rolle von DSP, Auswahl in Analytic-App , beliebige Cloud oder IIot-Plattform
- Caption DE: Drei Datenwelten werden zu einem gemeinsamen Kontextmodell verbunden – als Grundlage für KPIs, Analytik und AI.
- Alt-Text DE: Diagramm, das Business-, Shopfloor- und Umweltdaten in ein gemeinsames Kontextmodell und KPI/Analytics-Ergebnisse zusammenführt.
- Version 2: ![UC-02-3-Data-Pools-DE-v2.png](/.attachments/UC-02-3-Data-Pools-DE-v2-05fdbcc0-19f3-4fd8-a1ba-69339a4ecf8c.png)

### Visual 2: UC-02 Diagram (EN)
- Datei/Link: ![UC-02-3-Data-Pools-EN.png](/.attachments/UC-02-3-Data-Pools-EN-fa602cb1-58ff-4e02-b937-954578de748c.png)
- potentielle Änderung s.o.
- Caption EN: Three data worlds are unified into one context model—enabling KPIs, analytics, and AI.
- Alt text EN: Diagram combining business, shopfloor, and environment data into a shared context model and KPI/analytics outcomes.
- Version 2: ![UC-02-3-Data-Pools-EN-v2.png](/.attachments/UC-02-3-Data-Pools-EN-v2-a7f90102-bad5-45d1-8269-5da6a673f40d.png)

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
- **Datenpool 2 (Shopfloor)**: Station Events, AGV/FTS Transfers, Quality (AIQS), Warehouse moves
- **Datenpool 3 (Umwelt/Sensorik)**: Temperature/Humidity/Energy (optional Vibration)
- **Shared Context Model**: Verknüpfung über IDs + Zeit + Semantik (Order ↔ Workpiece/NFC ↔ Station ↔ Time)
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
