# Sprint 18 – LogiMAT-Messe Durchführung

**Zeitraum:** 19.03.2026 - 01.04.2026 (2 Wochen)  
**Status:** Laufend

**Stakeholder-Update:** Fokus liegt auf der erfolgreichen Durchführung der LogiMAT-Messe, der Stabilisierung der Software (Bugfixes) und dem Hardware-Setup für die Demo.

---

## 🎯 Ziele

### Priorität 1: Kritische Bugs (LogiMAT)

- [ ] **Message Monitor:** Anzeige aller Topics ist doppelt. (Regression, muss gefixt werden für Debugging auf Messe).
- [ ] **Camera Image (Sensors-Tab):** Bild wird nicht angezeigt ("camera Image Loading .." bleibt). Tritt im Live-Modus auf. (Vermutlich durch kürzliche Fixes entstanden).
- [ ] **AGV-Tab Navigation Commands:** Manuelle Navigationsbefehle (außer Initial-Dock/Charge) werden vom AGV nicht ausgeführt. Vermutung: `orderId` oder Payload-Details inkompatibel. Analyse notwendig (ggf. TXT-Sourcen SVR4H73275).
- [ ] **FTS Route-Overlay:**
  - Darstellung auf RPi "unschön" (anders als localhost).
  - Route (orange Linie) wird aktuell nicht mehr auf allen Tabs korrekt dargestellt.
  - Bewusste Unterschiede in Berechnung/Darstellung Shopfloor vs. FTS-Tab analysieren.

### Priorität 2: Übernommen aus Sprint 17 (LogiMAT Hardware & Demo)

- [ ] **Fixture-Playback im Mock:** Mock-Fixtures (Track & Trace, AGV) werden nicht abgespielt. Wichtig für Demo ohne Hardware.
- [ ] **Flammensensor-Anzeige (Sensor-Tab):** Umstellung von linearer auf logarithmische Skala für bessere Lesbarkeit.
- [ ] **Flammensensor Alarm-Werte:** Verifikation der angezeigten Werte im Alarm-Fall (Live-Test).
- [ ] **Vibrationssensor-Station:** Fertigstellung der messetauglichen Platte und Transportsicherung (Arduino R4 + MPU-6050 + Ampel).
- [ ] **UC-05 Live-Demo (Gefahrensimulation):** Button "Gefahr simulieren", `ccu/set/park` + `ccu/order/cancel`. Verifikation: Stoppt der Prozess wirklich?
- [ ] **UC-01 Anpassung:** Zusammenführung der Track-&-Trace Kacheln (Konzept/Live) gemäß UC-05/DR-22.

### Organisatorisches & Migration

- [ ] **Azure DevOps Migration:** Von Github zu Azure Devops (Repo + Boards).
- [ ] **Blog-Serie:** Review A1 (Marketing), A2 (Track & Trace), A3 (Überarbeitung).

### E2E-Tests & Verifikation

- [ ] **dsp/correlation/info:** End-to-End Test mit Request/Response Szenario finalisieren.

---

*Erstellt: 19.03.2026*
