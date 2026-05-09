import { Pool, PoolClient } from 'pg';
import { ServiceConfig } from './config';
import { Logger } from './logger';
import {
  NormalizedMessage,
  ProductionOrderRow,
  ProductionStepRow,
  SensorSnapshotRow,
  ShopfloorEventRow,
  WorkpieceRow,
} from './types';

export class PersistenceDb {
  private readonly pool: Pool;

  constructor(private readonly config: ServiceConfig, private readonly logger: Logger) {
    this.pool = new Pool({
      host: config.postgres.host,
      port: config.postgres.port,
      database: config.postgres.db,
      user: config.postgres.user,
      password: config.postgres.password,
      max: 10,
    });
  }

  async connect(): Promise<void> {
    await this.pool.query('SELECT 1');
    this.logger.info('Database connection ready');
  }

  async close(): Promise<void> {
    await this.pool.end();
  }

  async persist(normalized: NormalizedMessage): Promise<void> {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      await this.persistShopfloorEvents(client, normalized.shopfloorEvents);
      await this.persistOrders(client, normalized.productionOrders);
      await this.persistSteps(client, normalized.productionSteps);
      await this.persistWorkpieces(client, normalized.workpieces);
      await this.persistSensors(client, normalized.sensorSnapshots);
      await this.persistRaw(client, normalized);
      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async cleanupRawRetention(): Promise<void> {
    const days = Math.max(1, this.config.runtime.rawRetentionDays);
    await this.pool.query(`DELETE FROM mqtt_raw_message WHERE received_at < NOW() - ($1::text || ' days')::interval`, [String(days)]);
  }

  private sanitizeJsonValue(value: unknown): unknown {
    if (typeof value === 'string') {
      // Postgres JSONB rejects payloads containing zero bytes.
      return value.replace(/\u0000/g, '');
    }
    if (Array.isArray(value)) {
      return value.map((item) => this.sanitizeJsonValue(item));
    }
    if (value && typeof value === 'object') {
      const out: Record<string, unknown> = {};
      for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
        if (item === undefined) {
          continue;
        }
        out[key] = this.sanitizeJsonValue(item);
      }
      return out;
    }
    return value;
  }

  private toJsonbParam(value: unknown): string {
    try {
      return JSON.stringify(this.sanitizeJsonValue(value ?? {}));
    } catch {
      return '{}';
    }
  }

  private async persistShopfloorEvents(client: PoolClient, rows: ShopfloorEventRow[]): Promise<void> {
    for (const row of rows) {
      await client.query(
        `INSERT INTO shopfloor_event
          (ts, dedup_key, event_type, topic, source, module_type, module_serial, order_id, workpiece_id, workpiece_type, action, action_state, payload_json)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13::jsonb)
         ON CONFLICT (dedup_key) DO NOTHING`,
        [
          row.ts,
          row.dedupKey,
          row.eventType,
          row.topic,
          row.source,
          row.moduleType ?? null,
          row.moduleSerial ?? null,
          row.orderId ?? null,
          row.workpieceId ?? null,
          row.workpieceType ?? null,
          row.action ?? null,
          row.actionState ?? null,
          this.toJsonbParam(row.payload),
        ]
      );
    }
  }

  private async persistOrders(client: PoolClient, rows: ProductionOrderRow[]): Promise<void> {
    for (const row of rows) {
      await client.query(
        `INSERT INTO production_order
          (order_id, order_type, workpiece_id, workpiece_type, state, received_at, started_at, stopped_at, updated_at)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,NOW())
         ON CONFLICT (order_id) DO UPDATE SET
            order_type = COALESCE(EXCLUDED.order_type, production_order.order_type),
            workpiece_id = COALESCE(EXCLUDED.workpiece_id, production_order.workpiece_id),
            workpiece_type = COALESCE(EXCLUDED.workpiece_type, production_order.workpiece_type),
            state = COALESCE(EXCLUDED.state, production_order.state),
            received_at = COALESCE(EXCLUDED.received_at, production_order.received_at),
            started_at = COALESCE(EXCLUDED.started_at, production_order.started_at),
            stopped_at = COALESCE(EXCLUDED.stopped_at, production_order.stopped_at),
            updated_at = NOW()`,
        [
          row.orderId,
          row.orderType ?? null,
          row.workpieceId ?? null,
          row.workpieceType ?? null,
          row.state ?? null,
          row.receivedAt ?? null,
          row.startedAt ?? null,
          row.stoppedAt ?? null,
        ]
      );
    }
  }

