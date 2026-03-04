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
| 2   | Quality-Fail: Kein automatischer Ersatzauftrag | ✅ Umgesetzt | `central-control/src/modules/order/management/order-management.ts` | Sprint 17, [Analyse](../../docs/07-analysis/ccu-quality-fail-behaviour-2026-03.md) |

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
- **Betroffene Dateien:**
  - `common/protocol/ccu.ts`: `OrderRequest`, `OrderResponse` – optionales `requestId?: string`
  - `central-control/src/modules/order/index.ts`: `sendResponse()` – `requestId: orderRequest.requestId` in Response
- **Rückwärtskompatibel:** Fehlt `requestId`, Verhalten unverändert.

**Referenz:** [order-requestid-extension.md](../../docs/07-analysis/order-requestid-extension.md), Commit d2052f95 (Sprint 16)

---

### 2. Quality-Fail: Kein automatischer Ersatzauftrag

#### Zweck (Warum)

Vorbereitung für MES/DSP-Übernahme der QM-Entscheidung. Die CCU soll bei `CHECK_QUALITY result=FAILED` nicht mehr selbst einen Ersatzauftrag erzeugen – stattdessen bleibt die Order auf ERROR, und MES/DSP entscheiden (Ersatzauftrag, Reprocessing, Scrap).

#### Wie (Implementation)

- **Original-Verhalten:** Bei Quality-Fail erstellt die CCU automatisch einen neuen Production-Order (wenn Rohmaterial im HBW verfügbar).
- **OSF-Verhalten:** Kein automatischer Ersatzauftrag. Order bleibt auf ERROR, verbleibende Steps werden gecancelt, Order wird in `completedOrders` verschoben.
- **Betroffener Code:** `handleActionUpdateQualityCheckFailure()` in `order-management.ts` – Aufruf von `createOrder()` entfernt.
- **Unit-Test:** `order-management.test.ts` – "should NOT create replacement order when quality check fails"

**Referenz:** [ccu-quality-fail-behaviour-2026-03.md](../../docs/07-analysis/ccu-quality-fail-behaviour-2026-03.md), [sprint_17.md](../../docs/sprints/sprint_17.md)

---

*Letzte Aktualisierung: 2026-03-04*
