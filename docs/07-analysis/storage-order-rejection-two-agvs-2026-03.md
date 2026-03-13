# Storage-Order-Ablehnung trotz scheinbar leerem Lager (two-agvs Session)

**Datum:** 2026-03-12  
**Kontext:** Session „two-agvs“ aufgenommen. Nach Änderungen (Sprint 17: serialNumber in NAVIGATION, armv7 OSF-UI) zeigt die FMF unerwartetes Verhalten.

---

## Session-Analyse (two-agvs_20260312_085306.log)

### Befund 1: Storage-Order-Requests mit `type: "UNKNOWN"`

Alle 3 Storage-Order-Requests haben **`"type":"UNKNOWN"`**:

```json
{"orderType":"STORAGE","type":"UNKNOWN","workpieceId":"04a189ca341290"}
{"orderType":"STORAGE","type":"UNKNOWN","workpieceId":"04c090ca341291"}
{"orderType":"STORAGE","type":"UNKNOWN","workpieceId":"047b8bca341291"}
```

**CCU:** `emptyBayAvailable(Workpiece)` kennt nur BLUE, RED, WHITE. Für UNKNOWN existieren keine Bays → Ablehnung.  
**Quelle:** DPS/TXT sendet den Request – Werkstück-Typ-Erkennung liefert UNKNOWN statt BLUE/RED/WHITE.

### Befund 2: HBW-State meldet `loads: []` (leer)

Beide `module/v1/ff/SVR3QA0022/state`-Messages haben **`"loads":[]`**. Keine weiteren HBW-State-Updates in der Session (nur connection-heartbeats).

**Folge:** CCU setzt Stock auf leer → osf-ui zeigt leeres Lager (korrekt nach Meldung).  
**Quelle:** HBW oder Node-RED (OPC-UA→MQTT) sendet keine State-Updates mit den tatsächlichen loads.

### Keine CCU-Änderung als Ursache

Die CCU verarbeitet korrekt: UNKNOWN hat keine Bays; leere loads → leerer Stock. Die Änderungen (serialNumber in NAVIGATION, armv7) betreffen weder Order-Validation noch Stock-Handling.

---

## Symptome

| Beobachtung | Erwartet |
|-------------|----------|
| Lager (Stock) in osf-ui **scheinbar leer** | Sollte 3× Rot, 1× Blau, 2× Weiß zeigen |
| **Keine** Storage-Order wird akzeptiert | Sollte akzeptieren, wenn &lt; 3 Stück der Farbe im HBW |
| Physischer Zustand HBW (optisch): 3× Rot, 1× Blau, 2× Weiß | – |

**Vor der Änderung:** Storage-Order-Ablehnung nur bei 3 Stück derselben Farbe (Lager voll für diese Farbe).

---

## Datenfluss (Kurz)

1. **CCU** erhält `module/v1/ff/+/state` von HBW (TXT) mit `loads`
2. `handleStock()` → `StockManagementService.setStock(hbwSerial, loads)`
3. `updateActiveWarehouses()` → `setWarehouses([HBW-Serials])` aus `getAllPaired(ModuleType.HBW)`
4. `updateBaysFromModule()` → `setBays()` aus HBW-Factsheet `loadSpecification.loadSets`
5. **Storage-Order:** `emptyBayAvailable(type)` prüft `baysForType - stockOfType.length > bayReservations`
6. **Stock-Anzeige:** CCU publiziert `ccu/state/stock` aus `getStock()` + `getWarehouses()`

---

## Mögliche Ursachen

### 1. HBW nicht gepaired / Warehouses leer
- `getAllPaired(ModuleType.HBW)` liefert []
- Folge: `setWarehouses([])` → `emptyBayAvailable` findet keinen Warehouse → Ablehnung
- Folge: `mapHbwToCloudStock(stock, [])` fügt keine Slots hinzu → UI evtl. leer oder Fallback

### 2. warehouseStorageBays nicht gesetzt (kein Bays)
- `updateBaysFromModule` braucht Factsheet mit `loadSpecification.loadSets`
- Ohne: `baysForType = 0` → `baysFree ≤ 0` → keine freie Bay

