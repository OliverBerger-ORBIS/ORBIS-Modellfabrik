# UC-01 — Track & Trace Genealogy (A2)

## Status
- Owner: @<Oliver Berger>
- Scope: OSF-BLOG-2026
- Messe-Tag: LOGIMAT
- Referenziert in: A2 (DE/EN Draft) #69078 und #69079
- Feature: #69067
- User Stories: #69087

---

## DE

### Titel
**Track & Trace Genealogie**

### One-liner
Werkstückgenealogie in (nahezu) Echtzeit: Wo ist was passiert – und warum?

### Kundennutzen (3)
- End-to-End Traceability über Stationen, FTS/AGV, Lagerbewegungen und Qualität
- Schnellere Ursachenanalyse bei Qualitätsabweichungen, Reklamationen und Störungen
- Basis für Compliance, Rückrufmanagement und kontinuierliche Prozessoptimierung

### Pain Points (3)
- Werkstückdaten sind verteilt und zeitlich nicht konsistent synchronisiert
- Shopfloor-Events fehlen oder sind nicht eindeutig einem Werkstück zuordenbar
- Qualitätsinformationen liegen vor, sind aber nicht sauber mit Prozess- und Logistikereignissen korreliert

### Datenquellen
- **Business (ERP/MES):** Produktionsauftrag / Customer Order, Material/Batch, Qualitätsanforderungen, relevante Entitäten (z. B. ERP-ID, Kunde, Lieferant, Purchase Order / Wareneingang)
- **Shopfloor:** eindeutige Werkstück-/NFC-Identifikation, Stations-Events (Start/Ende/Status), Bearbeitungszeiten, FTS/AGV-Transfers, Lagerbewegungen (z. B. HBW), Qualitätsereignisse (z. B. AIQS)
- **Sensorik / Umwelt (optional, nicht Kern von UC-01):** Korrelation wird in UC-02 (Datenaggregation) vertieft

### KPI / Outcome-Bezug
FPY / Ausschussquote, Reklamationskosten, Durchlaufzeit, Rückverfolgbarkeitsabdeckung (Traceability Coverage)

### Orchestrierung / Systeminteraktion
Kernprinzip ist die eindeutige Identifikation des Werkstücks (z. B. NFC-Tag/Workpiece-ID) als „Join-Key“.  
Shopfloor-Events (Station/FTS/Lager/Qualität) werden entlang dieser ID zu einer lückenlosen Timeline korreliert und mit Business-Kontext (Order, Material/Batch, Kunde/Lieferant, ERP-IDs) angereichert.  
Ergebnis ist eine Genealogie (Werkstück → Prozess-/Logistikschritte → Prüfungen → Entscheidungen), die Ursachenanalysen, Compliance/Rückruf und Rückmeldungen in Zielsysteme (ERP/MES/Analytics) ermöglicht.

### Demonstrator vs. produktive Lösung (Pflicht)
Die ORBIS SmartFactory (OSF) dient als Demonstrator, um Datenflüsse, Zustände und Integrationsprinzipien anschaulich zu machen. In UC-01 wird jedoch bewusst ein **Live-Screen** genutzt: Er zeigt die jeweils aktuelle Werkstück-Timeline aus dem System und macht so den Mehrwert der Event- und Kontextkopplung unmittelbar sichtbar. Produktive End-to-End-Implementierungen (ERP/MES/Analytics) werden je nach Zielumgebung kundenspezifisch umgesetzt.

### CTA
**Track & Trace Readiness Check (Daten- & Prozess-Assessment)**

### Caption
Track & Trace entsteht durch die Korrelation von Events, Logistikbewegungen und Qualitätsinformationen zu einer Werkstück-Timeline – angereichert um Business-Kontext.

### Alt-Text
OSF-Ansicht mit Werkstückliste, Ereignishistorie (Timeline) und Order-Kontext, die Prozess-, Logistik- und Qualitätsinformationen verknüpft.

---

## EN

### Title
**Track & Trace Genealogy**

### One-liner
Near real-time genealogy: where did what happen—and why?

### Benefits (3)
- End-to-end traceability across stations, AGVs, warehouse movements, and quality
- Faster root-cause analysis for deviations, complaints, and disruptions
- Foundation for compliance, recall readiness, and continuous process improvement

### Pain points (3)
- Data is fragmented and not time-consistent across sources
- Shopfloor events are missing or cannot be uniquely linked to a workpiece
- Quality results exist but are not cleanly correlated with process and logistics events

