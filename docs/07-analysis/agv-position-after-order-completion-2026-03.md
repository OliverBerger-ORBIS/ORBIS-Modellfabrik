# AGV/FTS-Position nach Production-Order-Abschluss

**Datum:** 2026-03-13  
**Quelle:** Fischertechnik CCU-Code, Session-Logs  
**Ziel:** Analytische und empirische Auswertung – wo befindet sich ein AGV nach erfolgreichem bzw. fehlgeschlagenem Production-Prozess?

---

## ⚠️ Kritische Bedingung

**Entscheidend für die Analyse: keine weiteren parallelen oder offenen Orders.**

Sobald weitere Orders in der Queue oder aktiv sind, diktiert der offene Order-Prozess die FTS-Position (z.B. NAV zu HBW für nächsten Production-Order). Die folgende Auswertung bezieht sich auf den Fall **leere Queue, keine parallelen Orders**.

---

## Kurzantwort

| Szenario | AGV-Position danach (keine weiteren Orders) | Code-Analyse | User-Erfahrung | Sessions (mit weiteren Orders) |
|----------|---------------------------------------------|--------------|----------------|--------------------------------|
| **Production erfolgreich** | **HBW** (User) vs. DPS (Code) | Keine explizite Weiterfahrt nach Erfolg | Fahrt von DPS zu HBW | production-blue: DPS (Queue nicht leer?) |
| **Storage erfolgreich** | HBW | Letzter Step = HBW PICK | – | storage-blue: HBW ✓ |
| **Production mit Quality-Fail** (OSF Option B) | **HBW** (User) vs. erstes freies Modul (Code) | sendClearModuleNodeNavigationRequest | Fahrt von AIQS zu HBW | mixed-sr-pr-prnok: AIQS → DPS |
| **Production mit Quality-Fail** (Original) | HBW (bei Ersatzauftrag) | NAV zu HBW für Ersatz | – | – |

**Diskrepanz:** User-Erfahrung: End-Position = **HBW** in beiden Fällen (Success und Quality-Fail). Code-Analyse und bisherige Session-Auswertung zeigen teils DPS. Mögliche Ursachen: Sessions hatten weitere Orders in Queue; oder Reihenfolge in `pairingStates.getAll()` begünstigt HBW als „erstes freies Modul“.

---

## 1. Analytische Auswertung (CCU-Code)

### 1.1 Production-Order – Erfolgreicher Abschluss

**Flow (order-flow-service.ts):**
- BLUE/RED/WHITE: HBW PICK → [MILL/DRILL, AIQS] → **NAV to DPS** → **DPS PICK**
- Letzter Step = DPS PICK (Werkstück am DPS abgeben)
- **Keine** automatische Navigation nach Abschluss

**Code:** `handleActionUpdate()` in order-management.ts (Zeilen 450–453):
- Bei letztem Step: `activeOrder.state = FINISHED`, `deleteFinishedOrders()`, `retriggerFTSSteps()`, `startNextOrder()`
- **Kein** `sendClearModuleNodeNavigationRequest` nach Erfolg
- Das FTS bleibt an der Position des letzten Steps (DPS)

**Fazit:** Das AGV bleibt am **DPS**, es fährt **nicht** automatisch zum HBW.

### 1.2 Navigation unmittelbar nach Prozessabschluss

- Es gibt **keine** dedizierte „Weiterfahrt“ nach erfolgreichem Abschluss.
- `retriggerFTSSteps()` startet nur wartende Navigation-Steps **anderer** Orders.
- Wenn die nächste Order beginnt, erhält das FTS ggf. eine neue NAV-Anweisung (z.B. DPS → HBW für neuen Production-Order).

### 1.3 Production-Order – Quality-Fail an AIQS (OSF Option B)

**Code:** `handleActionUpdateQualityCheckFailure()` (order-management.ts, Zeilen 455–471):
- Kein Ersatzauftrag (OSF-Modifikation, OSF-MODIFICATIONS.md Mod²)
- `sendClearModuleNodeNavigationRequest(aiqsModuleSerial)` – FTS fährt vom AIQS weg
- Ziel: **erstes freies Modul** (nicht zwingend HBW)

**Zielmodul (navigation.ts, Zeilen 352–357):**
```typescript
const freeModule = pairingStates
  .getAll()
  .find(m => m.pairedSince && m.connected && m.subType !== ModuleType.CHRG && !ftsPairingStates.getFtsAtPosition(m.serialNumber));
```
- Reihenfolge aus `getAll()` – es wird das erste freie Modul gewählt
- Typischerweise: DPS, HBW, DRILL, MILL (je nach Belegung)
- **Nicht deterministisch HBW** – oft DPS, wenn dieser frei ist

### 1.4 Production-Order – Quality-Fail (Original Fischertechnik Option A)