### 3. handleStock nicht aufgerufen / loads leer
- Kein `module/v1/ff/<HBW_SERIAL>/state` mit loads
- Oder Factsheet sagt „kein HBW“ → handleStock returned früh (pendingHbwState)
- Replay: MQTT-Reihenfolge oder fehlende Messages

### 4. Replay vs. Live
- **Replay:** CCU bekommt Replay-Messages; wenn HBW-State beim Recording leer war → stock leer
- **Live:** CCU bekommt Live-Messages; wenn HBW nicht verbunden oder Topic falsch → stock leer

---

## Debug-Schritte

### 1. CCU-Logs prüfen
```bash
ssh 192.168.0.100 "docker logs central-control-prod --tail 100 2>&1 | grep -E 'CLOUD_STOCK|storage|HBW|empty'"
```
- Erwartung: `CLOUD_STOCK: Update stock for HBW SVR3QA0022, loads=6` (oder aktueller Wert)
- Fehlt das oder loads=0 → handleStock bekommt keine/leere loads

### 2. ccu/state/stock inspizieren
```bash
mosquitto_sub -h 192.168.0.100 -t 'ccu/state/stock' -v -C 1
```
- Prüfen: Enthält `stockItems` mit `workpiece`-Einträgen oder nur `workpiece: undefined`?
- Prüfen: Gibt es `hbw`-Einträge (SVR3QA0022)?

### 3. HBW-Modul-State prüfen
```bash
mosquitto_sub -h 192.168.0.100 -t 'module/v1/ff/+/state' -v -C 5
```
- Prüfen: Kommen Messages mit `serialNumber: "SVR3QA0022"` und `loads: [...]`?

### 4. Layout-/Pairing-Status
- CCU-Layout: Enthält es den HBW (SVR3QA0022)?
- Nach Layout-Load wird `updateActiveWarehouses` aufgerufen

### 5. Replay-Broker vs. Live
- Läuft die Session im **Replay**? Dann nutzt die CCU ggf. den Replay-Broker.
- Welcher Broker ist für die CCU konfiguriert (`MQTT_URL`)?

---

## Nächste Schritte

1. **Logs + MQTT** wie oben auswerten
2. **Live vs. Replay** klären – gleiches Verhalten in beiden Modi?
3. **Layout/Factsheet** prüfen – ist HBW mit loadSets korrekt gepaired?
4. Ggf. **CCU-Debug-Log** für `emptyBayAvailable`, `setWarehouses`, `setBays` ergänzen

---

## Topic-Übersicht (two-agvs Session)

| Topic | Anzahl | Anmerkung |
|-------|--------|-----------|
| module/v1/ff/SVR3QA0022/state | 2 | loads=[] (leer), retain |
| module/v1/ff/SVR3QA0022/factsheet | 2 | loadSets OK (WHITE/RED/BLUE je 3) |
| ccu/state/stock | 2 | 9 leere Slots (A1–C3) |
| ccu/order/request | 3 | type=UNKNOWN |
| fts/v1/ff/5iO4/state | 46 | AGV-1 |
| fts/v1/ff/jp93/state | 25 | AGV-2 |
| module/v1/ff/SVR4H73275/state | 17 | DPS (NodeRed 26) |

---

## Empfohlene Maßnahmen

### 1. Node-RED prüfen (Datenquelle für DPS + HBW)

DPS und HBW gehen beide über **Node-RED** (OPC-UA → MQTT). Beide Fehler sprechen für ein Problem in den Node-RED-Flows.

**Wichtig:** In `docker-compose-prod.yml` ist der Node-RED-Volume auskommentiert (`#node-red-data-prod`). Ohne Volume: **Keine Persistenz** – bei jedem Container-Neustart werden die Flows aus dem Image geladen. Custom Flows oder frühere Anpassungen gehen verloren.

- **DPS:** `type` aus Farbsensor → wird als UNKNOWN statt BLUE/RED/WHITE weitergegeben
- **HBW:** `loads` aus Rack-Positionen → werden nicht oder leer publiziert

