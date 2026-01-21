# A2 – Artikel (DE Draft)

## Status
- Version: v1
- Owner: @<Oliver Berger>
- Review: <Tech Reviewer> / <MES-ERP Reviewer> / <Redaktion>
- Zieltermin: <Datum>
- Scope-Tag: LOGIMAT
- Feature: #69067
- UserStory: #69078

## Executive Summary (5 bullets)
- Track & Trace wird erst belastbar, wenn Shopfloor-Events eindeutig einem Werkstück zugeordnet und mit Business-Kontext verknüpft sind.
- Ohne konsistente Identitäten (z. B. NFC/Workpiece-ID) entstehen Lücken, Doppelwahrheiten und hoher manueller Abstimmungsaufwand.
- Genealogie bedeutet mehr als „Position“: Prozessschritte, Transfers, Lagerbewegungen und Qualität müssen zu einer Timeline korreliert werden.
- Best-of-Breed bleibt zentral: ERP/MES/Analytics können variieren; SAP ist ein Beispiel, nicht Voraussetzung.
- OSF zeigt Track & Trace bewusst als Live-Sicht (aktueller Systemzustand) – produktive Implementierungen werden kundenspezifisch entlang der Zielarchitektur umgesetzt.

## Arbeitstitel
Track & Trace, das trägt: Werkstückgenealogie durch Event-Korrelation und Business-Kontext

## Artikeltext (DE)

### 1. Warum Track & Trace in der Fertigung oft scheitert
Viele Unternehmen starten Track & Trace mit dem Ziel, Rückverfolgbarkeit schnell „sichtbar“ zu machen. In der Praxis bleibt es jedoch häufig bei Insellösungen: einzelne Stationen loggen Daten, Lagerbewegungen werden separat erfasst, Qualitätsprüfung dokumentiert Ergebnisse – aber ohne durchgängige Klammer. Das Ergebnis sind Lücken, Medienbrüche und im Reklamationsfall manuelle Ursachenanalyse.

### 2. Was „Genealogie“ wirklich bedeutet – und warum Identitäten entscheidend sind
Echte Genealogie beantwortet nicht nur „wo ist das Werkstück“, sondern:
- **Welche Prozessschritte** hat es durchlaufen?
- **Welche Transfers/Lagerbewegungen** gab es (FTS/AGV, HBW etc.)?
- **Welche Qualitätsentscheidungen** wurden getroffen – und auf Basis welcher Daten?

Der Schlüssel ist eine eindeutige Identität als Join-Key – z. B. **NFC/Workpiece-ID**. Nur wenn Events konsistent entlang dieser ID korreliert werden, entsteht eine belastbare Timeline.

### 3. Vom Shopfloor-Event zur Werkstück-Timeline
Track & Trace entsteht durch Korrelation:
- **Shopfloor-Events** (Start/Ende/Status), Bearbeitungszeiten, Transfers
- **Logistikbewegungen** (Pick/Drop, Lager ein/aus)
- **Qualitätsereignisse** (z. B. AIQS Checks)
- **Business-Kontext** (Production Order, Customer Order, Material/Batch, ERP-IDs)

Damit wird aus „Signalen“ ein Prozessbild, das IT und OT gleichermaßen verstehen.

### 4. Integration in ERP/MES/Analytics – Best-of-Breed als Prinzip
Genealogie wird besonders wertvoll, wenn sie mit Business-Kontext verbunden ist: Customer Order, Lieferant/Purchase Order, ERP-IDs, Qualitätsanforderungen. Welche Zielsysteme genutzt werden (ERP, MES, Analytics) ist kundenspezifisch – entscheidend ist, dass die Shopfloor-Korrelation wiederverwendbar bleibt. SAP kann ein Zielsystem-Beispiel sein, ist aber keine Voraussetzung.

### 5. OSF als Proof: Live-Track-&-Trace statt statischem Mock
In OSF wird Track & Trace nicht nur als Konzeptfolie gezeigt, sondern als **Live-Sicht**: eine Werkstückliste mit Ereignishistorie und Order-Kontext macht die Kopplung von Shopfloor-Events und Business-Daten unmittelbar sichtbar. Wichtig bleibt die Abgrenzung: OSF ist ein Demonstrator – produktive End-to-End-Lösungen werden entlang der Systemlandschaft des Kunden umgesetzt.

