# Sprint 17 – MES/Integration & LogiMAT Vorbereitung

**Zeitraum:** 05.03.2026 - 18.03.2026 (2 Wochen)  
**Status:** Laufend

**Stakeholder-Update:** Fokus liegt auf MES-Integration (Prozessanpassungen) und der Vorbereitung des Showcases für die LogiMAT.

---

## 🎯 Ziele

### Übernommen aus Sprint 16 (Open Tasks)
- [ ] **Azure DevOps Migration:** Von Github zu Azure Devops (Repo + Boards)
- [ ] **Projektantrag:** ORBIS-Smartfactory Q1/Q2 2026 finalisieren
- [ ] **DSP_Edge:** Implementierung `dsp/correlation/info` (als Response auf Request oder Unsolicited nach Order-Response)

### MES / Integration (Fokus)
- [ ] **Einfache MES/ERP Integration:** Fokus auf Zusammenspiel mit DSP.
- [ ] **QM-Check Verlagerung (CCU Ausbau):** 
    - Logik implementieren, damit der QM-Check (Quality Result) von DSP/MES übernommen werden kann.
    - Ausbau der Funktionalität in der CCU (`integrations/APS-CCU`), um externe QM-Entscheidungen zu verarbeiten.
- [x] **CCU: Quality-Fail (Option B):** Bei `CHECK_QUALITY result=FAILED` kein Ersatzauftrag, Order bleibt ERROR. OSF-MODIFICATIONS.md Mod², Unit-Test. E2E ✓. Deploy ✓.
- [x] **TXT-AIQS: QoS 1 für quality_check:** `sorting_line.py`/`.blockly` QoS 2→1, beide Varianten (`_cam`, `_cam_clfn`), Doku, .ft-Archive. E2E ✓. Deploy ✓.
- [x] **Track & Trace: Order-Status FAILED/ERROR anzeigen:**
    - Kontext: Bei Quality-Fail (Order `state: ERROR`) zeigt Track & Trace im Order Context weiterhin "Active". Soll "Fehlgeschlagen"/"Abgebrochen" anzeigen.
    - WorkpieceHistoryService: `order.state` (ERROR/FAILED) aus CCU-Daten berücksichtigen, nicht nur ACTIVE vs COMPLETED aus Listen-Zugehörigkeit.
    - OrderContext: `status` um `'FAILED' | 'ERROR'` erweitert.
    - Track & Trace Template: Anzeige für `order.status === 'ERROR'`/`'FAILED'` ergänzt (Label "Fehlgeschlagen", styling .status-failed).
    - Unit-Tests für Service (generateOrderContext) und Component (track-trace.component.spec.ts).
    - **Nächster Schritt:** Neue osf-ui Version anlegen/ausrollen.
- [x] **Fixture mixed-pr-prnok:** Session `mixed-sr-pr-prnok_20260305_121602.log` als Mock-Fixture. `scripts/build_order_fixtures.py --only mixed_pr_prnok`. Order-Tab und Track & Trace: Fixture-Option "Mixed PR Quality-Fail".

### Arduino-Hardware & LogiMAT
- [x] **Arduino MPU-6050:** Vibrationssensor-Upgrade (I2C, 3-Stufen-Ampel, NTP/timestamp) – Sketch, Doku §5. **Done wenn:** a) MQTT per LAN funktioniert, b) Sensor-Info im Tab Sensor angezeigt wird (OSF-UI bereits ausgelegt).
- [x] **Hardware-Erweiterung (Ampel-System):** SW-420 + MPU-6050 einheitlich (Relais aktiv-niedrig), Doku §1.1 Schritt-für-Schritt analog §5.3.1.
- [ ] **E2E-Test Vibrationssensor:** Arduino (SW-420 oder MPU-6050) per LAN → MQTT-Broker → osf-ui Replay/Live → Sensor-Tab zeigt Ampel + Impulse. Optional: Preload-Test dokumentieren.

### LogiMAT Vorbereitung (Readiness)
*Detail-Tasks werden extern verwaltet. Wesentliche Checkpoints:*
- [ ] **Animation:** DSP-Architecture und Use-Cases (Check!)
- [ ] **OBS-Präsentation:** Startklar für Demos (Check!)
- [ ] **Zweites FTS/AGV:** Unterstützung eines zweiten/Ersatz FTS mit Serial-ID jp93. Komplette Analyse + Tests‚

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

---

## 🔗 Entscheidungen

- [docs/03-decision-records/](../03-decision-records/)
- [x] **[DR-20](../03-decision-records/20-aps-ccu-osf-modifications-documentation.md):** APS-CCU OSF-Modifikationen – zentrale Dokumentation in OSF-MODIFICATIONS.md
- [x] **[DR-21](../03-decision-records/21-ccu-osf-versioning.md):** CCU OSF-Versionierung – package.json `-osf.N`, Docker-Tags, selektives Build/Deploy
- [x] *Analyse (CCU Quality-Fail):* [docs/07-analysis/ccu-quality-fail-behaviour-2026-03.md](../07-analysis/ccu-quality-fail-behaviour-2026-03.md) – umgesetzt (Option B, FTS fährt weg, kein Ersatzauftrag)

---

## 📎 Referenzen
- [Use-Case Bibliothek](../02-architecture/use-case-library.md)
- [Arduino Vibrationssensor](../05-hardware/arduino-vibrationssensor.md)
- Session (Quality-Fail E2E erfolgreich): `data/osf-data/sessions/mixed-sr-pr-prnok_20260305_121602.log`
- Session (Quality-Fail Ablauf historisch): `data/osf-data/sessions/mixed-sw-pw-sw-pwnok-pw_20260303_093559.log`

---

*Letzte Aktualisierung: 09.03.2026*
