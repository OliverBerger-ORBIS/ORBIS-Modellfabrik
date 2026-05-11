# APS-CCU – Übergabe der ORBIS-Änderungen an Fischertechnik

Stand: 2026-05-11

Diese Notiz beschreibt zwei bereits in der ORBIS-Version umgesetzte Änderungen an der APS-CCU, inklusive der relevanten Code-Stellen und einer Einschätzung, was aus unserer Sicht für eine mögliche Übernahme ins Original-Repo geprüft werden sollte.

Hinweis zu den Pfaden: Die unten genannten Dateipfade beziehen sich auf das Fischertechnik-Upstream-Repo `Agile-Production-Simulation-24V-Dev` (Branch `release`). In unserem Workspace liegt davon eine lokale Spiegelung unter `integrations/APS-CCU/`. Die Links zeigen daher auf unseren lokalen Spiegel, die angezeigten Pfade entsprechen aber der Upstream-Struktur.

---

## 1. Erweiterung von `ccu/order/request` um `requestId`

### Ziel

Externe Requestor-Systeme wie APS-Frontend, DSP, SAP oder ERP sollen eine eigene Korrelations-ID mitsenden können. Die CCU erzeugt weiterhin ihre eigene `orderId`, gibt in der Antwort aber sowohl die generierte `orderId` als auch die mitgesendete `requestId` zurück. Dadurch kann der Empfänger direkt die Zuordnung `orderId -> requestId` herstellen.

### Umsetzung in unserer Version

- `ccu/order/request` akzeptiert optional `requestId`
- aus Kompatibilitätsgründen wird zusätzlich auch `request_id` akzeptiert
- `ccu/order/response` enthält bei vorhandenem Wert sowohl die generierte `orderId` als auch die übergebene `requestId`
- Gateway-Orders reichen `requestId` ebenfalls bis `ccu/order/request` durch

### Relevante Code-Stellen

