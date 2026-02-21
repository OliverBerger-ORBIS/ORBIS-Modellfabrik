# UC-00 — Interoperability: Event-to-Process Map (Foundation / Anchor for A1)

## Status
- Owner: @<Oliver Berger>
- Scope-Tag: OSF-BLOG-2026
- Messe-Tag: LOGIMAT
- Referenziert in: A1 (DE Draft)
- Feature: #69066
- User Stories: #69087

---

## DE

### Titel
**Interoperabilität: Event-to-Process Map (Foundation)**

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
Interoperabilität bedeutet, dass unterschiedliche Systeme, Maschinen, Softwarelösungen und Datenquellen reibungslos miteinander kommunizieren und Informationen nahtlos austauschen können – ohne Sonderprogrammierung, Medienbrüche oder proprietäre Abhängigkeiten. Kurz gesagt: **Alles versteht sich gegenseitig – automatisch, standardisiert und in Echtzeit.**

Dazu werden Events **normalisiert**, mit Kontext **angereichert** (Order / Werkstück / Station / Zeit) und zu interpretierbaren Prozessschritten **korreliert**. Ergebnis ist eine **Event-to-Process Map** als wiederverwendbare Foundation für weitere Use Cases (z. B. Track & Trace, KPI-Analytik, AI, Closed Loops).

Merksatz: **„Interoperabilität wird nicht programmiert – sie wird aktiviert.“**

### Demonstrator vs. produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. Die dargestellten Use Cases sind konzeptionell und werden je nach Zielumgebung (ERP/MES/Analytics) kundenspezifisch umgesetzt.

### CTA
**Reifegrad-Check (kompakt)**  
_Vertiefung (optional): Für komplexe Zielarchitekturen kann daraus ein Interoperability & Integration Assessment abgeleitet werden._

### Caption
UC-00 (Foundation): Interoperabilität macht aus technischen Shopfloor-Events ein prozessfähiges Prozessbild – durch Normalisieren, Kontextanreicherung und Korrelation zu Prozessschritten.

### Alt-Text
Diagramm zeigt Datenquellen aus Business und Shopfloor, die über DSP normalisiert und mit Kontext (Order/Werkstück/Station/Zeit) angereichert werden und als Prozessschritte in Zielsysteme (z. B. Analytics/MES/ERP) fließen.

---

## EN

### Title
**Interoperability: Event-to-Process Map (Foundation)**

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
Interoperability means that different systems, machines, software solutions, and data sources can communicate smoothly and exchange information seamlessly—without custom coding, media breaks, or proprietary dependencies. In short: **everything “understands” each other—automatically, standardized, and in real time.**

To achieve this, events are **normalized**, **enriched** with context (order / workpiece / station / time), and **correlated** into interpretable process steps. The result is an **event-to-process map** that serves as a reusable foundation for further use cases (e.g., track & trace, KPI analytics, AI, closed loops).

Key message: **“Interoperability isn’t programmed—it’s activated.”**

### Disclaimer (mandatory)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. The depicted use cases are conceptual and are implemented customer-specifically depending on the target landscape (ERP/MES/analytics).

### CTA
**Maturity check (compact)**  
_Optional deep dive: for complex target landscapes, this can be extended into an interoperability & integration assessment._

### Caption
UC-00 (foundation): Interoperability turns raw shopfloor events into a process-ready view—by normalizing, enriching with context, and correlating into process steps.

### Alt text
Diagram showing business and shopfloor data sources being normalized and enriched with context (order/workpiece/station/time) via DSP and delivered as process steps to target systems (e.g., analytics/MES/ERP).

---

## Screen Spec / Implementation Notes (UC-00) — DE

### Ziel
UC-00 visualisiert das Prinzip „Event-to-Process“: technische Shopfloor-Events werden normalisiert, mit Business-Kontext angereichert und als prozessfähige Sicht bereitgestellt. **Umsetzung:** dynamische SVG-Generierung mit Step-Animation (konsistent zu den bestehenden Use-Case Cards/Step-Animationen im DSP/OSF); siehe [use-case-library](../../../02-architecture/use-case-library.md).

### Platzierung & Verlinkung
- **Primär:** OSF UI → DSP-Tab → Abschnitt „DSP Anwendungsfälle“ als zusätzliche Card „Interoperabilität (Event-to-Process)“.
- **Sekundär (optional):** Wiki-Use-Case-Seite (UC-00) enthält Diagramm + Kurzbeschreibung.
- **Verlinkung (optional, später):**
  - Klick auf die UC-Card → Scroll/Jump auf Detailbereich oder Öffnen einer Detail-Ansicht.
  - Wiki ↔ UI können wechselseitig verlinken, ohne OSF als „produktive Use-Case-App“ darzustellen.

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
  - *Aktionen* (Bullets): Normalisieren, Kontext anreichern, Event-Ketten korrelieren, Wiederverwendbarkeit statt Punkt-zu-Punkt.
  - *Smart Factory* (Bullets): Gemeinsames Prozessbild, Basis für Track & Trace/KPIs/AI/Closed Loops, Best-of-Breed Zielsysteme.
- **Konzept-Diagramm (optional im Detailbereich oder als eigenes Asset im Wiki)**
  - Sources → DSP Mediation (Normalize / Enrich / Correlate) → Process View / Targets

