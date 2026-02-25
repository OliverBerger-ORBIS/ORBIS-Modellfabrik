# Sprint 16 – Vibration-Sensor, Doku-Check, Marketing-Konsistenz

**Zeitraum:** 19.02.2026 - 04.03.2026 (2 Wochen)  
**Status:** Laufend  

**Stakeholder-Update:** Fokus auf Hardware-Integration (Vibration-Sensor), Dokumentationsbereinigung und Konsistenz-Check Marketing vs. Use-Cases.

---

## 🎯 Ziele

### Übernommen aus Sprint 15
- [ ] Azure DevOps Migration & Docker-Setup
- [x] ORBIS-Projekt-Abschlussbericht finalisieren (für ORBIS-Modellfabrik Sprint 01-12 )
- [ ] Projektantrag ORBIS-Smartfactory Q1/Q2 2026

### Vibration-Sensor
- [x] Vorbereitung der IDE (Arduino-IDE) mit einfachem Test
- [ ] Wiring der Arduino-Komponenten und Test von sketch Vibrationsensor_SW420
- [ ] Integrieren in OSF-UI
- Projektplan: [arduino-vibrationssensor.md](../05-hardware/arduino-vibrationssensor.md)

### Dokumentation
- [x] Fischertechnik: Lokale Kopie der MQTT-Doku ([fischertechnik-official/](../06-integrations/fischertechnik-official/)) + Verweis auf Upstream ([FISCHERTECHNIK-OFFICIAL](../06-integrations/FISCHERTECHNIK-OFFICIAL.md))
- [x] Restrukturierung der docs und säubern des Repos
- [x] As-Is Doku: Aufräumen nach Vergleich mit aktueller Fischertechnik-Doku
- [x] dsp-architecture-inventory Dokumentation der SVGs

**Doku-Audit-Pfad:** ✅ [AS-IS vs. Fischertechnik Vergleich](../07-analysis/AS-IS-FISCHERTECHNIK-COMPARISON.md) – Abweichungen und Lücken dokumentiert. Autoritative Quelle: [fischertechnik-official/](../06-integrations/fischertechnik-official/).
  
### ERP/MES Integration
- [x] Erweiterung der APS/FMF/CCU-Komponente: Order/request-Topic von (DSP_Edge) sendet zusätzlich eine request-ID, CCU sendet Order/response mit requestId und orderId  
  → **Doku:** [order-requestid-extension.md](../07-analysis/order-requestid-extension.md) | **Analyse Deployment:** [ccu-modification-and-deployment-analysis.md](../07-analysis/ccu-modification-and-deployment-analysis.md)
- [x] OSF-UI: Sendet `dsp/correlation/request`, empfängt `dsp/correlation/info`, Anzeige in Order-Tab + Track & Trace (ErpOrderDataService als Fallback)
  → **Doku:** [order-requestid-extension.md](../07-analysis/order-requestid-extension.md) §8 | **Replay-Test:** `./scripts/run-correlation-test.sh [orderId]`
- [ ] **CCU Deployment RPi:** Image bauen und auf RPi deployen – Prozedur: [ccu-modification-and-deployment-analysis.md](../07-analysis/ccu-modification-and-deployment-analysis.md) §4 | `integrations/APS-CCU/DEPLOYMENT.md`
- [ ] **OSF-UI Live-Mode-Test:** Order-Tab Snapshot-Semantik (MessageMonitor statt Gateway) in Live-Umgebung prüfen, ob weiterhin funktionsfähig
- [ ] DSP_Edge: Sendet `dsp/correlation/info` (als Response auf Request oder Unsolicited nach Order-Response)

### Marketing & Konsistenz
- [x] Marketing-Präsentation zu DSP und Cross-Selling – Analyse: Die Präsentation ist inhaltlich konsistent zu eurer Blog-Storyline: Interoperabilität als Fundament, DSP als Schlüsseltechnologie (Edge+Cloud, plattformunabhängig), und der zentrale Claim „Interoperabilität wird nicht programmiert – sie wird aktiviert.“ lässt sich direkt und glaubwürdig in A1/UC-00 verwenden.
- [x] Konsistenz-Check: Marketing-Inhalte vs. Use-Cases der OSF-UI analysis with TODOS:        \docs\07-analysis\Marketing-DSP-Präsentation-Use-Case-Konsistency

### Blog-Serie
- [x] UC-06 -> UC-00 umbenennen 
- [x] UC-07 → UC-06 umbenennen (Process Optimization)
- [x] UC-00  Outcomes: 6 Use-Cases (UC-01 bis UC-06) als Outcomes in Process view & target systems darstellen als 6 Boxen mit Titel uns SVG-ICON.
- [x] a1-DE: TODO Review-Kommentare einarbeiten
- [x] UC-00: Prüfung ob DSP-Spalte angepasst werden soll: Erweiterung von Normalize -> Enrich -> Correlate , ggf Darstellung des Vorgehensmodells. Wir halten die DSP-Spalte im UC-00 bewusst schlank, weil UC-00 das Architektur-Prinzip „Event-to-Process“ (Normalize/Enrich/Correlate) visualisiert, während das Vorgehensmodell/Reifegradmodell eine Delivery-/Transformationssicht ist
- [ ] A2: Review-Prozess, 
- [ ] A3 Review mit UC-06 überarbeiten
- [ ] A4 Closed Loops – Draft erstellen

### Sprint-Abschluss (Pflicht vor Neuanlage Sprint 17)
- [ ] Sprint-Dokument: Status → "Abgeschlossen", Abschlussdatum setzen
- [ ] Neuer Sprint: Aus Template anlegen (`sprint_17.md`), offene `[ ]` übernehmen (inklusive Backlog)
- [ ] PROJECT_STATUS: Neue Tabellenzeile (Sprint 17, Zeitraum, ORBIS-Projekt, OSF-Phase, Externe Events)
- [ ] Roadmap prüfen: Phasen/Daten noch stimmig? (bei Bedarf anpassen)

---

## 📋 Backlog (optional)

*Tasks bei Gelegenheit angehen – kein separates Backlog-System.*

- [ ] **Session-Log-Analyse:** QoS/Retained für State-Topics empirisch verifizieren → [Anleitung](../04-howto/session-log-analyse.md), Kontext: [AS-IS vs. Fischertechnik](../07-analysis/AS-IS-FISCHERTECHNIK-COMPARISON.md)

---

## 🔗 Entscheidungen

*Wird bei Bedarf ergänzt.*

---

## 📎 Referenzen
- [Use-Case Bibliothek](../02-architecture/use-case-library.md) | [Inventar](../02-architecture/use-case-inventory.md)
- [Vibration-Sensor Projektplan](../05-hardware/arduino-vibrationssensor.md)

---

*Letzte Aktualisierung: 25.02.2026*
