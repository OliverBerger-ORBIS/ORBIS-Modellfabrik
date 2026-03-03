# Session-Recordings: Verwendung, Default-Wechsel, Preload-Audit

**Datum:** 03.03.2026  
**Kontext:** start-osf als neuer Default, alte Sessions aufräumen, Preloads vs. retained Topics prüfen

---

## 1. Wo werden alte Session-Recordings verwendet?

### 1.1 Scripts und Dokumentation

| Quelle | Referenz | Verwendung |
|--------|----------|------------|
| `scripts/replay-sessions.ts` | `start-osf_20260303_075408.log` | Beispiel in Kommentar, `--help` Output |
| `scripts/README-replay.md` | `start-osf_20260303_075408.log`, `production-white_20260303_081127.log` | Beispiele in allen Szenarien |
| `docs/04-howto/session-log-analyse.md` | `start-osf_20260303_075408.log` (Replay), `auftrag-blau_1.log` (Analyse) | Beispiel für Replay bzw. Analyse-Scripts |

### 1.2 Analysis-Metadaten (Output der Analyse-Scripts)

Die Verzeichnisse `data/osf-data/*-analysis/` enthalten **Output** der Analyse-Scripts (z.B. `scripts/analyze_dps_sessions.py`). Referenzierte Sessions:

- `default_test_session` – aiqs, dps, drill, hbw, mill
- `Start_20251110_175151` – aiqs, dps, drill, hbw, mill
- `auftrag-blau_1` – aiqs, dps, drill, hbw, mill, production-order-analysis

### 1.3 Session Manager / Replay Station

- **Kein fester Default:** Die Replay Station listet alle `.log`-Dateien aus `data/osf-data/sessions/` und nutzt eine `st.selectbox` ohne feste Vorauswahl.
- **Preloads:** Werden aus `data/osf-data/test_topics/preloads/*.json` geladen – **nicht** aus Session-Logs.

### 1.4 OSF Testing-Fixtures (`osf/testing/fixtures/`)

Die Mock-Fixtures in `osf/libs/testing-fixtures` und `osf/testing/fixtures/` laden **keine** Session-Recordings. Sie nutzen statische Dateien wie:

- `orders/startup/orders.log`, `orders/white/orders.log`, `orders/storage_blue/storage_blue.log`, etc.
- `modules/startup.log`, `stock/startup.log`, `flows/startup.log`, `config/startup.log`

**→ Session-Recordings werden in den OSF-Fixtures nicht verwendet.**

---

## 2. Sessions im Repo vs. Analyse-Sessions

### 2.1 Aktuell im Repo (`data/osf-data/sessions/`)

**Neue Sessions (03.03.2026, Default):**
- `start-osf_20260303_075408.log` – frischer Connect, alle retained Topics
- `storage-white_20260303_075954.log`, `storage-red_20260303_080428.log`, `storage-blue_20260303_080705.log`
- `production-white_20260303_081127.log`, `production-red_20260303_081525.log`, `production-blue_20260303_090705.log`
- `production-blue-part1_20260303_082030.log`, `production-blue-part2_20260303_090117.log`
- `mixed-pw-pr-sw-pb-sr-sb_20260303_092241.log`, `mixed-sw-pw-sw-pwnok-pw_20260303_093559.log`
- `storage-red234_20260303_094003.log`, `vibration-sw420_20260303_094240.log`

**Ältere Sessions (Legacy):**
- `default_test_session.log`, `Start_20251110_175151.log`
- `auftrag-blau_1.log`, `auftrag-rot_1.log`, `auftrag-weiss_1.log`
- `production_order_*_20251110_*.log`, `storage_order_*_20251110_*.log`
- `calibrate_dps_1_20251202_*.log`

---

## 3. Empfohlene Ersetzungen

| Alt | Neu | Aktion |
|-----|-----|--------|
| `default_test_session` | `start-osf` | Default in Scripts/README auf start-osf umstellen |
| (optional) alte Start/Production/Storage-Sessions | `storage-*`, `production-*`, `mixed-*` | Können gelöscht werden, wenn neue Sessions im Repo sind |

### 3.1 start-osf als Default (erledigt)

- `start-osf_20260303_075408.log` ist im Repo; Scripts und Doku verweisen auf den tatsächlichen Dateinamen.

