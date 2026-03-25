# Order–AGV-Zuordnung ohne Mod-3-Rücknahme

**Datum:** 2026-03-10  
**Kontext:** Mod 3 (optionales `serialNumber` in NAVIGATION-Steps) wurde zurückgebaut. Die osf-ui soll wieder AGV-1/AGV-2 pro Order-Step anzeigen können, **ohne** die bestehende CCU-Order- und NAVIGATION-Logik zu ändern.

---

## 1. Mod-3-Rekonstruktion

### Ursprüngliche Mod-3-Funktion

- **Zweck:** AGV-1/AGV-2 Anzeige in der osf-ui pro NAVIGATION-Step
- **Wie:** Optionales Feld `serialNumber?: string` in `OrderNavigationStep` (ccu/order/active, ccu/order/completed)
- **Wo gesetzt:** In der CCU beim Publish der Order-Liste – die FTS-Zuordnung aus `chooseReadyFtsForStep()` wurde in den Step geschrieben
- **Rückbau:** Aus OSF-MODIFICATIONS.md: Entfernt, da als potenzielle Ursache für Stillstände diskutiert

### Aktuelle CCU-Struktur

| Element | Inhalt |
|---------|--------|
| `ccu/order/active` | `OrderResponse[]` – Array von Orders, retained, QoS 2 |
| `OrderResponse.productionSteps` | `OrderNavigationStep \| OrderManufactureStep` |
| `OrderNavigationStep` | `type`, `source`, `target`, `id` – **kein** `serialNumber` |
| `OrderManufactureStep` | Hat optional `serialNumber` (Modul-Seriennummer) |

Die FTS-Zuordnung passiert intern in `chooseReadyFtsForStep()` → `sendNavigationRequest()` → Publish an `fts/v1/ff/<ftsSerial>/order`, wird aber **nicht** in die Order-Steps zurückgeschrieben.

---

## 2. osf-ui-Bedarf

### Verwendung

- **OrderCardComponent** (`order-card.component.ts`): Für NAVIGATION-Steps wird `step.serialNumber` genutzt, um über `mappingService.getAgvLabel(serialNumber)` „AGV-1“ oder „AGV-2“ anzuzeigen
- Ohne `serialNumber`: Fallback auf generisches „AGV“

```typescript
// order-card.component.ts (Auszug)
if (step.type === 'NAVIGATION') {
  const agvLabel = step.serialNumber
    ? this.mappingService.getAgvLabel(step.serialNumber)
    : null;
  return agvLabel ?? $localize`:@@moduleNameAGV:AGV`;
}
```

### Benötigte Zuordnung

- `(orderId, stepId)` → `ftsSerialNumber`
- `stepId` = `productionSteps[].id` des NAVIGATION-Steps
- `ftsSerialNumber` = z.B. `5iO4`, `IeJ4` (für AGV-1, AGV-2)

---

## 3. Optionen

### Option A: Ableitung aus `fts/v1/ff/+/order`

**Idee:** Die Zuordnung steckt bereits in den FTS-Order-Messages. Bei jedem Publish an `fts/v1/ff/<serial>/order` enthält der Topic den FTS-Serial; die Payload enthält `orderId` und die NAVIGATION-Step-Id (`action.id` des DOCK-Nodes).

**Datenfluss:**

1. CCU publiziert an `fts/v1/ff/5iO4/order` mit Payload:
   - `orderId`, `orderUpdateId`, `nodes`, `edges`
   - Letzter Node (DOCK) hat `action.id` = NAVIGATION-Step-Id
2. osf-ui abonniert bereits `fts/v1/#` (ConnectionService)
3. Ein neuer Service oder Erweiterung des bestehenden Merges:
   - Abonniert `fts/v1/ff/+/order` (z. B. über MessageMonitor)
   - Extrahiert: `ftsSerial` aus Topic, `orderId` und `stepId` (aus letztem Node mit `action.id`) aus Payload
   - Baut Map: `(orderId, stepId) → ftsSerial`
   - OrderCard erhält bei der Anzeige pro Step die Zuordnung aus dieser Map (z. B. via Service/Input)

**Vorteile:**

- **Keine CCU-Änderung**
- Nutzt bestehende Topics und Struktur
- Keine neuen MQTT-Topics
- Keine Änderung an Order-/NAVIGATION-Logik

**Nachteile:**