### 6. Ausblick: Sensorik und „3 Datentöpfe“ (UC-02)
Sensor- und Umweltdaten (z. B. Temperatur, Vibration, Energie) erhöhen den Mehrwert in der Ursachenanalyse – sie gehören jedoch nicht in die Kernlogik der Genealogie. Dieses Thema wird als Datenaggregation/Korrelation in **UC-02 (3 Datentöpfe)** behandelt.

### 7. Nächster Schritt: Track & Trace Readiness Check
Wenn Track & Trace bei Ihnen priorisiert ist, klären wir im Readiness Check:
- Welche Identitäten/Keys sind vorhanden (Workpiece, Order, Station)?
- Welche Events fehlen bzw. sind nicht eindeutig zuordenbar?
- Welche Zielsysteme sollen angebunden werden (ERP/MES/Analytics)?
Daraus leiten wir einen pragmatischen Pilot ab, der schnell Nutzen zeigt und skalierbar bleibt.

Call to Action: Sprechen Sie uns an für einen Track & Trace Readiness Check – wir planen den nächsten sinnvollen Schritt gemeinsam und setzen ihn pragmatisch um.

## CTA (Optionen – Auswahl im Review)

**Option 1 (Standard, A2): Track & Trace Readiness Check**
„In einem kompakten Track & Trace Readiness Check identifizieren wir Daten- und Integrationslücken und leiten den sinnvollsten nächsten Schritt für belastbare Genealogie ab.“

**Option 2: Traceability Workshop**
„In einem Traceability Workshop priorisieren wir Use Cases (Recall, Compliance, RCA) und definieren die Zielarchitektur für eine skalierbare Track-&-Trace-Lösung.“

**Option 3 (eventbezogen): Messe-/Demo-CTA**
„Treffen Sie uns auf der LogiMAT: Wir zeigen live, wie Werkstückgenealogie aus Events und Business-Kontext entsteht – und leiten daraus Ihren nächsten Schritt ab.“

## Visuals (Einbindung)

### Visual 1: UC-01 (Wiki-Template)
- Link: [UC-01 — Track & Trace Genealogy (A2) - Overview](https://dev.azure.com/ORBIS-AG-SAP/Modellfabrik/_wiki/wikis/Modellfabrik.wiki/8416/UC-01-%E2%80%94-Track-Trace-Genealogy-(A2))
- Caption DE: Track & Trace Genealogie entsteht durch Korrelation von Station-, Logistik- und Qualitätsereignissen entlang einer eindeutigen Werkstück-ID – angereichert um Business-Kontext.
- Alt-Text DE: Konzeptbeschreibung von Track & Trace Genealogie als Timeline pro Werkstück mit Order-Kontext.
- vorläufige Version ![UC-01-Track-Trace-Schema.png](/.attachments/UC-01-Track-Trace-Schema-75c953d7-4e2d-488c-8585-8393349b88ec.png)

### Visual 2: OSF Proof – Track & Trace Live Screen (DE)
- Datei/Link: ![UC-01-Trrack-Trace-DE.png](/.attachments/UC-01-Trrack-Trace-DE-c90e6006-233c-403d-88ba-ad686733a654.png)
- Caption DE: OSF Track & Trace (Live): Werkstückliste, Ereignishistorie und Order-Kontext zeigen die Kopplung von Shopfloor-Events und Business-Daten.
- Alt-Text DE: Screenshot aus OSF mit Workpiece-Liste, Event History und Order Context.

## Offene Punkte / Review Notes
- [ ] CTA-Entscheidung: Option 1 / 2 / 3
- [ ] Finaler OSF Track&Trace Screenshot (DE) auswählen und Cropping festlegen
- [ ] EN-Screenshot counterpart prüfen (Labels im Bild)
- [ ] SAP-Beispiele prüfen („SAP als Beispiel“ konsistent)