---

## 4. Preloads vs. retained Topics (Audit)

**Quelle:** [mqtt-topic-conventions.md](../06-integrations/00-REFERENCE/mqtt-topic-conventions.md), [SESSION-QOS-RETAIN-ANALYSIS-20260303.md](SESSION-QOS-RETAIN-ANALYSIS-20260303.md)

### 4.1 Retained Topics (für UI-Seitenaufbau)

| Topic-Typ | Retain | Zweck |
|-----------|--------|-------|
| layout | Yes | Fabrik-Layout beim Connect |
| `*/state` | Yes | Modul-State |
| `*/connection` | Yes | Verbindungsstatus |
| `*/factsheet` | Yes | Modul-Metadaten |
| `ccu/state/*` | Yes | CCU-State |
| stock (z.B. `/j1/txt/1/f/i/stock`) | Yes | Lagerbestand |
| `ccu/order/active` | Yes | Aktive Aufträge |
| `ccu/order/completed` | Yes | Abgeschlossene Aufträge |

### 4.2 Was ist in den Preloads (`data/osf-data/test_topics/preloads/`)?

| Topic-Typ | In Preloads? | Dateien |
|-----------|--------------|---------|
| layout | ✅ Ja | `ccu_state_layout.json` (ccu/state/layout, retain) |
| `*/state` | ✅ Ja | `module_v1_ff_SVR3QA0022_state.json`, `osf_arduino_vibration_sw420-1_state*.json` |
| `*/connection` | ✅ Ja | `module_v1_ff_SVR3QA0022_connection.json`, `osf_arduino_vibration_sw420-1_connection.json` |
| `*/factsheet` | ✅ Ja | `module_v1_ff_*_factsheet.json`, `fts_v1_ff_5iO4_factsheet.json` |
| `ccu/state/*` (außer layout) | ❌ Nein | – |
| stock | ❌ Nein | – |
| `ccu/order/active` | ❌ Nein | – |
| `ccu/order/completed` | ❌ Nein | – |

### 4.3 Bewertung und Entscheidungen (03.03.2026)

- **Preloads decken ab:** layout (`ccu/state/layout`), Modul-state, Modul-connection, Modul-factsheet.
- **Bewusst NICHT in Preloads:** order/active, order/completed – nicht benötigt für Preload-Setup.
- **Bewusst NICHT in Preloads:** ccu/state/* (außer layout), stock – Inhalte hängen von Session-Trajektorie ab. Falsche oder statische Werte würden Inkonsistenzen erzeugen (z.B. Lagerplatz A1 in Preloads leer, aber production-Session lagert von A1 aus → Rest passt nicht).

**Hinweis:** Die Session `start-osf` enthält alle relevanten Topics inkl. retained. Für Replay mit vollständigem Fabrik-Setup: Session nutzen oder Preloads + Session (Preloads liefern layout/Module, Session liefert stock/orders passend zur Trajektorie).

---

## 5. Nächste Schritte (Checkliste)

- [x] `start-osf_20260303_075408.log` (und neue Sessions) ins Repo übernommen
- [x] `scripts/replay-sessions.ts` – Beispiel auf `start-osf_20260303_075408.log` umgestellt
- [x] `scripts/README-replay.md` – Beispiele auf tatsächliche Dateinamen umgestellt
- [x] `docs/04-howto/session-log-analyse.md` – Replay-Beispiel auf `start-osf_20260303_075408.log` angepasst
- [x] Preloads: layout ergänzt (`ccu_state_layout.json`); ccu/state, stock, order bewusst nicht – siehe 4.3
- [ ] (Optional) Alte Sessions löschen, nachdem neue im Einsatz sind

---

## 6. Referenzen

- [SESSION-QOS-RETAIN-ANALYSIS-20260303.md](SESSION-QOS-RETAIN-ANALYSIS-20260303.md)
- [mqtt-topic-conventions.md](../06-integrations/00-REFERENCE/mqtt-topic-conventions.md)
- [session-log-analyse.md](../04-howto/session-log-analyse.md)
- [Test-Topics README](../../data/osf-data/test_topics/README.md)
- [Replay Station](../../docs/04-howto/helper_apps/session-manager/replay-station.md)
