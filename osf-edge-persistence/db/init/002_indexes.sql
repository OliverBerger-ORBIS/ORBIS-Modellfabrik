CREATE INDEX IF NOT EXISTS idx_shopfloor_event_ts ON shopfloor_event (ts DESC);
CREATE INDEX IF NOT EXISTS idx_shopfloor_event_order_id ON shopfloor_event (order_id);
CREATE INDEX IF NOT EXISTS idx_shopfloor_event_workpiece_id ON shopfloor_event (workpiece_id);
CREATE INDEX IF NOT EXISTS idx_shopfloor_event_topic ON shopfloor_event (topic);

CREATE INDEX IF NOT EXISTS idx_production_order_state ON production_order (state);
CREATE INDEX IF NOT EXISTS idx_production_order_stopped_at ON production_order (stopped_at DESC);

CREATE INDEX IF NOT EXISTS idx_production_step_order_id ON production_step (order_id);
CREATE INDEX IF NOT EXISTS idx_production_step_module_type ON production_step (module_type);
CREATE INDEX IF NOT EXISTS idx_production_step_stopped_at ON production_step (stopped_at DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_snapshot_ts ON sensor_snapshot (ts DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_snapshot_metric ON sensor_snapshot (metric_name);
CREATE INDEX IF NOT EXISTS idx_sensor_snapshot_station ON sensor_snapshot (station_id);
CREATE INDEX IF NOT EXISTS idx_sensor_snapshot_source ON sensor_snapshot (source);
CREATE INDEX IF NOT EXISTS idx_sensor_snapshot_order_id ON sensor_snapshot (order_id);
CREATE INDEX IF NOT EXISTS idx_sensor_snapshot_workpiece_id ON sensor_snapshot (workpiece_id);

CREATE INDEX IF NOT EXISTS idx_mqtt_raw_received_at ON mqtt_raw_message (received_at DESC);
CREATE INDEX IF NOT EXISTS idx_mqtt_raw_topic ON mqtt_raw_message (topic);
