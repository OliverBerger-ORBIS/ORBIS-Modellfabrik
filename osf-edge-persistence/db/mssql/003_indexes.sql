-- Indexes mirroring db/init/002_indexes.sql (Postgres).
USE osf_edge;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_shopfloor_event_ts' AND object_id = OBJECT_ID(N'dbo.shopfloor_event'))
  CREATE INDEX idx_shopfloor_event_ts ON dbo.shopfloor_event (ts DESC);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_shopfloor_event_order_id' AND object_id = OBJECT_ID(N'dbo.shopfloor_event'))
  CREATE INDEX idx_shopfloor_event_order_id ON dbo.shopfloor_event (order_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_shopfloor_event_workpiece_id' AND object_id = OBJECT_ID(N'dbo.shopfloor_event'))
  CREATE INDEX idx_shopfloor_event_workpiece_id ON dbo.shopfloor_event (workpiece_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_shopfloor_event_topic' AND object_id = OBJECT_ID(N'dbo.shopfloor_event'))
  CREATE INDEX idx_shopfloor_event_topic ON dbo.shopfloor_event (topic);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_order_state' AND object_id = OBJECT_ID(N'dbo.production_order'))
  CREATE INDEX idx_production_order_state ON dbo.production_order (state);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_order_stopped_at' AND object_id = OBJECT_ID(N'dbo.production_order'))
  CREATE INDEX idx_production_order_stopped_at ON dbo.production_order (stopped_at DESC);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_step_order_id' AND object_id = OBJECT_ID(N'dbo.production_step'))
  CREATE INDEX idx_production_step_order_id ON dbo.production_step (order_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_step_module_type' AND object_id = OBJECT_ID(N'dbo.production_step'))
  CREATE INDEX idx_production_step_module_type ON dbo.production_step (module_type);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_step_stopped_at' AND object_id = OBJECT_ID(N'dbo.production_step'))
  CREATE INDEX idx_production_step_stopped_at ON dbo.production_step (stopped_at DESC);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_ts' AND object_id = OBJECT_ID(N'dbo.sensor_snapshot'))
  CREATE INDEX idx_sensor_snapshot_ts ON dbo.sensor_snapshot (ts DESC);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_metric' AND object_id = OBJECT_ID(N'dbo.sensor_snapshot'))
  CREATE INDEX idx_sensor_snapshot_metric ON dbo.sensor_snapshot (metric_name);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_station' AND object_id = OBJECT_ID(N'dbo.sensor_snapshot'))
  CREATE INDEX idx_sensor_snapshot_station ON dbo.sensor_snapshot (station_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_source' AND object_id = OBJECT_ID(N'dbo.sensor_snapshot'))
  CREATE INDEX idx_sensor_snapshot_source ON dbo.sensor_snapshot (source);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_order_id' AND object_id = OBJECT_ID(N'dbo.sensor_snapshot'))
  CREATE INDEX idx_sensor_snapshot_order_id ON dbo.sensor_snapshot (order_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_workpiece_id' AND object_id = OBJECT_ID(N'dbo.sensor_snapshot'))
  CREATE INDEX idx_sensor_snapshot_workpiece_id ON dbo.sensor_snapshot (workpiece_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_mqtt_raw_received_at' AND object_id = OBJECT_ID(N'dbo.mqtt_raw_message'))
  CREATE INDEX idx_mqtt_raw_received_at ON dbo.mqtt_raw_message (received_at DESC);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_mqtt_raw_topic' AND object_id = OBJECT_ID(N'dbo.mqtt_raw_message'))
  CREATE INDEX idx_mqtt_raw_topic ON dbo.mqtt_raw_message (topic);
GO
