# UC-06 — Interoperability: Event-to-Process Map (Anchor for A1)

## Status
- Owner: @<Oliver Berger>
- Scope: OSF-BLOG-2026
- Messe-Tag: LOGIMAT
- Referenziert in: A1 (DE/EN Draft)
- Feature: #69066
- User Stories: #69087

---

## DE

### Titel
**Interoperabilität: Event-to-Process Map**

### One-liner
Shopfloor-Events werden zu einem verständlichen Prozessbild – als gemeinsame Sprache zwischen OT und IT.

### Kundennutzen (3)
- Gemeinsames Prozessverständnis über Anlagen, Systeme und Teams hinweg
- Schnellere Diagnose bei Störungen durch klare Event-/Status-Ketten
- Grundlage für ERP/MES/Analytics-Integration ohne Punkt-zu-Punkt-Wildwuchs

### Pain Points (3)
- Heterogene Events/Signale sind nicht prozessfähig (fehlende Semantik)
- Unterschiedliche Sichten auf „was passiert“ (OT vs. IT)
- Integrationsaufwand explodiert, weil jeder Use Case individuell verdrahtet wird

### Datenquellen
- **Business-Kontext:** Auftrags-/Stammdaten (z. B. Produktionsauftrag, Material, Kunde)
- **Shopfloor:** Maschinen-/FTS-/Stations-Events, Status, Zeiten, Qualitätsresultate
- **Umwelt/Sensorik (optional):** z. B. Temperatur, Energie, Vibration

### KPI / Outcome
Kürzere Störungsbehebungszeiten (MTTR), höhere Datenqualität, schnelleres Onboarding neuer Module/Systeme.

### Orchestrierung / Systeminteraktion
Events werden normalisiert und kontextualisiert (Order / Werkstück / Station / Zeit) und zu interpretierbaren Prozessschritten korreliert. Ergebnis ist eine Event-to-Process Map als wiederverwendbare Basis für weitere Use Cases (z. B. Track & Trace, Closed Loops, KPI-Analytik).

### Demonstrator vs. produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. Die dargestellten Use Cases sind konzeptionell und werden je nach Zielumgebung (ERP/MES/Analytics) kundenspezifisch umgesetzt.

### CTA
**Interoperability & Integration Assessment (Workshop)**

### Caption
Interoperabilität macht aus technischen Events ein Prozessbild, das IT und OT gleichermaßen verstehen.

### Alt-Text
Diagramm, das Shopfloor-Events in Prozessschritte und einen End-to-End Ablauf überführt.

---

## EN

### Title
**Interoperability: Event-to-Process Map**

### One-liner
Turn shopfloor events into a shared process view—one language for OT and IT.

### Benefits (3)
- Shared process understanding across systems and teams
- Faster troubleshooting through clear event/state chains
- Foundation for ERP/MES/analytics integration without point-to-point complexity

### Pain Points (3)
- Raw signals lack semantics and are not process-ready
- Conflicting views of what is happening (OT vs. IT)
- Integration costs explode due to custom wiring per use case

### Data sources
- **Business context:** orders and master data (e.g., production order, material, customer)
- **Shopfloor:** machine/AGV/station events, states, timestamps, quality results
- **Environment/sensors (optional):** e.g., temperature, energy, vibration

### KPI / Outcome
Reduced MTTR, higher data quality, faster onboarding of new modules/systems.

### Orchestration / interaction
Events are normalized and contextualized (order / workpiece / station / time) and correlated into interpretable process steps. The result is an event-to-process map that can be reused as a foundation for further use cases (e.g., track & trace, closed loops, KPI analytics).

### Disclaimer (mandatory)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual and are implemented customer-specifically depending on the target landscape (ERP/MES/analytics).

### CTA
**Interoperability & Integration Assessment workshop**

### Caption
Interoperability converts technical events into a process view understood by both OT and IT.

### Alt text
Diagram showing shopfloor events mapped to process steps and an end-to-end flow.

---

## Screen Spec / Implementation Notes (UC-06) — DE

