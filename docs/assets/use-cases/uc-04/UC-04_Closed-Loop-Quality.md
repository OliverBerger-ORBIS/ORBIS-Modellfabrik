# UC-04 — Closed Loop Quality: From detection to action (A4)

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
Closed Loop Quality: Qualitätsereignisse führen automatisiert zur nächsten Aktion

### One-liner
Qualitätsabweichungen werden erst wirksam beherrscht, wenn **Prüfergebnis → Entscheidung → Aktion** als geschlossener Regelkreis umgesetzt ist – mit Rückmeldung in MES/ERP.

### Kundennutzen (3)
- **Schnellere Reaktion** auf Qualitätsprobleme (weniger Ausschuss, weniger Nacharbeit)
- **Durchgängige Nachverfolgbarkeit** (Genealogie + Prüfentscheidungen + Folgeaktionen)
- **Standardisierte Rückmeldung** an MES/ERP (Best-of-Breed, SAP als Beispiel) statt manueller Sonderwege

### Pain Points (3)
- Qualität wird dokumentiert, aber **ohne konsequente Folgeprozesse** (z. B. Sperren, Nacharbeit, Neubau)
- Entscheidungen sind **nicht transparent/auditierbar** (warum wurde gestoppt/freigegeben?)
- Rückmeldungen an MES/ERP sind **manuell** oder use-case-spezifisch verdrahtet

### Datenquellen
- **Business-Kontext:** Produktionsauftrag, Material/Charge, Prüfplan/Anforderungen, Kundenauftrag/Termin
- **Shopfloor:** AIQS-Prüfergebnis (Pass/Fail, Merkmale), Stations-Events, Bearbeitungsparameter, Zeitstempel
- **Optional:** Sensor-/Umweltdaten zur Ursachenanalyse (typisch UC-02; hier nur referenzieren)

### KPI/Outcome-Bezug
FPY, Ausschuss-/Nacharbeitsquote, Reklamationskosten, Reaktionszeit bis Sperre/Stop, Durchlaufzeit, Auditfähigkeit (lückenlose Entscheidungskette)

### Orchestrierung / Systeminteraktion (Closed Loop – Layer-Logik)
**Obere Ebene – Prozess (Quality Loop):**
1) **Detect**: Prüfung erkennt Abweichung (AIQS/Prüfstation)  
2) **Decide**: Regel/Policy entscheidet (z. B. Sperre, Nacharbeit, Neubau, Freigabe mit Hinweis)  
3) **Act**: Aktion ausführen (Stop/Redirect/Rework-Route) + Rückmeldung an MES/ERP  
4) **Learn** (optional): Ursachenanalyse/Trend → Anpassung von Regeln/Modell/Prozess

**Zentrale Ebene – DSP (Vermittler & Governance):**
- **DSP Edge (1..n):** nimmt Qualitäts-Events auf, normalisiert/kontextualisiert (Order/Werkstück/Station/Zeit) und triggert lokale Aktionen (z. B. Stop/Redirect)
- **DSP Management Cockpit:** Policy/Ruleset-Versionierung, Freigabe, Rollout/Rollback auf relevante Stationen/Edges, Audit-Logik (wer/was/wann)

**Untere Ebene – Shopfloor & Zielsysteme:**
- **Shopfloor:** AIQS/Qualitätsstation + betroffene Produktionsstationen
- **MES/ERP (Beispiel SAP DM / SAP ERP):** Rückmeldung (Nonconformance, Rework Order, Scrap Booking, Quality Notification) – abhängig von der Zielsystem-Landschaft

**Kernmessage (muss sichtbar sein):**
„Quality event → contextual decision → orchestrated action → MES/ERP feedback“

### Demonstrator vs produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. Die dargestellten Use Cases sind konzeptionell; produktive Implementierungen erfolgen kundenspezifisch abhängig von Zielsystemen (MES/ERP/Analytics) und Governance-Anforderungen.

### CTA
Closed-Loop Quality Workshop (Assessment + Zielprozess + Integrations-/Orchestrierungsplan)

### Visuals (Einbindung)
#### Visual 1: UC-04 Konzept-Diagramm (statisch, später optional SVG-Animation)
- Datei/Link: <einfügen>
- Caption DE: Closed Loop Quality verbindet Prüfergebnis, Entscheidung, Aktion und Rückmeldung in MES/ERP – als auditierbarer Regelkreis.
- Alt-Text DE: Diagramm zeigt Qualitätsereignis (AIQS) → Policy/Decision (DSP) → Aktion im Shopfloor → Rückmeldung an MES/ERP.

#### Visual 2: OSF Proof Screenshot (optional)
- Datei/Link: <einfügen> (z. B. AIQS/Quality Events + Order Context)
- Caption DE: OSF macht Qualitätsereignisse und Kontext sichtbar – als Grundlage für Closed-Loop-Orchestrierung.
- Alt-Text DE: Screenshot zeigt Qualitätsereignisse verknüpft mit Auftrags-/Werkstückkontext.

