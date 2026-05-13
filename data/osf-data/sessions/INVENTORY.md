# Session Log Inventory

Übersicht aller Session-Logs für die Auswahl geeigneter Aufzeichnungen für Analysen, Fixtures und Tests.

**Ziel:** Anhand der Abläufe entscheiden, ob eine Session für Start-up, Production, Storage oder Mixed-Analyse geeignet ist.

### Pflege

- **Neue `.log`-Datei:** passende Zeile in der Schnellübersicht **ergänzen** (Session-Name = Dateiname ohne `.log`).
- **Datei gelöscht:** Zeile **entfernen** oder als veraltet markieren.
- **Detaillierte Kontexte** (Orders, Ergebnis, Dauer, OSF-Version): stehen in der **ersten Zeile** der jeweiligen `.log` (`session_meta`), siehe [README.md](./README.md) — die Tabelle hier bleibt die kompakte Übersicht.

Abgleich: `python scripts/check_session_inventory.py` (listet fehlende/überzählige Einträge heuristisch).

---

## Schnellübersicht

| Session | Start-up | Production | Storage | Mixed | AGVs | Besonderheiten |
|---------|:--------:|:----------:|:-------:|:-----:|:----:|----------------|
| start-osf_20260303_075408 | ✓ | | | | 1 | FTS-State, Layout, Config – minimal Orders |
| start-osf_20260401_073448 | ✓ | | | | 2 | Start-up mit vollem Topic-Set (inkl. Cam/Sensorik), zwei AGVs sichtbar, ohne aktive Orders |
| startup-clean_20260512_102831 | ✓ | | | | 2 | ORBIS Startup-Baseline ohne retained Preload: Factory-Reset + Re-Docking AGV1/AGV2 (no_cam, Sensoren enthalten) |
| start-problems_20260312_175942 | | | ✓ | | 1 | Sehr viele Storage-Orders (475 active), hohe Last |
| startup-referenz_20260512_102037 | ✓ | | | | 2 | ORBIS Startup-Baseline mit retained Messages: Factory-Reset + Re-Docking AGV1/AGV2 (no_cam, Sensoren enthalten) |
| two-agvs_20260312_085306 | | | ✓ | | 2 | Beide AGVs, vorwiegend Storage |
| two-agvs_20260401_081603 | | | ✓ | | 2 | Zwei AGVs, Storage-Orders, Full-Topic-Aufnahme inkl. Kamera |
| two-agvs-mixed_20260312_101514 | | ✓ | ✓ | ✓ | 2 | Beide AGVs, Prod+Storage parallel |
| two-agvs-mixed_20260312_165108 | | ✓ | ✓ | ✓ | 2 | **Stillstand:** DPS DROP hängt, TXT sendet setStatusLED statt DROP FINISHED |
| two-agvs-mixed_20260401_093149 | | ✓ | ✓ | ✓ | 2 | Zwei AGVs, Mixed (Prod+Storage), Full-Topic-Aufnahme inkl. Kamera |
| two-agvs-mixed_20260409_084546 | | ✓ | ✓ | ✓ | 2 | Zwei AGVs, Mixed (Prod+Storage), no_cam-Variante als Vergleichslauf |
| two-agvs-mixed_20260409_090306 | | ✓ | ✓ | ✓ | 2 | Zwei AGVs, Mixed (Prod+Storage), no_cam-Variante (Folgelauf) |
| agv-1-simple_20260312_113627 | | | | | 1 | Viele Orders (96), nur AGV-1 |
| agv-1-mixed_20260312_103130 | | | | | 1 | Kurz (3 min), wenige Orders |
| agv-1-mixed_20260312_133313 | | ✓ | ✓ | ✓ | 1 | Prod+Storage, AGV-1 |
| agv-2-mixed_20260312_134156 | | ✓ | ✓ | ✓ | 2 | Prod+Storage, beide AGVs |
| agv-2-mixed_20260312_164447 | | ✓ | ✓ | ✓ | 2 | Prod+Storage, beide AGVs |
| production-blue_20260303_090705 | | ✓ | | | 1 | Reine Produktion Blau |
| production-blue-agv1-clean_20260512_105826 | | ✓ | | | 1 | Produktion BLUE mit AGV-1 (clean, no_cam); Ablauf nach Plan, Quality-Check PASSED (BOHOMIPO2) |
| production-white-agv1-clean_20260512_112936 | | ✓ | | | 1 | Produktion WHITE mit AGV-1 (clean); AGV-2 musste den Ablaufbereich raeumen |
| production-white-agv1-nok-clean_20260512_105322 | | ✓ | | | 1 | Produktion WHITE mit AGV-1 (clean, no_cam, ohne retained); Quality-Check FAIL (NOK/CRACK), AGV-1 danach eigenstaendig Richtung HBW |
| production-blue-agv2-clean_20260512_113429 | | ✓ | | | 2 | Produktion BLUE mit AGV-2 (clean); AGV-1 musste Weg/Bereich raeumen |
| production-red-agv2-clean_20260512_104826 | | ✓ | | | 2 | Produktion RED mit AGV-2 (clean, no_cam, ohne retained); Feldbeobachtung: vermuteter NFC-Mismatch (Lagerplatz A1 vs. Messung am Ende) mit Ausschuss-Verhalten |
| production-red-agv2-clean_20260512_112033 | | ✓ | | | 2 | Zweiter RED-Produktionslauf; AGV-1 musste DPS-Bereich raeumen, NFC-sensitive Auffaelligkeit notiert |
| production-wb-agv1-r-agv2_20260512_120106 | | ✓ | | | 2 | Parallele Produktion: WHITE+BLUE (AGV-1) und RED (AGV-2) |
| production-wb-agv2-r-agv1-clean_20260512_121518 | | ✓ | | | 2 | Parallele Produktion (clean): WHITE+BLUE (AGV-2) und RED (AGV-1) |
| production-wr-agv1-b-agv2_20260512_123508 | | ✓ | | | 2 | Produktion WHITE+RED (AGV-1) plus BLUE (AGV-2); RED=NOK, BLUE nur nach Supervisor-Eingriff |
| production-rw-agv2-b-agv1_20260512_125623 | | ✓ | | | 2 | Produktion RED+WHITE (AGV-2) plus BLUE (AGV-1); erfolgreicher Replay mit Reihenfolgevariation |
| production-wr-agv1-b-agv2_20260512_135956 | | ✓ | | | 2 | Exakt-Replay WR+B; RED zuerst wegen DRILL-Belegung, AIQS-Sauggreiferproblem manuell korrigiert |
| production-wr-agv2-b-agv1_20260512_141431 | | ✓ | | | 2 | Produktion WHITE+RED (AGV-2) plus BLUE (AGV-1); erfolgreich (RED aussortiert, WHITE/BLUE zu DPS) |
| production-red_20260303_081525 | | ✓ | ✓ | ✓ | 1 | Prod überwiegend, wenig Storage |
| production-white_20260303_081127 | | ✓ | ✓ | ✓ | 1 | Prod überwiegend, wenig Storage |
| production-blue-part1_20260303_082030 | | ✓ | ✓ | ✓ | 1 | Prod Blau Teil 1 |
| production-blue-part2_20260303_090117 | | ✓ | ✓ | ✓ | 1 | Prod Blau Teil 2 |
| storage-blue_20260303_080705 | | | ✓ | | 1 | Reine Einlagerung Blau |
| storage-blue-agv2-clean_20260512_104111 | | | ✓ | | 2 | Storage BLUE mit AGV-2 (clean, no_cam, ohne retained); Sonderfall: AGV-2 navigierte von HBW nach DPS |
| storage-red-agv2-clean_20260512_103526 | | | ✓ | | 2 | Storage RED mit AGV-2 (clean, no_cam, ohne retained); Sonderfall: AGV-1 verliess wegen voller Ladung CHRG und fuhr Richtung HBW |
| storage-rwb-clean_20260512_115152 | | | ✓ | | 2 | Storage RED->WHITE->BLUE (clean) mit Stillstand nach WHITE; AGV-2 fuhr nicht zu DPS, Factory-Reset noetig |
| storage-wrb-clean_20260512_120639 | | | ✓ | | 2 | Storage WHITE->RED->BLUE (clean), Lauf abgeschlossen |
| storage-rbw_20260512_122437 | | | ✓ | | 2 | Storage RED->BLUE->WHITE als Vorbereitung auf NOK-Replays |
| storage-rbw_20260512_124845 | | | ✓ | | 2 | Storage RED->BLUE->WHITE (Wiederholung) als Vorbereitung |
| storage-rbw_20260512_130304 | | | ✓ | | 2 | Storage RED->BLUE->WHITE (zusaetzliche Vorbereitung) |
| storage-wbr_20260512_140621 | | | ✓ | | 2 | Storage WHITE->BLUE->RED als Vorbereitung vor finalem Produktionslauf |
| storage-white-agv2-clean_20260512_103825 | | | ✓ | | 2 | Storage WHITE mit AGV-2 (clean, no_cam, ohne retained); Sonderfall: AGV-2 navigierte von HBW nach DPS |
| storage-red_20260303_080428 | | | ✓ | | 1 | Reine Einlagerung Rot |
| storage-white_20260303_075954 | | | ✓ | | 1 | Reine Einlagerung Weiß |
| storage-red234_20260303_094003 | | ✓ | ✓ | ✓ | 1 | Storage überwiegend, wenig Prod |
| mixed-pw-pr-sw-pb-sr-sb_20260303_092241 | | ✓ | ✓ | ✓ | 1 | Gemischt: White, Red, Blue Prod+Storage |
| mixed-sw-pw-sw-pwnok-pw_20260303_093559 | | ✓ | ✓ | ✓ | 1 | **Quality-Fail:** White prnok (CHECK_QUALITY FAILED), Ersatzauftrag |
| mixed-sr-pr-prnok_20260305_121602 | | ✓ | ✓ | ✓ | 1 | **Quality-Fail:** Fixture mixed_pr_prnok |
| calibrate_dps_1_20251202_101939 | | | ✓ | | 1 | DPS-Kalibrierung, Storage |
| vibration-sw420_20260303_094240 | | ✓ | ✓ | ✓ | 1 | Kurz, SW-420 Vibrationssensor im Kontext |
| synthetic-arduino-sensors_20260508_091000 | | | | | 0 | **Synthetisch:** Arduino-Topics aus OSF_MultiSensor-Sketch, inkl. EVENT/THRESHOLD/INTERVAL-Faelle (lokaler Replay/Persistence-Test ohne Hardware) |
| version1.1.6_20260511_134733 | | ✓ | ✓ | ✓ | 2 | ORBIS Live-Aufnahme (v1.1.6), 2 AGVs, Arduino/BME680/LDR vorhanden; Orders aus OSF-UI |
| version1.1.6-test2_20260511_141131 | | ✓ | ✓ | ✓ | 2 | ORBIS Live-Aufnahme (v1.1.6-test2), 2 AGVs, Replay/Persistence/Grafana-Durchstich genutzt |
| orbis-fulltopics-baseline_20260409_082701 | | ✓ | | | 2 | Full-Topics-Baseline (Cam+Sensorik+State), kurzer Produktionsimpuls mit zwei AGVs |
| auftrag-blau_1.log | | ✓ | | | 0 | Mock/Synthetisch, keine FTS-Events |
| auftrag-rot_1.log | | ✓ | | | 0 | Mock/Synthetisch, keine FTS-Events |
| auftrag-weiss_1.log | | ✓ | | | 1 | Älteres Format, wenig FTS |

