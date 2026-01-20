# UC-05 — Predictive Maintenance (A4)

## Status
- Owner: @<Oliver Berger>
- Scope-Tag: OSF-BLOG-2026
- Messe-Tag: HANNOVER-MESSE
- Referenziert in: A4 (DE/EN Draft) #69084 und #69085
- Feature: #69070
- User Stories: #69088

---

## DE

### Titel
Predictive Maintenance: Vibrationen erkennen – Ausfälle vermeiden

### One-liner
Zustandsüberwachung mit Frühwarnung: Vibrationen werden erkannt, bewertet und lösen ereignisbasiert Alarm und – optional – eine Reaktion aus.

### Kundennutzen (3)
- **Frühwarnung statt Stillstand:** Störungen werden früh erkannt, bevor es zum Ausfall kommt.
- **Schnellere Reaktion:** Alarmierung und Eskalation erfolgen ereignisbasiert und nachvollziehbar.
- **Geringere Kosten:** Weniger ungeplante Stillstände und reduzierte Folgeschäden.

### Pain Points (3)
- Zustandsdaten fehlen oder sind nicht kontinuierlich verfügbar.
- Alarme sind nicht mit Prozess-/Auftragskontext verknüpft (wer/was/wo/wann betroffen?).
- Reaktionen erfolgen manuell, spät oder inkonsistent (kein geschlossener Ablauf von Signal → Entscheidung → Aktion).

### Datenquellen
- **Shopfloor:** Vibrations-/Schwingungswerte (Sensor), Maschinen-/Stationsstatus, Prozessereignisse
- **Business (optional):** Auftrags-/Materialkontext, Wartungsfenster, Prioritäten
- **Umwelt/Sensorik (optional):** z. B. Temperatur zur Korrelation

### KPI/Outcome-Bezug
MTBF/MTTR, ungeplante Stillstandszeit, Alarm-zu-Reaktion-Zeit; indirekt: Ausschuss-/Nacharbeitsquote

### Orchestrierung / Systeminteraktion
- Sensorwerte werden als Zeitreihe erfasst und mit Stations-/Order-Kontext verknüpft.
- DSP wertet Schwellwerte/Regeln aus (Edge-nah, Realtime) und erzeugt bei Anomalien ein **Event** (Alarm).
- Optional: **automatisierte Reaktion** im Shopfloor (z. B. Produktionsstopp / Safe-State) sowie Rückmeldung an Zielprozesse/Zielsysteme (MES/ERP/Service/Analytics – Best-of-Breed).

**Hinweis zur Erweiterbarkeit (ohne Fischertechnik-Abhängigkeit):**  
Im Demonstrator kann externe Sensorik angebunden werden, um die Offenheit der Architektur zu zeigen: Zusätzliche Geräte und Protokolle lassen sich integrieren, während DSP die Orchestrierung (Ingestion → Kontext → Alarm → Aktion) konsistent übernimmt. (Die Sensorwahl ist dabei austauschbar und nicht der Kernnutzen.)

### Demonstrator vs. produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. Die dargestellten Use Cases sind konzeptionell und werden je nach Systemlandschaft (ERP/MES/Analytics) kundenspezifisch umgesetzt.

### CTA
**Predictive Maintenance Readiness Check (Workshop):** Datenquellen, Monitoring-Logik, Alarmierung, Zielprozesse und Integration bewerten – und den nächsten sinnvollen Umsetzungsschritt planen.

---

## Visuals (Einbindung)

### Visual 1: UC-05 Konzeptdiagramm (DE)
- Datei/Link: ![UC-05-SVG-Template-DE](/.attachments/UC-05-SVG-Template-DE-7cc5086c-2611-42df-a9df-4526a45e5aa5.png)
- Caption DE: Frühwarnung durch Vibrationsmonitoring: DSP korreliert Sensordaten mit Prozesskontext und löst Alarm sowie – optional – eine Aktion aus; Zielsysteme bleiben Best-of-Breed.
- Alt-Text DE: Diagramm zeigt Sensorwerte → DSP Edge Regelprüfung/Kontext → Alarm-Event → optionale Aktion (Stop/Safe-State) → Rückmeldung an Zielsysteme.

### Visual 2: OSF Proof (DE) – Live/aktuelle Systemdaten (optional)
- Datei/Link: <einfügen> (z. B. Environment Data / Message Monitor / Alarm-Event)
- Caption DE: OSF als Proof: Alarm-Events und Statusänderungen werden in Echtzeit sichtbar und bleiben nachvollziehbar.
- Alt-Text DE: Screenshot zeigt Zeitreihe/Events und den ausgelösten Alarm inkl. Timestamp.

---

## Screen Spec / Implementation Notes (DE)

### Ziel
Ein Use-Case-Screen, der den **End-to-End Alarmfluss** verständlich macht: Sensor → DSP → Alarm → (optional) Aktion → (optional) Rückmeldung.

### Modellierungsprinzip
- **Statisch modelliert** (Wiki/Diagramm als Template) – später optional **SVG-Animation** analog DSP-Architecture.
- OSF-Integration optional: als statischer „Use Case Screen“ oder Verlinkung vom DSP-Tab-Use-Case.

### Layer / Layout (CI-konform)
- **Process Layer (Highlight-Green):** Detect → Evaluate → Alert → Act → Feedback
- **DSP Layer (Blau):** DSP Edge (Rule/Threshold Evaluation) + optional DSP Management Cockpit (Policy/Config)
- **Shopfloor Layer (Grau):** Station(en) + External Sensor (Vibration)