### Screen Spec / Implementation Notes (OSF)
**Current state (lean, static):**
- UC-04 wird als **statisch modellierter Use-Case-Screen** umgesetzt (Text + Diagramm + kurze Erläuterung)
- OSF zeigt: Qualitätsereignis + Kontext + konzeptionelle Folgeaktion (z. B. „Stop/Redirect“ + „ERP/MES feedback“ als Status)

**Diagrammregeln (CI/Reuse DSP-Style):**
- Prozess-Container: Highlight-Green (klar als Prozess erkennbar)
- DSP-Container: Blau; Shopfloor: Grau
- Pfeile orthogonal (L-Shape), keine Pfeile über Boxen, Vermittlung über DSP Edge

**Optional later (SVG animation, DSP-style):**
- Ein SVG, stabile Gruppen-IDs, Steps über Highlighting/Opacity
- Steps (Vorschlag): Detect → Decide → Act → Feedback → (Learn)

**Wichtig (Scope-Abgrenzung):**
- UC-04 erklärt das Prinzip; die konkrete Umsetzung (z. B. SAP QM/DM, Nonconformance, Rework Order) ist **Best-of-Breed** und kundenspezifisch.

---

## EN

### Title
Closed Loop Quality: Turning quality events into orchestrated actions

### One-liner
Quality only becomes controllable at scale when **detection → decision → action** is implemented as a closed loop—including governed feedback to MES/ERP.

### Benefits (3)
- **Faster response** to quality issues (less scrap, less rework)
- **End-to-end traceability** (genealogy + decisions + follow-up actions)
- **Standardized feedback** to MES/ERP (best-of-breed; SAP as an example) instead of manual wiring

### Pain points (3)
- Quality is documented without consistent follow-up processes (block, rework, rebuild)
- Decisions are not transparent/auditable (why was it stopped/released?)
- MES/ERP feedback is manual or custom per use case

### Data sources
- **Business context:** production order, material/batch, inspection plan/requirements, customer order/due date
- **Shopfloor:** AIQS/inspection result (pass/fail, characteristics), station events, process parameters, timestamps
- **Optional:** sensors/environment for root-cause analytics (typically UC-02; referenced only)

### KPI/Outcome
FPY, scrap/rework rate, complaint cost, time-to-containment (block/stop), lead time impact, auditability (complete decision chain)

### Orchestration / interaction (Closed loop with clear layers)
**Top layer — Process (quality loop):**
1) **Detect**: inspection detects deviation  
2) **Decide**: policy/rules decide (block, rework route, rebuild, conditional release)  
3) **Act**: execute action (stop/redirect/rework) + send feedback to MES/ERP  
4) **Learn** (optional): trends/root cause → improve rules/model/process

**Middle layer — DSP (mediator & governance):**
- **DSP Edge (1..n):** ingests quality events, normalizes and contextualizes (order/workpiece/station/time), triggers local actions
- **DSP Management Cockpit:** versioned policies, approvals, rollout/rollback to relevant edges/stations, audit logic

**Bottom layer — Shopfloor & target systems:**
- **Shopfloor:** AIQS/quality station + impacted production stations
- **MES/ERP (e.g., SAP DM / SAP ERP):** feedback (nonconformance, rework order, scrap booking, quality notification) depending on the target landscape

**Core message (must be explicit):**
“Quality event → contextual decision → orchestrated action → MES/ERP feedback”

### Demonstrator vs productive solution (mandatory)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual; productive implementations are customer-specific depending on target systems (MES/ERP/analytics) and governance requirements.

### CTA
Closed-loop quality workshop (assessment + target process + integration/orchestration plan)

### Visuals
#### Visual 1: UC-04 concept diagram (static now, optional SVG animation later)
- File/Link: ![UC-04-Closed-Loop](/.attachments/UC-04-Closed-Loop-6c4ec168-b815-40a6-ab03-7ba4ba450778.png)
- Caption EN: Closed-loop quality connects inspection results, governed decisions, shopfloor actions, and MES/ERP feedback into an auditable loop.
- Alt text EN: Diagram showing AIQS quality event → DSP policy decision → shopfloor action → feedback to MES/ERP.

#### Visual 2: OSF proof screenshot (optional)
- File/Link: <insert>
- Caption EN: OSF makes quality events and context visible—enabling closed-loop orchestration.
- Alt text EN: Screenshot showing quality events linked to order/workpiece context.

### Screen Spec / Implementation Notes (OSF)
**Current state (lean, static):**
- UC-04 is delivered as a **static use-case screen** (content + diagram + short explanation)
- OSF shows: quality event + context + conceptual follow-up (e.g., “stop/redirect” + “ERP/MES feedback”)

**Diagram rules (CI / reuse DSP style):**
- Process container: highlight green (clearly a process)
- DSP: blue; shopfloor: grey
- Orthogonal (L-shaped) connectors; no arrows crossing boxes; mediation via DSP Edge

**Optional later (SVG animation, DSP-style):**
- Single SVG, stable group IDs, step-based highlighting/opacity
- Steps: Detect → Decide → Act → Feedback → (Learn)

**Scope note:**
- UC-04 explains the principle; concrete mappings (e.g., SAP QM/DM objects) remain **best-of-breed** and customer-specific.
