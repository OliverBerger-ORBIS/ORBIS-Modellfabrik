# Sprint 17 – MES/Integration & LogiMAT Vorbereitung

**Zeitraum:** 05.03.2026 - 18.03.2026 (2 Wochen)  
**Status:** Laufend

**Stakeholder-Update:** Fokus liegt auf MES-Integration (Prozessanpassungen) und der Vorbereitung des Showcases für die LogiMAT.

---

## 🎯 Ziele

### Übernommen aus Sprint 16 (Open Tasks)
- [ ] **Azure DevOps Migration:** Von Github zu Azure Devops (Repo + Boards)
- [ ] **Projektantrag:** ORBIS-Smartfactory Q1/Q2 2026 finalisieren
- [ ] **DSP_Edge:** Implementierung `dsp/correlation/info` (als Response auf Request oder Unsolicited nach Order-Response) – *osf-ui vorbereitet (CorrelationInfoService, dsp/#). DSP_Edge wird in anderem Projekt entwickelt. Offen: E2E-Test mit simuliertem dsp/correlation/info.*

### MES / Integration (Fokus)
- [ ] **Einfache MES/ERP Integration:** Fokus auf Zusammenspiel mit DSP.
- [x] **QM-Check Verlagerung (CCU Ausbau):** Erledigt durch Quality-Fail (Option B). CCU erstellt bei FAILED keinen Ersatzauftrag; MES/DSP senden zukünftig `ccu/order/request` bei Bedarf (anderes Projekt). osf-ui ist senderneutral.
- [x] **CCU: Quality-Fail (Option B):** Bei `CHECK_QUALITY result=FAILED` kein Ersatzauftrag, Order bleibt ERROR. OSF-MODIFICATIONS.md Mod², Unit-Test. E2E ✓. Deploy ✓.
- [ ] **E2E-Test ccu/order/request von MES/DSP:** Simulieren, dass MES/DSP nach Quality-Fail einen Ersatzauftrag per `ccu/order/request` stellt. osf-ui vorbereitet (egal wer sendet). *(Verifikation → siehe E2E-Tests (manuell))*
- [x] **Positiver Test requestId (Mod 1):** `requestId` aus `ccu/order/request` wird in `ccu/order/response` und `ccu/order/active` mitgegeben. Verifiziert 12.03.2026 (OSF-UI → CCU auf RPi 192.168.0.100).
- [x] **TXT-AIQS: QoS 1 für quality_check:** `sorting_line.py`/`.blockly` QoS 2→1, beide Varianten (`_cam`, `_cam_clfn`), Doku, .ft-Archive. E2E ✓. Deploy ✓.
- [x] **Track & Trace: Order-Status FAILED/ERROR anzeigen:**
    - Kontext: Bei Quality-Fail (Order `state: ERROR`) zeigt Track & Trace im Order Context weiterhin "Active". Soll "Fehlgeschlagen"/"Abgebrochen" anzeigen.
    - WorkpieceHistoryService: `order.state` (ERROR/FAILED) aus CCU-Daten berücksichtigen, nicht nur ACTIVE vs COMPLETED aus Listen-Zugehörigkeit.
    - OrderContext: `status` um `'FAILED' | 'ERROR'` erweitert.
    - Track & Trace Template: Anzeige für `order.status === 'ERROR'`/`'FAILED'` ergänzt (Label "Fehlgeschlagen", styling .status-failed).
    - Unit-Tests für Service (generateOrderContext) und Component (track-trace.component.spec.ts).
    - *(E2E-Verifikation → siehe E2E-Tests (manuell): Track & Trace FAILED/ERROR)*
- [x] **Fixture mixed-pr-prnok:** Session `mixed-sr-pr-prnok_20260305_121602.log` als Mock-Fixture. `scripts/build_order_fixtures.py --only mixed_pr_prnok`. Order-Tab und Track & Trace: Fixture-Option "Mixed PR Quality-Fail".

### Arduino-Hardware & LogiMAT
- [x] **Arduino MPU-6050:** Vibrationssensor-Upgrade (I2C, 3-Stufen-Ampel, NTP/timestamp) – Sketch, Doku §5. **Done wenn:** a) MQTT per LAN funktioniert, b) Sensor-Info im Tab Sensor angezeigt wird (OSF-UI bereits ausgelegt).
- [x] **Hardware-Erweiterung (Ampel-System):** SW-420 + MPU-6050 einheitlich (Relais aktiv-niedrig), Doku §1.1 Schritt-für-Schritt analog §5.3.1.
- [ ] **E2E-Test Vibrationssensor:** Arduino (SW-420 oder MPU-6050) per LAN → MQTT-Broker → osf-ui Replay/Live → Sensor-Tab zeigt Ampel + Impulse. *(Verifikation → siehe E2E-Tests (manuell))*
- [ ] **UC-05 Live-Demo: Gefahrensimulation** *(Reihenfolge: 1 – vor UC-01)*
  - **Kontext:** Gemäß [DR-22](../03-decision-records/22-dsp-use-case-konzept-live-demo.md), [Analyse alarm-fabrik-stop](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md).
  - **Umsetzung:** „Gefahr simulieren“ in UC-05 Live-Demo (Tabs „Konzept" | „Live Demo"). Button aus Sensor-Tab entfernen. Sendet `ccu/set/park` + `ccu/order/cancel` (ENQUEUED-IDs aus `ccu/order/active`). Business-Layer `simulateDanger` bleibt (wird in UC-05 eingebunden).
  - **Betroffene Dateien:** `osf/apps/osf-ui/src/app/pages/use-cases/predictive-maintenance/` (Tabs + Live-Demo mit Button), `osf/apps/osf-ui/src/app/tabs/sensor-tab.component.ts` (Button entfernen).
  - **Definition of Done:**
    - Konzept-Anzeige: UC-05-Konzept (Diagramm/Steps) ist klar und nachvollziehbar.
    - E2E-Nachweis: Der E2E-Test (oder empirische Live-Demo) zeigt:
      1. **Prozess-Anhalt:** Beim Auslösen von „Gefahr simulieren" wird der Produktionsprozess angehalten.
      2. **Stillstand im Shopfloor:** Die Aktion führt zu sichtbarem/erkennbarem Stillstand auf dem Shopfloor (z.B. Module parken, FTS stoppt, keine neuen Aufträge).
      3. **Produktion fortsetzen:** Nach virtuellem „Fix" (z.B. Bestätigung, Reset oder manuelles Eingreifen gemäß [08-manual-intervention](../06-integrations/fischertechnik-official/08-manual-intervention.md)) kann die Produktion wieder aufgenommen werden.
    - Optional dokumentiert: empirischer Test `ccu/set/park` bei laufender AIQS-Aktion.