### Ziel
UC-06 visualisiert das Prinzip „Event-to-Process“: technische Shopfloor-Events werden normalisiert, mit Business-Kontext angereichert und als prozessfähige Sicht bereitgestellt. **Umsetzung:** dynamische SVG-Generierung mit Step-Animation (analog zu UC-01 bis UC-07); siehe [use-case-library](../../../02-architecture/use-case-library.md).

### Platzierung & Verlinkung
- **Primär:** DSP-Tab → Abschnitt „DSP Anwendungsfälle“ als zusätzlicher Use Case „Interoperabilität (Event-to-Process)“.
- **Sekundär (optional):** Wiki-Use-Case-Seite (UC-06) enthält das Diagramm + Kurzbeschreibung.
- **Verlinkung (optional, später):**
  - Klick auf die UC-Card im DSP-Tab → Scroll/Jump auf Detailbereich oder Öffnen einer Detail-Ansicht.
  - Wiki verlinkt zurück auf DSP-Tab (und umgekehrt), ohne OSF als „produktive Use-Case-App“ darzustellen.

### Visual Pattern (OSF/DSP konsistent)
- **Pattern wie bestehende DSP Use Cases (mit Step-Animation):**
  - **Top:** Use-Case-Cards (Grid) inkl. Icon, Titel, One-liner.
  - **Detailbereich:** „Aktionen“ (links) + „Smart Factory“ (rechts) als Bullet-Listen.
  - **Footer-Disclaimer:** OSF ist Demonstrator (konzeptionell, kundenspezifische Umsetzung).

### Inhaltliche Elemente (statisch)
- **Use-Case-Card (Kurz)**
  - Titel: *Interoperabilität (Event-to-Process)*
  - One-liner: *Shopfloor-Events normalisieren und mit Kontext anreichern – als gemeinsames Prozessbild für OT und IT.*
- **Detailbereich**
  - *Aktionen* (Bullets): Normalisieren, Kontext anreichern, Event-Ketten korrelieren, Wiederverwendbarkeit statt P2P.
  - *Smart Factory* (Bullets): Gemeinsames Prozessbild, Basis für Traceability/KPIs/Closed Loops, Best-of-Breed Zielsysteme.
- **Konzept-Diagramm (optional im Detailbereich oder als eigenes Asset im Wiki)**
  - Variante A: „3 Säulen“ (Quellen → DSP Verarbeitung → Prozesssicht/Targets)
  - Variante B: „Business-first“ (oben Business-Kontext, unten Shopfloor)

### Daten-/Begriffsmodell (für Konsistenz)
- Standardbegriffe (DE): **Event**, **Kontext**, **Order**, **Werkstück**, **Station**, **Zeit**, **Status**, **Prozessschritt**
- Ziel: Begriffe identisch in
  - Blog A1 (Abschnitt Interoperabilität)
  - UC-06 Seite
  - DSP-Tab Use Case Texten

### Icon/Assets
- Icon: vorhandenes **Interoperabilität-SVG** (CI-konform).
- Keine neuen Icon-Stile einführen.
- Diagramm-Farben/Typografie orientieren sich an bestehenden DSP-Visuals (OSF/DSP CI).

### Statische Implementierung (MVP)
- **Kein** Live-Datenbezug erforderlich.
- Inhalte werden als **statische Konfiguration** modelliert (z. B. JSON / i18n keys).
- DE/EN über i18n; Bilder getrennt je Sprache, falls Labels im Bild.

### Step-Animation (umgesetzt)
- UC-06 nutzt wie alle Use-Cases die gemeinsame Step-Logik (Step-Controls, Highlighting, Auto-Dim).
- SVG wird dynamisch aus `uc-06-structure.config.ts` generiert; Steps steuern Sichtbarkeit/Highlight über `uc-06-event-to-process-map.steps.json`.

### Acceptance Criteria (MVP)
- UC-06 erscheint als zusätzliche Card im DSP Use-Case-Grid (DE/EN).
- Detailbereich zeigt Titel, One-liner, zwei Bullet-Listen, Disclaimer (DE/EN).
- Interoperabilität-Icon konsistent, keine neuen Stile.
- Optionales Diagramm (PNG/SVG) kann eingebunden werden, ohne UI-Refactoring.

---

## Screen Spec / Implementation Notes (UC-06) — EN

