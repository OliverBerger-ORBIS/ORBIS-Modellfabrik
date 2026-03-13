# OSF-Modifikationen an der Fischertechnik APS-CCU

**Quelle:** [Fischertechnik Agile-Production-Simulation-24V-Dev](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev)  
**Referenz:** [docs/06-integrations/FISCHERTECHNIK-OFFICIAL.md](../../docs/06-integrations/FISCHERTECHNIK-OFFICIAL.md)  
**Dokumentations-Entscheidung:** [DR-20: APS-CCU OSF-Modifikationen – zentrale Dokumentation](../../docs/03-decision-records/20-aps-ccu-osf-modifications-documentation.md)

---

Diese Datei listet alle Abweichungen der OSF-Version von der Original-Fischertechnik-CCU.  
Phase-5-Kontext: MES und DSP (ORBIS) übernehmen zunehmend die Steuerung; die CCU dient als Interim-Layer.

---

## Übersicht der Modifikationen

| Nr. | Kurzbeschreibung | Status | Betroffene Datei(en) | Anlass |
|-----|------------------|--------|----------------------|--------|
| 1   | ccu/order/request: Optionale Erweiterung um requestId | ✅ Umgesetzt | `common/protocol/ccu.ts`, `central-control/.../order/index.ts` | Sprint 16, Commit d2052f95 |
| 2   | Quality-Fail: Kein automatischer Ersatzauftrag | ✅ Umgesetzt (seit v1.3.0-osf.1) | `central-control/src/modules/order/management/order-management.ts` | Sprint 17, [Analyse](../../docs/07-analysis/ccu-quality-fail-behaviour-2026-03.md), [DR-21](../../docs/03-decision-records/21-ccu-osf-versioning.md) |
| 3   | ccu/order/active, completed: Optional serialNumber in NAVIGATION steps | ❌ Zurückgenommen (2026-03) | – | Ursprünglich für AGV-1/AGV-2 Anzeige; entfernt, da potenzielle Ursache für Stillstand |

---

## Detaillierte Beschreibung

Struktur je Modifikation: **Zweck (Warum)** → **Wie (Implementation)**.

---

### 1. ccu/order/request: Optionale Erweiterung um requestId

#### Zweck (Warum)

Korrelation zwischen CCU-Produktionsaufträgen und übergeordneten Business-Prozessen (Customer-Order, Purchase-Order, ERP/MES-Aufträge). Externe Systeme (DSP, ERP, MES) können ihre eigene Auftrags-ID (`requestId`) mitschicken und erhalten sie in der CCU-Response zurück – damit ist die Zuordnung `requestId ↔ orderId` hergestellt (Track & Trace, ERP-Synchronisation).

#### Wie (Implementation)

- **OrderRequest** (`ccu/order/request`): Optionales Attribut `requestId?: string`. Beliebiger String, Eindeutigkeit liegt beim Requestor (OSF-UI, DSP, ERP).
- **OrderResponse** (`ccu/order/response`): CCU übernimmt `requestId` aus dem Request und gibt es unverändert zurück.
- **Snake-Case-Fallback:** Für Kompatibilität mit DSP/ERP wird auch `request_id` (snake_case) akzeptiert und als `requestId` in der Response ausgegeben.
- **Betroffene Dateien:**
  - `common/protocol/ccu.ts`: `OrderRequest`, `OrderResponse` – optionales `requestId?: string`
  - `central-control/src/modules/order/index.ts`: `handleMessage()` – Normalisierung von `request_id` → `requestId`; `sendResponse()` – `requestId` in Response; Payload für Publish wird explizit mit `requestId` aus `orderRequest` gebaut (verhindert Verlust durch Referenz-Mutation in cacheOrder).
  - **`central-control/src/modules/gateway/order/index.ts`:** Gateway-Orders von `/j1/txt/1/f/o/order` haben bisher `requestId` verworfen – jetzt wird es durchgereicht (entscheidend für Cloud-Orders).
- **Rückwärtskompatibel:** Fehlt `requestId`/`request_id`, Verhalten unverändert.

**Referenz:** [order-requestid-extension.md](../../docs/07-analysis/order-requestid-extension.md), Commit d2052f95 (Sprint 16)

---

### 2. Quality-Fail: Kein automatischer Ersatzauftrag

#### Zweck (Warum)

Vorbereitung für MES/DSP-Übernahme der QM-Entscheidung. Die CCU soll bei `CHECK_QUALITY result=FAILED` nicht mehr selbst einen Ersatzauftrag erzeugen – stattdessen bleibt die Order auf ERROR, und MES/DSP entscheiden (Ersatzauftrag, Reprocessing, Scrap).

#### Wie (Implementation)

- **Original-Verhalten:** Bei Quality-Fail erstellt die CCU automatisch einen neuen Production-Order (wenn Rohmaterial im HBW verfügbar).
- **OSF-Verhalten:** Kein automatischer Ersatzauftrag. Order bleibt auf ERROR, verbleibende Steps werden gecancelt, Order wird in `completedOrders` verschoben.
- **FTS-Weiterfahrt:** Das FTS fährt per `sendClearModuleNodeNavigationRequest()` vom AIQS weg (Navigationsanweisung ohne neuen Production-Order), damit die Fabrik nicht blockiert bleibt.
- **Betroffener Code:** `handleActionUpdateQualityCheckFailure()` in `order-management.ts` – Aufruf von `createOrder()` entfernt; Aufruf von `sendClearModuleNodeNavigationRequest(aiqsModuleSerial)` und `retriggerFTSSteps()` ergänzt.
- **Unit-Test:** `order-management.test.ts` – "should NOT create replacement order when quality check fails"

**Referenz:** [ccu-quality-fail-behaviour-2026-03.md](../../docs/07-analysis/ccu-quality-fail-behaviour-2026-03.md), [sprint_17.md](../../docs/sprints/sprint_17.md). Version: v1.3.0-osf.1 ([DR-21](../../docs/03-decision-records/21-ccu-osf-versioning.md)).

---

### 3. ccu/order/active, completed: Optional serialNumber in NAVIGATION steps (zurückgenommen)

**Status:** ❌ Zurückgenommen (2026-03)

Ursprünglich für AGV-1/AGV-2 Anzeige in osf-ui. Entfernt, da potenzielle Ursache für Stillstände (z.B. agv-2-mixed) diskutiert wurde. Die osf-ui behandelt fehlendes `serialNumber` bereits als optional.

---

*Letzte Aktualisierung: 2026-03-12*
