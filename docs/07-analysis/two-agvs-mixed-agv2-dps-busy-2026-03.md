# two-agvs-mixed: AGV-2 bleibt an DPS mit Rot geladen – Stillstand (Busy)

**Datum:** 2026-03-12  
**Session:** `two-agvs-mixed_20260312_165108.log` (16:51, Recording 16:45–16:51)  
**Symptom:** AGV-2 (jp93) bleibt an DPS-Station stehen, nachdem das rote Werkstück geladen wurde. Zustand „busy“. Keine weiteren Aufträge möglich. Parallel: AGV-1 (5iO4) mit Production-Order hat Werkstück vom AIQS und soll zum DPS – die DPS ist aber durch jp93 belegt.

**Event-getriebene Analyse + Fischertechnik-Frage:** [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](two-agvs-mixed-event-chain-fischertechnik-2026-03.md)

---

## Ablauf bis zum Stillstand

### RED Storage Order (fc14e7f5-a1c4-4af9-8057-b76b9c7079e8)

| Zeit (Log) | Ereignis |
|------------|----------|
| 16:47:44 | STORAGE RED erstellt, workpieceId 04d78cca341290 |
| 16:47:44 | jp93 erhält Order: START → DPS (NAVIGATION) |
| 16:47:58 | jp93 DOCK FINISHED an DPS, ROT geladen (loadPosition 1) |
| 16:47:58 | DPS (SVR4H73275) erhält DROP-Order – ROT an AGV übergeben |
| 16:47:58 | CCU: Step 2 (MANUFACTURE DROP) auf IN_PROGRESS |
| 16:48:11 | **NodeRed** sendet DROP FINISHED auf `module/v1/ff/NodeRed/SVR4H73275/state` |
| 16:48:12 | **SVR4H73275** sendet actionState FINISHED für **setStatusLED** (nicht DROP!) |
| 16:50:58 | Letzte jp93-State: ROT noch geladen, lastNodeId SVR4H73275, waitingForLoadHandling: true |

**Step-Status der RED Storage Order (bei 16:47:58):**
- Step 1: NAVIGATION START→DPS – **FINISHED**
- Step 2: MANUFACTURE DROP (DPS) – **IN_PROGRESS** (bleibt hängen)
- Step 3: NAVIGATION DPS→HBW – **ENQUEUED** (abhängig von Step 2)
- Step 4: MANUFACTURE PICK (HBW) – ENQUEUED

---

## Ursache: CCU erhält nie DROP FINISHED

### Topic- und Source-Mismatch

| Quelle | Topic | DROP RUNNING | DROP FINISHED |
|--------|-------|--------------|---------------|
| **TXT/SPS direkt** | `module/v1/ff/SVR4H73275/state` | 16:47:58 ✓ | **nie** |
| **NodeRed** | `module/v1/ff/NodeRed/SVR4H73275/state` | 16:47:58 (WAITIING) | 16:48:11 ✓ |

Die CCU abonniert `module/v1/ff/+/state` – das `+`-Wildcard entspricht **nur einem** Segment. Es matcht:
- `module/v1/ff/SVR4H73275/state` ✓
- `module/v1/ff/NodeRed/SVR4H73275/state` ✗ (6 Segmente, `+` deckt nur `NodeRed` ab)

**Folge:** Die CCU erhält DROP FINISHED nur von NodeRed, hört aber nur auf dem TXT-Topic. Von SVR4H73275 kommt zuletzt FINISHED für **setStatusLED** – das wird in `production/index.ts` in `ignoredCommands` verworfen und löst kein `handleActionUpdate` aus.

### Verhalten bei WHITE Storage (zum Vergleich)

Für die WHITE Storage Order (16:46) war die Sequenz:
- 16:46:07 – DROP an DPS
- 16:46:21 – **SVR4H73275/state** meldet `actionState: FINISHED DROP` ✓

Dort kam DROP FINISHED auf dem TXT-Topic an, die CCU hat Step 2 abgeschlossen und Step 3 (DPS→HBW) ausgelöst.

### Unterschied ROT vs. WEISS

- **WEISS:** TXT sendet DROP FINISHED auf `module/v1/ff/SVR4H73275/state` → CCU verarbeitet korrekt.
- **ROT:** TXT sendet kein DROP FINISHED auf SVR4H73275; nur NodeRed sendet DROP FINISHED auf dem NodeRed-Topic → CCU bekommt es nicht.