**Prüfen:**
- Node-RED-UI: http://192.168.0.100:1880
- DPS-Flow: Woher kommt der `type`? (OPC-UA Node für Farbsensor)
- HBW-Flow: Wer erzeugt `module/v1/ff/SVR3QA0022/state` mit `loads`?
- Sind die Flows nach einem `docker compose up -d` noch vorhanden? (Volume für Node-RED in docker-compose-prod?)

### 2. OPC-UA-Verbindung prüfen

- OPC-UA-Verbindung zum DPS (z.B. 192.168.0.90:4840)?
- OPC-UA-Verbindung zum HBW (z.B. 192.168.0.80:4840)?

### 3. Fallback in CCU (Optional)

Falls die Fehlerquelle nicht behoben werden kann: CCU könnte bei `type === 'UNKNOWN'` den Typ aus `workpieceId` ableiten (z.B. 04a189ca341290 → BLUE, falls das Format bekannt ist). Das wäre ein Workaround, kein Ersatz für die Korrektur in Node-RED.

---

---

## Session-Analyse 2: two-agvs-mixed_20260312_101514.log

**Szenario:** Zwei AGVs im Einsatz, DPS-Station wird inaktiv, zweites Werkstück (RED) Storage-Order wird nicht ausgeführt, Werkstück liegt in Annahmestation.

### Ablauf (Zeitachse)

| Zeit (UTC+1) | Ereignis |
|--------------|----------|
| 10:09:05 | DPS: WHITE erkannt (loads), RGB_NFC FINISHED |
| 10:10:43 | STORAGE WHITE: AGV dockt DPS, DROP läuft |
| 10:10:59 | DPS DROP fertig, AGV fährt zu HBW |
| 10:11:28 | **STORAGE WHITE abgeschlossen** (HBW PICK fertig) |
| 10:11:28 | ccu/order/active = [] |
| **10:12:04** | **DPS State: loads=[loadType:UNKNOWN], errors=[{}], actionState=null** |
| 10:12:59 | BLUE PRODUCTION von OSF-UI gestartet |
| 10:15:14 | Session-Ende (BLUE PRODUCTION noch in AIQS-Phase) |

### Befund 1: UNKNOWN ist Normalzustand in der Annahmestation (Vergleich storage-white)

**storage-white_20260303_075954.log:** Der typische Ablauf:

| Zeit | DPS State | Aktion |
|------|-----------|--------|
| 07:57:50 | loads: UNKNOWN, errors: **[]** | Werkstück in Annahmestation erkannt; Farbsensor noch nicht aktiv |
| 07:57:50 | INPUT_RGB WAITING → RUNNING | Farbsensor-Lesung startet |
| 07:58:05 | INPUT_RGB FINISHED | |
| 07:58:06 | loads: **WHITE** | Typ nach Farbsensor-Lesung gesetzt |
| 07:58:06 | RGB_NFC (NFC-Schreiben) | |
| 07:58:36 | DROP läuft (Storage-Order) | |

**Folgerung:** `loadType: UNKNOWN` ist erwartbar, wenn das Werkstück noch in der Annahmestation liegt. Der Farbsensor kommt erst bei **INPUT_RGB** ins Spiel.

### Befund 2: two-agvs-mixed – INPUT_RGB startet nicht

Nach 10:12:04 **kein weiterer DPS-State** in der Session. Der letzte DPS-State (09:12:04 UTC):

```json
{
  "loads": [{"loadType": "UNKNOWN"}],
  "actionState": null,
  "errors": [{}],
  "orderId": "0"
}
```

- **loadType: UNKNOWN** – normal in der Annahmestation (wie storage-white).
- **errors: [{}]** – DPS meldet Fehler; in storage-white war `errors: []`.
- **INPUT_RGB fehlt** – in storage-white startet direkt nach UNKNOWN INPUT_RGB; hier bleibt der Ablauf stehen.
- **Folge:** Kein Übergang zu WHITE/RED/BLUE, kein Storage-Request, DPS erscheint „inaktiv“.