---

## Besondere Topics

| Topic | Sessions mit Vorkommen | Zweck |
|-------|------------------------|-------|
| ccu/set/park | *(keine in aktuellen Logs)* | Fabrik-Park-Befehl (z.B. UC-05 Gefahrensimulation) |
| ccu/order/cancel | *(bei Bedarf prüfen)* | Order-Abbruch |
| fts/v1/ff/5iO4/state, fts/v1/ff/leJ4/state | two-agvs*, agv-2*, agv-1* | AGV-1 (5iO4), AGV-2 (leJ4) |

---

## Versionen (aus Logs/Factsheets)

- **CCU:** 1.3.0 (typisch in pairing/state)
- **Module:** 1.3.0 (HBW, DRILL, MILL, AIQS), DPS 1.6.0
- **osf-ui:** Nicht in Logs – Aufnahmezeitpunkt als Proxy (z.B. 2026-03-12 = v0.8.8/0.8.9)

---

## Detaillierte Abläufe (Auswahl)

### Start-up

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **start-osf** | CCU state (layout, config, flows, stock), pairing, wenig Orders, FTS-State. Kurzer Zeitraum (~4 min). | Gut für Start-up/Preload-Tests, wenig Order-Traffic |
| **start-osf_20260401_073448** | Start-up-Lauf mit vollem Topic-Set (inkl. Kamera/Sensorik), Pairing/State sichtbar, keine aktiven Orders. Zwei AGVs in den FTS-States vorhanden. | Gut als Start-up-Referenz mit Kamera- und Sensorlast |
| **startup-clean_20260512_102831** | ORBIS Startup-Referenz ohne retained Preload, mit Factory-Reset sowie Re-Docking (AGV1/AGV2). Kamera ausgeschlossen (`no_cam`), Sensor-Topics enthalten. | Sehr gut als „clean baseline“ für reproduzierbare Eventketten (weniger retained-Rauschen) |
| **start-problems** | Sehr viele Storage-Orders (475 active, 460 completed), sehr hohe Message-Rate. | Last-Test, nicht für saubere Ablauf-Analyse |
| **startup-referenz_20260512_102037** | ORBIS Startup-Referenz mit retained Startzustand, Factory-Reset sowie Re-Docking (AGV1/AGV2). Kamera ausgeschlossen (`no_cam`), Sensor-Topics enthalten. | Sehr gut als reproduzierbare Startup-Baseline für Fixtures/Track&Trace/Test-Framework |

