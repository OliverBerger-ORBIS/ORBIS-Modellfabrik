# AGV-2-Mixed Stillstand – Session-Analyse

**Datum:** 2026-03-12  
**Session:** `agv-2-mixed_20260312_134156.log`  
**Aktuellste Recordings:**
- agv-1-mixed: `agv-1-mixed_20260312_133313.log`
- agv-2-mixed: `agv-2-mixed_20260312_134156.log`

---

## Symptome

| Beobachtung | Erwartet |
|-------------|----------|
| **Stillstand** – keine AGV-Bewegung | Laufende Produktion |
| **agv-2 (jp93)** an AIQS-Station | Sollte zur DPS fahren (Blau abliefern) |
| **Blau** bei agv-2 nach Quality-PASSED | Sollte zur DPS transportiert werden |
| **Weiß** am NFC-Reader (DPS) | Sollte von agv-2 (oder agv-1) abgeholt werden |
| **LED gelb** (DPS SVR4H73275) | Zeigt „Busy“ – Modul oder FTS aktiv |

---

## Ablauf bis zum Stillstand

### BLUE-Produktionsauftrag (9805333d)

1. **13:36** – HBW → PICK (Blau geholt)
2. **13:37** – HBW → DRILL → Bearbeitung
3. **13:38** – DRILL → DROP
4. **13:39** – DRILL → MILL (jp93), Bearbeitung, DROP
5. **13:39** – MILL → AIQS (jp93), DOCK, CHECK_QUALITY
6. **13:39:54** – CHECK_QUALITY **PASSED** (Blau)
7. **13:39:56** – AIQS: DROP (jp93 holt Blau von AIQS)
8. **13:40:04** – DROP **FINISHED** – jp93 hat Blau an Bord

**Letzte jp93-Order:** `SVR3QA2098 (MILL) → 1 → 2 → SVR4H76530 (AIQS)` mit DOCK-Aktion.  
Diese Route ist abgeschlossen (DOCK FINISHED 13:39:39).

### Nächster logischer Schritt (nicht ausgeführt)

**Produktionsschritte (BLUE):**

- Step 10: NAVIGATION (72e64424) MILL→AIQS – **FINISHED**
- Step 11: CHECK_QUALITY – **FINISHED** (PASSED)
- Step 12/13: DROP (jp93 holt Blau) – **FINISHED**
- Step 14: **NAVIGATION (fc006bee)** AIQS→DPS – **ENQUEUED**
- Step 15: MANUFACTURE (DROP an DPS)

Step 14 ist NAVIGATION von AIQS nach DPS. Dafür müsste die CCU eine neue FTS-Order an jp93 schicken.

---

## Befund: keine neue Navigation für jp93

Nach 13:40:04 gibt es **keine weitere Order** für jp93.

- Letzte `fts/v1/ff/jp93/order`: 13:39:25 (Route endet bei AIQS)
- jp93 steht an AIQS mit Blau
- Step 14 (AIQS→DPS) bleibt ENQUEUED, wird aber nicht als FTS-Order ausgeliefert

**Folgerung:** Die CCU erzeugt oder versendet keine Navigations-Order für den Übergang AIQS→DPS.

---

## Parallele Situation: WHITE Storage Order

- **Order 74b1ddcc:** STORAGE WHITE, workpieceId 04798eca341290
- **13:37:58** – Order erstellt (Weiß am NFC-Reader)
- Weiß liegt weiterhin an der DPS

Weiß soll von einem AGV abgeholt und ins HBW gebracht werden.  
5iO4 (agv-1) hatte um 13:41:11 eine Order: `CHRG0 → 4 → 2 → 1 → HBW` – vermutlich andere Aufgabe.

---

## LED gelb (DPS SVR4H73275)

Aus `calcStatusLEDFromPairingState` (pairing/index.ts):

- **Gelb** = `overallBusy`: mindestens ein Modul oder FTS ist BUSY
- DPS mit Load und `assigned` → wird als `overallBusy` gewertet (Zeile 122–124)

Die gelbe LED passt zu: DPS hat Weiß am NFC und wartet auf Abholung.

---

## Mögliche Ursachen für den Stillstand

### 1. DPS als „besetzt“ blockiert Anlieferung

- DPS hat Weiß am NFC
- CCU könnte DPS als „voll“/„besetzt“ einstufen
- Dann würde sie keine DROP-Order „Blau an DPS abgeben“ erzeugen
- Gleichzeitig kann Weiß nicht abgeholt werden, weil jp93 für Blau vorgesehen ist → **Deadlock**

### 2. Keine Freigabe nach CHECK_QUALITY/DROP

- Übergang von Step 13 auf Step 14 funktioniert möglicherweise nicht korrekt
- CHECK_QUALITY und DROP an AIQS laufen, aber der nächste NAVIGATION-Step wird nicht ausgelöst

### 3. Zwei-AGV-Dispatcher