Mögliche Erklärungen:
1. Unterschiedliches Timing/Sequenzierung zwischen TXT- und NodeRed-Meldungen.
2. Nach DROP geht das TXT direkt zu setStatusLED über und meldet DROP nie als FINISHED.
3. Unterschiedliche Verarbeitung je nach Werkstücktyp (z.B. durch Sensoren/Qualitätsprüfung).

---

## Zustand „Busy“

Aus `handleModuleAvailability` in `production/index.ts`:
- DPS mit Load **und** `actionState` nicht FINISHED → `AvailableState.BUSY`.
- Step 2 (DROP) bleibt IN_PROGRESS, weil die CCU kein DROP FINISHED sieht.
- DPS gilt damit weiter als BUSY, jp93 bleibt für die Order blockiert, Step 3 (DPS→HBW) wird nie freigegeben.

---

## Zusammenfassung

| Aspekt | Befund |
|--------|--------|
| **Symptom** | AGV-2 mit ROT an DPS, keine weiteren Orders |
| **Ursache** | CCU erhält nie DROP FINISHED für Step 2 |
| **Grund** | DROP FINISHED kommt nur von NodeRed auf `NodeRed/SVR4H73275/state`, CCU hört nur `SVR4H73275/state` |
| **Folge** | Step 2 bleibt IN_PROGRESS, Step 3 (DPS→HBW) wird nie erzeugt, jp93 erhält keine nächste Order |

---

## Warum die ursprünglichen Ansätze nicht greifen

Ein Stillstand wegen fehlender DROP-FINISHED-State-Messages ist **vor Mod 3 und vor 2-AGV-Betrieb nie aufgetreten**. Folgerungen:

| Ansatz | Warum nicht |
|--------|-------------|
| **CCU soll NodeRed-Topic abonnieren** | CCU hat sich nicht geändert; der Fehler war vorher nicht da → falsche Richtung. |
| **NodeRed weiterleiten** | NodeRed wurde nicht geändert und hat zuvor funktioniert. |
| **TXT/Blockly anpassen** | Aufwendig und fehleranfällig; erklärt nicht, *welche Änderung* das Verhalten ausgelöst hat. |

**Offene Frage:** Welche Änderung führt zu dem Fehlverhalten? Die CCU-Subscription und NodeRed-Topics waren vorher wie jetzt.

---

## Mögliche Ursachen (reduziert)

### 1. TXT/Blockly – szenarioabhängiges Verhalten

**Analyse aller Sessions vom 12.03. (nach Mod-3-Rückbau):**

| Session | DROP RUNNING | DROP FINISHED | setStatusLED statt DROP |
|---------|--------------|---------------|-------------------------|
| agv-1-mixed_103130 | 3 | 1 | 0 ✓ |
| agv-1-mixed_133313 | 3 | 1 | 0 ✓ |
| agv-2-mixed_134156 | 1 | 1 | 0 ✓ |
| agv-2-mixed_164447 | 4 | 2 | 0 ✓ |
| two-agvs-mixed_101514 | 1 | 1 | 0 ✓ |
| **two-agvs-mixed_165108** | **2** | **1** | **1** ✗ |
| two-agvs-orders_094643 | 2 | 1 | 0 ✓ |
| test_120052 | 45 | 3 | 0 ✓ |

**Einzige betroffene Session:** `two-agvs-mixed_20260312_165108`

Das Problem ist **nicht farbabhängig** – in der gleichen Session schlägt der **2. DROP** fehl (1. DROP = WEISS ✓, 2. DROP = ROT ✗). Andere Sessions mit mehreren DROPs (agv-2-mixed_164447, two-agvs-orders) zeigen das Verhalten nicht.

**Mögliches Muster:** 2. Storage-Order in kurzer Folge bei two-agvs-mixed – Race/Timing oder spezieller Ablauf in diesem Szenario.

### 1b. Hypothese: AGV bleibt zu lange am DPS → kein DROP FINISHED

**User-Hypothese:** Wenn AGV-2 zu lange am DROP-Punkt bleibt (weil keine freie Fahrt / Pfad blockiert durch AGV-1), kommt von der DPS kein DROP FINISHED. Das Problem tritt nur bei zwei AGVs auf – mit einem AGV kann DROP FINISHED immer sofort gesendet werden.

**Kausalität ( plausibel):**
- **Ein AGV:** AGV fährt immer frei ab, DPS meldet DROP FINISHED direkt nach physischem Abschluss
- **Zwei AGVs:** AGV-2 blockiert (z.B. AGV-1 auf Strecke DPS→HBW), AGV-2 bleibt am DPS
- DPS wartet möglicherweise auf „Abgabezone geräumt“ (Sensor/Bedingung), bevor DROP FINISHED gesendet wird
- Oder: Timeout/Race im TXT – bei längerem Warten wechselt die State-Machine zu setStatusLED statt DROP FINISHED