### Production (ein AGV)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **production-blue** | Reine Produktion Blau: DRILL→MILL→AIQS→DPS. Ein AGV. | Ideal für Production-Only-Analyse |
| **production-blue-agv1-clean_20260512_105826** | Produktion BLUE mit AGV-1 als Primär-Transport (clean/no_cam), Sensor-Topics enthalten. Quality-Check erfolgreich (`PASSED`, Klassifikation `BOHOMIPO2`), Ablauf laut Feldbeobachtung nach Plan. | Sehr gut als reproduzierbare BLUE-Production-Basis (Happy Path) |
| **production-white-agv1-clean_20260512_112936** | Produktion WHITE mit AGV-1 (clean/no_cam). Feldhinweis: AGV-2 musste den Ablaufbereich freigeben. | Gut als WHITE-Happy-Path mit dokumentierter Verkehrsinteraktion |
| **production-white-agv1-nok-clean_20260512_105322** | Produktion WHITE mit AGV-1 als Primär-Transport (clean/no retained), Sensor-Topics enthalten. Quality-Check schlug fehl (`CHECK_QUALITY`, Ergebnis `FAILED`, Klassifikation `CRACK`); danach AGV-1 laut Feldbeobachtung autonom Richtung HBW. | Sehr gut für reproduzierbaren NOK-/Quality-Fail-Ablauf in WHITE-Produktion |
| **production-blue-agv2-clean_20260512_113429** | Produktion BLUE mit AGV-2 (clean/no_cam). Feldhinweis: AGV-1 musste den Bereich raeumen, danach regulärer Ablauf. | Gut als BLUE-Variante mit AGV-2 und dokumentiertem Unblock-Schritt |
| **production-red-agv2-clean_20260512_104826** | Produktion RED mit AGV-2 als Primär-Transport (clean/no retained), Sensor-Topics enthalten. Feldhinweis: vermuteter NFC-Mismatch (A1-Lagerplatz vs. Endmessung) mit Ausschuss-/Reject-Anteil. | Gut für reproduzierbare RED-Production-Basis inkl. dokumentiertem Anomalie-Hinweis |
| **production-red-agv2-clean_20260512_112033** | Zweiter RED-Lauf mit AGV-2; Feldhinweis aus Session-Notiz: NFC-sensitives Verhalten und AGV-1 musste DPS-Bereich raeumen. | Gut als Vergleichslauf zur RED-Serie (gleicher Session-Name, anderer Timestamp) |
| **production-wb-agv1-r-agv2_20260512_120106** | Parallele Produktionsauftraege: WHITE+BLUE auf AGV-1, RED auf AGV-2. | Gut fuer Multi-Order-Production mit verteilter AGV-Rolle |
| **production-wb-agv2-r-agv1-clean_20260512_121518** | Parallele Produktionsauftraege (clean): WHITE+BLUE auf AGV-2, RED auf AGV-1. | Gut als Gegenlauf mit invertierter AGV-Zuordnung |
| **production-wr-agv1-b-agv2_20260512_123508** | WHITE+RED auf AGV-1, BLUE auf AGV-2; RED als NOK-Fall. BLUE stoppte nach MILL und wurde erst per Supervisor-Kommando (AGV-2->AIQS) fortgesetzt. | Sehr gut fuer NOK-Seiteneffekt-Analyse in parallelen Produktionsauftraegen |
| **production-rw-agv2-b-agv1_20260512_125623** | Replay paralleler Orders mit RED+WHITE auf AGV-2 und BLUE auf AGV-1; Lauf erfolgreich, Reihenfolge bei Produktion variierte. | Gut fuer Robustheits-/Reihenfolgeanalyse ohne Stillstand |
| **production-wr-agv1-b-agv2_20260512_135956** | Exakt-Replay des WR+B-Szenarios: RED zuerst wegen DRILL-Belegung; AIQS-Sauggreiferproblem bei WHITE, manuelle Korrektur via DROP+clearLoadHandler. | Sehr gut fuer Analyse manueller Recovery-Pfade unter Last/Parallelitaet |
| **production-wr-agv2-b-agv1_20260512_141431** | WHITE+RED auf AGV-2 und BLUE auf AGV-1; laut Feldnotiz erfolgreicher Abschluss (RED aussortiert, WHITE/BLUE zu DPS). | Gut als erfolgreicher Abschlusslauf nach den WR+B-Replays |
| **orbis-fulltopics-baseline_20260409_082701** | Full-Topic-Aufnahme (Kamera, Arduino-Sensorik, retained States) mit kurzem Produktionsimpuls; zwei AGVs in den FTS-Topics. | Gut als technische Baseline fuer Track&Trace-/UI-Tests mit maximalem Topic-Spektrum |
| **production-red** | Produktion Rot überwiegend, minimal Storage. | Prod-fokussiert |
| **production-white** | Produktion Weiß überwiegend, minimal Storage. | Prod-fokussiert |
| **production-blue-part1/2** | Produktion Blau in zwei Phasen. | Längere Prod-Sequenz |

