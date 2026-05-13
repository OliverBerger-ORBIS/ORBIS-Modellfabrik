# ORBIS Checklist: CCU `v1.3.0-osf.4` Deploy + Retest

Stand: 2026-05-13

Ziel: Vor-Ort bei ORBIS die vorbereitete CCU-Haertung deployen und danach die Sessions erneut aufnehmen, um den intermittierenden Quality-Fail-Stillstand zu validieren.

---

## 1) Pre-Deploy (lokal, vor Ort)

1. Branch/Workspace prüfen (keine ungewollten Änderungen).
2. Version prüfen:
   - `integrations/APS-CCU/package.json` -> `1.3.0-osf.4`
   - `integrations/APS-CCU/central-control/package.json` -> `1.3.0-osf.4`
3. Optional lokaler Test:
   - `cd integrations/APS-CCU/central-control`
   - `npm test -- src/modules/order/management/order-management.test.ts src/modules/fts/navigation/navigation.test.ts`

---

## 2) Deploy auf RPi (erst bei ORBIS ausführen)

```bash
cd integrations/APS-CCU
npm run docker:build v1.3.0-osf.4 central
npm run docker:deploy -- ff22@192.168.0.100 v1.3.0-osf.4 central
```

Verifikation:

```bash
ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml ps"
ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml logs central-control --tail 80"
```

---

## 3) Session-Retest (Race-/Intermittent-Fokus)

Empfohlener Ablauf:

1. Referenz-Storage + Production-Ketten erneut fahren (insbesondere Chains B und C).
2. Mindestens 4 Vergleichsläufe mit ähnlichem Order-Timing.
3. Ergebnis pro Lauf in die Run-Matrix eintragen:
   - siehe `docs/07-analysis/intermittent-quality-fail-runbook-template.md`
4. Marker prüfen:
   - `CHECK_QUALITY FAILED`
   - `ccu/order/cancel` (falls vorhanden)
   - FTS/Module-Blockade-Signatur
   - Recovery nötig? (`AGV -> HBW`, `clearLoadHandler`)

---

## 4) Akzeptanzkriterien vor „Fix bestätigt“

- Kein ungelöster Stillstand im vergleichbaren Testset.
- Parallele Orders laufen nach Quality-Fail anderer Orders weiter.
- Kein manueller Recovery-Zwang in den nominalen Wiederholungsläufen.
- Session-Inventory + session_meta aktualisiert (inkl. `trackTraceChain` falls zutreffend).

---

## 5) Nacharbeiten (nach ORBIS-Lauf)

1. `data/osf-data/sessions/INVENTORY.md` ergänzen.
2. Erkenntnisse in `docs/07-analysis/` dokumentieren (inkl. Häufigkeit `x/y`).
3. Bei bestätigter Stabilität: Change in Sprint-Doku als verifiziert markieren.