- [ ] **UC-01 anpassen (gemäß UC-05 / DR-22)** *(Reihenfolge: 2 – nach UC-05)*
  - **Umsetzung:** Beide Track-&-Trace-Kacheln zu einer zusammenführen; Auswahl „Konzept" | „Live Demo" statt zweier Kacheln.
  - **UseCase-Interface:** `conceptRoute`, `liveDemoRoute`; Detail-UI: zwei Buttons.
  - **Betroffene Dateien:** `osf/apps/osf-ui/src/app/pages/dsp/components/dsp-use-cases/dsp-use-cases.component.ts` (Kacheln `track-trace-genealogy`, `track-trace-live` → eine Kachel), UseCase-Interface/Config, Routing.

### LogiMAT Vorbereitung (Readiness)
*Detail-Tasks werden extern verwaltet. Wesentliche Checkpoints:*
- [ ] **Animation:** DSP-Architecture und Use-Cases (Check!)
- [ ] **OBS-Präsentation:** Startklar für Demos (Check!)
- [x] **Zweites FTS/AGV:** Unterstützung eines zweiten FTS (Serial jp93) – umgesetzt.
  - **Erreicht:** Zweites AGV in allen Tabs; AGV-Tab und Presentation-Tab mit Dropdown pro AGV; Darstellung beider AGVs im Shopfloor; AGV-1/AGV-2 farblich unterscheidbar (orange/gelb inkl. Hervorhebung); Fixtures storage_blue_agv2, storage_blue_parallel; DR-24 Shopfloor-Highlight-Farben
  - *(E2E-Verifikation → siehe E2E-Tests (manuell): Zwei AGVs)*
- [ ] **Analyse/Klärung Stillstand bei zwei AGVs im mixed-Modus:** Zur Info. Nicht unbedingt messerelevant – entweder keine mixed-Szenarien oder nur ein AGV aktiv.
- [ ] **Deployment v0.8.10 auf RPi:** osf-ui v0.8.10 auf RPi (192.168.0.100) ausrollen
- [x] **GitHub Pages Auto-Deploy:** Bei Version-Bump und Push auf main läuft CI → Deploy automatisch (v0.8.10 13.03.2026)

### E2E-Tests (manuell, mit osf-Version)

*Diese Tests werden manuell verifiziert. Nach Durchführung abhaken inkl. Version.*

