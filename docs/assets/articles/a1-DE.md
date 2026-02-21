# A1 – Artikel (DE Draft)

## Status
- Version: v3
- Owner: @<Oliver Berger>
- Review: <Tech Reviewer> / <MES-ERP Reviewer> / <Redaktion>
- Zieltermin: <Datum>
- Scope-Tag: LOGIMAT
- Feature: #69066
- UserStory: #69072

## Executive Summary (5 bullets)
- Viele Smart-Factory-Initiativen scheitern nicht an Ideen, sondern an Integrationskomplexität zwischen IT und OT.
- Use Cases (Track & Trace, KI-Analysen, Closed Loops) werden erst möglich, wenn Events und Prozesskontext konsistent vorliegen.
- Interoperabilität reduziert Punkt-zu-Punkt-Integration und schafft eine gemeinsame Sprache für Systeme und Teams.
- Best-of-Breed bleibt zentral: ERP/MES/Analytics können variieren; SAP ist ein Beispiel, nicht Voraussetzung.
- Mit einem 5-Phasen-Vorgehensmodell holen wir Kunden je nach Reifegrad ab und setzen den nächsten sinnvollen Schritt gemeinsam um.

## Arbeitstitel
Vom IT/OT-Bruch zur Use-Case-Fähigkeit: Interoperabilität als Fundament der Smart Factory

## Artikeltext (DE)

### 1. Warum IT/OT-Integration jetzt geschäftskritisch ist
In vielen Fertigungsunternehmen sind Daten vorhanden – aber sie sind nicht so verfügbar, dass man daraus verlässlich steuern kann. Typische Symptome: unterschiedliche „Wahrheiten“ über Status und Leistung der Produktion, manueller Abstimmungsaufwand, Medienbrüche und verzögerte Reaktionen bei Qualitäts- oder Störfällen.

Das Kernproblem liegt selten in der einzelnen Maschine oder in einer einzelnen Software. Es liegt in den Brüchen zwischen IT und OT: heterogene Protokolle, unterschiedliche Datenmodelle, isolierte Inseln. Das Ergebnis ist ein hoher Aufwand, sobald ein neuer Use Case oder ein neues System hinzommt – und damit eine Smart Factory, die zwar viele Daten besitzt, aber nur langsam lernt und noch langsamer skaliert.

### 2. Use Cases umsetzen – aber auf einem skalierbaren Fundament
Der schnelle Reflex lautet oft: „Wir brauchen Track & Trace“, „Wir wollen Predictive Maintenance“, „Wir setzen KI ein“. Diese Ziele sind richtig – aber in der Praxis werden sie häufig als Einzellösungen umgesetzt. Dann entsteht eine Landschaft aus Punkt-zu-Punkt-Integrationen: Jeder Use Case verdrahtet Datenquellen, Zustände und Entscheidungen erneut.

Das kann kurzfristig demonstrierbar sein – langfristig wird es teuer: Änderungen im Shopfloor, neue Stationen oder neue Anforderungen (z. B. Audits) führen zu aufwändigen Anpassungen.

Der robuste Weg ist deshalb: Use Cases **gezielt** realisieren, aber auf einer wiederverwendbaren Basis. Use-Case-Fähigkeit entsteht durch ein Fundament aus:
- **Interoperabilität** (Systeme können herstellerunabhängig miteinander sprechen),
- **Events** (was passiert wann, wo, mit welchem Objekt),
- **Kontext** (Order/Werkstück/Station/Qualität) und
- **Governance** (Versionierung, Verantwortlichkeiten, Auditierbarkeit).

### 3. Interoperabilität als Architekturprinzip
Interoperabilität ist mehr als „ein System kann Daten senden“. In der Fertigung bedeutet es, technische Signale und Statusmeldungen so zu normalisieren und zu kontextualisieren, dass sie prozessfähig werden. Erst dann können Teams und Systeme eine gemeinsame Sicht auf die Produktion aufbauen – unabhängig davon, ob die Daten aus Maschinen, Sensoren, FTS oder aus IT-Systemen stammen.

