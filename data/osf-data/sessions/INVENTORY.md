# Session Log Inventory

Übersicht der **aktuellen** Session-Logs für Analysen, Fixtures und Track&Trace-Regression.

**Kriterien (ab 05.08.2026):** eindeutige NFC wo fachlich relevant · Sensor-Topics (Arduino) · kein NFC-Wiederverwendungs-Rauschen.

### Pflege

- **Neue `.log`-Datei:** passende Zeile in der Schnellübersicht **ergänzen** (Session-Name = Dateiname ohne `.log`).
- **Datei gelöscht:** Zeile **entfernen**.
- **Detaillierte Kontexte** (Orders, Ergebnis, Dauer, OSF-Version): erste Zeile der `.log` (`session_meta`), siehe [README.md](./README.md).

Abgleich: `python scripts/check_session_inventory.py`

**Geplant (DR-30 Nachtrag 26.08.2026):** ~~Alle Sessions mit **Storage** um `osf/workpiece/intake`-Zeilen anreichern.~~ **Erledigt 26.08.2026:** `python scripts/patch_session_intake_events.py` (+38 Intake-Zeilen). Ohne Storage-Intake belassen: `startup-clean` (Startup-Referenz), `production-wr-agv2-…` (2-AGV Interim, kein DPS-RGB_NFC), `synthetic-arduino-sensors` (Sensor-only) — weiterhin Mehrwert, **nicht gelöscht**.

**Intake-Vollständigkeit:** Patch erzeugt **eine Intake-Zeile pro NFC**, nur wenn im Log ein DPS-`RGB_NFC` FINISHED **mit Farbe** vorkommt (wie die Bridge). Unvollständige Aug-04-Multi-Loads (Name vor Aufnahme, Lauf abgebrochen → nur 2 DPS-Zyklen) **gelöscht 26.08.2026:** `storage-production-ml-wbr_…115849`, `…-brw_…121835`, `…-bwr_…131822`. Für **3 Intakes** die Aug-07-`ml-*`-Sessions nutzen (z. B. `ml-wbr_20260807_125133`).

---

## Schnellübersicht

