# UC-03 — AI Lifecycle: Train centrally → Deploy to multiple stations (A3)

## Status
- Owner: @<Oliver Berger>
- Scope-Tag: OSF-BLOG-2026
- Messe-Tag: HANNOVER-MESSE
- Referenziert in: A4 (DE/EN Draft) #69084 und #69085
- Feature: #69070
- User Stories: #69088

## DE

### Titel
AI Lifecycle: Von Daten zu Modellen – und kontrolliert zurück in die Edge

### One-liner
AI wird industrietauglich, wenn Daten, Training, Deployment und Betrieb als **Lifecycle** gedacht sind – inklusive zentralem Rollout auf mehrere Stationen.

### Kundennutzen (3)
- **Realtime-Entscheidungen an der Edge**, dort wo sie benötigt werden (Stationen/Module)
- **Governed Deployment**: Versionierung, Freigabe, Rollout/Rollback über ein zentrales Cockpit
- **Kontinuierliche Verbesserung** durch Monitoring, Feedback und Retraining

### Pain Points (3)
- Daten sind nicht ML-ready (Qualität, Kontext, Labeling)
- Modelle bleiben in PoCs stecken (kein Deployment-/Ops-Modell, keine Verteilung in die Fläche)
- Drift/Performance wird nicht überwacht; Feedback-Schleifen fehlen

### Datenquellen
- **Business-Kontext:** Qualitätsanforderungen, Auftrags-/Materialkontext, Stammdaten
- **Shopfloor:** Prozessdaten, Events/Signale, (optional) Bilder, Qualitätsereignisse
- **Umwelt/Sensorik (optional):** z. B. Temperatur/Energie zur Korrelation (falls relevant)

### KPI/Outcome-Bezug
FPY, Ausschuss/Nacharbeit, Reaktionszeit, Modellgüte (Accuracy/Precision/Recall je nach Use Case), Drift-Indikatoren, Rollout-Stabilität (z. B. Fehlerquote nach Deployment)

### Orchestrierung / Systeminteraktion (Lifecycle – Layer-Logik)
**Obere Ebene – Prozess (Lifecycle):**
1) **Data Capture & Context**: Events/Signale erfassen und mit Kontext (Order/Werkstück/Station/Zeit) anreichern  
2) **Train & Validate (Cloud)**: Modelle trainieren/validieren, versionieren und paketieren  
3) **Monitor & Feedback**: Betrieb überwachen, Feedback/Labels sammeln, Retraining auslösen  

**Zentrale Ebene – DSP (Vermittler & Rollout-Steuerung):**
- **DSP Management Cockpit**: Model Registry, Freigabe/Release, Rollout/Rollback, Zieldefinition „welche Stationen benötigen welches Modell“
- **DSP Edge (1..n)**: Runtime/Inference, Provisioning Richtung Stationen, lokale Pufferung/Regeln/Aktionen

**Untere Ebene – Shopfloor:**
- **Stationen 1..m je Edge** (mehrere Instanzen pro Edge): Modelle laufen dort, wo Echtzeit-Entscheidungen benötigt werden

**Kernmessage (muss sichtbar sein):**  
**„Train centrally → Deploy to multiple stations (where needed)“** (DE sinngemäß: „Zentral trainieren → kontrolliert an alle relevanten Stationen ausrollen“)

### Demonstrator vs produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. Die dargestellten Use Cases sind konzeptionell; produktive Umsetzungen erfolgen kundenspezifisch abhängig von Zielsystemen (ERP/MES/Analytics/Cloud) und Betriebsanforderungen.

### CTA
AI Use-Case Discovery + Lifecycle Setup Workshop (inkl. Rollout-/Betriebsmodell)

### Visual (Diagramm)
**Diagramm-Typ (Primary):** *Layer-/Deployment-View*  
- Oben: Lifecycle-Prozess (Data Capture & Context → Train & Validate → Monitor & Feedback)  
- Mitte: DSP Management Cockpit + DSP Edge (1..n) als zentrale Vermittlung  
- Unten: Shopfloor Stationen als Mehrfachinstanzen je Edge  
**Gestaltungsregeln:** DSP-Layer blau, Shopfloor grau, Prozess-Container Highlight-Green; Pfeile nur orthogonal (L-Shape); keine Pfeile über Boxen; Vermittlung über DSP Edge.

**Optional (Secondary):** *Loop-Fokus-Ansicht* (für Animation/Deep Dive)  
- Lifecycle als geschlossener Kreislauf (Feedback Loop), ohne Multi-Edge/Stations-Details