### Storage (ein AGV)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **storage-blue** | Reine Einlagerung Blau. HBW→DPS. | Ideal für Storage-Only |
| **storage-blue-agv2-clean_20260512_104111** | Storage BLUE mit AGV-2 als Primär-Transport (clean/no retained), Sensor-Topics enthalten. Nebenereignis: AGV-2 navigierte im Ablauf von HBW nach DPS. | Gut für reproduzierbare Storage-Basis mit dokumentiertem AGV-Navigationspfad (HBW→DPS) |
| **storage-red-agv2-clean_20260512_103526** | Storage RED mit AGV-2 als Primär-Transport (clean/no retained), Sensor-Topics enthalten. Nebenereignis: AGV-1 verließ CHRG bei voller Ladung und erhielt Fahrtauftrag Richtung HBW. | Gut für reproduzierbare Storage-Basis mit dokumentiertem AGV-Nebenpfad |
| **storage-rwb-clean_20260512_115152** | Storage RED->WHITE->BLUE (clean). Nach WHITE trat Stillstand auf: AGV-2 fuhr nicht zu DPS; Supervisor-Kommandos wirkungslos, erst Factory-Reset half. | Sehr gut fuer Reproduktion/Analyse des Storage-Stillstands nach WHITE |
| **storage-wrb-clean_20260512_120639** | Storage WHITE->RED->BLUE (clean), Lauf erfolgreich abgeschlossen. | Gut als stabiler Gegenlauf zum RWB-Stillstand |
| **storage-rbw_20260512_122437 / 124845 / 130304** | Drei RBW-Storage-Vorbereitungslaufe vor NOK-/Replay-Produktionen. | Gut als vorbereitende Referenzlaeufe mit vergleichbarer Ausgangslage |
| **storage-wbr_20260512_140621** | Storage WHITE->BLUE->RED als Vorbereitung vor finalem Produktionslauf. | Gut als letzter Vorbereitungslauf in der Serie |
| **storage-white-agv2-clean_20260512_103825** | Storage WHITE mit AGV-2 als Primär-Transport (clean/no retained), Sensor-Topics enthalten. Nebenereignis: AGV-2 navigierte im Ablauf von HBW nach DPS. | Gut für reproduzierbare Storage-Basis mit dokumentiertem AGV-Navigationspfad (HBW→DPS) |
| **storage-red** | Reine Einlagerung Rot. | Storage-Only |
| **storage-white** | Reine Einlagerung Weiß. | Storage-Only |
| **calibrate_dps** | DPS-Kalibrierung, Storage-Orders. | Speziell DPS/Calibration |
| **two-agvs** | Beide AGVs, vorwiegend Storage (3 Orders). | Zwei-AGV Storage, wenig Last |
| **two-agvs_20260401_081603** | Zwei-AGV-Storage-Lauf mit Full-Topic-Aufnahme (inkl. Kamera) und sichtbaren Storage-Orders. | Gut als Storage-Referenz mit vollem Topic-Volumen |

