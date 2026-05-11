# Anhang Mail 1 – APS-CCU Änderung: requestId-Korrelation

Stand: 2026-05-11

## Ziel

Externe Requestor-Systeme (APS-Frontend, DSP, SAP/ERP/MES) sollen eine eigene Korrelations-ID mitschicken können.
Die CCU erzeugt weiterhin ihre interne `orderId`, gibt in der Antwort aber zusätzlich die mitgesendete `requestId` zurück.
Dadurch ist die Zuordnung `orderId -> requestId` direkt möglich.

## Umgesetztes Verhalten (ORBIS-Version)

- `ccu/order/request` akzeptiert optional `requestId`
- zusätzlich kompatibel: `request_id` (snake_case)
- `ccu/order/response` enthält bei vorhandenem Wert ebenfalls `requestId`
- Gateway-Orders reichen `requestId` ebenfalls durch

## Relevante Upstream-Dateien (Agile-Production-Simulation-24V-Dev, Branch `release`)

- `common/protocol/ccu.ts`
  - `OrderRequest.requestId?: string`
  - `OrderResponse.requestId?: string`
- `central-control/src/modules/order/index.ts`
  - Request-Normalisierung (`requestId` / `request_id`)
  - Echo von `requestId` in `ccu/order/response`
- `central-control/src/modules/gateway/order/index.ts`
  - Durchreichen von `requestId` aus Gateway-Orders

## Relevante Stellen im ORBIS-Spiegel (mit Zeilen)

- [common/protocol/ccu.ts](../../integrations/APS-CCU/common/protocol/ccu.ts#L114-L132)
- [central-control/src/modules/order/index.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.ts#L74-L98)
- [central-control/src/modules/order/index.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.ts#L155-L165)
- [central-control/src/modules/gateway/order/index.ts](../../integrations/APS-CCU/central-control/src/modules/gateway/order/index.ts#L10-L24)

## Tests

- [central-control/src/modules/order/index.test.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.test.ts#L146-L187)
- [central-control/src/modules/order/index.test.ts](../../integrations/APS-CCU/central-control/src/modules/order/index.test.ts#L224-L258)
- [central-control/src/modules/gateway/order/index.test.ts](../../integrations/APS-CCU/central-control/src/modules/gateway/order/index.test.ts#L72-L82)

## Hinweis

In unserer aktuellen Implementierung wird `requestId` faktisch auch über `ccu/order/active` und `ccu/order/completed` mitgeführt, da das angereicherte Order-Objekt in die Queue übernommen wird.

- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L88-L105)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts#L888-L905)

## Bitte an Fischertechnik

Bitte prüfen, ob diese rückwärtskompatible Erweiterung (inkl. optionalem `request_id`-Fallback) im Upstream übernommen werden kann.