- Abhängigkeit von der FTS-Order-Payload (nodes, letzter action.id) – stabil, aber CCU-intern
- FTS-Order ist nicht retained (qos 2) – bei Spät-Join könnte eine Zuordnung fehlen, bis die nächste Nav-Order kommt
- osf-ui muss FTS-Order-Struktur parsen (bekannt und dokumentiert)

---

### Option B: Eigenes Topic `ccu/order/fts-assignments`

**Idee:** CCU publiziert Zuordnungen separat, ohne die Order-Struktur zu ändern.

**Struktur:**

- Topic: `ccu/order/fts-assignments`
- Payload (z. B.): `{ "orderId": { "stepId": "ftsSerial" } }` (Snapshot oder inkrementell)
- Retained: ja (Snapshot der aktuellen Zuordnungen)
- QoS: 2

**CCU-Änderung (minimal):**

- Beim oder direkt nach `sendNavigationRequest()`: zusätzlicher `mqtt.publish()` mit der Zuordnung `(orderId, navStep.id) → fts.serialNumber`
- Keine Änderung an `orderQueue`, `productionSteps`, `chooseReadyFtsForStep()` oder `sendNavigationRequest()` selbst

**Vorteile:**

- Klare, dedizierte Datenquelle für Zuordnungen
- Retained ermöglicht zuverlässigen Spät-Join
- osf-ui implementiert nur Abo + Merge, keine FTS-Order-Payload-Logik

**Nachteile:**

- CCU muss ein zusätzliches Publish ergänzen
- Neues Topic, Dokumentation nötig

---

### Option C: Optionales Feld in `OrderNavigationStep` (Mod-3-Wiederherstellung)

**Idee:** Mod 3 wieder einführen, aber isoliert und ohne Einfluss auf die Kernlogik.

**Risiko:** Mod 3 wurde wegen möglicher Stillstand-Ursache entfernt. Eine erneute Einführung könnte dasselbe Risiko bergen, sofern der Rückbau tatsächlich ursächlich war.

**Bewertung:** Ohne klare Entkräftung der Stillstand-Hypothese **nicht empfohlen**.

---

### Option D: Ableitung aus `fts/v1/ff/+/state`

**Idee:** `ftsState.orderId` zeigt, welche Order ein FTS aktuell ausführt. Eine Zuordnung zu einem **konkreten Step** ist daraus aber nur indirekt ableitbar (aktueller Step über actionState.id).

**Bewertung:** `state` liefert pro FTS nur eine Order und einen Action-Status; die Zuordnung zu allen NAVIGATION-Steps einer Order ist damit schwierig und fehleranfällig. **Nicht empfohlen** als Hauptquelle.

---

## 4. Empfehlung

| Kriterium | Option A (Ableitung fts/order) | Option B (ccu/order/fts-assignments) |
|-----------|-------------------------------|--------------------------------------|
| CCU-Änderung | Keine | Minimal (1 zusätzlicher Publish) |
| Zuverlässigkeit Spät-Join | Möglich Lücke (nicht retained) | Gut (retained) |
| Komplexität osf-ui | Mittel (FTS-Order parsen) | Gering (einfache Map) |
| Neue Abhängigkeiten | FTS-Order-Schema | Eigenes Topic-Schema |

**Empfehlung:** **Option A** als erste Umsetzung, **Option B** als Alternative bei Bedarf.

**Begründung für Option A:**

1. Keine CCU-Änderung – entspricht der Vorgabe „ohne Änderung der bestehenden Order- und NAVIGATION-Logik“.
2. Alle benötigten Daten sind bereits vorhanden; die FTS-Order-Struktur ist stabil und dokumentiert.
3. Der Spät-Join-Fall ist selten (Session-Replay/Neustart); eine kurzfristige Lücke ist akzeptabel, bis die nächste Nav-Order publiziert wird.
4. Schnell umsetzbar, ohne CCU-Deployment.

**Option B** bietet sich an, wenn:

- Spät-Join-Zuverlässigkeit zwingend sein soll, oder
- FTS-Order-Payload nicht in der osf-ui geparst werden soll (Separation of Concerns).

---

## 5. Implementierungshinweise für Option A

### Schritte