### Data sources
- **Business (ERP/MES):** production order / customer order, material/batch, quality requirements, related entities (e.g., ERP IDs, customer, supplier, purchase order / goods receipt)
- **Shopfloor:** unique workpiece identification (e.g., NFC/workpiece ID), station events (start/end/status), processing times, AGV transfers, warehouse movements, quality events (e.g., AIQS)
- **Sensors / environment (optional, not core for UC-01):** correlation is covered in UC-02 (data aggregation)

### KPI / Outcome
FPY / scrap rate, complaint cost, lead time, traceability coverage

### Orchestration / interaction
The key principle is a unique workpiece identifier (e.g., NFC/workpiece ID) used as the join key.  
Shopfloor events (station/AGV/warehouse/quality) are correlated into a complete timeline along that ID and enriched with business context (order, material/batch, customer/supplier, ERP IDs).  
The result is a genealogy (workpiece → process/logistics steps → inspections → decisions) enabling root-cause analysis, compliance/recall, and feedback into target systems (ERP/MES/analytics).

### Demonstrator vs. productive solution (mandatory)
The ORBIS SmartFactory (OSF) is a demonstrator used to showcase data flows, states, and integration principles. For UC-01, we deliberately use a **live screen**: it displays the current workpiece timeline from the system, making the value of event-to-context correlation tangible. Productive end-to-end implementations (ERP/MES/analytics) are delivered customer-specifically depending on the target landscape.

### CTA
**Track & Trace readiness check (data & process assessment)**

### Caption
Track & Trace is enabled by correlating events, logistics moves, and quality results into a workpiece timeline—enriched with business context.

### Alt text
OSF view showing a workpiece list, event history (timeline), and order context linking process, logistics, and quality information.

---

## Screen Spec / Implementation Notes (UC-01) — DE/EN

### Ziel
UC-01 macht Track & Trace als Werkstück-Genealogie sichtbar: eine Timeline aus Shopfloor-Events, Logistikbewegungen und Qualitätsresultaten, angereichert mit Business-Kontext.

### OSF-Umsetzung (Live statt statisch)
- UC-01 ist **kein statisches Mock**, sondern zeigt **jeweils aktuelle Systeminformationen** (Live oder Replay-Session, abhängig vom OSF-Environment).
- Der Screen dient als Proof, dass Events und Kontext über eine Workpiece-ID/NFC „joinbar“ sind und damit echte Traceability möglich wird.

### UI-Pattern (bestehender Screen)
1) **Tracked Workpieces (Liste)**: Workpiece-ID, aktueller Ort/Station, Anzahl Events  
2) **Event History**: Timeline/Swimlane, gruppiert nach Domain (Shopfloor/Logistik/Qualität), inkl. Zeitstempel  
3) **Order Context**: Production/Customer Order, ERP-ID, Kunde, Start/Delivery, relevante Felder

### Join-Key-Prinzip (Pflicht)
- Workpiece-ID/NFC muss als verbindendes Element zwischen Timeline und Order Context klar erkennbar sein (Badges/Chips/Labels).
- In Events sollten referenzierte IDs (Workpiece, Order, Station) konsistent dargestellt werden.

### Scope-Abgrenzung
- **In Scope UC-01:** Timeline + Business-Panel + Korrelationsprinzip (Workpiece-ID/NFC → Order Context).
- **Out of Scope UC-01:** Sensor-/Umweltdaten-Korrelation (UC-02).

### i18n / Assets
- DE/EN via i18n (Labels/Field names).
- Wenn Screenshots in Blog/Wiki genutzt werden: je Sprache eigenes Bild, wenn Labels im Bild enthalten sind.

### Optional: SVG-Animation (später)
- Nicht erforderlich für UC-01, da Live-Screen bereits erklärstark ist.
- Falls ein „Explain Mode“ gewünscht ist: Step-by-step Highlighting analog DSP-Architecture (Workpiece → Station → Logistics → Quality → Full genealogy).

### Acceptance Criteria
- UC-01 Screen funktioniert im Live- und Replay-Environment und zeigt aktuelle Timeline/Order Context.
- Workpiece-ID/NFC und Order-IDs sind nachvollziehbar verknüpft.
- DE/EN Labels sind konsistent; Wiki/BLog nutzen sprachspezifische Screenshots.

---

## Visuals / Assets
- OSF Track & Trace Live Screen (DE): ![UC-01-Trrack-Trace-DE.png](/.attachments/UC-01-Trrack-Trace-DE-c3340b70-01c3-4d29-a5b9-892e740f9af7.png)
- OSF Track & Trace Live Screen (EN): ![UC-01-Trrack-Trace-EN.png](/.attachments/UC-01-Trrack-Trace-EN-d487b1a0-6ac8-472f-a051-a23f9d3df22d.png)
- Hinweis: Die Screens werden als „Proof Visual“ primär in Artikel A2 verwendet.