### Daten-/Begriffsmodell (für Konsistenz)
- Standardbegriffe (DE): **Event**, **Kontext**, **Order**, **Werkstück**, **Station**, **Zeit**, **Status**, **Prozessschritt**
- Ziel: Begriffe identisch in
  - Blog A1 (Abschnitt Interoperabilität)
  - UC-00 Seite
  - DSP-Tab Use Case Texten

### Icon/Assets
- Icon: vorhandenes **Interoperabilität-SVG** (CI-konform; Steuerrad mit 5 Speichen).
- Keine neuen Icon-Stile einführen.
- Diagramm-Farben/Typografie orientieren sich an bestehenden DSP-Visuals (OSF/DSP CI).

### Statische Implementierung (MVP)
- **Kein** Live-Datenbezug erforderlich.
- Inhalte werden als **statische Konfiguration** modelliert (z. B. JSON / i18n keys).
- DE/EN über i18n; Bilder getrennt je Sprache, falls Labels im Bild.

### Step-Animation (Umsetzung / Konzept)
- UC-00 nutzt wie alle Use-Cases die gemeinsame Step-Logik (Step-Controls, Highlighting, Auto-Dim).
- SVG wird dynamisch aus `uc-00-structure.config.ts` generiert; Steps steuern Sichtbarkeit/Highlight über `uc-00-event-to-process-map.steps.json`.

### Acceptance Criteria (MVP)
- UC-00 erscheint als zusätzliche Card im DSP Use-Case-Grid (DE/EN).
- Detailbereich zeigt Titel, One-liner, zwei Bullet-Listen, Disclaimer (DE/EN).
- Interoperabilität-Icon konsistent, keine neuen Stile.
- Optionales Diagramm (PNG/SVG) kann eingebunden werden, ohne UI-Refactoring.

---

## Screen Spec / Implementation Notes (UC-00) — EN

### Goal
UC-00 visualizes the “event-to-process” principle: raw shopfloor events are normalized, enriched with business context, and turned into a process-ready view. **Implementation:** dynamic SVG generation with step animation (aligned with existing DSP/OSF use-case cards and step animations); see [use-case-library](../../../02-architecture/use-case-library.md).

### Placement & Linking
- **Primary:** OSF UI → DSP tab → “DSP Use Cases” section as an additional card: “Interoperability (Event-to-Process)”.
- **Secondary (optional):** UC-00 wiki page hosts the diagram and a concise description.
- **Linking (optional, later):**
  - Click on the UC card → scroll/jump to the detail panel or open a detail view.
  - Cross-link wiki ↔ UI without positioning OSF as the productive use-case application.

### Visual Pattern (consistent with OSF/DSP)
- **Pattern aligned with existing DSP use cases (including step animation):**
  - **Top:** use-case cards (grid) with icon, title, one-liner.
  - **Detail panel:** “Actions” (left) + “Smart Factory” (right) as bullet lists.
  - **Footer disclaimer:** OSF is a demonstrator (conceptual; customer-specific implementation).

### Content Elements (static)
- **Use-case card (short)**
  - Title: *Interoperability (Event-to-Process)*
  - One-liner: *Normalize shopfloor events and enrich them with context—creating a shared process view for OT and IT.*
- **Detail panel**
  - *Actions* (bullets): normalize, enrich context, correlate event chains, reuse instead of point-to-point.
  - *Smart Factory* (bullets): shared process view, basis for track & trace/KPIs/AI/closed loops, best-of-breed target systems.
- **Concept diagram (optional in the detail panel or as a separate wiki asset)**
  - Sources → DSP mediation (Normalize / Enrich / Correlate) → Process view / targets

### Data/Terminology Model (for consistency)
- Standard terms (EN): **event**, **context**, **order**, **workpiece**, **station**, **time**, **status**, **process step**
- Keep terminology consistent across:
  - Blog A1 (interoperability section)
  - UC-00 page
  - DSP tab use-case texts

### Icon/Assets
- Icon: existing **Interoperability SVG** (CI-compliant; 5-spoke wheel).
- Do not introduce new icon styles.
- Diagram colors/typography follow existing DSP visuals (OSF/DSP CI).

### Static Implementation (MVP)
- No live data integration required.
- Content is modeled as **static configuration** (e.g., JSON / i18n keys).
- DE/EN via i18n; separate images per language if labels are embedded in the image.

### Step Animation (implementation / concept)
- UC-00 uses the shared step logic (step controls, highlighting, auto-dim) like all use cases.
- SVG is generated dynamically from `uc-00-structure.config.ts`; steps control visibility/highlighting via `uc-00-event-to-process-map.steps.json`.

### Acceptance Criteria (MVP)
- UC-00 appears as an additional card in the DSP use-case grid (DE/EN).
- Detail panel shows title, one-liner, two bullet lists, and the disclaimer (DE/EN).
- Interoperability icon is consistent; no new styles are introduced.
- Optional diagram (PNG/SVG) can be embedded without UI refactoring.

---

## Assets
- Diagram DE:

![uc-00-event-to-process-map-DE.svg](/.attachments/uc-00-event-to-process-map-DE-faa6ddc3-3b4a-4216-ac32-2717c8dd8ce3.svg)
- Diagram EN: 

![uc-00-event-to-process-map-EN.svg](/.attachments/uc-00-event-to-process-map-EN-3e8ad471-08cd-4359-b8a8-7ba9146ab332.svg)

---

## Open points / review notes
- [ ] Final labels for DE/EN (glossary alignment)
- [ ] Verify CTA wording (default: maturity check / Reifegrad-Check)
- [ ] Confirm whether the optional diagram is embedded in the OSF UI detail panel or only linked via wiki