### Befund 3: Kein Storage-Order-Request für RED

In der gesamten Session **kein** `ccu/order/request` mit `orderType: STORAGE` für das zweite Werkstück.

**Erwartung:** DPS erkennt Werkstück → Node-RED sendet `ccu/order/request` (STORAGE, type: RED).

**Mögliche Ursachen:**
1. DPS bleibt wegen UNKNOWN+errors im Fehlerzustand und löst keinen Storage-Request aus
2. Node-RED sendet nur bei gültigem `type` (BLUE/RED/WHITE), nicht bei UNKNOWN
3. DPS/TXT blockiert die Request-Erzeugung bei Fehlern

### Befund 4: Zwei parallele Abläufe

- **AGV 1 (jp93):** STORAGE WHITE durchgeführt
- **AGV 2 (5iO4):** HBW PICK für BLUE PRODUCTION
- **DPS:** Nach Abholung von WHITE wird RED aufgelegt; DPS meldet UNKNOWN+errors, kein Storage-Request

### Zusammenhang mit two-agvs-Session

**Unterschied:** In two-agvs wurden Storage-Requests mit UNKNOWN gesendet (CCU lehnt ab). In two-agvs-mixed wird **kein** Storage-Request gesendet, weil INPUT_RGB nicht startet und der Typ nie ermittelt wird.

**Gemeinsam:** `errors: [{}]` blockiert vermutlich den Ablauf (INPUT_RGB startet nicht). Ohne Farbsensor-Lesung bleibt UNKNOWN, ohne Type kein Storage-Request.

---

## Session-Analyse 3: agv-1-mixed_20260312_103130.log (nach RPi-Neustart)

**Szenario:** Fabrik nach vollständigem RPi-Neustart. Ein AGV. DPS geht sofort in Fehlerzustand, Werkstück wird nicht aus Annahmestation geholt. DPS-LED gelb ("Busy"). Fabrik steht still.

### Ablauf (Zeitachse)

| Zeit (UTC+1) | Ereignis |
|--------------|----------|
| 10:28:32 | Session-Start: transports: **[]** (kein AGV gepaired) |
| 10:28:35 | DPS Reset (instantAction) |
| 10:28:40 | Module verbinden sich (DRILL, MILL, AIQS, HBW, DPS) |
| 10:28:41 | **Node-RED: OFFLINE** (kurzer Absturz/Reconnect) |
| 10:28:44 | Node-RED: ONLINE |
| 10:29:02 | CCU setzt DPS-LED auf **grün** (setStatusLED) |
| **10:29:40** | Werkstück aufgelegt: loads=UNKNOWN, errors=**[]**, INPUT_RGB **WAITING** |
| 10:29:18 | AGV 5iO4 erscheint (transports), BLOCKED |
| 10:29:24 | AGV findInitialDockPosition → DPS |
| Session-Ende | INPUT_RGB bleibt bei WAITING, nie RUNNING |

### Befund 1: INPUT_RGB bleibt bei WAITING (Vergleich storage-white)

| storage-white (funktioniert) | agv-1-mixed (Problem) |
|------------------------------|------------------------|
| UNKNOWN → INPUT_RGB WAITING → **RUNNING** → FINISHED | UNKNOWN → INPUT_RGB WAITING → **Stopp** |
| loads wechselt zu WHITE | bleibt bei UNKNOWN |

**Folge:** Farbsensor-Lesung wird nicht ausgeführt. Kein Type → kein Storage-Request → AGV kommt zwar zur DPS, aber DPS holt Werkstück nicht aus Annahmestation.

### Befund 2: Keine errors im DPS-State

`errors: []` – anders als two-agvs-mixed. Das Problem ist nicht `errors: [{}]`, sondern dass **INPUT_RGB nie ausgeführt** wird (physische DPS/TXT führt den Befehl nicht aus).

### Befund 3: Node-RED kurz OFFLINE nach Start

10:28:41 – `NodeRed/status: OFFLINE`, 10:28:44 wieder ONLINE. Kurzer Reconnect. Ob das den Ablauf beeinflusst, ist unklar (INPUT_RGB kommt erst 10:29:40).