**Caption (DE):**
Der AI Lifecycle verbindet Datenpipeline, Training, zentralen Rollout und Betrieb: Modelle werden zentral trainiert und kontrolliert an mehrere Stationen (über DSP Cockpit & Edge) verteilt.

**Alt-Text (DE):**
Diagramm zeigt den AI Lifecycle (Daten erfassen, Trainieren/Validieren, Monitoring/Feedback) und das zentrale Ausrollen von Modellversionen auf mehrere Stationen über DSP Management Cockpit und DSP Edge.

---

## EN

### Title
AI Lifecycle: From data to models—and back to the edge with governed rollout

### One-liner
Industrial AI requires a lifecycle: **data, training, deployment, and operations**—including centralized rollout to multiple stations where inference is needed.

### Benefits (3)
- **Real-time decisions at the edge**, exactly where they are required (stations/modules)
- **Governed deployment**: versioning, approval, rollout/rollback via a central cockpit
- **Continuous improvement** through monitoring, feedback, and retraining

### Pain points (3)
- Data is not ML-ready (quality, context, labeling)
- Models get stuck in PoCs (no deployment/ops model, no scalable distribution)
- Drift/performance is not monitored; feedback loops are missing

### Data sources
- **Business context:** quality requirements, order/material context, master data
- **Shopfloor:** process data, events/signals, (optional) images, quality events
- **Environment/sensors (optional):** e.g., temperature/energy for correlation

### KPI/Outcome
FPY, scrap/rework, response time, model quality metrics (use-case dependent), drift indicators, rollout stability (e.g., post-deployment error rate)

### Orchestration / interaction (Lifecycle with clear layers)
**Top layer — Process (lifecycle):**
1) **Data capture & context**: capture events/signals and enrich with context (order/workpiece/station/time)  
2) **Train & validate (cloud)**: train/validate, version, and package models  
3) **Monitor & feedback**: monitor operations, collect feedback/labels, trigger retraining  

**Middle layer — DSP (mediator & rollout control):**
- **DSP Management Cockpit**: model registry, approval/release, rollout/rollback, target definition (“which stations need which model”)
- **DSP Edge (1..n)**: runtime/inference, provisioning to stations, local buffering/rules/actions

**Bottom layer — Shopfloor:**
- **Stations 1..m per edge** (multiple instances): inference runs where it is needed

**Core message (must be explicit):**  
**“Train centrally → Deploy to multiple stations (where needed)”**

### Demonstrator vs productive solution (mandatory)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual; productive implementations are customer-specific depending on target systems (ERP/MES/analytics/cloud) and operational requirements.

### CTA
AI use-case discovery + lifecycle setup workshop (including rollout/operating model)

### Visual (diagram)
**Primary diagram:** *Layer / deployment view*  
- Top: lifecycle process (Data capture & context → Train & validate → Monitor & feedback)  
- Middle: DSP Management Cockpit + DSP Edge (1..n) as the mediation layer  
- Bottom: shopfloor stations shown as multiple instances per edge  
**Design rules:** DSP layer blue, shopfloor grey, process container highlight green; orthogonal (L-shaped) connectors only; no arrows crossing boxes; mediation via DSP Edge.

**Optional secondary:** *Loop-focused view* (for animation/deep dive)  
- lifecycle as a closed loop, without multi-edge/station detail

**Caption (EN):**
The AI lifecycle connects data pipelines, cloud training, governed rollout, and operations: models are trained centrally and deployed to multiple stations via DSP Management Cockpit and DSP Edge.

**Alt text (EN):**
Diagram showing the AI lifecycle (data capture, training/validation, monitoring/feedback) and the governed rollout of model versions to multiple stations through DSP Management Cockpit and DSP Edge.

---

## Screen Spec / Implementation Notes (OSF)
### Current state (lean, static modeling)
- UC-03 is modeled as a **static use-case screen** (content + diagram + short explanation)
- The diagram can be embedded as **PNG now**, and later replaced by a **single SVG** for animation

### Optional future (SVG animation, DSP-style)
- One SVG, grouped elements with stable IDs
- Animation steps: overview → capture/context → train/validate → rollout to edges → inference at stations → monitor/feedback → retraining loop
- All connectors orthogonal; highlight/opacity transitions only (no layout shifts)

### OSF integration guidance
- Keep wording aligned with DSP (not “OSF method”): OSF shows the principle, DSP provides the methodology and architecture.
- Do not show AGV/FTS in UC-03 (keep focus on AI lifecycle + governed rollout).
