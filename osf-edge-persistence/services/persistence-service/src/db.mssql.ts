import sql, { ConnectionPool } from 'mssql';
import { ServiceConfig } from './config';
import { Logger } from './logger';
import { PersistenceStore } from './persistenceStore';
import {
  NormalizedMessage,
  ShopfloorOrderRow,
  ProductionStepRow,
  SensorSnapshotRow,
  ShopfloorEventRow,
  WorkpieceRow,
} from './types';

export class MssqlPersistenceDb implements PersistenceStore {
  private pool: ConnectionPool | null = null;

  constructor(
    private readonly config: ServiceConfig,
    private readonly logger: Logger
  ) {}

  async connect(): Promise<void> {
    const { mssql: cfg } = this.config;
    this.pool = await new sql.ConnectionPool({
      server: cfg.host,
      port: cfg.port,
      database: cfg.db,
      user: cfg.user,
      password: cfg.password,
      options: {
        encrypt: cfg.encrypt,
        trustServerCertificate: cfg.trustServerCertificate,
        enableArithAbort: true,
      },
      pool: { max: 10, min: 0, idleTimeoutMillis: 30000 },
    }).connect();
    await this.pool.request().query('SELECT 1 AS ok');
    this.logger.info('Database connection ready', { dialect: 'mssql', db: cfg.db });
  }

  async close(): Promise<void> {
    if (this.pool) {
      await this.pool.close();
      this.pool = null;
    }
  }

  async persist(normalized: NormalizedMessage): Promise<void> {
    // Avoid long multi-statement transactions: MQTT fan-in deadlocks MSSQL under load.
    // Dedup is enforced by UNIQUE keys (duplicate / deadlock → ignore).
    await this.persistShopfloorEvents(normalized.shopfloorEvents);
    await this.persistOrders(normalized.shopfloorOrders);
    await this.persistSteps(normalized.productionSteps);
    await this.persistWorkpieces(normalized.workpieces);
    await this.persistSensors(normalized.sensorSnapshots);
    await this.persistRaw(normalized);
  }

  async cleanupRawRetention(): Promise<void> {
    const days = Math.max(1, this.config.runtime.rawRetentionDays);
    const pool = this.requirePool();
    await pool
      .request()
      .input('days', sql.Int, days)
      .query(
        `DELETE FROM dbo.mqtt_raw_message
         WHERE received_at < DATEADD(day, -@days, SYSUTCDATETIME())`
      );
  }

  async hasReplaySession(sessionId: string): Promise<boolean> {
    const pool = this.requirePool();
    const result = await pool
      .request()
      .input('session_id', sql.NVarChar(256), sessionId)
      .query(`SELECT TOP 1 1 AS ok FROM dbo.replay_session_ingest WHERE session_id = @session_id`);
    return (result.recordset?.length ?? 0) > 0;
  }

  async recordReplaySession(sessionId: string): Promise<void> {
    const pool = this.requirePool();
    await this.execIgnoreDuplicate(
      pool.request().input('session_id', sql.NVarChar(256), sessionId),
      `INSERT INTO dbo.replay_session_ingest (session_id) VALUES (@session_id);`
    );
  }

  private requirePool(): ConnectionPool {
    if (!this.pool) {
      throw new Error('MSSQL pool is not connected');
    }
    return this.pool;
  }

  private async execIgnoreDuplicate(request: sql.Request, queryText: string): Promise<void> {
    try {
      await request.query(queryText);
    } catch (error: unknown) {
      const number =
        typeof error === 'object' && error !== null && 'number' in error
          ? Number((error as { number?: number }).number)
          : undefined;
      // 2627/2601 = unique violation; 1205 = deadlock victim
      if (number === 2627 || number === 2601 || number === 1205) {
        return;
      }
      throw error;
    }
  }

