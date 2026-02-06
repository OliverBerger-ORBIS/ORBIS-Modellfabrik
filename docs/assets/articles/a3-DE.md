# A3 – Artikel (DE Draft)

## Status
- Version: v1
- Owner: @<Oliver Berger>
- Review: <Tech Reviewer> / <MES-ERP Reviewer> / <Redaktion>
- Zieltermin: <Datum>
- Scope-Tag: LOGIMAT
- Feature: #69068
- UserStory: #69081 und #69082

## Executive Summary (5 bullets)
- KPIs werden erst dann belastbar, wenn Business-, Shopfloor- und (optional) Umwelt-/Sensordaten in einem gemeinsamen Kontext zusammengeführt sind.
- Ohne Kontext (Order/Werkstück/Station/Zeit) bleiben Zahlen erklärungsbedürftig und führen zu KPI-Diskussionen statt Entscheidungen.
- DSP übernimmt die vermittelnde Rolle: Streams harmonisieren, Kontext anreichern, Ereignisse korrelieren – zielsystemoffen (Best-of-Breed).
- Eine Analytics-App/Use-Case-Konsument entscheidet, welche Zielplattform genutzt wird (Cloud/IIoT/BI/MES/ERP) – SAP ist ein Beispiel, nicht Voraussetzung.
- OSF zeigt das Prinzip als Demonstrator: Datenpools, Kontextmodell und Outcomes (KPIs/RCA/AI) werden anschaulich; produktive Umsetzungen sind kundenspezifisch.

## Arbeitstitel
Belastbare KPIs statt Zahlendiskussionen: Drei Datentöpfe als Basis für erklärbare Analytik

## Artikeltext (DE)

### 1. Warum KPI-Transparenz in der Praxis oft scheitert
Viele Fertigungsunternehmen messen viel – und entscheiden dennoch zu langsam. Der Grund ist selten ein fehlender KPI. Das Problem ist die fehlende gemeinsame Datenbasis: OT-Daten stehen isoliert, Business-Kontext fehlt, und Umwelt-/Sensordaten werden nicht korreliert. So entstehen KPI-Diskussionen („Welche Zahl stimmt?“) statt handlungsfähiger Erkenntnisse.

### 2. Drei Datentöpfe – ein Kontextmodell: der Unterschied zwischen Messen und Verstehen
Belastbare KPIs entstehen, wenn drei Datenwelten zusammengeführt werden:
- **Business-Kontext**: Kunden-/Produktionsaufträge, Material/Charge, Plan/Vorgang, ERP-Referenzen (z. B. Supplier/PO)
- **Shopfloor-Prozessdaten**: Stations-Events, Zustände, Zeiten, Qualität (AIQS), FTS-Transfers, Lagerbewegungen
- **Umwelt/Sensorik (optional)**: Energie, Temperatur/Feuchte, Vibration

Der entscheidende Schritt ist das **gemeinsame Kontextmodell**: Order ↔ Werkstück-ID (NFC) ↔ Station ↔ Zeit. Erst dadurch werden Zahlen erklärbar.

### 3. DSP als Vermittler: Harmonisierte Streams statt Insellösungen
DSP übernimmt die vermittelnde Rolle zwischen Quellen und Konsumenten:
- **Normalize**: Semantik und Formate harmonisieren
- **Enrich**: Kontext anreichern (IDs, Zeit, Zuordnung)
- **Correlate**: Ereignisse zu Ketten und Prozessschritten verbinden

Damit werden neue Use Cases nicht jedes Mal neu verdrahtet, sondern setzen auf einer wiederverwendbaren Basis auf.

### 4. Best-of-Breed in der Praxis: Zielplattform je nach Bedarf
Nicht jedes Unternehmen hat die gleiche Zielarchitektur. Entscheidend ist, dass die Daten produktiv nutzbar werden – unabhängig davon, ob die Auswertung in einer Cloud-Analytics-Lösung, einer IIoT-Plattform, einem Data Lake/BI oder (optional) über Rückkopplung in MES/ERP erfolgt. SAP-Produkte können konkrete Zielsysteme sein – sind aber nur Beispiele innerhalb einer offenen Architektur.

### 5. Outcomes: von KPIs zu erklärbarer Ursachenanalyse und AI Enablement
Mit einem gemeinsamen Kontextmodell werden KPIs nicht nur sichtbar, sondern interpretierbar:
- **OEE** inkl. Stillstandsgründen
- **FPY / Ausschussquote** und Nacharbeit
- **Energie pro Werkstück/Los**
- **Durchlaufzeit / WIP** und Engpassindikatoren
Darauf aufbauend wird **Root-Cause Analysis** möglich – und perspektivisch AI-gestützte Mustererkennung, weil Daten und Kontext konsistent vorliegen.