1. **FtsOrderAssignmentService** (oder ähnlich) in osf-ui:
   - Abonniert alle `fts/v1/ff/+/order` Messages (z. B. über MessageMonitor mit Wildcard oder gezielte Topics)
   - Parst Payload: `orderId`, `nodes`; sucht letzten Node mit `action?.id` → `stepId`
   - Extrahiert `ftsSerial` aus Topic (z. B. `fts/v1/ff/5iO4/order` → `5iO4`)
   - Hält Map: `Map<string, Map<string, string>>` bzw. `Record<orderId, Record<stepId, ftsSerial>>`

2. **OrderCard / Order-Tab:**
   - Ruft Service ab: `getFtsSerialForStep(orderId, stepId): string | null`
   - Bei NAVIGATION-Steps: nutzt `step.serialNumber ?? service.getFtsSerialForStep(...)` für Anzeige

3. **MessageMonitor / Topic-Subscription:**
   - `getLastMessage(topic)` arbeitet mit exaktem Topic-Match (kein Wildcard). Pro FTS-Serial muss separat subscribet werden: `fts/v1/ff/5iO4/order`, `fts/v1/ff/IeJ4/order`.
   - FTS-Seriennummern können aus Konfiguration stammen (z. B. AGV-Mapping, `docs/05-hardware/arduino-r4-multisensor.md` oder second-agv-Referenz) oder dynamisch aus `getTopics()` gefiltert werden (Topics mit Pattern `fts/v1/ff/*/order`), sobald mindestens eine Message angekommen ist.

### FTS-Order-Payload (Referenz)

```json
{
  "timestamp": "...",
  "orderId": "...",
  "orderUpdateId": 0,
  "serialNumber": "5iO4",
  "nodes": [
    { "id": "...", "linkedEdges": [...], "action": { "type": "PASS", "id": "..." } },
    { "id": "...", "linkedEdges": [...], "action": { "type": "DOCK", "id": "<NAV_STEP_ID>", "metadata": {...} } }
  ],
  "edges": [...]
}
```

Die NAVIGATION-Step-Id steht im **letzten** Node (`action.id` des DOCK-Actions).

---

## 6. Verifizierung: Track & Trace und Orders Tab

### Orders Tab (OrderCard – Steps)

- **Aktuell:** `moduleName(step)` nutzt `step.serialNumber` für NAVIGATION → `getAgvLabel(serialNumber)` → „AGV-1“/„AGV-2“. Ohne serialNumber: Fallback „AGV“.
- **Mit Option A:** `FtsOrderAssignmentService.getFtsSerialForStep(orderId, step.id)` liefert die Zuordnung. OrderCard nutzt `step.serialNumber ?? assignmentService.getFtsSerialForStep(...)` → **AGV-1/AGV-2 wie bei Mod 3**.

### Track & Trace

- **Shopfloor Events (linke Spalte):** Events werden aus FTS-State und Modul-State gebaut. Jedes Event hat eine Quelle (Topic): `fts/v1/ff/5iO4/state` oder `fts/v1/ff/IeJ4/state` → Serial ist im Topic bzw. im Payload. `WorkpieceHistoryService` setzt `moduleName = getAgvLabel(moduleSerialId)` für FTS-Events. **AGV-1/AGV-2 wird bereits angezeigt** – keine Änderung nötig.
- **Order Context (rechte Spalte):** Zeigt Order-Metadaten (orderId, Status, ERP-Links). Keine Darstellung von Steps mit AGV-Zuordnung – das ist bewusst so (Order-Ebene, nicht Step-Ebene).

**Fazit:** Track & Trace zeigt FTS/AGV pro Event schon korrekt (Quelle = FTS-Topic). Option A ergänzt die fehlende Zuordnung nur dort, wo sie aus **ccu/order/active** kommt: im **Orders Tab** bei den Steps. Zusätzlich kann die **Shopfloor Preview** im OrderCard (Badge bei NAVIGATION) von „FTS“ auf „AGV-1“/„AGV-2“ umgestellt werden, sobald `effectiveSerial` aus dem Assignment-Service verfügbar ist.

---

## 7. Referenzen

- [OSF-MODIFICATIONS.md](../../integrations/APS-CCU/OSF-MODIFICATIONS.md) – Mod 3 Status
- [order-card.component.ts](../../osf/apps/osf-ui/src/app/components/order-card/order-card.component.ts) – AGV-Label-Nutzung
- [navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts) – `sendNavigationRequest`, FTS-Order-Publish
- [NavigatorService.getFTSOrder](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigator-service.ts) – `actionId` = nav step id
