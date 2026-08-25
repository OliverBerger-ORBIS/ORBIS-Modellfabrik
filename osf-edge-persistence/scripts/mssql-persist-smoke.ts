/**
 * Smoke: persist one intake-shaped message into local MSSQL (no MQTT required).
 *
 *   cd osf-edge-persistence
 *   bash scripts/mssql-init-schema.sh   # once
 *   MSSQL_HOST=localhost MSSQL_PASSWORD='OsfEdge_App9#' \
 *     npx tsx scripts/mssql-persist-smoke.ts
 */
import { loadConfig } from '../services/persistence-service/src/config';
import { createPersistenceStore } from '../services/persistence-service/src/db.factory';
import { Logger } from '../services/persistence-service/src/logger';
import { NormalizedMessage } from '../services/persistence-service/src/types';

async function main(): Promise<void> {
  const config = loadConfig();

  const logger = new Logger('info');
  const db = createPersistenceStore(config, logger);
  await db.connect();

  const nfc = `smoke${Date.now().toString(36)}`;
  const ts = new Date();
  const dedup = `smoke-intake-${nfc}`;

  const normalized: NormalizedMessage = {
    shopfloorEvents: [
      {
        ts,
        dedupKey: dedup,
        eventType: 'WORKPIECE_INTAKE',
        topic: 'osf/workpiece/intake',
        source: 'osf',
        workpieceId: nfc,
        workpieceType: 'BLUE',
        action: 'intake',
        actionState: 'FINISHED',
        payload: { productRaw: 'BLUE', nfc, timestamp: ts.toISOString() },
      },
    ],
    shopfloorOrders: [],
    productionSteps: [],
    workpieces: [
      {
        workpieceId: nfc,
        type: 'BLUE',
        currentState: 'INTAKE',
        lastLocation: 'DPS',
        firstSeenAt: ts,
        lastSeenAt: ts,
      },
    ],
    sensorSnapshots: [],
    raw: {
      receivedAt: ts,
      topic: 'osf/workpiece/intake',
      qos: 0,
      retain: false,
      payloadJson: { productRaw: 'BLUE', nfc },
      payloadText: JSON.stringify({ productRaw: 'BLUE', nfc }),
      persistedReason: 'smoke',
      payloadHash: dedup,
      dedupKey: `raw-${dedup}`,
    },
  };

  await db.persist(normalized);
  await db.close();
  console.log(`OK: persisted intake smoke NFC=${nfc} into ${config.mssql.db}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
