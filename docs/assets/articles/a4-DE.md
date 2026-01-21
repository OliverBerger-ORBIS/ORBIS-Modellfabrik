# A4 – Artikel (DE Draft)

## Status
- Version: v1
- Owner: @<Oliver Berger>
- Review: <Tech Reviewer> / <MES-ERP Reviewer> / <Redaktion>
- Zieltermin: <Datum>
- Scope-Tag: HANNOVER
- Feature: #69069
- UserStory: #69084 und #69085

---
## Executive Summary (5 bullets)
- „Closed Loops“ sind der Schritt von Transparenz zu Wirkung: Ereignisse führen zu Entscheidungen und Maßnahmen – auditierbar und steuerbar.
- Voraussetzung ist nicht ein einzelnes Tool, sondern eine interoperable Event- und Kontextbasis auf dem Shopfloor (DSP als Vermittler/Orchestrator).
- Qualität und Instandhaltung profitieren besonders: schnelle Eindämmung (Containment), weniger Stillstände, weniger Ausschuss.
- Best-of-breed bleibt zentral: MES/ERP/Service/Analytics sind Zielsysteme – SAP ist ein Beispiel, nicht Voraussetzung.
- OSF zeigt das Prinzip als Demonstrator; die produktive Umsetzung erfolgt reifegradbasiert und kundenspezifisch.

## Arbeitstitel
Von Events zu Wirkung: Closed Loops für Qualität und Instandhaltung – orchestriert über DSP

## Artikeltext (DE)

### 1. Warum „Closed Loop“ der nächste Reifegrad ist
Viele Smart-Factory-Initiativen schaffen Sichtbarkeit: Dashboards, Statusanzeigen, KPIs. Der wirtschaftliche Hebel entsteht jedoch erst, wenn aus Erkenntnissen **konsequente Folgeaktionen** werden – zuverlässig, nachvollziehbar und skalierbar. Genau das ist ein „Closed Loop“:  
**Detect → Decide → Act → Feedback (→ Learn)**.

### 2. Das Problem: Aktionen scheitern an fehlendem Kontext und Governance
In der Praxis sind Signale vorhanden, aber nicht prozessfähig. Typische Symptome:
- Alarme ohne Kontext (welcher Auftrag, welches Werkstück, welche Station ist betroffen?)
- Entscheidungen ohne Nachvollziehbarkeit (wer/was hat warum reagiert?)
- Rückmeldungen in MES/ERP/Service sind manuell oder als Einzellösungen verdrahtet

Ein Closed Loop benötigt daher mehr als Sensoren und Regeln: **Interoperabilität, Event-to-Process-Kontext und Governance** (Versionierung, Freigabe, Audit-Logik).

### 3. DSP als Vermittler: Von Events zur orchestrierten Aktion
DSP übernimmt die Vermittlungsrolle zwischen Shopfloor und Zielsystemen:
- Events werden **normalisiert** und mit Kontext **angereichert** (Order/Werkstück/Station/Zeit)
- Policies/Regeln werden **versioniert, freigegeben und ausgerollt**
- Aktionen können **lokal** (Edge-nah) ausgelöst und **systemisch** (MES/ERP/Service) rückgemeldet werden  
So bleibt die Architektur best-of-breed-fähig und vermeidet Punkt-zu-Punkt-Integration.

### 4. Closed Loop Quality: Von Prüfergebnis zur Folgeaktion (UC-04)
Qualität wird erst wirksam beherrscht, wenn **Prüfergebnis → Entscheidung → Aktion** als Regelkreis umgesetzt ist – inkl. Rückmeldung in MES/ERP.  
Beispiele für Aktionen: Sperre, Nacharbeit, Neubau, bedingte Freigabe – abhängig von Regeln/Policies und Kontext.

### 5. Predictive Maintenance: Frühwarnung mit nachvollziehbarer Reaktion (UC-05)
Zustandsüberwachung liefert Mehrwert, wenn aus einer Anomalie **ein nachvollziehbarer Alarmfluss** wird – bis hin zu optionalen Aktionen (Stop/Safe-State) und Rückmeldungen in Service-/MES-/ERP-Prozesse.  
Wichtig: Der Nutzen entsteht aus **Kontext + Orchestrierung**, nicht aus dem Sensor allein.

### 6. AI Lifecycle als Enabler: Zentral trainieren, kontrolliert ausrollen (UC-03)
Closed Loops skalieren besonders dann, wenn Modelle (z. B. visuelle Qualitätsprüfung) **zentral trainiert** und anschließend **kontrolliert an mehrere Stationen** ausgerollt werden.  
DSP Management Cockpit + DSP Edge ermöglichen Freigabe, Rollout/Rollback und den Betrieb mit Monitoring/Feedback.

### 7. OSF als Proof: Prinzip sichtbar machen – produktiv best-of-breed umsetzen
Die ORBIS SmartFactory (OSF) ist ein Messe- und Kunden-Demonstrator. Sie macht Ereignisse, Kontext und Integrationsprinzipien sichtbar – und zeigt, wie Closed Loops technisch und organisatorisch gedacht werden.  
Wichtig ist die Abgrenzung: OSF ist nicht die produktive MES/ERP/Service-Lösung, sondern der Proof für die Use-Case-Fähigkeit und den Architekturansatz.