### Mixed (Production + Storage, ein oder zwei AGVs)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **mixed-pw-pr-sw-pb-sr-sb** | Gemischte Folge: White, Red, Blue – Prod und Storage. Ein AGV. | Typisches Mixed-Szenario |
| **mixed-sw-pw-sw-pwnok-pw** | White Prod, Quality-Fail (prnok), Ersatzauftrag. | Quality-Fail, Order ERROR, Ersatzauftrag |
| **mixed-sr-pr-prnok** | Red+Purple Prod, Quality-Fail. Fixture `mixed_pr_prnok`. | Quality-Fail-Analyse |
| **agv-1-mixed** (133313) | AGV-1, Prod+Storage parallel. | Ein-AGV Mixed |
| **agv-2-mixed** | AGV-1 und AGV-2, Prod+Storage parallel. | Zwei-AGV Mixed |
| **two-agvs-mixed** (101514) | Beide AGVs, Prod+Storage. | Zwei-AGV Mixed, früher am Tag |
| **two-agvs-mixed** (165108) | Beide AGVs, Prod+Storage. **Stillstand:** AGV-2 an DPS, DROP hängt (TXT sendet setStatusLED statt DROP FINISHED), AGV-1 blockiert. | **Analyse Stillstand zwei AGVs** – siehe [two-agvs-mixed-event-chain](../07-analysis/two-agvs-mixed-event-chain-fischertechnik-2026-03.md) |
| **two-agvs-mixed_20260401_093149** | Zwei AGVs, parallele Production+Storage-Orders, Full-Topic-Aufnahme inkl. Kamera. | Gut als Mixed-Baseline mit hohem Topic-Volumen |
| **two-agvs-mixed_20260409_084546** | Zwei AGVs, parallele Production+Storage-Orders, no_cam-Variante (Sensorik/States ohne Bildstream). | Gut als Vergleich zum Full-Topic-Mixed-Lauf bei reduzierter Topic-Last |
| **two-agvs-mixed_20260409_090306** | Folge-Mixed-Lauf mit zwei AGVs (no_cam), Production+Storage parallel. | Gut fuer Reproduzierbarkeit/Varianzvergleich in no_cam-Konfiguration |

