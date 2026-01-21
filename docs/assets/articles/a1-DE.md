# A1 – Artikel (DE Draft)

## Status
- Version: v1
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

### 2. Das Missverständnis „Use Case zuerst“
Der schnelle Reflex lautet oft: „Wir brauchen Track & Trace“, „Wir wollen Predictive Maintenance“, „Wir setzen KI ein“. Diese Ziele sind richtig – aber in der Praxis werden sie häufig als Einzellösungen umgesetzt. Dann entsteht eine Landschaft aus Punkt-zu-Punkt-Integrationen: jeder Use Case verdrahtet Datenquellen, Zustände und Entscheidungen erneut.

Das lässt sich kurzfristig demonstrieren, aber langfristig wird es teuer: Änderungen im Shopfloor, neue Stationen oder neue Anforderungen (z. B. Audits) führen zu aufwändigen Anpassungen.

Der robuste Weg ist umgekehrt: Use-Case-Fähigkeit entsteht durch ein Fundament aus
- Interoperabilität (Systeme können herstellerunabhängig miteinander sprechen),
- Events (was passiert wann, wo, mit welchem Objekt),
- Kontext (Order/Werkstück/Station/Qualität) und
- Governance (Versionierung, Verantwortlichkeiten, Auditierbarkeit).

### 3. Interoperabilität als Architekturprinzip
Interoperabilität ist mehr als „ein System kann Daten senden“. In der Fertigung bedeutet es, technische Signale und Statusmeldungen so zu normalisieren und zu kontextualisieren, dass sie prozessfähig werden. Erst dann können Teams und Systeme eine gemeinsame Sicht auf die Produktion aufbauen – unabhängig davon, ob die Daten aus Maschinen, Sensoren, FTS/AGVs oder aus IT-Systemen stammen.

Der entscheidende Effekt: Interoperabilität reduziert Punkt-zu-Punkt-Integration und schafft eine wiederverwendbare Event-to-Process Logik. Damit können neue Use Cases schneller umgesetzt werden, weil sie auf einer konsistenten Basis aufsetzen.

### 4. Best-of-Breed statt Lock-in – mit ERP/MES als integrierbare Zielsysteme
Eine skalierbare Smart Factory muss unterschiedliche Zielarchitekturen unterstützen. Manche Unternehmen nutzen klassische ERP- und MES-Landschaften, andere setzen auf Cloud Analytics oder spezialisierte Plattformen. Entscheidend ist nicht das einzelne Produkt, sondern die Fähigkeit, Daten und Prozesse durchgängig zu verbinden.

Wir verfolgen daher einen Best-of-Breed Ansatz: ERP/MES/Analytics werden integriert, ohne dass die Shopfloor-Integration jedes Mal neu gebaut werden muss. SAP-Produkte können dabei konkrete Zielsysteme sein (z. B. SAP ERP oder SAP Digital Manufacturing) – sind aber nur Beispiele innerhalb einer offenen Architektur.

### 5. ORBIS Vorgehensmodell in 5 Phasen: Reifegradbasiert zum nächsten Schritt
Damit die Transformation pragmatisch bleibt, arbeiten wir reifegradbasiert. Das DSP Vorgehensmodell beschreibt eine strukturierte 5-Phasen-Vorgehensweise – von der Datenbasis bis zur Orchestrierung. Es hilft, Use Cases nicht als Einzellösungen zu „verdrahten“, sondern schrittweise auf einer wiederverwendbaren Integrationsbasis aufzubauen.

![A1-ORBIS-Vorgehensmodell-DE.png](/.attachments/A1-ORBIS-Vorgehensmodell-DE-c75315af-2a6b-431a-9587-f157dcb02eeb.png)

Unser Vorgehen lässt sich in fünf Phasen beschreiben:

1) **Datenbasis & Konnektivität**  
   Relevante Quellen werden angebunden, Events werden verfügbar und beobachtbar.

2) **Datenintegration & Modellierung**  
   Events werden normalisiert, Objekte (Order/Werkstück/Station) werden konsistent verknüpft.

3) **Erweiterte Analytik & Intelligence**  
   KPIs, Ursachenanalyse und erste KI-gestützte Auswertungen werden möglich.

4) **Automation & Orchestration**  
   Erkenntnisse führen zu Aktionen: Closed Loops, Workflows, Rückmeldungen in MES/ERP.

5) **Autonomes & Adaptives Unternehmen**  
   Kontinuierliche Optimierung über Flotten-/Standortgrenzen hinweg, Governance und Skalierung.

Der entscheidende Punkt: Nicht jedes Unternehmen startet in Phase 1. Wir klären gemeinsam, wo Sie stehen, welche Use Cases priorisiert werden – und welcher nächste Schritt in Architektur und Umsetzung wirklich sinnvoll ist.


### 6. ORBIS SmartFactory als Proof: Was heute sichtbar ist (und was nicht)
Die ORBIS SmartFactory (OSF) ist ein Messe- und Kunden-Demonstrator. Sie zeigt, wie Interoperabilität, Events und Kontext zusammenkommen und so Use-Case-Fähigkeit entsteht. Sichtbar sind beispielsweise Status- und Ereignisströme, Prozesszustände und die Grundlage für Korrelation.

Wichtig ist die Abgrenzung: OSF ist nicht die produktive Track-&-Trace- oder Analytics-Anwendung. Sie macht das Prinzip anschaulich, auf dem kundenspezifische Lösungen mit ERP/MES/Analytics aufbauen.