- jp93: Blau von AIQS → DPS
- 5iO4: eigene Route (z. B. HBW)
- Zuweisung oder Scheduling könnte blockieren (z. B. Route oder Ressourcenkonflikt)

### 4. DPS-Logik bei gleichzeitigem Input und Output

- Weiß wartet auf Abholung
- Blau soll abgegeben werden
- Unklar, ob die CCU diese Kombination (ein Slot frei, einer belegt) korrekt handhabt

---

## Modifikationen der CCU – mögliche Fehlerquellen?

| Modifikation | Risiko für Stillstand | Begründung |
|--------------|------------------------|-----------|
| **1. request_id (optional)** | ❌ Gering | Nur Pass-Through in Request/Response. Beeinflusst Order-Ausführung und FTS-Routing nicht. |
| **2. Quality-Fail → keine neue Order** | ⚠️ Mittleres | Im vorliegenden Fall: **PASSED**, nicht FAILED. `handleActionUpdateQualityCheckFailure` wird nicht aufgerufen. Jedoch: Falls `result` falsch geparst oder vorzeitig gecacht wird (z. B. alte FAILED-Message), könnte fälschlich der Quality-Fail-Pfad genommen werden. **Prüfen:** `isQualityCheckFailure` wird nur bei `result === 'FAILED'` true – Verwechslung unwahrscheinlich. |
| **3. serialNumber in NAVIGATION (2 AGVs)** | ⚠️ **Hoch** | Komplexeste Änderung. Mögliche Fehler: `getForOrder(orderId)` liefert `undefined` (z. B. wenn FTS-State nach DOCK-FINISHED `orderId` verliert); `isReadyForOrder` schlägt fehl; `lastModuleSerialNumber` wird nicht korrekt gesetzt; `getFtsAtPosition` wählt falsches AGV; Navigator/Route schlägt bei 2 FTS fehl. **Wahrscheinlichste Quelle**, wenn Stillstand nach AIQS-DOCK auftritt. |

### Konkrete Prüfpunkte Modifikation 3

1. **`getForOrder(9805333d)` nach DOCK-FINISHED**  
   - Wird jp93 noch als FTS für die Order geführt?  
   - Nach DOCK wird `updateAvailability(serial, READY, undefined)` aufgerufen (helper.ts) → `orderId` kann auf `undefined` gesetzt werden.  
   - `getForOrder` nutzt sonst `loadingBayCache.getLoadingBayForOrder` – Cache korrekt?

2. **`lastModuleSerialNumber` von jp93**  
   - Muss SVR4H76530 (AIQS) sein, damit Route AIQS→DPS berechnet werden kann.

3. **`isReadyForOrder(jp93, orderId)`**  
   - Muss true sein (connected, READY, orderId passt oder ist frei).

---

## Empfohlene Debug-Schritte

### 1. CCU-Logs nach 13:40:04

```bash
ssh 192.168.0.100 "docker logs central-control-prod --since '2026-03-12T12:40:00' 2>&1 | grep -E 'navigation|jp93|NAVIGATION|fc006bee|order'"
```

Prüfen: Wird für Step 14 (NAVIGATION AIQS→DPS) eine FTS-Order erzeugt bzw. an jp93 gesendet?

### 2. CCU Order-Management

- Wo wird nach abgeschlossenem Step 13 der nächste NAVIGATION-Step (14) ausgelöst?
- Gibt es eine Prüfung der DPS-Verfügbarkeit vor dem Erzeugen der AIQS→DPS-Route?
- Wenn ja: Welche Bedingung blockiert hier?

### 3. DPS-State aus Sicht der CCU

- Welchen State meldet die DPS um 13:40? (Loads, Slots)
- Wird DPS als „full“ oder „blocked“ behandelt, obwohl ein Slot für Blau frei wäre?

### 4. Replay zur Reproduktion

- Session `agv-2-mixed_20260312_134156.log` im Replay bis kurz vor 13:40 abspielen
- Beobachten: Wird `fts/v1/ff/jp93/order` mit Route AIQS→DPS publiziert?

---

## Topic-Übersicht (agv-2-mixed Session)

| Topic | Anzahl | Anmerkung |
|-------|--------|-----------|
| fts/v1/ff/jp93/state | 74 | agv-2, letzter State: DOCK FINISHED an AIQS, load BLUE |
| fts/v1/ff/jp93/order | 4 | Letzte Order endet bei AIQS |
| fts/v1/ff/5iO4/state | 24 | agv-1 |
| fts/v1/ff/5iO4/order | 1 | Route CHRG0→HBW (13:41) |
| ccu/order/active | 20 | BLUE 9805333d IN_PROCESS |
| module/v1/ff/SVR4H73275/instantAction | 293 | setStatusLED gelb |
| module/v1/ff/SVR4H76530/state | – | AIQS |

---

## Serials

- **jp93** = agv-2
- **5iO4** = agv-1  
- **SVR4H73275** = DPS (LED gelb)
- **SVR4H76530** = AIQS
