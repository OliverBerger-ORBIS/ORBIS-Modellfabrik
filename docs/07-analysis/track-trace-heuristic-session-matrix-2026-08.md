# Track & Trace — Heuristik × Session Matrix (2026-08-10)

**Zweck:** Entscheiden, welche Attribution-Sonderlogik wir behalten / eng fassen / streichen — **ohne** White-OK als einzigen Maßstab.  
**Kontext:** Session Manager **v1.8.5** (Publish-Integrity). Viele „fehlende Events“ bei Replay waren `Fail≫0`, nicht kaputte Attribution. White-OK sieht mit `Fail=0` auf dem **committed** Live-Pfad gut aus.  
**Kein Code in diesem Dokument** — Entscheidungsgrundlage vor dem Aufräumen.

**Verwandt:** [SOLL by color](../04-howto/osf-ui-track-trace-soll-by-color.md) · [Attribution How-to](../04-howto/osf-ui-track-trace-history-attribution.md) · [Replay Diagnose](../04-howto/helper_apps/session-manager/replay-station.md)

---

## 0) Zwei Code-Welten (wichtig)

| Welt | Ort | Status |
|------|-----|--------|
| **Live (Produkt)** | `WorkpieceHistoryService` (~2800 Z.) | **committed** — `getLastMessage` (Topic-Tails); Sticky FTS; `pendingDpsIntake`; Dock/Order-Match |
| **WIP Pipeline** | `osf/apps/osf-ui/src/app/track-trace/` (untracked) | **nicht verdrahtet** — zusätzliche Heuristiken: `pendingModule`, `nfcByOrderId`, sole-history, Payload-Zeit-Sort, kein FTS-Bootstrap |

**Regel für Tests jetzt:** Visuelle Abnahme läuft gegen **Live WHS**. WIP-Pipeline erst bewerten, wenn sie verdrahtet ist oder Gate-A-only.

**Replay-Voraussetzung:** Diagnose `OK=total Fail=0` („valid for Track & Trace acceptance“). Sonst Session **nicht** als Attribution-Bug werten. Empfohlene Speed: **5x** (1x zu langsam; max nur Spot-Check).

---

## 1) Heuristik-Katalog

### A — Live WHS (committed, läuft heute)

| ID | Heuristik | Kurz |
|----|-----------|------|
| **A1** | `pendingDpsIntake` (Color→NFC) | `INPUT_RGB` puffern bis `RGB_NFC` |
| **A2** | FTS sticky loads | `loadType` ohne `loadId` weiterführen |
| **A3** | Modul-ID aus `result` / CCU `workpieceId` / Order | Identity-Resolve |
| **A4** | Match per `orderId` (+ Farbe+Order) | DROP ohne NFC im Payload |
| **A5** | `findWorkpieceDockedAtModule` | Modul ohne Id → docked NFC |
| **A6** | FTS **legt** Historien aus `loadId` an | Bootstrap (Ghost-Risiko nach Refresh) |
| **A7** | Synth / Sonderfälle (z. B. DPS PICK) | Shopfloor-Lücken füllen wo dokumentiert |
| **A8** | Dedup / HBW-Slot / TURN | Darstellung & Rauschen |

### B — nur WIP Pipeline (noch nicht live)

| ID | Heuristik | Kurz |
|----|-----------|------|
| **B1** | `pendingModule` Queue + Flush | Modul-FINISHED ohne NFC → Retry nach Order/NFC |
| **B2** | `nfcByOrderId` sticky | leeres `result` → NFC von Order merken |
| **B3** | sole-history (`size===1`) | einziges Werkstück bekommt alles |
| **B4** | sole-color (eine History dieser Farbe) | wie B3, farbgefiltert |
| **B5** | kein FTS-History-Bootstrap | nur MODULE startet NFC-Historie |
| **B6** | Payload-Zeit-Sort (`ingestAll`) | Shopfloor-ts statt Receive-ts |

---

## 2) Session-Klassen (Testreihenfolge)

Lokal vorhanden (Auszug, Aug-2026-Referenzen bevorzugt):

| Prio | Klasse | Beispiel-Session | Warum |
|:----:|--------|------------------|-------|
| 0 | Single White OK | `white-storage-production_20260807_111716` | Baseline — **bereits OK** |
| 1 | Single Red OK | `red-storage-production_20260807_113213` | 2. Farbe, oft Color/NFC-Lücken in ml, hier Single sauber |
| 2 | Single Blue OK | `blue-storage-production_20260807_112530` | 3. Farbe Pass |
| 3 | Single NOK (je 1) | `white-…-nok_…114322`, `red-…-nok_…113739`, `blue-…-nok_…110943` | Quality FAILED + Abbruch |
| 4 | Multi all-OK | `ml-wbr_20260807_125133` | **3 NFCs** — B3/B4 müssen hier **scheitern dürfen**, wenn falsch |
| 5 | Multi gleiche Farbe | `storage-production-ml-rrr_20260804_133245` / `…-bbb_…` | B4 besonders gefährlich |
| 6 | Multi + NOK / CHRG | `ml-rbw-blue-nok_…`, `ml-wrb-chrg-blue-nok_…` | Sticky + Mitfahrt + Fail |
| — | Interim 2-AGV | später | nicht Blocker für Heuristik-Schnitt |

---

## 3) Matrix: Heuristik × Session-Klasse

Legende: **K** = Keep (brauchen wir) · **?** = messen · **X** = Streich-Kandidat wenn Tests grün · **—** = irrelevant · **G** = Session-Gap (kein UI-Fill)