### Befund 4: RPi-Neustart / Timing

Nach Neustart: OPC-UA Node-RED ↔ DPS TXT (192.168.0.90) braucht Zeit. Wenn das Werkstück **zu früh** aufgelegt wird, könnte die DPS noch nicht bereit sein. Oder die DPS/TXT-Firmware hat einen anderen Fehler nach Kaltstart.

### Hypothesen (ohne Code-Beweis)

1. **OPC-UA nach Neustart:** Verbindung Node-RED → DPS TXT noch nicht stabil; INPUT_RGB-Befehl kommt nicht an oder wird nicht ausgeführt.
2. **DPS TXT Start-up:** DPS benötigt nach Reset/Neustart längere Bereitschaft; zu frühes Auflegen blockiert.
3. **Gelbe LED:** DPS wartet auf Ausführung (z.B. auf OPC-UA-Befehl) → zeigt "Busy".

### Empfohlene Prüfungen

1. **Warten nach Neustart:** Z.B. 2–3 Min ab DPS-Connection, dann erst Werkstück auflegen. Testen, ob INPUT_RGB dann durchläuft.
2. **Node-RED-Logs:** Nach INPUT_RGB WAITING – wird der Befehl an OPC-UA/DPS gesendet? Kommt Rückmeldung?
3. **DPS TXT direkt:** OPC-UA-Client (z.B. UaExpert) an 192.168.0.90 – ist die DPS nach Neustart erreichbar, antwortet sie auf INPUT_RGB?

---

## DPS-Inaktivität: Warum funktioniert DPS selbst in einfacher Session nicht?

**Kontext:** Keine Node-RED-Anpassungen; Flows kommen von Fischertechnik/OMM. Mit v130 wurden DPS/HBW-Probleme behoben. Nach einigen erfolgreichen Orders (Storage + Production) ging DPS in einen inaktiven Zustand. Jetzt bleibt INPUT_RGB bei WAITING – auch bei 1 AGV, keine parallelen Orders.

### Ablauf: Wer sendet INPUT_RGB?

1. **S7-1200 (192.168.0.90):** OPC-UA-Variable `stat__input` = true, wenn Werkstück auf Annahmeband liegt.
2. **Node-RED (OPC-UA-Client):** Liest `stat__input`, Flow `move-workpiece-to-rgb` erzeugt INPUT_RGB-Order.
3. **Node-RED:** Veröffentlicht auf `module/v1/ff/NodeRed/{DEVICEID}/order`.
4. **DPS TXT (192.168.0.102):** Abonniert dieses Topic, empfängt INPUT_RGB.
5. **DPS TXT:** Setzt `actionState` auf WAITING, publiziert State.
6. **DPS TXT/S7:** Sollte physisch ausführen (Werkstück zum Farbsensor) → RUNNING → FINISHED.

**Kernbefund:** INPUT_RGB WAITING erscheint in der Session → Die MQTT-Kette (Node-RED → TXT) funktioniert. Der TXT hat den Befehl erhalten und bestätigt mit WAITING. Der Fehler liegt danach: Die **physische Ausführung** startet nicht.

### Warum bleibt es bei WAITING?

| Hypothese | Wahrscheinlichkeit | Begründung |
|-----------|-------------------|------------|
| **Retained Messages im Broker** | **Hoch** | Mosquitto hat `persistence true`. State/Connection/Order-Topics werden teils mit **retain** publiziert (Fischertechnik vda5050, connection, state). Alte Fehler-/Zustands-Messages überleben jeden Neustart. Beim Reconnect erhält der DPS TXT sofort die alte retained Message – z.B. einen alten INPUT_RGB-Order oder einen State mit `errors: [{}]`. Der TXT könnte dadurch in einen falschen Zustand geraten und neue Befehle blockieren. |
| **DPS-Hardware in fehlerhaftem Zustand** | Mittel | Wurde durch Voll-Stromzyklus (5 min) bereits durchgeführt – normaler Morgen-Start, funktioniert seit >100 Tagen. Somit weniger plausibel. |
| **TXT↔S7-Kommunikation** | Mittel | TXT braucht S7 für Lichtschranken, Farbsensor etc. Wenn die interne Kommunikation nach dem Vorfall nicht mehr stimmt, bleibt TXT bei WAITING. |
| **Node-RED kurz OFFLINE** | Niedrig | In agv-1-mixed: 10:28:41 OFFLINE, 10:28:44 ONLINE. INPUT_RGB kam erst 10:29:40. Unwahrscheinlich. |
| **Timing (zu früh nach Neustart)** | Möglich | WAITING wird erreicht → Befehl ist angekommen. |

