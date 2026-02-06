# A2 – Artikel (DE Draft)

## Status
- Version: v2
- Owner: @<Oliver Berger>
- Review: <Tech Reviewer> / <MES-ERP Reviewer> / <Redaktion>
- Zieltermin: <Datum>
- Scope-Tag: LOGIMAT
- Feature: #69067
- UserStory: #69078

## Executive Summary (5 bullets)
- Track & Trace wird erst belastbar, wenn Shopfloor-Events eindeutig einem Werkstück zugeordnet und mit Business-Kontext verknüpft sind.
- **Konzept vs. Realität:** Wir unterscheiden zwischen der konzeptionellen "Partitur" (horizontaler Ablaufplan) und dem operativen "Live-Snapshot" (vertikale Historie).
- Der Schlüssel ist eine eindeutige Identität als Join-Key (z. B. Werkstück-ID/NFC), die wie der "Rote Faden" durch alle Systeme läuft.
- Genealogie bedeutet mehr als „Position“: Prozessschritte, Transfers, Lagerbewegungen und Qualität müssen zu einer Timeline korreliert werden.
- OSF zeigt Track & Trace bewusst als Live-Sicht – produktive Implementierungen werden kundenspezifisch entlang der Zielarchitektur umgesetzt.

## Arbeitstitel
Track & Trace, das trägt: Werkstückgenealogie durch Event-Korrelation und Business-Kontext

## Artikeltext (DE)

### 1. Warum Track & Trace in der Fertigung oft scheitert
Viele Unternehmen starten Track & Trace mit dem Ziel, Rückverfolgbarkeit schnell „sichtbar“ zu machen. In der Praxis bleibt es jedoch häufig bei Insellösungen: einzelne Stationen loggen Daten, Lagerbewegungen werden separat erfasst, Qualitätsprüfung dokumentiert Ergebnisse – aber ohne durchgängige Klammer. Das Ergebnis sind Lücken, Medienbrüche und im Reklamationsfall manuelle Ursachenanalyse.

### 2. Die Identität als roter Faden (Der NFC-Thread)
Echte Genealogie beantwortet nicht nur „wo ist das Werkstück“, sondern erzählt dessen ganze Geschichte.
Der Schlüssel ist eine eindeutige Identität als Join-Key – die **Werkstück-ID (NFC)**. 
Man kann sich das wie den "Roten Faden" in einem **Objekt-Gewebe** (siehe Visual 3) vorstellen: 
- Die Systeme (ERP, MES, WMS) bilden die Schichten oder Lanes.
- Die Werkstück-ID (NFC) ist der Faden, der diese Schichten verbindet.
Nur wo sich diese Ebenen und ID kreuzen (Events), entsteht ein belastbarer Knotenpunkt für die Timeline.

### 3. Die Partitur des Werkstücks: Plan vs. Realität
Um Track & Trace konzeptionell zu verstehen, nutzen wir das Bild einer **Partitur (Horizontaler Flow)**:
- **Events als Noten:** Jedes Ereignis ist ein fester Punkt auf dem Zeitstrahl. Architektonisch ist das Minimalset: `Timestamp + Station + Werkstück-ID + Result`.
- **Die Notenzeilen (Lanes):** Repräsentieren Systeme und Ressourcen (Stationen, FTS, Lager, Qualitätsprüfungen).
- **Die Melodie (Trace):** Der tatsächliche Weg des Werkstücks durch diese Zeilen.
- **Plan vs. Ist:** Im Idealfall folgt die Melodie genau den Noten (Plan/Order). In der Realität gibt es "Improvisationen": Umwege über ein FTS, Puffer-Zeiten im Lager oder Rework-Schleifen.
Unsere Genealogie-Lösung muss fähig sein, diese Abweichungen (Detours) nicht als Fehler, sondern als validen Teil der Historie ("Ist-Spur") abzubilden, während der ursprüngliche Plan ("Soll-Spur") als Referenz erhalten bleibt.

### 4. Integration in ERP/MES/Analytics – Best-of-Breed als Prinzip
Genealogie wird besonders wertvoll, wenn sie mit Business-Kontext verbunden ist: Customer Order, Lieferant/Purchase Order, ERP-IDs, Qualitätsanforderungen. Welche Zielsysteme genutzt werden (ERP, MES, Analytics) ist kundenspezifisch – entscheidend ist, dass die Shopfloor-Korrelation wiederverwendbar bleibt. SAP kann ein Zielsystem-Beispiel sein, ist aber keine Voraussetzung.

### 5. OSF als Proof: Der Live-Snapshot
Während die "Partitur" (Visual 1) das Konzept und die Logik erklärt, zeigt der **OSF Live-Screen** (Visual 2) die Realität im "Hier und Jetzt".
Hier wechseln wir die Perspektive von horizontal (Prozess) auf vertikal (Historie):
- Eine **Werkstückliste** zeigt den aktuellen Status.
- Die **Event-Timeline** wächst stetig von oben nach unten (wie ein Chat-Verlauf). Die unveränderliche Historie sichert dabei die Auditierbarkeit.
- Der **Order-Kontext** ist fest angeheftet.
Dies dient als Proof, dass Events und Kontext über die Werkstück-ID (NFC) live „joinbar“ sind. Wichtig bleibt die Abgrenzung: OSF ist ein Demonstrator – produktive End-to-End-Lösungen werden entlang der Systemlandschaft des Kunden umgesetzt.

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

### Visual 1: Die Konzept-Partitur (Concept Diagram)
- **Datei:** `docs/assets/use-cases/uc-01/diagrams/Track-Trace_Concept_Partiture.drawio` (Export als PNG)
- **Bildunterschrift:** Die "Partitur" eines Werkstücks: Der horizontale Pfad (Ist-Spur) zeigt den Verlauf durch Stationen, Lager und FTS-Transporte, korreliert mit den geplanten Business-Phasen und Orders (Soll-Spur).
- **Zweck:** Zeigt die komplexe Logik von Plan vs. Ist und die Rolle des NFC-Tags als verbindendes Element.

### Visual 2: OSF Proof – Track & Trace Live Screen (DE)
- **Datei:** `/.attachments/UC-01-Track-Trace-DE-c90e6006-233c-403d-88ba-ad686733a654.png`
- **Bildunterschrift:** Die operative Sicht im OSF: Eine vertikale Timeline zeigt Events in Echtzeit, verknüpft mit dem Business-Kontext (rechts).
- **Zweck:** Beweis der technischen Machbarkeit (Live-Demo).

### Visual 3: Das Objekt-Gewebe (Domain Model)
- **Datei:** `docs/assets/products/common/domain-model/ObjectMesh_ER_simplified.drawio` (Export als PNG)
- **Bildunterschrift:** Das "Gewebe" unter der Oberfläche: Die SinglePart-Identität (NFC) verbindet Aufträge (Manufacturing Order), Transporte (Transport Order) und Qualitätsdaten.
- **Zweck:** Zeigt IT-Architekten das Datenmodell hinter der Timeline.

## Offene Punkte / Review Notes

- [ ] CTA-Entscheidung: Option 1 / 2 / 3
- [ ] Finaler OSF Track&Trace Screenshot (DE) auswählen und Cropping festlegen
- [ ] EN-Screenshot counterpart prüfen (Labels im Bild)
- [ ] SAP-Beispiele prüfen („SAP als Beispiel“ konsistent)