**Marketing-Definition (konsistent):** Interoperabilität bedeutet, dass unterschiedliche Systeme, Maschinen, Softwarelösungen und Datenquellen reibungslos miteinander kommunizieren und Informationen nahtlos austauschen können – ohne Sonderprogrammierung, Medienbrüche oder proprietäre Abhängigkeiten.

Merksatz: **„Interoperabilität wird nicht programmiert – sie wird aktiviert.“** 

Der entscheidende Effekt: Interoperabilität reduziert Punkt-zu-Punkt-Integration und schafft eine wiederverwendbare **Event-to-Process Logik**. Damit können neue Use Cases schneller umgesetzt werden, weil sie auf einer konsistenten Basis aufsetzen.

### 4. Anwendungs- und zielsystemoffen: Best-of-Breed in Kundenarchitekturen
Eine skalierbare Smart Factory muss unterschiedliche Zielarchitekturen unterstützen. Manche Unternehmen nutzen klassische ERP- und MES-Landschaften, andere setzen auf Cloud Analytics oder spezialisierte Plattformen. Entscheidend ist nicht das einzelne Produkt, sondern die Fähigkeit, Daten und Prozesse durchgängig zu verbinden.

Wir unterstützen daher den **Best-of-Breed Ansatz unserer Kunden**: ERP/MES/Analytics werden integriert, ohne dass die Shopfloor-Integration jedes Mal neu gebaut werden muss. SAP-Produkte können dabei konkrete Zielsysteme sein (z. B. SAP ERP oder SAP Digital Manufacturing) – sind aber nur Beispiele innerhalb einer offenen, anwendungs- und zielsystemoffenen Architektur.

### 5. ORBIS Vorgehensmodell in 5 Phasen: Reifegradbasiert zum nächsten Schritt
Damit die Transformation pragmatisch bleibt, arbeiten wir reifegradbasiert. Unser DSP-Vorgehensmodell ist mit gängigen Industrie-4.0-Reifegradlogiken kompatibel: **Konnektivität → Sichtbarkeit/Transparenz → Prognosefähigkeit → Adaptierbarkeit**. Wir nutzen diese Begriffe als Orientierung – und übersetzen sie in konkrete, umsetzbare Schritte entlang Ihrer Zielarchitektur.

![A1-ORBIS-Vorgehensmodell-DE.png](/.attachments/A1-ORBIS-Vorgehensmodell-DE-c75315af-2a6b-431a-9587-f157dcb02eeb.png)

Unser Vorgehen lässt sich in fünf Phasen beschreiben:

1) **Datenbasis & Konnektivität** *(Konnektivität)*  
   Relevante Quellen werden angebunden; Events werden verfügbar und beobachtbar.

2) **Datenintegration & Modellierung** *(Sichtbarkeit / Transparenz)*  
   Events werden normalisiert; Objekte (Order/Werkstück/Station) werden konsistent verknüpft – damit entsteht ein belastbarer Prozesskontext.

3) **Erweiterte Analytik & Intelligence** *(Prognosefähigkeit)*  
   KPIs, Ursachenanalyse und erste KI-gestützte Auswertungen werden möglich. (Klassische ML-Methoden können hier bereits genutzt werden.)

4) **Automation & Orchestration** *(Wirkung / geschlossene Regelkreise)*  
   Erkenntnisse führen zu Aktionen: Workflows, Closed Loops, Rückmeldungen in MES/ERP.

5) **Autonomes & Adaptives Unternehmen** *(Adaptierbarkeit)*  
   Kontinuierliche Optimierung über Linien/Standorte hinweg; Governance und Skalierung. (Hier entstehen zusätzliche Potenziale durch GenAI/Agenten als Assistenz und Orchestrierungsunterstützung.)

Der entscheidende Punkt: Nicht jedes Unternehmen startet in Phase 1. Wir klären gemeinsam, wo Sie stehen, welche Use Cases priorisiert werden – und welcher nächste Schritt in Architektur und Umsetzung wirklich sinnvoll ist.
### 6. ORBIS SmartFactory als Proof: Was heute sichtbar ist (und was nicht)
Die ORBIS SmartFactory (OSF) ist ein Messe- und Kunden-Demonstrator. Sie zeigt, wie Interoperabilität, Events und Kontext zusammenkommen und so Use-Case-Fähigkeit entsteht. Sichtbar sind beispielsweise Status- und Ereignisströme, Prozesszustände und die Grundlage für Korrelation.