### Retained Messages: Prüfung und Bereinigung

**Szenario:** Beim „DPS ging inaktiv“ wurden State- oder Order-Messages mit `retain: true` veröffentlicht. Diese liegen in `mosquitto.db` und werden bei jedem Broker-Start wieder geladen. Jeder Subscriber (DPS TXT, Node-RED) erhält sie sofort beim Reconnect.

**Retained Messages anzeigen (Broker läuft):**
```bash
# Alle retained Topics auflisten (mosquitto_sub mit -v und Wildcard, bei Connect erhält man retained)
mosquitto_sub -h localhost -p 1883 -t '#' -v -C 1 --retained-only 2>/dev/null || true

# Oder: dynamisch alle Topics mit Retain abonnieren
mosquitto_sub -h <RPI_IP> -p 1883 -t 'module/v1/ff/#' -v
# Beim ersten Connect erscheinen retained Messages sofort
```

**Retained Messages löschen (pro Topic):** Leere Payload mit retain publizieren:
```bash
# DPS Order-Topic (SVR4H73275 = DPS Serial)
mosquitto_pub -h <RPI_IP> -p 1883 -t 'module/v1/ff/NodeRed/SVR4H73275/order' -r -n

# DPS State-Topic
mosquitto_pub -h <RPI_IP> -p 1883 -t 'module/v1/ff/NodeRed/SVR4H73275/state' -r -n
mosquitto_pub -h <RPI_IP> -p 1883 -t 'module/v1/ff/SVR4H73275/state' -r -n

# Optional: komplette Persistenz löschen (Broker stoppen, mosquitto.db entfernen, Broker starten)
# Achtung: Löscht alle retained Messages und Subscription-Infos
```

**Hinweis:** Für `mosquitto_pub` ggf. User/Passwort angeben (`-u`, `-P`), wenn der Broker Auth nutzt.

### Empfohlene Prüfungen (Priorität)

1. **Retained Messages löschen:** DPS-relevante Topics (`order`, `state`) per `mosquitto_pub -r -n` leeren. Oder `mosquitto.db` löschen und Broker neu starten (komplett blank).
2. **Test:** Nach Bereinigung Fabrik normal starten, Werkstück auflegen – läuft INPUT_RGB durch?
3. **Node-RED-Logs:** Bei INPUT_RGB WAITING – wird der Befehl gesendet? (MQTT-Subscription auf `module/v1/ff/NodeRed/+/order`)
4. **DPS TXT direkt:** OPC-UA (UaExpert) an 192.168.0.90 – erreichbar, reagiert auf INPUT_RGB?

### Abgrenzung

- Node-RED erzeugt INPUT_RGB korrekt. Der TXT empfängt die Nachricht (WAITING erscheint).
- Die Blockade kann **entweder** auf DPS-Hardware **oder** auf alter retained Message liegen, die den TXT in einen falschen Zustand bringt. Retained-Messages-Hypothese zuerst prüfen (einfach, reversibel).

---

## Referenzen

- [cloud-stock.ts](../../integrations/APS-CCU/central-control/src/modules/production/cloud-stock.ts)
- [stock-management-service.ts](../../integrations/APS-CCU/central-control/src/modules/order/stock/stock-management-service.ts)
- [order/index.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.ts) – `validateStorageOrderRequestAndReserveBay`
- [second-agv-2026-03.md](second-agv-2026-03.md)