- CCU erstellt Ersatzauftrag
- FTS bleibt zunächst am AIQS
- Ersatzauftrag startet mit NAV HBW → FTS fährt zur HBW für PICK

---

## 2. Empirische Auswertung (Session-Logs)

**Tool:** `scripts/analyze_session_fts_positions.py`

**Referenz-Module:**
- SVR4H73275 = DPS (Ein-/Ausgang)
- SVR3QA0022 = HBW (Hochregallager)
- SVR4H76530 = AIQS (Qualitätsprüfung)

### 2.1 Erfolgreicher Production-Abschluss

| Session | Order-Typ | FTS-Position nach FINISHED |
|---------|-----------|----------------------------|
| production-blue | Production (BLUE) | DPS (SVR4H73275) |
| storage-blue | Storage | HBW (SVR3QA0022) |
| mixed-sr-pr-prnok | Mixed (Production + Storage) | DPS bzw. HBW je nach Order |
| mixed-sw-pw-sw-pwnok-pw | Mixed | DPS bei Production, HBW bei Storage |

**Ergebnis:** In diesen Sessions blieb das FTS am Modul des letzten Steps. Diese Sessions hatten vermutlich weitere Orders in der Queue – bei explizit leerer Queue könnte das Verhalten abweichen (vgl. User-Erfahrung: HBW).

### 2.2 Quality-Fail (CHECK_QUALITY FAILED)

| Session | CCU-Variante | FTS vor FAILED | FTS nach FAILED |
|---------|--------------|----------------|-----------------|
| mixed-sr-pr-prnok | OSF Option B | AIQS (SVR4H76530) | DPS (SVR4H73275) |
| mixed-sw-pw-sw-pwnok-pw | Original Option A | AIQS | Bleibt am AIQS (Ersatzauftrag, NAV zu HBW folgt später) |

---

## 3. Zusammenfassung und offene Punkte

### User-Erfahrung (unter Bedingung: keine weiteren Orders)
- **Production erfolgreich:** AGV fährt von DPS zu **HBW**
- **Quality-Fail:** AGV fährt von AIQS zu **HBW**
- **Storage erfolgreich:** AGV bleibt an HBW (letzter Step)

### Code-Analyse
- **Production erfolgreich:** Kein expliziter „Weiterfahr“-Befehl nach Abschluss; FTS bliebe am DPS
- **Quality-Fail:** `sendClearModuleNodeNavigationRequest` → Ziel = erstes freies Modul aus `pairingStates.getAll()` (Reihenfolge variabel; HBW möglich)
- **Blocked-Module-Logik:** Wenn eine Order zum Modul X möchte und FTS dort steht, wird FTS per Clear wegbewegt – könnte DPS betreffen, wenn eine spätere Order DPS als Ziel hat

### Mögliche Erklärungen für die Diskrepanz
1. **Sessions mit weiteren Orders:** Die analysierten Sessions (production-blue, mixed-*) könnten weitere Orders in der Queue haben – dann würde `startNextOrder()` + NAV HBW die Fahrt DPS→HBW auslösen
2. **Reihenfolge `getAll()`:** HBW als „erstes freies Modul“ bei sendClearModuleNodeNavigationRequest (z.B. durch Verbindungs-/Factsheet-Reihenfolge)
3. **Andere CCU-Version/Modifikation:** Möglicherweise andere Logik als im analysierten Code
4. **DPS als blockiert:** Falls eine Order DPS als Ziel hat und FTS dort steht, würde Clear ausgelöst – Ziel dann freies Modul (evtl. HBW)

---

## 4. Empfohlene Verifikation

**Test mit explizit leerer Queue:**
1. Einzelne Production-Order auslösen, warten bis COMPLETED
2. Sicherstellen: Keine weiteren Orders in Queue (`ccu/order/active` leer bzw. nur die eine Order die gerade fertig wird)
3. FTS-Position aus `fts/v1/ff/+/state` bzw. `ccu/pairing/state` nach Abschluss prüfen
4. Analog für Quality-Fail: eine Order mit AIQS, CHECK_QUALITY FAILED, danach Queue leer

**Analyse-Skript erweitern:** Filter für „letzte Order in Session“ bzw. „ccu/order/active Länge = 1 vor Abschluss“, um nur Single-Order-Szenarien auszuwerten.

---

## 5. Referenzen

- [OSF-MODIFICATIONS.md](../../integrations/APS-CCU/OSF-MODIFICATIONS.md) – Mod² Quality-Fail
- [ccu-quality-fail-behaviour-2026-03.md](ccu-quality-fail-behaviour-2026-03.md)
- [order-flow-service.ts](../../integrations/APS-CCU/central-control/src/modules/order/flow/order-flow-service.ts)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts)
- [navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts) – `sendClearModuleNodeNavigationRequest`
- Analyse-Skript: `scripts/analyze_session_fts_positions.py`
