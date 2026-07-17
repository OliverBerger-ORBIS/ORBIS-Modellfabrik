# Plan: NFC logische workpieceId (B-soft) — TXT-DPS

**Status:** Blockly-Änderungen in `archives/FF_DPS_24V_osf_nfc.ft` erledigt (17.07.2026) · Deploy + Live-Test vor Ort ausstehend · **Sprint:** 26  
**Nach erfolgreichem Test:** dieses Dokument kann gelöscht werden. TXT-UI/Workflow: [txt-controller-deployment.md](../04-howto/txt-controller-deployment.md).

## Ziel

Bei jedem Wareneingang eine **neue 14-Hex-`workpieceId`** erzeugen (nicht die unveränderliche NTAG-UID), damit Track&Trace frische Identitäten sieht. Am Ausgang nur prüfen, dass ein Tag vorhanden ist; Identität kommt aus der CCU-Order.

## Dauerhafte Doku (nicht hier duplizieren)

| Thema | Quelle |
|--------|--------|
| ROBO Pro: Öffnen, Backup, Deploy, Autostart | [txt-controller-deployment.md](../04-howto/txt-controller-deployment.md) |
| `archives/` vs `workspaces/`, kein Hand-Edit als Deploy | [DR-17](../03-decision-records/17-txt-controller-deployment.md) |
| Vorbild Varianten/Backup | [TXT-AIQS README](../06-integrations/TXT-AIQS/README.md) |
| DPS NFC Memory / Topics | [APS-CCU dps.md](../../integrations/APS-CCU/docs/06-modules/dps.md) |

## Voraussetzungen (Checkliste On-Site)

- [ ] Laptop im FT-/Demo-LAN, DPS-TXT erreichbar (historisch oft `192.168.0.101`)
- [ ] ROBO Pro Coding installiert, API-Key vom TXT-Display
- [ ] **`.ft` in `archives/`:** Fischertechnik [FF_DPS_24V.ft](https://github.com/fischertechnik/Agile-Production-Simulation-24V/tree/main/TXT4.0-programs) oder TXT-Webserver-Backup — dann [How-To](../04-howto/txt-controller-deployment.md) (AIQS-Muster: Laden → Lokal)
- [ ] Arbeitskopie: `archives/FF_DPS_24V_osf_nfc.ft`
- [ ] Live-Test möglich (Wareneingang + kompletter Auftrag bis Ausgang)

**Remote (ohne Shopfloor):** keine weitere Code-Vorbereitung — `workspaces/` nur Analyse, kein Deploy-Format.

## Änderung (nur TXT `lib/VGR.py`, B-soft)

Analyse-Spiegel: `integrations/TXT-DPS/workspaces/FF_DPS_24V/lib/VGR.py`  
**Nicht** im Repo-`workspaces/` deployen — nur in ROBO Pro an der `.ft`-Kopie ändern.

### 1) Wareneingang — `handle_NFC()`

- Tag lesen: physische UID nur für „Tag da?“
- Wenn gültig: `uid = os.urandom(7).hex()` (14 Hex; `import os` falls nötig)
- `nfc_input_history_handle()` unverändert (nutzt globales `uid`)
- `set_vda_action_result(uid)` bleibt → Node-RED/CCU bekommen die neue ID

### 2) Ausgang — `delivery_verify_nfctag()` und `delivery_write_history()`

- Ersetzen: `valid = wp_uid == uid`
- Durch: `valid = wp_uid != None and wp_uid != ''`
- History-Schreiben über CCU-`metadata.workpieceId` bleibt

### Nicht ändern (B-soft)

- `Nfc.py` / Memory-Map, Node-RED, CCU, OSF-UI

## On-Site Ablauf (Kurz)

1. ~~Original + Arbeitskopie~~ → erledigt (`archives/FF_DPS_24V.ft`, `_osf_nfc.ft`)  
2. ~~Drei Stellen Blockly in `lib/VGR`~~ → erledigt (siehe How-To-Beispiel DPS NFC)  
3. Vor Ort: verbinden → Toolbar **Programm hochladen** → Load + Autostart  
4. Test: neuer Wareneingang → neue ID; Ausgang ohne `NFC_workpieceId_mismatch`  
5. Bei Erfolg: `.ft` committen; optional `unzip` nach `workspaces/`; Sprint-Task abhaken  
6. Bei Misserfolg: `FF_DPS_24V.ft` wieder deployen  
7. Plan-Dokument löschen

## Abnahmekriterien

- Gleicher physischer Tag, zwei Wareneingänge → **zwei** verschiedene `workpieceId`s in MQTT/Track&Trace  
- Auslieferung (PICK) ohne UID-Mismatch-Warnung  
- Rollback auf Original-`.ft` jederzeit möglich