### 8. Nächster Schritt: Closed-Loop Roadmap – reifegradbasiert starten
Typisch starten wir mit einem kurzen Assessment:
- Welche Events/Signale sind vorhanden – und welcher Kontext fehlt?
- Welche Policies/Regeln sind nötig (Governance, Versionierung, Audit)?
- Welche Zielsysteme sollen rückgemeldet werden (MES/ERP/Service/Analytics)?
Daraus entsteht eine Roadmap: Pilot → Skalierung → kontinuierliches Lernen.

## CTA (Optionen – Auswahl im Review)

**Option 1 (Standard): Closed-Loop Workshop**
„Lassen Sie uns Ihre Closed-Loop-Potenziale bewerten: In einem Workshop definieren wir Zielprozesse, Ereignisse/Kontext, Governance und die Integrationsarchitektur – und planen den nächsten Umsetzungsschritt.“

**Option 2: Hannover Messe / Demo**
„Treffen Sie uns auf der Hannover Messe: Wir zeigen live, wie Qualitäts- und Maintenance-Events zu orchestrierten Aktionen werden – und leiten daraus Ihren nächsten Schritt ab.“

---

## Visuals (Einbindung)

### Visual 1: UC-03 – AI Lifecycle (Konzept)
- Link: [UC-03 — AI Lifecycle - Overview](https://dev.azure.com/ORBIS-AG-SAP/Modellfabrik/_wiki/wikis/Modellfabrik.wiki/8410/UC-03-%E2%80%94-AI-Lifecycle)
- Bild/Datei (optional): ![UC-03-AI-Lifecycle-DE-v2-layered.png](/.attachments/UC-03-AI-Lifecycle-DE-v2-layered-e9806017-e08c-488f-9505-cea9b14a49f1.png)
- Caption DE: Zentral trainieren, kontrolliert ausrollen: Der AI Lifecycle verbindet Datenpipeline, Cloud-Training und den Rollout von Modellversionen an mehrere Stationen über DSP Management Cockpit und DSP Edge.
- Alt-Text DE: Diagramm zeigt AI Lifecycle (Data Capture & Context → Train & Validate → Monitor & Feedback) und das Ausrollen von Modellen auf mehrere Stationen über DSP Cockpit/Edge.

### Visual 2: UC-04 – Closed Loop Quality (Konzept)
- Link: [UC-04 — Closed Loop Quality - Overview](https://dev.azure.com/ORBIS-AG-SAP/Modellfabrik/_wiki/wikis/Modellfabrik.wiki/8408/UC-04-%E2%80%94-Closed-Loop-Quality)
- Bild/Datei (optional): ![UC-04-Closed-Loop.png](/.attachments/UC-04-Closed-Loop-69f866b8-d2c6-4104-9bd4-2238baebf6a7.png)
- Caption DE: Closed Loop Quality verbindet Prüfergebnis, Entscheidung, Aktion und Rückmeldung in MES/ERP – als auditierbarer Regelkreis.
- Alt-Text DE: Diagramm zeigt Qualitätsereignis (AIQS) → Policy/Decision (DSP) → Aktion im Shopfloor → Rückmeldung an MES/ERP.

### Visual 3: UC-05 – Predictive Maintenance (Konzept)
- Link: [UC-05 — Predictive Maintenance - Overview](https://dev.azure.com/ORBIS-AG-SAP/Modellfabrik/_wiki/wikis/Modellfabrik.wiki/8406/UC-05-%E2%80%94-Predictive-Maintenance)
- Bild/Datei (optional): ![UC-05-Predictive-Maintenance.png](/.attachments/UC-05-Predictive-Maintenance-3e372040-fd43-46dc-8fd4-f10ae12bd892.png)
- Variante : ![UC-05_Predictive-Maintenance_Var1-und-Var2.png](/.attachments/UC-05_Predictive-Maintenance_Var1-und-Var2-38c6c810-c2a7-473f-a7f6-67c340074760.png)
- Caption DE: Frühwarnung durch Vibrationsmonitoring: DSP korreliert Sensordaten mit Prozesskontext und löst Alarm sowie – optional – eine Aktion aus; Zielsysteme bleiben Best-of-Breed.
- Alt-Text DE: Diagramm zeigt Sensorwerte → DSP Edge Regelprüfung/Kontext → Alarm-Event → optionale Aktion (Stop/Safe-State) → Rückmeldung an Zielsysteme.

### Visual 4: OSF Proof Screens (Platzhalter)
Hinweis: Für DE/EN jeweils sprachspezifische Screens verwenden.

| OSF Proof 1 (z. B. Quality Event + Context) | OSF Proof 2 (z. B. Message Monitor / Alarm Event) |
|---|---|
| ![OSF-Proof-Quality-Context](/.attachments/<de-proof-1>.png) | ![OSF-Proof-Alarm-Event](/.attachments/<de-proof-2>.png) |

- Caption DE: OSF macht Ereignisse und Kontext sichtbar – als Grundlage für orchestrierte Closed Loops (Qualität, Maintenance) und Rückmeldungen in Zielsysteme.
- Alt-Text DE: Zwei Screenshots zeigen Qualitäts-/Alarm-Events verknüpft mit Kontext sowie die Ereignis-/Statusdarstellung in Echtzeit.

## Offene Punkte / Review Notes
- [ ] CTA auswählen (Option 1 oder 2) und finalen Wortlaut freigeben
- [ ] UC-03/04/05 Links in ADO-Wiki final eintragen
- [ ] OSF Proof Screens (DE/EN) auswählen und Cropping festlegen
- [ ] SAP-Beispiele prüfen (Terminologie, „SAP als Beispiel“ konsistent)