### Goal
UC-06 visualizes the “event-to-process” principle: raw shopfloor events are normalized, enriched with business context, and turned into a process-ready view. **Implementation:** dynamic SVG generation with step animation (aligned with UC-01–UC-07); see [use-case-library](../../../02-architecture/use-case-library.md).

### Placement & Linking
- **Primary:** DSP tab → “DSP Use Cases” section as an additional use case: “Interoperability (Event-to-Process)”.
- **Secondary (optional):** UC-06 wiki page hosts the diagram and a concise description.
- **Linking (optional, later):**
  - Click on the UC card → scroll/jump to the detail panel or open a detail view.
  - Cross-link wiki ↔ DSP tab, without positioning OSF as the productive use-case application.

### Visual Pattern (consistent with OSF/DSP)
- **Pattern aligned with existing DSP use cases (including step animation):**
  - **Top:** Use-case cards (grid) with icon, title, one-liner.
  - **Detail panel:** “Actions” (left) + “Smart Factory” (right) as bullet lists.
  - **Footer disclaimer:** OSF is a demonstrator (conceptual; customer-specific implementation).

### Content Elements (static)
- **Use-case card (short)**
  - Title: *Interoperability (Event-to-Process)*
  - One-liner: *Normalize shopfloor events and enrich them with context—creating a shared process view for OT and IT.*
- **Detail panel**
  - *Actions* (bullets): normalize, enrich context, correlate event chains, reuse instead of point-to-point.
  - *Smart Factory* (bullets): shared process view, basis for traceability/KPIs/closed loops, best-of-breed target systems.
- **Concept diagram (optional in the detail panel or as a separate wiki asset)**
  - Option A: “3 pillars” (sources → DSP processing → process view/targets)
  - Option B: “business-first” (business context on top, shopfloor at the bottom)

### Data/Terminology Model (for consistency)
- Standard terms (EN): **event**, **context**, **order**, **workpiece**, **station**, **time**, **status**, **process step**
- Keep terminology consistent across:
  - Blog A1 (interoperability section)
  - UC-06 page
  - DSP tab use-case texts

### Icon/Assets
- Icon: existing **Interoperability SVG** (CI-compliant).
- Do not introduce new icon styles.
- Diagram colors/typography follow existing DSP visuals (OSF/DSP CI).

### Static Implementation (MVP)
- No live data integration required.
- Content is modeled as **static configuration** (e.g., JSON / i18n keys).
- DE/EN via i18n; separate images per language if labels are embedded in the image.

### Step Animation (implemented)
- UC-06 uses the shared step logic (step controls, highlighting, auto-dim) like all use cases.
- SVG is generated dynamically from `uc-06-structure.config.ts`; steps control visibility/highlighting via `uc-06-event-to-process-map.steps.json`.

### Acceptance Criteria (MVP)
- UC-06 appears as an additional card in the DSP use-case grid (DE/EN).
- Detail panel shows title, one-liner, two bullet lists, and the disclaimer (DE/EN).
- Interoperability icon is consistent; no new styles are introduced.
- Optional diagram (PNG/SVG) can be embedded without UI refactoring.


---

## Assets (placeholders)
- Version 1 Shopfloor-first: ![UC-06-Interoperability-Shopfloor-first.png](/.attachments/UC-06-Interoperability-Shopfloor-first-84b2f388-914e-4b74-b677-0eaf6b0ba0c6.png) 
- Version 2 Business-first: ![UC-06-Interoperability-Business-first.png](/.attachments/UC-06-Interoperability-Business-first-d6dffb56-c520-4385-a8f5-6b1fc029b0c1.png)
- SVG DE
![UC-06-SVG-Template-DE.png](/.attachments/UC-06-SVG-Template-DE-54365d72-52c0-48c2-9bf9-b9dfc9f34f7b.png)

- SVG EN
![UC-06-SVG-Template-EN.png](/.attachments/UC-06-SVG-Template-EN-d20ed899-dd3b-4faa-a1f3-4fe56671809d.png)

---

## Open points / review notes
- [ ] Final CTA wording confirmation
- [ ] Decide whether UC-06 is shown only in blog/wiki, or also in OSF UI (Use-Case card)
- [ ] Final labels for DE/EN (glossary alignment)