| Session | Start-up | Production | Storage | Mixed | AGVs | Besonderheiten |
|---------|:--------:|:----------:|:-------:|:-----:|:----:|----------------|
| startup-clean_20260512_102831 | ✓ | | | | 2 | **Startup-Referenz** (einzige): Factory-Reset + Re-Docking, `no_cam`, Sensoren, ohne retained Preload |
| white-storage-production_20260807_111716 | | ✓ | ✓ | ✓ | 1 | **T&T-Referenz Pass:** WHITE Storage→Production, Arduino; eindeutige NFC |
| red-storage-production_20260807_113213 | | ✓ | ✓ | ✓ | 1 | **T&T-Referenz Pass:** RED Storage→Production, Arduino; eindeutige NFC |
| blue-storage-production_20260807_112530 | | ✓ | ✓ | ✓ | 1 | **T&T-Referenz Pass:** BLUE Storage→Production, Arduino; eindeutige NFC |
| white-storage-production-nok_20260807_114322 | | ✓ | ✓ | ✓ | 1 | **T&T-Referenz Quality-Fail:** WHITE AIQS FAILED |
| red-storage-production-nok_20260807_113739 | | ✓ | ✓ | ✓ | 1 | **T&T-Referenz Quality-Fail:** RED AIQS FAILED |
| blue-storage-production-nok_20260807_110943 | | ✓ | ✓ | ✓ | 1 | **T&T-Referenz Quality-Fail:** BLUE AIQS FAILED |
| ml-wbr_20260807_125133 | | ✓ | ✓ | ✓ | 1 | Multi-Load W→B→R, 3 NFCs, Pass (Aug T&T Acceptance) |
| ml-wrb-red-nok_20260807_130729 | | ✓ | ✓ | ✓ | 1 | Multi-Load W→R→B; RED Quality-Fail |
| ml-rbw-blue-nok_20260807_135854 | | ✓ | ✓ | ✓ | 1 | Multi-Load R→B→W; BLUE Quality-Fail |
| ml-wrb-chrg-blue-nok_20260807_142119 | | ✓ | ✓ | ✓ | 1 | Multi-Load W→R→B + Charge; BLUE Quality-Fail |
| storage-production-ml-wrb_20260804_114227 | | ✓ | ✓ | ✓ | 1 | Multi-Load W→R→B, Pass; **unvollständig für Mfg:** kaum DRILL/MILL/AIQS `/state` — Mapping-Abnahme → `ml-wbr` |
| storage-production-ml-bwr_20260804_130016 | | ✓ | ✓ | ✓ | 1 | **Störfall (behalten):** DPS→FTS-Befehl kam nicht an, DPS blockiert; Prod stoppt nahe AIQS; 3 Intakes |
| storage-production-ml-rrr_20260804_133245 | | ✓ | ✓ | ✓ | 1 | 3× RED Multi-Load; **2. RED** Pos2 Quality-Fail (CRACK, `f6caa206181682`) |
| storage-production-ml-bbb_20260804_134700 | | ✓ | ✓ | ✓ | 1 | 3× BLUE Multi-Load; **2. BLUE** Pos2 Quality-Fail (MIPO2, `b7b84ce7ad920f`); DRILL+MILL |
| production-wr-agv2-b-agv1-clean_20260513_135600 | | ✓ | | | 2 | **2-AGV (Interim, historisch):** osf.4 WR+B; ersetzt durch `storage-blue-dual-agv-bwr_*` |
| storage-blue-dual-agv-bwr_20260901_124524 | | ✓ | ✓ | ✓ | 2 | **2-AGV (01.09.):** STORAGE BLUE → PROD B+W parallel, dann RED; FTS **5iO4**/**xkI4**; OSF **1.3.5** |
| storage-brw-dual-agv-brw_20260903_092247 | | ✓ | ✓ | ✓ | 2 | **2-AGV (03.09. morgen):** STORAGE B/W/R → PROD B+R parallel, dann WHITE; Dock/Init + Charge; OSF **1.3.6** |
| storage-wbr-dual-agv-rwb_20260903_094319 | | ✓ | ✓ | ✓ | 2 | **2-AGV-Referenz (aktuell):** STORAGE W/B/R → PROD R/W/B (HBW-Start auf AGV-2, AGV-1 später); Charge; FTS **5iO4**/**xkI4**; OSF **1.3.6**; Grafana+T&T **live OK** |
| two-agvs-mixed_20260312_165108 | | ✓ | ✓ | ✓ | 2 | **2-AGV (Interim):** Stillstand DPS DROP; Forensik März 2026 |
| synthetic-arduino-sensors_20260508_091000 | | | | | 0 | Synthetisch: Arduino-Topics (ohne Hardware) |

---

## Abdeckung & Lücken