Wichtig ist die Abgrenzung: OSF ist nicht die produktive Track-&-Trace- oder Analytics-Anwendung. Sie macht das Prinzip anschaulich, auf dem kundenspezifische Lösungen mit ERP/MES/Analytics aufbauen.

Im Zusammenspiel aus digitalem Shopfloor-Layout und realer Modellfabrik wird das Prinzip des digitalen Zwillings unmittelbar greifbar: Die visuelle Abbildung verknüpft den physischen Ablauf mit Zuständen und Ereignissen in der OSF. Genau diese Transparenz ist die Voraussetzung, um Use Cases später belastbar in kundenspezifische Zielarchitekturen zu integrieren.

### 7. Nächster Schritt: Reifegrad-Check und Roadmap
Wenn Sie aktuell Use Cases priorisieren, aber der Weg dorthin unklar ist, starten wir typischerweise mit einem Reifegrad-Check: Welche Daten sind vorhanden, welcher Kontext fehlt, und welche Integrationslogik ist wiederverwendbar? Daraus entsteht eine Roadmap mit einem Pilot, der schnell Nutzen zeigt – ohne später in einer Sackgasse zu enden.

Hinweis: Der Reifegrad-Check ist bewusst kompakt angelegt – mit klarem Ergebnisbild und einem pragmatischen Vorschlag für den nächsten umsetzbaren Schritt.

Call to Action: Sprechen Sie uns an für einen Reifegrad-Check oder ein Interoperability & Integration Assessment – wir planen den nächsten sinnvollen Schritt gemeinsam und setzen ihn pragmatisch um.

## CTA (Optionen – Auswahl im Review)

**Option 1 (Default, A1): Reifegrad-Check**  
„Lassen Sie uns gemeinsam Ihren Reifegrad bestimmen: In einem kompakten Reifegrad-Check identifizieren wir Daten- und Integrationslücken und leiten den sinnvollsten nächsten Schritt ab.“

**Option 2 (Vertiefung): Interoperability & Integration Assessment**  
„Für komplexere Zielarchitekturen bieten wir ein Interoperability & Integration Assessment an: Wir schaffen Transparenz über Ihre Systemlandschaft und definieren eine Integrationsarchitektur, die neue Use Cases beschleunigt.“

**Option 3 (eventbezogen): Messe-/Demo-CTA**  
„Treffen Sie uns auf der LogiMAT/Hannover Messe: Wir zeigen live, wie Interoperabilität und Orchestrierung Use-Case-Fähigkeit schaffen – und leiten daraus Ihren nächsten Schritt ab.“

## Architecture Note (optional)
In einer interoperablen Fertigungsarchitektur werden technische Events (z. B. Station „Start/End“, Transfer, Qualitätsresultat) normalisiert und mit Kontext (Order, Werkstück, Station, Zeit) verknüpft. Dadurch entsteht ein prozessfähiges Modell, das KPI-Berechnung, Ursachenanalyse und Orchestrierung ermöglicht. Edge-Komponenten unterstützen Realtime-Verarbeitung und lokale Reaktionen; Cloud-Komponenten unterstützen Training, Benchmarking und skalierbare Auswertung. Best-of-Breed bedeutet, dass ERP/MES/Analytics austauschbar bleiben; SAP kann ein Zielsystem sein, ist aber nicht Voraussetzung.

## Visuals (Einbindung)

### Visual 1a: Interoperabilität (Icon)
![edge-interoperability.svg](/.attachments/edge-interoperability-93cd0e6b-db6a-4d28-92c0-98c8a583100e.svg)

**Caption DE:** Interoperabilität: Unterschiedliche Systeme, Maschinen, Softwarelösungen und Datenquellen kommunizieren reibungslos und tauschen Informationen nahtlos aus – ohne Sonderprogrammierung, Medienbrüche oder proprietäre Abhängigkeiten („Interoperabilität wird nicht programmiert – sie wird aktiviert.“). 

