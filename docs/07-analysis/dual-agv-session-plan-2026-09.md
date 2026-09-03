# Dual-AGV Referenz-Sessions — Plan (Sept. 2026)

**Stand:** 03.09.2026  
**Kontext:** AGV-2 **`xkI4`**, OSF-UI **1.3.6**; Demos **Bühler (14.09.)**, **Welcome Days (17.09.)**  
**Dispatch-Modell:** [second-agv-2026-03.md](second-agv-2026-03.md) § CCU-Dispatch — **keine Order↔AGV-Bindung**, Step-Vergabe durch CCU.

---

## 1. Was wir aufnehmen wollen

| Ziel | Warum |
|------|--------|
| Zwei **PRODUCTION**-Orders **parallel** | Einziger realistischer Dual-FTS-Mehrwert am Shopfloor |
| **Beide FTS** (`5iO4`, `xkI4`) in `fts/v1/ff/…/order` | Step-Dispatch sichtbar; ersetzt Interim-Logs (`jp93`/`leJ4`) |
| Replay: Shopfloor, AGV-Tab, Orders (Steps), T&T | Demo + Regression |
| **Kein** Storage/Intake in derselben Session nötig | HBW vorbestückt; Storage→Production bereits in 1-AGV-Aug-Sessions |

**Erfolgskriterium (Replay):**

- Beide Orders **completed**
- In Orders-Tab: **unterschiedliche AGV-Labels auf verschiedenen NAVIGATION-Steps** (auch innerhalb einer Order möglich)
- **Nicht** prüfen: „WHITE = AGV-1“ o. Ä.

---

## 2. Empfohlene Sessions (Priorität)

### Session A — **Pflicht** *(aufgenommen 01.09.2026)*

| Feld | Wert |
|------|------|
| **Datei** | `storage-blue-dual-agv-bwr_20260901_124524.log` |
| **Ablauf** | STORAGE BLUE → PRODUCTION BLUE + WHITE (parallel) → PRODUCTION RED |
| **FTS** | **5iO4**, **xkI4** — CCU Step-Dispatch |
| **Status** | Aufnahme **ok**; Vorgänger-Referenz (OSF 1.3.5) |

### Session A2 — **Referenz** *(03.09.2026 vormittag)*

| Feld | Wert |
|------|------|
| **Datei** | `storage-brw-dual-agv-brw_20260903_092247.log` |
| **Ablauf** | STORAGE B/W/R → PRODUCTION BLUE + RED (parallel) → PRODUCTION WHITE; Dock/Init + Charge |
| **FTS** | **5iO4**, **xkI4** — CCU Step-Dispatch |
| **Status** | Aufnahme **ok**; OSF **1.3.6** |

### Session A3 — **Aktuelle Referenz** *(03.09.2026, Live-Abnahme)*

| Feld | Wert |
|------|------|
| **Datei** | `storage-wbr-dual-agv-rwb_20260903_094319.log` |
| **Ablauf** | STORAGE W/B/R → PRODUCTION RED, WHITE, BLUE (HBW-Start auf AGV-2; AGV-1 später); Charge |
| **FTS** | **5iO4**, **xkI4** — CCU Step-Dispatch |
| **Status** | Aufnahme **ok**; Grafana + T&T **live OK**; **Replay-Abnahme** noch offen |

### Session B — **Optional** (zweite Farbkombination)

| Feld | Wert |
|------|------|
| **Name** | `production-dual-wb-clean_*` |
| **Orders** | **WHITE + BLUE** parallel |
| **Nutzen** | Zweites Referenzmaterial; leicht andere Step-Timing-Überlappung |

Nur aufnehmen, wenn Session A Replay sauber ist.

### Bewusst **nicht** (Stand Sept. 2026)

| Szenario | Grund |
|----------|--------|
| Dual **Storage** | Selten, hoher DPS-Aufwand; kein Dual-FTS-Kernfall |
| Storage + Production in **einer** 2-AGV-Session | Lang; 1-AGV `*-storage-production_*` deckt Intake/T&T ab |
| Neues `startup-clean` | Existiert (`startup-clean_20260512_*`, xkI4); nur bei Factory-Reset neu |
| Multi-Load + 2 FTS | Später; Demo-Fokus erst Parallel-Production |

---

## 3. Ablauf Checkliste (Aufnahme)

1. Message Monitor: **`5iO4`** und **`xkI4`** online, Pairing OK  
2. HBW-Bestand für geplante Farben prüfen  
3. Session Recorder starten; `session_meta` ausfüllen  
4. Beide PRODUCTION-Requests **ohne große Pause** nacheinander  
5. Bis beide Orders **completed** warten (kein manueller Eingriff)  
6. Stop; Log prüfen: beide `fts/v1/ff/<serial>/order`-Topics mit Substanz  
7. Replay OSF-UI: Shopfloor (2 AGVs), AGV-Tab, Orders-Steps, T&T  
8. [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md) ergänzen; Sprint-29-Task abhaken  

---

## 4. Demo-Narrative (Bühler / Welcome Days)

**Kurz (DE):** „Zwei Fertigungsaufträge laufen parallel. Die CCU vergibt **jeden Transport-Schritt** an das **nächste freie FTS** — die Zuordnung wechselt stepweise, nicht pro Auftrag.“

**Storage/Intake (optional):** Separat mit 1-AGV-Session zeigen (`blue-storage-production_20260807_*`) — „Werkstück lag bereits im HBW.“

---

## 5. Referenzen

- Interim (historisch): `production-wr-agv2-b-agv1-clean_20260513_135600`, `two-agvs-mixed_20260312_165108`  
- [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md)  
- [session-recorder.md](../04-howto/helper_apps/session-manager/session-recorder.md)  
- Cursor-Regel: `.cursor/rules/fts-agv-step-dispatch.mdc`