### Sonstige

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **vibration-sw420** | Kurze Aufnahme, Vibrationssensor SW-420, gemischter Kontext. | Sensor-Kontext |
| **auftrag-*** | Mock/Synthetisch, keine echten FTS/Module-Events. | Ältere Testdaten |

---

## Referenzen

- [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](../../docs/07-analysis/two-agvs-mixed-event-chain-fischertechnik-2026-03.md) – Stillstand-Analyse two-agvs-mixed_165108
- [mixed-sr-pr-prnok](../../osf/testing/fixtures/) – Fixture für Quality-Fail
- [order-agv-mapping-without-mod3](../../docs/07-analysis/order-agv-mapping-without-mod3-2026-03.md) – Order↔AGV-Zuordnung
- [intermittent-quality-fail-runbook-template.md](../../docs/07-analysis/intermittent-quality-fail-runbook-template.md) – Vorlage fuer intermittierende Quality-Fail-/Stillstand-Analyse

---

## Track&Trace-Verknuepfungen (NFC-Kontinuitaet)

Feldhinweis fuer die neuen Serien: Mehrere Production-Sessions bauen direkt auf vorherigen Storage-Sessions auf; NFC-IDs der Werkstuecke sollen ueber die Session-Grenze hinweg konsistent bleiben.