**Alt-Text DE:** Icon „Interoperabilität“ als Steuerrad mit fünf Speichen (Mensch, Maschine, Anwendung, Prozesse, Operation/Steuerung) – steht für standardisierte Echtzeit-Kommunikation und nahtlosen Informationsaustausch zwischen IT und OT.

### Visual 1b: UC-00 – Event-to-Process Map (Foundation)
[UC-00 -- Interoperability](/blog%2Dseries%2D2026/05-–-Use%2DCase-Screens-\(UC%2D01…UC%2D06\)/UC%2D00-%2D%2D-Interoperability)


![uc-00-event-to-process-map-DE.svg](/.attachments/uc-00-event-to-process-map-DE-0fccb0a3-3ceb-45ab-8f06-58c23a838da4.svg)

- Caption DE: UC-00 (Foundation): Interoperabilität macht aus technischen Shopfloor-Events ein prozessfähiges Prozessbild – durch Normalisieren, Kontextanreicherung und Korrelation zu Prozessschritten.
- Alt-Text DE: Diagramm zeigt Datenquellen aus Business und Shopfloor, die über DSP normalisiert und mit Kontext (Order/Werkstück/Station/Zeit) angereichert werden und als Prozessschritte in Zielsysteme (z. B. Analytics/MES/ERP) fließen.

**Teaser (Serie / Outcomes aus Interoperabilität):**
UC-00 (Event-to-Process) ist die Foundation: Erst wenn Events normalisiert, mit Kontext angereichert und zu Prozessschritten korreliert sind, werden wiederverwendbare Use Cases möglich. In den Folgeartikeln zeigen wir diese Outcomes konkret:
- **A2 / UC-01 – Track & Trace Genealogie:** Live-Historie pro Werkstück über Werkstück-ID/NFC als Join-Key (OSF-Proof).
- **A3 / UC-02 – 3 Datentöpfe:** Business-, Shopfloor- und Umweltdaten werden im Kontextmodell zusammengeführt – dadurch werden KPIs erklärbar und Analytik/AI skalierbar.
- **A3 / UC-06 – Process Optimization (geplant):** Aus den korrelierten Daten entstehen Optimierungshebel (z. B. OEE-Treiber, Energie/Qualität-Korrelation) – als optionales, zielsystemoffenes Outcome von UC-02.
- **A4 / UC-03 – AI Lifecycle:** Zentral trainieren, kontrolliert in die Edge ausrollen (Management Cockpit → mehrere Stationen).
- **A4 / UC-04/UC-05 – Closed Loops:** Qualitäts- und Wartungsereignisse führen zu nachvollziehbaren Entscheidungen und Aktionen inkl. Rückmeldung an MES/ERP (Best-of-Breed).

### Visual 2: OSF Proof „Digital Twin Pair“ (50/50)
Hinweis: Für DE/EN wird jeweils die sprachspezifische Layout-Grafik verwendet (Labels im Bild).

| OSF Shopfloor Layout (digital) | Fischertechnik Modellfabrik |
|---|---|
| ![A1-shopfloor-layout](/.attachments/A1-shopfloor-layout-1555f581-46ad-498c-8098-2237b7658644.png) |![Fischertechnik-Shopfloor.jpg](/.attachments/Fischertechnik-Shopfloor-a8407361-f01f-419f-b511-02a2044a022e.jpg) |

- Caption DE: Digitaler Zwilling im Demonstrator: Das OSF Shopfloor-Layout bildet die reale Modellfabrik ab und macht Zustände und Ereignisse transparent – als Grundlage für Use-Case-Fähigkeit.
- Alt-Text DE: Kombi-Ansicht aus OSF Shopfloor-Layout und Foto der Modellfabrik zur Veranschaulichung des digitalen Zwillings.

## Offene Punkte / Review Notes
- [ ] CTA-Entscheidung final (Default: Reifegrad-Check)
- [ ] SAP-Beispiele prüfen („SAP als Beispiel“ konsistent)