### Elemente / Wording
- Sensor: „Vibration Sensor (External)“
- DSP Edge: „Rule / Threshold Check“ + „Context Enrichment“
- Event: „Alarm Event“ (Severity, Timestamp)
- Action: „Stop / Safe-State (optional)“
- Feedback: „Notification / Ticket / MES-ERP Update (optional)“

### Pfeile / Darstellung
- Nur orthogonale **L-Shape** Pfeile.
- Pfeile laufen **nicht über Boxen**, sondern in klaren „Gassen“ zwischen Layern.
- Konsistente Farblogik für Flüsse:
  - Sensor/Signals → DSP: neutral
  - Prozess-/Alarmfluss: Highlight-Green
  - Rückmeldung an Zielsysteme: DSP-Blau

### Optional: SVG-Animation Steps
- Step 0 Overview
- Step 1 Sensor stream highlight
- Step 2 Threshold evaluation highlight (DSP Edge)
- Step 3 Alarm event highlight
- Step 4 Action highlight (Stop/Safe-State)
- Step 5 Feedback highlight (MES/ERP/Service)

---

## EN

### Title
Predictive Maintenance: Detect vibration – prevent downtime

### One-liner
Condition monitoring with early warning: vibrations are detected, evaluated, and can trigger event-based alerts and—optionally—actions.

### Benefits (3)
- **Early warning instead of downtime:** issues are detected before failures occur.
- **Faster response:** event-based alerting and escalation with traceability.
- **Lower cost impact:** fewer unplanned stops and reduced downstream effects.

### Pain points (3)
- Condition data is missing or not continuously available.
- Alerts are not linked to process/order context (who/what/where/when is affected?).
- Responses are manual, late, or inconsistent (no end-to-end flow from signal to action).

### Data sources
- **Shopfloor:** vibration/time-series data (sensor), machine/station states, process events
- **Business (optional):** order/material context, maintenance windows, priorities
- **Environment/sensors (optional):** e.g., temperature for correlation

### KPI/Outcome
MTBF/MTTR, unplanned downtime, alert-to-response time; indirectly: scrap/rework rate

### Orchestration / system interaction
- Capture sensor values as a time series and enrich them with station/order context.
- DSP evaluates rules/thresholds (edge-near, real time) and emits an **alert event** on anomalies.
- Optionally, trigger **automated actions** (stop/safe state) and send feedback to target processes/systems (MES/ERP/service/analytics—best-of-breed).

**Extensibility note (not Fischertechnik-dependent):**  
The demonstrator can connect external sensors to highlight architectural openness: additional devices and protocols can be integrated while DSP keeps orchestration consistent (ingestion → context → alert → action). The specific sensor choice is interchangeable and not the primary value.

### Demonstrator vs. production (required)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual and are implemented customer-specifically depending on the target landscape (ERP/MES/analytics).

### CTA
**Predictive Maintenance Readiness Check (workshop):** assess data sources, monitoring logic, alerting, target processes, and integration—and define the next pragmatic implementation step.

---

## Visuals (embedding)

### Visual 1: UC-05 concept diagram (EN)
- File/link: ![UC-05-SVG-Template-EN](/.attachments/UC-05-SVG-Template-EN-65390815-ddb1-456c-b7b3-a65d3ce368a7.png)
- Caption EN: Early warning via vibration monitoring: DSP correlates sensor data with process context and triggers alerts and—optionally—actions; target systems remain best-of-breed.
- Alt text EN: Diagram shows sensor stream → DSP edge rule check/context → alert event → optional stop/safe-state → feedback into target systems.

### Visual 2: OSF proof (EN) – live/current system data (optional)
- File/link: <insert> (e.g., Environment Data / Message Monitor / alarm event)
- Caption EN: OSF proof: alert events and status changes are visible in real time and remain traceable.
- Alt text EN: Screenshot showing a time series/events and the triggered alert with timestamp.

---

## Screen Spec / Implementation Notes (EN)

### Goal
A use-case screen that makes the end-to-end alert flow clear: sensor → DSP → alert → (optional) action → (optional) feedback.

### Modeling approach
- **Statically modeled** (wiki/diagram template) – later optional **SVG animation** aligned with the DSP-architecture approach.
- Optional OSF integration: either as a static “Use Case Screen” or via deep link from the DSP tab use-case card.

### Layers / layout (CI-aligned)
- **Process layer (highlight green):** Detect → Evaluate → Alert → Act → Feedback
- **DSP layer (blue):** DSP Edge (rule/threshold evaluation) + optional DSP Management Cockpit (policy/config)
- **Shopfloor layer (grey):** station(s) + external vibration sensor

### Elements / wording
- Sensor: “Vibration Sensor (External)”
- DSP Edge: “Rule / Threshold Check” + “Context Enrichment”
- Event: “Alert Event” (severity, timestamp)
- Action: “Stop / Safe-State (optional)”
- Feedback: “Notification / Ticket / MES-ERP Update (optional)”

### Arrow rules / visuals
- Only orthogonal **L-shaped** arrows.
- No arrows running across boxes; use clear “lanes” between layers.
- Consistent flow coloring:
  - sensor/signals → DSP: neutral
  - process/alert flow: highlight green
  - feedback to target systems: DSP blue

### Optional SVG animation steps
- Step 0 overview
- Step 1 sensor stream highlight
- Step 2 threshold evaluation highlight (DSP edge)
- Step 3 alert event highlight
- Step 4 action highlight (stop/safe-state)
- Step 5 feedback highlight (MES/ERP/service)
