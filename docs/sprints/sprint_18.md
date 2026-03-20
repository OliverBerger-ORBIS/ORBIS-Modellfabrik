# Sprint 18 – LogiMAT-Messe Durchführung

**Zeitraum:** 19.03.2026 - 01.04.2026 (2 Wochen)  
**Status:** Laufend

**Vorgänger:** [Sprint 17](./sprint_17.md)

**Stakeholder-Update:** Fokus auf LogiMAT-Durchführung, kritische Bugfixes und Hardware-Demo-Stabilität.

---

## 🎯 Ziele

### Priorität 1: Kritische Bugs (LogiMAT)

- [ ] **Message Monitor:** Anzeige aller Topics doppelt (Regression, blockiert Debugging auf Messe).
- [ ] **Camera Image (Sensor-Tab):** Bild wird nicht angezeigt ("Camera Image Loading…" bleibt). Live-Modus betroffen.
- [ ] **AGV-Tab NAV-Buttons:** Manuelle Navigationsbefehle (DPS→HBW, HBW→Intersection-2, AIQS→HBW) werden nicht ausgeführt. Vermutung: `orderId` oder Payload inkompatibel. Analyse: TXT-Sourcen SVR4H73275.
- [ ] **FTS Route-Overlay:** Darstellung auf RPi abweichend von localhost; orange Linie nicht auf allen Tabs korrekt.

### Priorität 2: Übernommen aus Sprint 17

- [x] **Vibrationssensor-Station:** Fertigstellung messetaugliche Platte und Transportsicherung (Arduino R4 + MPU-6050 + SW-420 + DHT11 + Flamme + MQ-2 + Ampel + Sirene). Verdrahtung, Konfiguration, Doku konsolidiert ([arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md)), alle Sensoren getestet.
- [ ] **Fixture-Playback im Mock:** Mock-Fixtures (Track & Trace, AGV-Tab) werden nicht abgespielt. Wichtig für Demo ohne Hardware. *(Constraint: Fix darf Live-Modus nicht beeinträchtigen.)*
- [x] **Flammensensor-Anzeige (Sensor-Tab):** Darstellung von linearer auf logarithmische Skala umstellen.
- [ ] **Flammensensor Alarm-Werte:** Verifikation der angezeigten Werte im Alarm-Fall (Live-Test).
- [ ] **Arduino Sketch Deployment:** OSF_MultiSensor_R4WiFi v1.1.0 auf Arduino R4 flashen. SKETCH_VERSION im Header prüfen, Serial Monitor „Sketch v1.1.0“, MQTT-Heartbeat 5 s. Doku: [arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md) §4.
- [ ] **UC-05 Live-Demo (Gefahrensimulation):** Button „Gefahr simulieren“ in UC-05; `ccu/set/park` + `ccu/order/cancel`. Verifikation: Stoppt der Prozess wirklich? *(CCU-Limitation bei IN_PROGRESS prüfen.)*
- [ ] **UC-01 Anpassung:** Zusammenführung der Track-&-Trace-Kacheln (Konzept/Live) gemäß DR-22.

### Organisatorisches

- [ ] **Azure DevOps Migration:** Von Github zu Azure Devops (Repo + Boards).
- [ ] **Blog-Serie:** Review A1 (Marketing), A2 (Track & Trace), A3 (Überarbeitung).

### E2E-Tests & Verifikation

- [ ] **dsp/correlation/info:** End-to-End Test mit Request/Response Szenario finalisieren.
- [ ] **ccu/order/request von MES/DSP:** Simulierter Ersatzauftrag nach Quality-Fail; osf-ui zeigt neue Order.

### Sprint-Abschluss (Vorbereitung Sprint 19)

*Erledigung vor Start Sprint 19.*

- [ ] Sprint-Dokument [Sprint 18]: Status → „Abgeschlossen“, Abschlussdatum setzen
- [ ] Neuer Sprint [Sprint 19]: Aus Template anlegen, offene `[ ]` übernehmen
- [ ] PROJECT_STATUS: Neue Zeile für Sprint 19 anlegen
- [ ] Roadmap prüfen: Phasen/Daten noch stimmig?

---

## 📋 Backlog (Optional / Prio 2)

### EPIC: Prozess-Anpassung "2-mal Bohren" (Product WHITE)
*Ziel: Das Produkt "Weiß" soll an der Bohrstation eine abweichende Bearbeitung (2 Löcher statt 1) erhalten. Dies erfordert Anpassungen durch die gesamte Kette.*

- **Story 1 (MES/DSP):** Definition des Produkts "WHITE" mit speziellem Workplan-Parameter (z.B. `drill_count: 2`) im MES-Auftrag.
- **Story 2 (CCU/Logic):** Anpassung der `OrderManager`-Logik, um den Parameter auszuwerten. Entweder Generierung zweier separater Bohr-Steps im Workplan (`Drill -> Drill`) oder Erweiterung des Kommandos an die Station.
- **Story 3 (Station/Hardware):** Anpassung der Bohrstation (TXT-Controller), um differenzierte Kommandos ("1x Bohren" vs. "2x Bohren") zu verstehen und physikalisch auszuführen.
- **Story 4 (AI/OSF-AIQS):** Neues ML-Modell trainieren. Erweiterung der Klassifikation um den Zustand "2 Löcher" (vs. "1 Loch" vs. "kein Loch").
- **Story 5 (Hardware/Prep):** Anpassung der Werkstücke (Produkt WHITE) mit Aufklebern/Folien, um das Bohrergebnis "2 Löcher" visuell für die Kamera zu simulieren.

- **Customer Architecture Netzsch:** Neue DSP-Customer-Config `NETZSCH_CONFIG` anlegen – Vorlage: `osf/apps/osf-ui/.../customer/ecme/` und `customer-selector-page.component.ts`.

### Sensor-Erweiterung Arduino (Backlog)

*Siehe [Arduino R4 Multi-Sensor](../05-hardware/arduino-r4-multisensor.md).* Backlog: TM1637/MAX7219 Display für 4-stelliges 7-Segment.

### EPIC: Aufbau eines Test-Frameworks für osf-ui (Backlog)

*Siehe [Test-Framework vs. Replay – Analyse](../07-analysis/test-framework-replay-comparison-2026-03.md).* Optionale Ergänzung zum Replay-Workflow: Framework-Evaluierung (Playwright/Cypress), Fixture-Anbindung, Pilot-Tests für kritische Szenarien.

- **Analyse Stillstand bei zwei AGVs im mixed-Modus:** Zur Info. Nicht messerelevant für LogiMAT.

---

## 🔗 Entscheidungen

- [DR-22](../03-decision-records/22-dsp-use-case-konzept-live-demo.md), [Alarm → Fabrik-Stop](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md)

---

## 📎 Referenzen

- [Arduino R4 Multi-Sensor](../05-hardware/arduino-r4-multisensor.md)
- [Use-Case Bibliothek](../02-architecture/use-case-library.md)
- [Zweites AGV (jp93)](../07-analysis/second-agv-2026-03.md)

---

*Letzte Aktualisierung: 19.03.2026*
