# Plan: Marketing-Inhalte vs. Use-Cases Konsistenz

Das Dokument `docs\07-analysis\Marketing-DSP-Präsentation-Use-Case-Konsistency` zeigt Inkonsistenzen zwischen Marketing-Präsentation und OSF-UI auf. Dieser Plan adressiert die Punkte für Sprint 16.

## 1. Wording Alignment & Konsistenz (Begriffe)
**Status:** Teils inkonsistent.
- **Problem:** Mischung aus FTS/AGV und Workpiece/SinglePart/Werkstück.
- **Maßnahme:**
    - [x] Glossar-Eintrag erstellen (oder erweitern) für Kernbegriffe: Event, Context, Order, Workpiece/SinglePart, Station, Transfer (FTS/AGV).
    - [x] In der UI (DE) primär deutsche Begriffe verwenden, aber englische Fachbegriffe (SinglePart, AGV) ggf. in Klammern ergänzen, wo es technisch wird (z.B. "FTS (AGV)").
    - [x] Sicherstellen, dass "Normalize / Enrich / Correlate" konsequent als DSP-Dreiklang verwendet wird. In `messages.de.json` sind die Titel aktuell "Normalisieren", "Kontext anreichern", "Korrelation". 
        - *Vorschlag:* Ändern auf "Normalize (Normalisieren)", "Enrich (Kontext anreichern)", "Correlate (Events korrelieren)" oder die englischen Begriffe als Hauptbegriffe nutzen, da es sich um DSP-Methodik handelt.

## 2. Low-Code / Plug-and-Play "Proof"
**Status:** Marketing verspricht Plug-and-Play, UI zeigt es nicht explizit.
- **Maßnahme:**
    - [x] In UC-00 (Interoperabilität) und UC-02 Text ergänzen: "Neue Quellen werden über wiederverwendbare Templates/Connectoren angebunden (konzeptionell)."
    - [ ] Prüfen, ob ein "Connector Registry" Mock-Teaser im Konfigurations-Tab sinnvoll ist (optional, später).

## 3. Adaptivität vs. Realität (Disclaimer)
**Status:** Marketing verspricht adaptive Prozesse, OSF ist ein starrer Demonstrator.
- **Maßnahme:**
    - [x] Disclaimer "OSF ist ein Demonstrator..." (bereits in UC-00/UC-02 vorhanden) auf alle Use-Case-Detailseiten ausrollen.
    - [x] Text-Anpassung: "OSF zeigt die Voraussetzungen; Adaptivität entsteht in der kundenspezifischen Umsetzung (Closed Loops)."

## 4. Use-Case Outcomes (KPIs)
**Status:** Fehlen in der Detailansicht.
- **Maßnahme:**
    - [x] In `messages.de.json` für jeden Use-Case (UC-01 bis UC-06) einen Key `@@ucXX.outcome` hinzufügen/pflegen.
    - [x] Werte:
        - UC-01: Traceability Coverage (100%)
        - UC-02: OEE / Enery per Unit
        - UC-04: FPY (First Pass Yield)
        - UC-05: MTTR (Mean Time To Recovery)
        - UC-00/06: Process Efficiency / Latency
    - [x] UI-Code anpassen: In der Use-Case-Card oder Detailansicht diese Outcome-Zeile anzeigen.

## Nächste Schritte (Sofortmaßnahmen für Sprint 16)
- [x] `messages.de.json` überarbeiten:
    - [x] "Normalize / Enrich / Correlate" vereinheitlichen.
    - [x] Disclaimer-Text zentralisieren oder duplizieren.
    - [x] Outcome-Texte hinzufügen.
- [x] UI-Code Check: Wo wird der Disclaimer angezeigt? Muss er in andere UCs kopiert werden?

---
*Dieser Plan dient als Grundlage für die Umsetzung im aktuellen Sprint.*

## Offene Punkte (Post-Implementation Review)
- [x] **Inhaltliche Überprüfung der Outcomes:** Die Einträge `uc0x.outcome` sind technisch implementiert, aber inhaltlich teils redundant (z.B. UC-03 Title vs. Outcome).
    - [x] Abgleich mit Marketing-Folien und Blog-Artikeln.
    - [x] Anpassung in `messages.de.json`:
        - UC-03: AI Lifecycle (Redundant) -> "AI Deployment Speed & Model Accuracy"
        - UC-04: Closed Loop Qualität (FPY) -> "First Pass Yield (FPY) & Quality Costs"
        - UC-05: Prädiktive Instandhaltung (MTTR) -> "Zero Unplanned Downtime (MTTR ↓)"
        - UC-06: Prozess Optimierung (Redundant) -> "Cycle Time Stability & Throughput"