  private async persistSteps(client: PoolClient, rows: ProductionStepRow[]): Promise<void> {
    for (const row of rows) {
      await client.query(
        `INSERT INTO production_step
          (dedup_key, order_id, step_id, step_type, module_type, module_serial, command, state, source, target, started_at, stopped_at, payload_json)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13::jsonb)
         ON CONFLICT (dedup_key) DO NOTHING`,
        [
          row.dedupKey,
          row.orderId ?? null,
          row.stepId ?? null,
          row.stepType ?? null,
          row.moduleType ?? null,
          row.moduleSerial ?? null,
          row.command ?? null,
          row.state ?? null,
          row.source ?? null,
          row.target ?? null,
          row.startedAt ?? null,
          row.stoppedAt ?? null,
          this.toJsonbParam(row.payload),
        ]
      );
    }
  }

  private async persistWorkpieces(client: PoolClient, rows: WorkpieceRow[]): Promise<void> {
    for (const row of rows) {
      await client.query(
        `INSERT INTO workpiece
          (workpiece_id, type, current_state, last_location, first_seen_at, last_seen_at, updated_at)
         VALUES ($1,$2,$3,$4,$5,$6,NOW())
         ON CONFLICT (workpiece_id) DO UPDATE SET
            type = COALESCE(EXCLUDED.type, workpiece.type),
            current_state = COALESCE(EXCLUDED.current_state, workpiece.current_state),
            last_location = COALESCE(EXCLUDED.last_location, workpiece.last_location),
            first_seen_at = COALESCE(workpiece.first_seen_at, EXCLUDED.first_seen_at),
            last_seen_at = COALESCE(EXCLUDED.last_seen_at, workpiece.last_seen_at),
            updated_at = NOW()`,
        [
          row.workpieceId,
          row.type ?? null,
          row.currentState ?? null,
          row.lastLocation ?? null,
          row.firstSeenAt ?? null,
          row.lastSeenAt ?? null,
        ]
      );
    }
  }

  private async persistSensors(client: PoolClient, rows: SensorSnapshotRow[]): Promise<void> {
    for (const row of rows) {
      await client.query(
        `INSERT INTO sensor_snapshot
          (ts, source, station_id, sensor_type, metric_name, value_numeric, value_text, unit, reason, order_id, workpiece_id, payload_json, dedup_key)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12::jsonb,$13)
         ON CONFLICT (dedup_key) DO NOTHING`,
        [
          row.ts,
          row.source,
          row.stationId ?? null,
          row.sensorType ?? null,
          row.metricName,
          row.valueNumeric ?? null,
          row.valueText ?? null,
          row.unit ?? null,
          row.reason,
          row.orderId ?? null,
          row.workpieceId ?? null,
          this.toJsonbParam(row.payload),
          row.dedupKey,
        ]
      );
    }
  }

  private async persistRaw(client: PoolClient, normalized: NormalizedMessage): Promise<void> {
    if (!normalized.raw) {
      return;
    }
    await client.query(
      `INSERT INTO mqtt_raw_message
        (received_at, topic, qos, retain, payload_json, payload_text, persisted_reason, payload_hash, dedup_key)
       VALUES ($1,$2,$3,$4,$5::jsonb,$6,$7,$8,$9)
       ON CONFLICT (dedup_key) DO NOTHING`,
      [
        normalized.raw.receivedAt,
        normalized.raw.topic,
        normalized.raw.qos,
        normalized.raw.retain,
        normalized.raw.payloadJson ? this.toJsonbParam(normalized.raw.payloadJson) : null,
        normalized.raw.payloadText ?? null,
        normalized.raw.persistedReason,
        normalized.raw.payloadHash,
        normalized.raw.dedupKey,
      ]
    );
  }
}