| Thema | Stand |
|-------|--------|
| 1-AGV Storage→Production Pass (W/R/B) | ✓ Aug `*-storage-production_20260807_*` |
| 1-AGV Storage→Production Fail (W/R/B) | ✓ Aug `*-storage-production-nok_20260807_*` |
| Multi-Load 1 AGV (gemischt + Fail + Charge) | ✓ Aug `ml-*_20260807_*` + Aug04 `storage-production-ml-*` |
| Quality-Fail isoliert (gleiche Farbe, Multi-Load) | ✓ `ml-rrr`, `ml-bbb` |
| Charge zwischendurch | ✓ `ml-brw`, `ml-wrb-chrg-blue-nok`, **`storage-brw-dual-agv-brw_*`** (2-AGV + Charge) |
| DPS/FTS-Störfall | ✓ `ml-bwr_130016` |
| Startup clean | ✓ `startup-clean` |
| **2-AGV / parallele FTS** | ✓ **`storage-wbr-dual-agv-rwb_20260903_094319`** (03.09.2026): STORAGE W/B/R → PROD R/W/B (zunächst AGV-2 am HBW); Charge; **5iO4**/**xkI4**; OSF **1.3.6**; Grafana+T&T **live OK**. Auch: `storage-brw-dual-agv-brw_*` (Dock/Charge). Vorgänger: `storage-blue-dual-agv-bwr_*` (01.09.). Replay-Abnahme noch offen. |

---

## Detaillierte Abläufe

### Start-up

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **startup-clean_20260512_102831** | Factory-Reset + Re-Docking AGV1/AGV2; `no_cam`; Sensor-Topics; ohne retained Preload. | **Einzige Startup-Referenz** (start-osf / startup-referenz entfernt 05.08.2026) |

### Production / Storage (1 AGV, T&T)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **\*storage-production_20260807_*** | Pass: Storage→Production je Farbe (W/R/B), Arduino. | **T&T Single-Color Pass-Referenz** |
| **\*storage-production-nok_20260807_*** | Quality-Fail je Farbe (W/R/B). | **T&T Single-Color Fail-Referenz** |
| **ml-*_20260807_*** | Multi-Load 1 AGV (Pass / Fail / Charge). | T&T Acceptance Aug 2026 |
| **storage-production-ml-*** | Multi-Load 1 AGV (04.08., eindeutige NFC). | T&T Mitfahrt / Attribution / Fail |

### 2-AGV (Referenz + Interim)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **storage-wbr-dual-agv-rwb_20260903_094319** | STORAGE W/B/R (NFC `513601ee741a12` / `b8b3588da7d8f4` / `aaf21ca1ef1d86`) → PRODUCTION RED, WHITE, BLUE (HBW-Start alle auf AGV-2/`xkI4`; AGV-1 später); Charge stop `5iO4` / start `xkI4`; dual FTS **5iO4**/**xkI4**. | **Aktuelle 2-AGV-Referenz** (OSF 1.3.6); Grafana+T&T live OK; Replay abnehmen |
| **storage-brw-dual-agv-brw_20260903_092247** | STORAGE B/W/R → PRODUCTION BLUE+RED parallel → WHITE; Dock/Init + Charge; dual FTS **5iO4**/**xkI4**. | 2-AGV 03.09. (Dock/Charge) |
| **storage-blue-dual-agv-bwr_20260901_124524** | STORAGE BLUE → PRODUCTION BLUE+WHITE parallel → PRODUCTION RED; dual FTS **5iO4**/**xkI4**; Intake NFC `9167f7e4d1d752`. | Vorgänger 01.09. (OSF 1.3.5) |
| **production-wr-agv2-b-agv1-clean_20260513_135600** | WR+B unter CCU `1.3.0-osf.4`. | Interim / historisch (`leJ4`-Ära) |
| **two-agvs-mixed_20260312_165108** | Stillstand: AGV-2 an DPS, DROP hängt. | Stillstand-Analyse + Forensik |

### Sonstige

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **synthetic-arduino-sensors** | Arduino-Topics aus Sketch. | Lokaler Sensor-/Persistence-Test |

---

## Referenzen

- [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](../../docs/07-analysis/two-agvs-mixed-event-chain-fischertechnik-2026-03.md) – Stillstand `two-agvs-mixed_165108`
- [osf-ui-track-trace-history-attribution.md](../../docs/04-howto/osf-ui-track-trace-history-attribution.md) – T&T Attribution / ml-Sessions
- [track-trace-heuristic-session-matrix-2026-08.md](../../docs/07-analysis/track-trace-heuristic-session-matrix-2026-08.md) – Aug-2026 Acceptance-Matrix

---

*Stand: 2026-09-03. 2-AGV-Referenz: **`storage-wbr-dual-agv-rwb_20260903_094319`** (live Grafana+T&T OK); auch `storage-brw-dual-agv-brw_*`; Vorgänger `storage-blue-dual-agv-bwr_*`.*