| Heuristik | White OK | Red/Blue OK | Single NOK | ml-wbr (3 NFC) | ml-rrr/bbb | ml+NOK/CHRG |
|-----------|:--------:|:-----------:|:----------:|:--------------:|:----------:|:-----------:|
| **A1** Color pending | K | K | K | K | K | K |
| **A2** FTS sticky | K | K | K | K | K | K |
| **A3** result/CCU wpId | K | K | K | K | K | K |
| **A4** orderId match | K | K | K | K | K | K |
| **A5** docked match | ? | ? | ? | **K** | **K** | **K** |
| **A6** FTS bootstrap | ? Ghost | ? | ? | ? Ghost | ? | ? |
| **A7** Synth DPS PICK | ? | ? | ? | ?/G | ? | ? |
| **A8** Dedup/HBW/TURN | K | K | K | K | K | K |
| **B1** pendingModule | ? | ? | ? | ? | ? | ? |
| **B2** nfcByOrderId | ?→K | ?→K | ? | **K?** | **K?** | **K?** |
| **B3** sole-history | wirkt | wirkt | wirkt | **X gefährlich** | **X** | **X** |
| **B4** sole-color | wirkt | wirkt | wirkt | **X** | **X tödlich** | **X** |
| **B5** no FTS bootstrap | ? | ? | ? | ? gegen Ghost | ? | ? |
| **B6** payload-time sort | Replay | Replay | Replay | Replay | Replay | Replay |

**Lesart:** Was bei White „überflüssig wirkt“, kann bei **ml-*** **Pflicht** (A5, A2) oder **Gift** (B3/B4) sein.

---

## 4) Abnahme-Protokoll (zügig, je Session)

Voraussetzung: SM **v1.8.5**, Speed **5x**, Header-Refresh **nur vor Start**.

1. Session laden → Play → warten bis Diagnose **Fail=0**.  
2. OSF Live Demo → Farbe wählen → NFC öffnen.  
3. Checkliste (kurz):
   - STORAGE + PRODUCTION Karten vorhanden?
   - Planned-Stations-Haken vs Timeline (SOLL-Doku)?
   - **Falsche NFC-Zuordnung?** (Event einer NFC auf anderer Historie) → sofort notieren (Heuristik-Verdacht A5/B3/B4).
   - Fehlende Station **nur** akzeptieren, wenn SOLL **gap/session** sagt.
4. Ergebnis in Tabelle unten eintragen (eine Zeile pro Session).

### Ergebnis-Log (ausfüllen beim Test)

| Session | SM Fail=0? | T&T Urteil | Auffälligkeit / vermutete Heuristik | Keep-Hinweis |
|---------|:----------:|------------|-------------------------------------|--------------|
| white `…111716` | ✓ | OK (Referenz) | — | Baseline |
| red `…113213` | |ok | | |
| blue `…112530` | |ok | | |
| white-nok `…114322` | |ok | | |
| red-nok `…113739` | |ok | | |
| blue-nok `…110943` | |ok | | |
| ml-wbr `…125133` | |ok | | **B3/B4 beobachten** |
| ml-rrr / ml-bbb | |ok | | **B4 beobachten** |
| ml-rbw-blue-nok / chrg | |ok | | sticky/CHRG |

**Abnahme 2026-08-10 (User):** Alle gelisteten Sessions bei Replay **v=10** — T&T durchgängig gut (SM Publish-Integrity vorausgesetzt). **Committed Live-Pfad reicht**; WIP-Pipeline/B3/B4 nicht live nötig. Sole-Heuristiken nicht übernehmen, solange ml-* ohne sie ok ist.

---

## 5) Entscheidungsregeln nach den Tests

1. **Nur streichen**, wenn **alle** getesteten Klassen ohne die Heuristik korrekt bleiben **oder** die Heuristik in ml-* **falsch zuordnet**.  
2. **B3/B4:** Default-Empfehlung **nicht live übernehmen** (bzw. aus WIP entfernen), sobald ml-wbr/`rrr` laufen — außer stark eingeschränkt (z. B. nur Demo-Flag).  
3. **A6 vs B5:** Wenn nach Refresh Ghost-NFCs → Richtung **B5** (kein FTS-Bootstrap). Wenn Multi-Load ohne MODULE früh unsichtbar → A6 behalten, Ghosts anders lösen.  
4. **B1:** Nur behalten, wenn mit `Fail=0` und chronologischem Stream noch Events „zu früh“ ohne Order verloren gehen.  
5. **B2:** Behalten-Kandidat, wenn Modul-Events ohne `result` in ml-* an der **richtigen** NFC landen (sonst A4/A5 reichen?).  
6. Keine UI-Spekulation für SOLL-**session**-Gaps (Red ohne NFC in manchen ml-*).

---

## 6) Nächster Arbeitsschritt (nach Matrix-Tests)

1. Ergebnis-Log füllen (Abschnitt 4).  
2. Keep/Drop-Liste fixieren (1 Seite).  
3. Dann erst: WIP Pipeline verdrahten **oder** entschlacken — nicht beides parallel.  
4. Optional Gate-A um Red/Blue/ml erweitern (nur für behaltene Heuristiken).

---

## Kurzfazit

- White-OK gut ≠ Logik überflüssig.  
- **ml-*** entscheidet über sole-Heuristiken (B3/B4).  
- Sticky/Color/Order/Dock (A1–A5, A8) sind die wahrscheinlichen **Keep**-Kern.  
- SM `Fail=0` bleibt die Eintrittskarte für jedes Urteil.