**Zu prüfen (TXT/SPS):**
- Sendet die DPS DROP FINISHED erst, wenn ein Sensor „Output frei“ meldet?
- Gibt es ein Timeout, nach dem stattdessen setStatusLED gesendet wird?
- Wie reagiert die DPS, wenn das AGV gedockt bleibt und nicht abfährt?

### 2. Deploy/Image-Rollback?

**Hypothese:** Ein „docker build all and deploy all“ könnte ältere Images (z.B. NodeRed) wieder aktiviert haben.

**Aktueller Stand:**
- CCU-Deploy baut nur `central`; NodeRed wird nicht mitgebaut.
- NodeRed kommt aus `ghcr.io/ommsolutions/ff-nodered-armv7:release-24v-v130`.
- DPS-State kommt **direkt vom TXT** auf `SVR4H73275/state`; NodeRed ist nur parallele Anreicherung.

**Fazit:** Ein NodeRed-Rollback würde die fehlende DROP-FINISHED-Meldung auf `SVR4H73275/state` **nicht** erklären – diese wird vom TXT gesendet, nicht von NodeRed.

### 3. Wer/Was kann Topics unterdrücken?

| Komponente | Kann senden unterdrücken? | Kann empfangen unterdrücken? |
|------------|---------------------------|------------------------------|
| **Mosquitto** | Nein (nur relay) | QoS/Retain, Überlast |
| **CCU** | – | Falsches Subscription-Topic |
| **TXT-DPS** | Ja – State-Machine sendet kein DROP FINISHED | – |
| **NodeRed** | Ja – publish-Logik | – |
| **Watchtower** | – | Kann Container neu starten (Netzwerk-Unterbrechung) |

### 4. Nutzen einer Live-MQTT-Prüfung

**Was eine Live-Prüfung bringt:**
- Reproduzierbarkeit: Tritt das Problem bei wiederholter ROT-Storage als 2. Order erneut auf?
- Reihenfolge: Kommt setStatusLED vor oder nach einem evtl. DROP FINISHED?
- Kontext: Gibt es Meldungen auf `SVR4H73275/state`, die im Session-Log fehlen (z.B. durch Sampling)?

**Was sie nicht klärt:**
- Die Ursache einer Änderung im Verhalten (wenn Blockly/TXT unverändert ist).
- Ob ein älteres Image aktiv ist (dafür müssten Images/Versions-Tags geprüft werden).

---

## Empfohlene Debug-Schritte

1. **Image-Versionen auf dem Pi prüfen**
   ```bash
   ssh ff22@192.168.0.100 "docker images --format '{{.Repository}}:{{.Tag}}' | grep -E 'nodered|central|mosquitto'"
   ```
   Stimmen die Tags mit den erwarteten Versionen überein?

2. **Live-MQTT bei reproduziertem Szenario**
   - two-agvs-mixed wiederholen: WEISS Storage, dann ROT Storage.
   - `mosquitto_sub -h 192.168.0.100 -t 'module/v1/ff/SVR4H73275/state' -v`
   - Beobachten: Kommt für ROT jemals DROP FINISHED, oder nur setStatusLED FINISHED?

3. **TXT/Blockly-DPS prüfen**
   - Wird DROP FINISHED vor setStatusLED gesendet?
   - Gibt es eine Bedingung (2. Order, ROT), unter der DROP FINISHED übersprungen wird?
   - **Hypothese AGV-Wartezeit:** Bleibt das AGV zu lange am DPS (keine freie Fahrt)? Reagiert die DPS darauf (Sensor, Timeout)?

---

## Zusammenhang: Zwei AGVs + Mixed

**Wichtig:** Mod-3-Änderungen sind vollständig zurückgebaut (`OSF-MODIFICATIONS.md`). Mod 3 kann **nicht** die Ursache sein.

Mögliche Erklärungen für das Verhalten:
- **Zwei AGVs:** Erhöhtes Konfliktpotenzial – AGV-2 muss oft warten (Pfad blockiert). Die „AGV bleibt zu lange“-Bedingung wird häufiger erreicht.
- **Latentes Verhalten:** Mit einem AGV wird die Bedingung praktisch nie erfüllt. Mit zwei AGVs im Mixed-Betrieb tritt sie auf.

---

*Letzte Aktualisierung: 2026-03-12*