  private sanitizeJsonValue(value: unknown): unknown {
    if (typeof value === 'string') {
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

  private toJsonParam(value: unknown): string {
    try {
      return JSON.stringify(this.sanitizeJsonValue(value ?? {}));
    } catch {
      return '{}';
    }
  }

  private async persistShopfloorEvents(rows: ShopfloorEventRow[]): Promise<void> {
    const pool = this.requirePool();
    for (const row of rows) {
      await this.execIgnoreDuplicate(
        new sql.Request(pool)
          .input('ts', sql.DateTimeOffset, row.ts)
          .input('dedup_key', sql.NVarChar(512), row.dedupKey)
          .input('event_type', sql.NVarChar(128), row.eventType)
          .input('topic', sql.NVarChar(512), row.topic)
          .input('source', sql.NVarChar(64), row.source)
          .input('module_type', sql.NVarChar(64), row.moduleType ?? null)
          .input('module_serial', sql.NVarChar(128), row.moduleSerial ?? null)
          .input('order_id', sql.NVarChar(128), row.orderId ?? null)
          .input('workpiece_id', sql.NVarChar(128), row.workpieceId ?? null)
          .input('workpiece_type', sql.NVarChar(64), row.workpieceType ?? null)
          .input('action', sql.NVarChar(128), row.action ?? null)
          .input('action_state', sql.NVarChar(64), row.actionState ?? null)
          .input('payload_json', sql.NVarChar(sql.MAX), this.toJsonParam(row.payload)),
        `
          INSERT INTO dbo.shopfloor_event
            (ts, dedup_key, event_type, topic, source, module_type, module_serial, order_id,
             workpiece_id, workpiece_type, action, action_state, payload_json)
          VALUES
            (@ts, @dedup_key, @event_type, @topic, @source, @module_type, @module_serial, @order_id,
             @workpiece_id, @workpiece_type, @action, @action_state, @payload_json);
        `
      );
    }
  }

  private async persistOrders(rows: ShopfloorOrderRow[]): Promise<void> {
    const pool = this.requirePool();
    for (const row of rows) {
      await this.execIgnoreDuplicate(
        new sql.Request(pool)
          .input('order_id', sql.NVarChar(128), row.orderId)
          .input('order_type', sql.NVarChar(64), row.orderType ?? null)
          .input('workpiece_id', sql.NVarChar(128), row.workpieceId ?? null)
          .input('workpiece_type', sql.NVarChar(64), row.workpieceType ?? null)
          .input('state', sql.NVarChar(64), row.state ?? null)
          .input('received_at', sql.DateTimeOffset, row.receivedAt ?? null)
          .input('started_at', sql.DateTimeOffset, row.startedAt ?? null)
          .input('stopped_at', sql.DateTimeOffset, row.stoppedAt ?? null),
        `
          MERGE dbo.shopfloor_order AS t
          USING (SELECT @order_id AS order_id) AS s
          ON t.order_id = s.order_id
          WHEN MATCHED THEN UPDATE SET
            order_type = COALESCE(@order_type, t.order_type),
            workpiece_id = COALESCE(@workpiece_id, t.workpiece_id),
            workpiece_type = COALESCE(@workpiece_type, t.workpiece_type),
            state = COALESCE(@state, t.state),
            received_at = COALESCE(@received_at, t.received_at),
            started_at = COALESCE(@started_at, t.started_at),
            stopped_at = COALESCE(@stopped_at, t.stopped_at),
            updated_at = SYSUTCDATETIME()
          WHEN NOT MATCHED THEN INSERT
            (order_id, order_type, workpiece_id, workpiece_type, state, received_at, started_at, stopped_at, updated_at)
          VALUES
            (@order_id, @order_type, @workpiece_id, @workpiece_type, @state, @received_at, @started_at, @stopped_at, SYSUTCDATETIME());
        `
      );
    }
  }

  private async persistSteps(rows: ProductionStepRow[]): Promise<void> {
    const pool = this.requirePool();
    for (const row of rows) {
      await this.execIgnoreDuplicate(
        new sql.Request(pool)
          .input('dedup_key', sql.NVarChar(512), row.dedupKey)
          .input('order_id', sql.NVarChar(128), row.orderId ?? null)
          .input('step_id', sql.NVarChar(128), row.stepId ?? null)
          .input('step_type', sql.NVarChar(64), row.stepType ?? null)
          .input('module_type', sql.NVarChar(64), row.moduleType ?? null)
          .input('module_serial', sql.NVarChar(128), row.moduleSerial ?? null)
          .input('command', sql.NVarChar(128), row.command ?? null)
          .input('state', sql.NVarChar(64), row.state ?? null)
          .input('source', sql.NVarChar(128), row.source ?? null)
          .input('target', sql.NVarChar(128), row.target ?? null)
          .input('started_at', sql.DateTimeOffset, row.startedAt ?? null)
          .input('stopped_at', sql.DateTimeOffset, row.stoppedAt ?? null)
          .input('payload_json', sql.NVarChar(sql.MAX), this.toJsonParam(row.payload)),
        `
          INSERT INTO dbo.production_step
            (dedup_key, order_id, step_id, step_type, module_type, module_serial, command, state,
             source, target, started_at, stopped_at, payload_json)
          VALUES
            (@dedup_key, @order_id, @step_id, @step_type, @module_type, @module_serial, @command, @state,
             @source, @target, @started_at, @stopped_at, @payload_json);
        `
      );
    }
  }

  private async persistWorkpieces(rows: WorkpieceRow[]): Promise<void> {
    const pool = this.requirePool();
    for (const row of rows) {
      await this.execIgnoreDuplicate(
        new sql.Request(pool)
          .input('workpiece_id', sql.NVarChar(128), row.workpieceId)
          .input('type', sql.NVarChar(64), row.type ?? null)
          .input('current_state', sql.NVarChar(64), row.currentState ?? null)
          .input('last_location', sql.NVarChar(128), row.lastLocation ?? null)
          .input('first_seen_at', sql.DateTimeOffset, row.firstSeenAt ?? null)
          .input('last_seen_at', sql.DateTimeOffset, row.lastSeenAt ?? null),
        `
          MERGE dbo.workpiece AS t
          USING (SELECT @workpiece_id AS workpiece_id) AS s
          ON t.workpiece_id = s.workpiece_id
          WHEN MATCHED THEN UPDATE SET
            type = COALESCE(@type, t.type),
            current_state = COALESCE(@current_state, t.current_state),
            last_location = COALESCE(@last_location, t.last_location),
            first_seen_at = COALESCE(t.first_seen_at, @first_seen_at),
            last_seen_at = COALESCE(@last_seen_at, t.last_seen_at),
            updated_at = SYSUTCDATETIME()
          WHEN NOT MATCHED THEN INSERT
            (workpiece_id, type, current_state, last_location, first_seen_at, last_seen_at, updated_at)
          VALUES
            (@workpiece_id, @type, @current_state, @last_location, @first_seen_at, @last_seen_at, SYSUTCDATETIME());
        `
      );
    }
  }

  private async persistSensors(rows: SensorSnapshotRow[]): Promise<void> {
    const pool = this.requirePool();
    for (const row of rows) {
      await this.execIgnoreDuplicate(
        new sql.Request(pool)
          .input('ts', sql.DateTimeOffset, row.ts)
          .input('source', sql.NVarChar(64), row.source)
          .input('station_id', sql.NVarChar(128), row.stationId ?? null)
          .input('sensor_type', sql.NVarChar(64), row.sensorType ?? null)
          .input('metric_name', sql.NVarChar(128), row.metricName)
          .input('value_numeric', sql.Float, row.valueNumeric ?? null)
          .input('value_text', sql.NVarChar(512), row.valueText ?? null)
          .input('unit', sql.NVarChar(32), row.unit ?? null)
          .input('reason', sql.NVarChar(32), row.reason)
          .input('order_id', sql.NVarChar(128), row.orderId ?? null)
          .input('workpiece_id', sql.NVarChar(128), row.workpieceId ?? null)
          .input('payload_json', sql.NVarChar(sql.MAX), this.toJsonParam(row.payload))
          .input('dedup_key', sql.NVarChar(512), row.dedupKey),
        `
          INSERT INTO dbo.env_sensor_snapshot
            (ts, source, station_id, sensor_type, metric_name, value_numeric, value_text, unit,
             reason, order_id, workpiece_id, payload_json, dedup_key)
          VALUES
            (@ts, @source, @station_id, @sensor_type, @metric_name, @value_numeric, @value_text, @unit,
             @reason, @order_id, @workpiece_id, @payload_json, @dedup_key);
        `
      );
    }
  }

  private async persistRaw(normalized: NormalizedMessage): Promise<void> {
    if (!normalized.raw) {
      return;
    }
    const raw = normalized.raw;
    const pool = this.requirePool();
    await this.execIgnoreDuplicate(
      new sql.Request(pool)
        .input('received_at', sql.DateTimeOffset, raw.receivedAt)
        .input('topic', sql.NVarChar(512), raw.topic)
        .input('qos', sql.SmallInt, raw.qos)
        .input('retain', sql.Bit, raw.retain)
        .input(
          'payload_json',
          sql.NVarChar(sql.MAX),
          raw.payloadJson ? this.toJsonParam(raw.payloadJson) : null
        )
        .input('payload_text', sql.NVarChar(sql.MAX), raw.payloadText ?? null)
        .input('persisted_reason', sql.NVarChar(64), raw.persistedReason)
        .input('payload_hash', sql.NVarChar(128), raw.payloadHash)
        .input('dedup_key', sql.NVarChar(512), raw.dedupKey),
      `
        INSERT INTO dbo.mqtt_raw_message
          (received_at, topic, qos, retain, payload_json, payload_text, persisted_reason, payload_hash, dedup_key)
        VALUES
          (@received_at, @topic, @qos, @retain, @payload_json, @payload_text, @persisted_reason, @payload_hash, @dedup_key);
      `
    );
  }
}