Im Zusammenspiel aus digitalem Shopfloor-Layout und realer Modellfabrik wird das Prinzip des digitalen Zwillings unmittelbar greifbar: Die visuelle Abbildung verknüpft den physischen Ablauf mit Zuständen und Ereignissen in der OSF. Genau diese Transparenz ist die Voraussetzung, um Use Cases später belastbar in kundenspezifische ERP/MES/Analytics-Landschaften zu integrieren.


### 7. Nächster Schritt: Reifegrad-Check und Roadmap
Wenn Sie aktuell Use Cases priorisieren, aber der Weg dorthin unklar ist, starten wir typischerweise mit einem Reifegrad-Check: Welche Daten sind vorhanden, welcher Kontext fehlt, und welche Integrationslogik ist wiederverwendbar? Daraus entsteht eine Roadmap mit einem Pilot, der schnell Nutzen zeigt – ohne später in einer Sackgasse zu enden.

Call to Action: Sprechen Sie uns an für einen Reifegrad-Check oder einen Smart-Factory-Workshop – wir planen den nächsten Schritt gemeinsam und setzen ihn pragmatisch um.
## CTA (Optionen – Auswahl im Review)

**Option 1 (Standard, A1): Reifegrad-Check**
„Lassen Sie uns gemeinsam Ihren Reifegrad bestimmen: In einem kompakten Reifegrad-Check identifizieren wir Daten- und Integrationslücken und leiten den sinnvollsten nächsten Schritt ab.“

**Option 2: Interoperability & Integration Assessment**
„Mit einem Interoperability & Integration Assessment schaffen wir Transparenz über Ihre Systemlandschaft und definieren eine Integrationsarchitektur, die neue Use Cases beschleunigt.“

**Option 3 (eventbezogen): Messe-/Demo-CTA**
„Treffen Sie uns auf der LogiMAT/Hannover Messe: Wir zeigen live, wie Interoperabilität und Orchestrierung Use-Case-Fähigkeit schaffen – und leiten daraus Ihren nächsten Schritt ab.“


## Architecture Note (optional)
In einer interoperablen Fertigungsarchitektur werden technische Events (z. B. Station „Start/End“, Transfer, Qualitätsresultat) normalisiert und mit Kontext (Order, Werkstück, Station, Zeit) verknüpft. Dadurch entsteht ein prozessfähiges Modell, das KPI-Berechnung, Ursachenanalyse und Orchestrierung ermöglicht. Edge-Komponenten unterstützen Realtime-Verarbeitung und lokale Reaktionen; Cloud-Komponenten unterstützen Training, Benchmarking und skalierbare Auswertung. Best-of-Breed bedeutet, dass ERP/MES/Analytics austauschbar bleiben; SAP kann ein Zielsystem sein, ist aber nicht Voraussetzung.

## Visuals (Einbindung)
### Visual 1: UC-06 (Konzept-Screen)
- Link: [UC-06 — Interoperability Event-to-Process Map (Klammer für A1)]([UC-06 — Interoperability Event-to-Process Map (Klammer für A1) - Overview](https://dev.azure.com/ORBIS-AG-SAP/Modellfabrik/_wiki/wikis/Modellfabrik.wiki/8405/UC-06-%E2%80%94-Interoperability-Event-to-Process-Map-(Klammer-f%C3%BCr-A1))))
- Caption DE: Interoperabilität macht aus technischen Events ein verständliches Prozessbild – als gemeinsame Sprache zwischen Shopfloor und IT.
- Alt-Text DE: Diagramm zeigt, wie Shopfloor-Events mit Prozesskontext zu einem End-to-End Prozessbild zusammengeführt werden.

SVG DE (vorläufig)
![UC-06-SVG-Template-DE.png](/.attachments/UC-06-SVG-Template-DE-73d2c2d8-2542-4d0a-a337-94b0e304aec1.png)

### Visual 2: OSF Proof „Digital Twin Pair“ (50/50)
Hinweis: Für DE/EN wird jeweils die sprachspezifische Layout-Grafik verwendet (Labels im Bild).

| OSF Shopfloor Layout (digital) | Fischertechnik Modellfabrik |
|---|---|
| ![A1-shopfloor-layout](/.attachments/A1-shopfloor-layout-1555f581-46ad-498c-8098-2237b7658644.png) |![Fischertechnik-Shopfloor.jpg](/.attachments/Fischertechnik-Shopfloor-a8407361-f01f-419f-b511-02a2044a022e.jpg) |
- Caption DE: Digitaler Zwilling im Demonstrator: Das OSF Shopfloor-Layout bildet die reale Modellfabrik ab und macht Zustände und Ereignisse transparent – als Grundlage für Use-Case-Fähigkeit.
- Alt-Text DE: Kombi-Ansicht aus OSF Shopfloor-Layout und Foto der Modellfabrik zur Veranschaulichung des digitalen Zwillings.

- Caption EN: Digital twin in the demonstrator: the OSF shopfloor layout mirrors the physical model factory and makes states and events transparent—enabling use-case readiness.
- Alt-Text EN: Side-by-side view of the OSF shopfloor layout and a photo of the model factory illustrating the digital twin concept.


## Offene Punkte / Review Notes
- [ ] CTA-Entscheidung: Option 1 / 2 / 3 (bitte auswählen und finalen Wortlaut freigeben)
- [ ] Finales OSF Proof Screenshot auswählen (DE/EN) und Cropping festlegen
- [ ] SAP-Beispiele prüfen (Terminologie, Produktauswahl, „SAP als Beispiel“ konsistent)