- Typdefinitionen in [common/protocol/ccu.ts](../../integrations/APS-CCU/common/protocol/ccu.ts#L114-L132)
  - `OrderRequest.requestId?: string`
  - `OrderResponse.requestId?: string`
- Request-Normalisierung und Response-Echo in [central-control/src/modules/order/index.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.ts#L74-L98)
  - `sendResponse(...)` ergänzt `requestId` in der Response
- Unterstützung von `request_id` und Normalisierung auf `requestId` in [central-control/src/modules/order/index.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.ts#L155-L165)
- Durchreichen aus Gateway-Orders in [central-control/src/modules/gateway/order/index.ts](../../integrations/APS-CCU/central-control/src/modules/gateway/order/index.ts#L10-L24)

### Tests

- Response enthält `requestId` in [central-control/src/modules/order/index.test.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.test.ts#L146-L187)
- Snake-case `request_id` wird akzeptiert in [central-control/src/modules/order/index.test.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.test.ts#L224-L258)
- Gateway reicht `requestId` durch in [central-control/src/modules/gateway/order/index.test.ts](../../integrations/APS-CCU/central-control/src/modules/gateway/order/index.test.ts#L72-L82)

### Wichtiger Hinweis zum Ist-Verhalten

In unserer aktuellen Implementierung wird das angereicherte `OrderResponse`-Objekt in die Order-Queue gecacht und diese Queue direkt als `ccu/order/active` publiziert. Dadurch läuft `requestId` derzeit faktisch auch in `ccu/order/active` und später in `ccu/order/completed` mit, obwohl die eigentliche fachliche Kernanforderung nur das Echo in `ccu/order/response` war.

Relevante Stellen:

- Queue/Active-Publish in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L88-L105)
- Übergang nach `completedOrders` in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L888-L905)

### Vorschlag an Fischertechnik

Bitte prüfen, ob diese Erweiterung in ähnlicher Form übernommen werden kann:

- optionales Feld `requestId` in `ccu/order/request`
- zusätzlich Kompatibilität für `request_id`
- Echo von `requestId` in `ccu/order/response`
- keine Änderung des Standardverhaltens, wenn kein `requestId` gesetzt ist

Diese Änderung ist klein, rückwärtskompatibel und aus unserer Sicht technisch unkritisch.

---

## 2. Quality-Fail an AIQS ohne automatischen Ersatzauftrag

### Fachliche Idee

Wenn bei einer `PRODUCTION`-Order an der AIQS ein `CHECK_QUALITY = FAILED` auftritt, soll die CCU nicht zwingend automatisch einen neuen Produktionsauftrag erzeugen. Stattdessen soll ein übergeordneter Business-Prozess (z. B. SAP, ERP, MES, DSP) entscheiden, ob ein Ersatzauftrag ausgelöst, nachbearbeitet oder verworfen wird.

Wichtig aus unserer Sicht:

- die übrigen Orders in der Fabrik sollen normal weiterlaufen
- Module und FTS sollen nach dem Quality-Fail nicht unnötig blockiert bleiben
- die Entscheidung über den Folgeprozess soll aus der CCU herausgelöst werden

### Umsetzung in unserer Version

Unsere aktuelle Implementierung ist **ohne Konfigurationsschalter** umgesetzt. Sie erzwingt also immer die Variante „kein automatischer Ersatzauftrag“.

Der Quality-Fail-Pfad macht aktuell Folgendes:

1. AIQS wird für die betroffene Order freigegeben
2. der aktuelle Step geht auf `ERROR`
3. verbleibende Steps der Order werden abgebrochen
4. die Order selbst geht auf `ERROR`
5. die Order wird aus den aktiven Listen entfernt und in `completedOrders` verschoben
6. anschließend wird versucht, das am AIQS stehende FTS mit `sendClearModuleNodeNavigationRequest(...)` wegzufahren
7. danach werden blockierte FTS-Schritte erneut angestoßen (`retriggerFTSSteps()`)

### Relevante Code-Stellen

- Quality-Fail-Handling in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L614-L631)
- Active-/Completed-Publish in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L88-L105)
- Verschieben nach `completedOrders` in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L888-L905)
- Retrigger blockierter FTS-Schritte in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L842-L858)
- Normales Triggern von Navigation und Umgang mit blockierten Modulen in [central-control/src/modules/order/management/order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L300-L399)
- Clearing-Navigation des FTS in [central-control/src/modules/fts/navigation/navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts#L338-L390)

### Tests

- Kein automatischer Ersatzauftrag bei Quality-Fail in [central-control/src/modules/order/management/order-management.test.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.test.ts#L653-L712)

### Wichtiger technischer Hinweis

Das von uns verwendete `sendClearModuleNodeNavigationRequest(...)` sendet keinen expliziten Business-Befehl wie „fahre zum HBW“, sondern erzeugt eine **ungeführte Clearing-Navigation** zu dem **ersten freien verbundenen Modul**, das nicht der Charger ist.

Das Ziel wird hier gewählt:

- [central-control/src/modules/fts/navigation/navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts#L347-L356)

Dadurch ist das Verhalten **nicht deterministisch auf HBW**. Je nach Layout- und Belegungssituation kann das FTS z. B. auch zu DPS oder einem anderen freien Modul fahren.

### Unsere aktuelle Einschätzung zu möglichen Problemen

Wir sind nicht sicher, ob unsere Implementierung für alle Parallel-Order-Szenarien korrekt ist. In vielen Fällen funktioniert sie, in einigen Situationen zeigt die APS aber nach einem Quality-Fail nicht das gewünschte Verhalten.

Unsere Vermutung ist, dass insbesondere diese Punkte kritisch sein können:

1. **Kein Schalter vorhanden**
   - das Verhalten „kein Ersatzauftrag“ ist hart codiert
   - das ursprüngliche Fischertechnik-Szenario kann nicht mehr konfiguriert aktiviert werden

2. **Clearing-Ziel des FTS ist nicht fachlich deterministisch**
   - `sendClearModuleNodeNavigationRequest(...)` wählt das erste freie Modul, nicht zwingend HBW
   - dadurch kann sich das Verhalten je nach Reihenfolge der Pairing-States ändern

3. **Das Clearing erfolgt als technische Navigation, nicht als explizit modellierter Business-Fall**
   - möglicherweise wäre eine dedizierte, von Fischertechnik bevorzugte Lösung besser, z. B. ein gezielterer FTS-Befehl oder ein sauber eingebetteter interner Workflow

4. **Parallelbetrieb sollte explizit geprüft werden**
   - insbesondere der Fall „eine Order FAIL an AIQS, andere Orders sollen normal weiterlaufen“ sollte vom Original-Repo-Owner technisch überprüft werden

Siehe auch unsere Analyse-Hinweise:

- [docs/07-analysis/agv-position-after-order-completion-2026-03.md](agv-position-after-order-completion-2026-03.md#L52-L76)
- [docs/07-analysis/agv-2-mixed-standstill-2026-03.md](agv-2-mixed-standstill-2026-03.md#L115-L132)

### Vorschlag an Fischertechnik

Bitte prüfen,

1. ob das Verhalten „kein automatischer Ersatzauftrag bei Quality-Fail“ grundsätzlich als optionale Erweiterung sinnvoll ist
2. ob dies **über einen Konfigurationsschalter beim Start der APS/CCU** umgesetzt werden kann
3. ob unsere aktuelle technische Umsetzung korrekt ist oder an einer anderen Stelle eingebaut werden sollte

Ein möglicher Schalter wäre zum Beispiel:

- `autoReplaceOnQualityFail = true` → Originalverhalten: automatischer Ersatzauftrag
- `autoReplaceOnQualityFail = false` → kein Ersatzauftrag; Entscheidung liegt beim übergeordneten Business-Prozess

### Erwünschtes Verhalten bei deaktiviertem Auto-Replace

Wenn der Schalter deaktiviert ist, wäre aus unserer Sicht das gewünschte Verhalten:

- betroffene Order geht auf `ERROR`
- kein automatischer Ersatzauftrag
- AIQS wird freigegeben
- andere parallele Orders laufen normal weiter
- das am AIQS stehende FTS wird fachlich sinnvoll freigeräumt oder gezielt an einen geeigneten Ort geschickt
- die Folgeentscheidung übernimmt ein übergeordnetes System

---

## Kurzfassung für eine externe Übergabe

### Änderung 1

Wir haben `ccu/order/request` um ein optionales Feld `requestId` erweitert. Die CCU erzeugt weiterhin ihre eigene `orderId`, gibt aber in `ccu/order/response` zusätzlich die vom Requestor mitgesendete `requestId` zurück. Dadurch kann der Empfänger die Zuordnung `orderId -> requestId` herstellen. Die Implementierung ist rückwärtskompatibel und akzeptiert zusätzlich `request_id`.

### Änderung 2

Wir haben den Quality-Fail-Pfad für `PRODUCTION`-Orders so angepasst, dass bei `CHECK_QUALITY = FAILED` kein automatischer Ersatzauftrag erzeugt wird. Stattdessen geht die Order auf `ERROR`, verbleibende Steps werden abgebrochen, die AIQS wird freigegeben und das FTS wird aus der AIQS-Situation heraus freigeräumt. Die fachliche Idee ist, die Folgeentscheidung einem übergeordneten Business-Prozess zu überlassen. Diese Lösung ist bei uns aktuell hart codiert und sollte aus unserer Sicht im Original-Repo eher als konfigurierbare Option geprüft werden. Zusätzlich sollte geprüft werden, ob unsere technische Umsetzung – insbesondere das Clearing des FTS bei parallelen Orders – an der richtigen Stelle und mit der richtigen Semantik umgesetzt ist.