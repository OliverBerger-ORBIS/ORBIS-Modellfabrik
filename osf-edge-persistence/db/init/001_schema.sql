CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS shopfloor_event (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL,
  dedup_key TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL,
  topic TEXT NOT NULL,
  source TEXT NOT NULL,
  module_type TEXT,
  module_serial TEXT,
  order_id TEXT,
  workpiece_id TEXT,
  workpiece_type TEXT,
  action TEXT,
  action_state TEXT,
  payload_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS production_order (
  order_id TEXT PRIMARY KEY,
  order_type TEXT,
  workpiece_id TEXT,
  workpiece_type TEXT,
  state TEXT,
  received_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  stopped_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS production_step (
  id BIGSERIAL PRIMARY KEY,
  dedup_key TEXT NOT NULL UNIQUE,
  order_id TEXT,
  step_id TEXT,
  step_type TEXT,
  module_type TEXT,
  module_serial TEXT,
  command TEXT,
  state TEXT,
  source TEXT,
  target TEXT,
  started_at TIMESTAMPTZ,
  stopped_at TIMESTAMPTZ,
  payload_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workpiece (
  workpiece_id TEXT PRIMARY KEY,
  type TEXT,
  current_state TEXT,
  last_location TEXT,
  first_seen_at TIMESTAMPTZ,
  last_seen_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensor_snapshot (
  id BIGSERIAL,
  ts TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  station_id TEXT,
  sensor_type TEXT,
  metric_name TEXT NOT NULL,
  value_numeric DOUBLE PRECISION,
  value_text TEXT,
  unit TEXT,
  reason TEXT NOT NULL CHECK (reason IN ('EVENT', 'INTERVAL', 'THRESHOLD')),
  related_event_id BIGINT REFERENCES shopfloor_event(id) ON DELETE SET NULL,
  order_id TEXT,
  workpiece_id TEXT,
  payload_json JSONB NOT NULL,
  dedup_key TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id, ts),
  UNIQUE (dedup_key)
);

CREATE TABLE IF NOT EXISTS mqtt_raw_message (
  id BIGSERIAL,
  received_at TIMESTAMPTZ NOT NULL,
  topic TEXT NOT NULL,
  qos SMALLINT,
  retain BOOLEAN,
  payload_json JSONB,
  payload_text TEXT,
  persisted_reason TEXT,
  payload_hash TEXT NOT NULL,
  dedup_key TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id, received_at),
  UNIQUE (dedup_key)
);