| Kette | Storage-Session | Nachfolgende Production-Session(s) | Track&Trace-Hinweis |
|-------|------------------|------------------------------------|---------------------|
| A | `storage-rwb-clean_20260512_115152` | `production-wb-agv1-r-agv2_20260512_120106`, `production-wb-agv2-r-agv1-clean_20260512_121518` | Storage-Reihenfolge RED->WHITE->BLUE als Ausgangslage fuer WB+R-Produktionsreplays |
| B | `storage-rbw_20260512_122437`, `storage-rbw_20260512_124845`, `storage-rbw_20260512_130304` | `production-wr-agv1-b-agv2_20260512_123508`, `production-rw-agv2-b-agv1_20260512_125623`, `production-wr-agv1-b-agv2_20260512_135956` | RBW-Vorbereitung fuer WR+B/RW+B-Replays inkl. NOK-/Recovery-Szenarien |
| C | `storage-wbr_20260512_140621` | `production-wr-agv2-b-agv1_20260512_141431` | WBR-Storage direkt vor erfolgreichem WR+B-Abschlusslauf |

Ergaenzende Feldbeobachtung zu WR+B-Serien (insbesondere Chain B/C): Der zuvor beobachtete automatische Abort/Stillstand nach RED-Ausschuss war im Wiederholungslauf `production-wr-agv2-b-agv1_20260512_141431` nicht reproduzierbar. Das spricht fuer timing-sensitive Abarbeitung (Reihenfolge/zeitlicher Versatz bei Order-Submission). Je nach Interleaving von Order-, Modul- und FTS-Topics kann der Flow entweder durchlaufen oder in einen teilweisen Stillstand laufen. Teilweise ist Recovery durch manuelle Eingriffe moeglich (z. B. AGV gezielt Richtung HBW senden, danach `clearLoadHandler`).

---

*Stand: 2026-05-13. Bei neuen Sessions: Ablauf kurz beschreiben, in Schnellübersicht einordnen, Besonderheiten (Stillstand, ccu/set/park, etc.) vermerken.*