### 6. OSF als Proof: Prinzip zeigen, Umsetzung skalieren
OSF ist ein Messe- und Kunden-Demonstrator. Er zeigt, wie die drei Datentöpfe zusammengeführt werden und wie DSP als Vermittler wirkt. Wichtig bleibt die Abgrenzung: OSF ist nicht die produktive KPI- oder Analytics-Anwendung – sondern macht die Architekturprinzipien greifbar, auf denen kundenspezifische Lösungen aufsetzen.

### 7. Nächster Schritt: KPI & Data Readiness Check
Wenn KPI-Transparenz oder AI-Analysen bei Ihnen priorisiert sind, starten wir typischerweise mit einem Readiness Check:
- Welche Datenquellen sind vorhanden – und welche fehlen?
- Welche Keys/IDs und welcher Kontext sind notwendig (Order/Werkstück/Station/Zeit)?
- Welche Zielplattformen sollen angebunden werden (Best-of-Breed)?
Daraus entsteht eine Roadmap mit einem Pilot, der schnell Nutzen zeigt und skalierbar bleibt.

Call to Action: Sprechen Sie uns an für einen KPI & Data Readiness Check – wir planen den nächsten sinnvollen Schritt gemeinsam und setzen ihn pragmatisch um.

## CTA (Optionen – Auswahl im Review)

**Option 1 (Standard, A3): KPI & Data Readiness Check**
„In einem kompakten KPI & Data Readiness Check identifizieren wir Daten- und Integrationslücken und definieren den nächsten sinnvollen Schritt zu belastbaren KPIs.“

**Option 2: KPI-to-Action Workshop**
„Im KPI-to-Action Workshop definieren wir priorisierte KPIs, notwendige Kontext-Keys und leiten konkrete Maßnahmen/Use Cases (RCA, Closed Loops) ab.“

**Option 3 (eventbezogen): Messe-/Demo-CTA**
„Treffen Sie uns auf der LogiMAT/Hannover Messe: Wir zeigen live, wie drei Datentöpfe und DSP belastbare KPIs ermöglichen – und leiten daraus Ihren nächsten Schritt ab.“

## Visuals (Einbindung)

### Visual 1: Die Architektur (3 Datentöpfe & DSP)
Dieses Hauptdiagramm visualisiert den Kern des Artikels: Business, Shopfloor und Environment fließen zusammen.
- **Variante A (Konzept):** `docs/assets/use-cases/uc-02/diagrams/UC-02_3-Data-Pools_Concept.drawio` (Export als PNG)
- **Variante B (Lanes):** `docs/assets/use-cases/uc-02/diagrams/UC-02_3-Data-Pools_Architecture_Lanes.drawio` (Export als PNG)
- **Caption DE:** Best-of-Breed Datenaggregation: DSP vermittelt zwischen Datenpools und Zielplattformen – KPIs werden erklärbar und steuerbar.
- **Alt-Text DE:** Schematische Darstellung von Business/Shopfloor/Umwelt-Datenbanken, DSP-Kontextschicht und auswählbaren Zielplattformen.

### Visual 2: Die Logik (Das Objekt-Geflecht)
Hier greifen wir den Gedanken aus Artikel 2 auf: Die Daten ergeben nur Sinn, wenn sie über Order, Werkstück und Station verknüpft sind.
- **Datei:** `docs/assets/use-cases/uc-01/diagrams/ObjectMesh_ER.drawio` (oder `ObjectMesh_ER_simplified.png`)
- **Caption DE:** Das Kontextmodell verbindet die Welten: Eine Order besteht aus Werkstücken (Shopfloor), die an Stationen bearbeitet werden (Environment/Energy).
- **Alt-Text DE:** Entity-Relationship-Darstellung der Verbindungen zwischen Order, Batch, Unit, Station und Sensor-Events.

### Visual 3: Der Beweis (OSF Screenshot)
Wir zeigen, dass die Theorie in der Praxis (OSF) als echter Datenstrom existiert.
- **Motiv:** "OSF Message Monitor" oder "Order Detail View"
- **Warum:** Der Message Monitor zeigt live, wie Sensor-Werte und Order-IDs in einer JSON-Nachricht (DSP Result) zusammenkommen.
- **Caption DE:** Ein Blick in den Maschinenraum: OSF zeigt live, wie Prozess-Events mit Order-Kontext angereichert werden.
- **Alt-Text DE:** Screenshot des OSF Message Monitors mit JSON-Payloads, die Temperatur, Sensorwerte und Auftragsnummern enthalten.

## Offene Punkte / Review Notes
- [ ] CTA-Entscheidung: Option 1 / 2 / 3
- [ ] Auswahl der OSF Proof Screens (DE/EN) und Cropping festlegen
- [ ] Begrifflichkeiten konsistent (FTS, Werkstück-ID, Environment/Sensorik) - ✅
- [ ] SAP-Beispiele prüfen („SAP als Beispiel“ konsistent)