- [ ] **Track & Trace FAILED/ERROR:** Fixture mixed_pr_prnok → Order Context zeigt „Fehlgeschlagen“ bei Quality-Fail *(osf v0.8.10)*
- [ ] **Zwei AGVs:** Beide AGVs (jp93 + zweites) im Shopfloor/Replay sichtbar, Farben orange/gelb, Fixtures storage_blue_agv2, storage_blue_parallel *(osf v0.8.10)*
- [ ] **Vibrationssensor:** Arduino (SW-420 oder MPU-6050) per LAN → MQTT → osf-ui Replay/Live → Sensor-Tab Ampel + Impulse *(osf v0.8.10)*
- [ ] **ccu/order/request von MES/DSP:** Simulierter Ersatzauftrag nach Quality-Fail; osf-ui zeigt neue Order *(osf vorbereitet)*
- [ ] **UC-05 Live-Demo testen:** Toggle aktivieren → Order im Process-Tab auslösen → Vibration erzeugen (Stoß/Stimmgabel) → Reaktion im Orders-Tab prüfen. Abhängigkeit: Arduino-Vibrationssensor (SW-420 oder MPU-6050) fertiggestellt. *(osf v0.8.11)*

### Blog-Serie & Marketing
- [ ] **A1 Review mit Marketing:**  (Carola Stammen) durchführen
- [ ] **A2 Review (UC-01 Track & Trace):** Review-Prozess durchführen.
- [ ] **A3 Review (UC-02 Datentöpfe, UC-06 Process Optimization):** Überarbeiten.
- [ ] **A4 Review (UC-03 AI Lifecycle, UC-04 Closed Loop Quality, UC-05 Predictive Maintenance):** Review-Prozess.

### Sprint-Abschluss (Pflicht vor Neuanlage Sprint 18)
- [ ] Sprint-Dokument: Status → "Abgeschlossen", Abschlussdatum setzen
- [ ] Neuer Sprint: Aus Template anlegen (`sprint_18.md`), offene `[ ]` übernehmen (inklusive Backlog)
- [ ] PROJECT_STATUS: Neue Tabellenzeile (Sprint 18, Zeitraum, ORBIS-Projekt, OSF-Phase, Externe Events)
- [ ] Roadmap prüfen: Phasen/Daten noch stimmig? (bei Bedarf anpassen)

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

### Sensor-Erweiterung Arduino R3 (Backlog)

*Siehe [Arduino Vibrationssensor](../05-hardware/arduino-vibrationssensor.md) §6.* R3 weitere Sensoren anbinden, Werte im Sensor-Tab; Flammensensor (Prio 1); R4 zweite Priorität.

### EPIC: Aufbau eines Test-Frameworks für osf-ui (Backlog)

*Siehe [Test-Framework vs. Replay – Analyse](../07-analysis/test-framework-replay-comparison-2026-03.md).* Optionale Ergänzung zum Replay-Workflow: Framework-Evaluierung (Playwright/Cypress), Fixture-Anbindung, Pilot-Tests für kritische Szenarien (z.B. beide AGVs, Quality-Fail). Replay bleibt primärer Ansatz.

---

## 🔗 Entscheidungen

- [docs/03-decision-records/](../03-decision-records/)
- [x] **[DR-20](../03-decision-records/20-aps-ccu-osf-modifications-documentation.md):** APS-CCU OSF-Modifikationen – zentrale Dokumentation in OSF-MODIFICATIONS.md
- [x] **[DR-21](../03-decision-records/21-ccu-osf-versioning.md):** CCU OSF-Versionierung – package.json `-osf.N`, Docker-Tags, selektives Build/Deploy
- [x] *Analyse (CCU Quality-Fail):* [docs/07-analysis/ccu-quality-fail-behaviour-2026-03.md](../07-analysis/ccu-quality-fail-behaviour-2026-03.md) – umgesetzt (Option B, FTS fährt weg, kein Ersatzauftrag)
- [x] **[DR-22](../03-decision-records/22-dsp-use-case-konzept-live-demo.md):** Use-Cases – Konzept vs. Live Demo; eine Kachel pro UC; Gefahrensimulation in UC-05 Live-Demo

---

## 📎 Referenzen
- [Zweites AGV (jp93)](../07-analysis/second-agv-2026-03.md)
- [Use-Case Bibliothek](../02-architecture/use-case-library.md)
- [Arduino Vibrationssensor](../05-hardware/arduino-vibrationssensor.md)
- [Alarm → Fabrik-Stop (CCU-Commands)](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md)
- Session (Quality-Fail E2E erfolgreich): `data/osf-data/sessions/mixed-sr-pr-prnok_20260305_121602.log`
- Session (Quality-Fail Ablauf historisch): `data/osf-data/sessions/mixed-sw-pw-sw-pwnok-pw_20260303_093559.log`

---

*Letzte Aktualisierung: 13.03.2026*
