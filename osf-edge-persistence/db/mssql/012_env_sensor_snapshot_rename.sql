-- UC-02: migrate legacy sensor_snapshot → env_sensor_snapshot (idempotent).
-- Fresh installs only have env_sensor_snapshot from 002_schema.sql.
-- Existing DBs may still have sensor_snapshot; 002 may have created an empty env_* first.
USE osf_edge;
GO

-- Case A: only legacy table → rename
IF OBJECT_ID(N'dbo.sensor_snapshot', N'U') IS NOT NULL
   AND OBJECT_ID(N'dbo.env_sensor_snapshot', N'U') IS NULL
BEGIN
  EXEC sp_rename N'dbo.sensor_snapshot', N'env_sensor_snapshot';
END
GO

-- Case B: both exist (common after 002 ran first) → keep env_*, drop legacy
IF OBJECT_ID(N'dbo.sensor_snapshot', N'U') IS NOT NULL
   AND OBJECT_ID(N'dbo.env_sensor_snapshot', N'U') IS NOT NULL
BEGIN
  DECLARE @env_rows BIGINT = (SELECT COUNT_BIG(*) FROM dbo.env_sensor_snapshot);
  DECLARE @old_rows BIGINT = (SELECT COUNT_BIG(*) FROM dbo.sensor_snapshot);

  IF @env_rows = 0 AND @old_rows > 0
  BEGIN
    -- Empty new table + data in legacy: drop empty, rename legacy
    DROP TABLE dbo.env_sensor_snapshot;
    EXEC sp_rename N'dbo.sensor_snapshot', N'env_sensor_snapshot';
  END
  ELSE
  BEGIN
    -- Prefer env_* as canonical; copy any missing dedup keys then drop legacy
    SET IDENTITY_INSERT dbo.env_sensor_snapshot ON;
    INSERT INTO dbo.env_sensor_snapshot (
      id, ts, source, station_id, sensor_type, metric_name, value_numeric, value_text,
      unit, reason, related_event_id, order_id, workpiece_id, payload_json, dedup_key, created_at
    )
    SELECT
      s.id, s.ts, s.source, s.station_id, s.sensor_type, s.metric_name, s.value_numeric, s.value_text,
      s.unit, s.reason, s.related_event_id, s.order_id, s.workpiece_id, s.payload_json, s.dedup_key, s.created_at
    FROM dbo.sensor_snapshot s
    WHERE NOT EXISTS (
      SELECT 1 FROM dbo.env_sensor_snapshot e WHERE e.dedup_key = s.dedup_key
    );
    SET IDENTITY_INSERT dbo.env_sensor_snapshot OFF;
    DROP TABLE dbo.sensor_snapshot;
  END
END
GO

IF OBJECT_ID(N'dbo.env_sensor_snapshot', N'U') IS NOT NULL
BEGIN
  IF EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = N'PK_sensor_snapshot' AND parent_object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
    EXEC sp_rename N'dbo.PK_sensor_snapshot', N'PK_env_sensor_snapshot', N'OBJECT';
  IF EXISTS (SELECT 1 FROM sys.objects WHERE name = N'UQ_sensor_snapshot_dedup_key' AND parent_object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
    EXEC sp_rename N'dbo.UQ_sensor_snapshot_dedup_key', N'UQ_env_sensor_snapshot_dedup_key', N'OBJECT';
  IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = N'CK_sensor_snapshot_reason' AND parent_object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
    EXEC sp_rename N'dbo.CK_sensor_snapshot_reason', N'CK_env_sensor_snapshot_reason', N'OBJECT';
  IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = N'FK_sensor_snapshot_related_event' AND parent_object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
    EXEC sp_rename N'dbo.FK_sensor_snapshot_related_event', N'FK_env_sensor_snapshot_related_event', N'OBJECT';
  IF EXISTS (SELECT 1 FROM sys.default_constraints WHERE name = N'DF_sensor_snapshot_created_at' AND parent_object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
    EXEC sp_rename N'dbo.DF_sensor_snapshot_created_at', N'DF_env_sensor_snapshot_created_at', N'OBJECT';
END
GO

IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_ts' AND object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
  DROP INDEX idx_sensor_snapshot_ts ON dbo.env_sensor_snapshot;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_metric' AND object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
  DROP INDEX idx_sensor_snapshot_metric ON dbo.env_sensor_snapshot;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_station' AND object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
  DROP INDEX idx_sensor_snapshot_station ON dbo.env_sensor_snapshot;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_source' AND object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
  DROP INDEX idx_sensor_snapshot_source ON dbo.env_sensor_snapshot;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_order_id' AND object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
  DROP INDEX idx_sensor_snapshot_order_id ON dbo.env_sensor_snapshot;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_sensor_snapshot_workpiece_id' AND object_id = OBJECT_ID(N'dbo.env_sensor_snapshot'))
  DROP INDEX idx_sensor_snapshot_workpiece_id ON dbo.env_sensor_snapshot;
GO
