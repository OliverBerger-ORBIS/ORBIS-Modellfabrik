-- OSF Edge schema for Microsoft SQL Server (no Timescale).
-- Logical model mirrors db/init/001_schema.sql (Postgres).
USE osf_edge;
GO

IF OBJECT_ID(N'dbo.shopfloor_event', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.shopfloor_event (
    id BIGINT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_shopfloor_event PRIMARY KEY,
    ts DATETIMEOFFSET NOT NULL,
    dedup_key NVARCHAR(512) NOT NULL,
    event_type NVARCHAR(128) NOT NULL,
    topic NVARCHAR(512) NOT NULL,
    source NVARCHAR(64) NOT NULL,
    module_type NVARCHAR(64) NULL,
    module_serial NVARCHAR(128) NULL,
    order_id NVARCHAR(128) NULL,
    workpiece_id NVARCHAR(128) NULL,
    workpiece_type NVARCHAR(64) NULL,
    action NVARCHAR(128) NULL,
    action_state NVARCHAR(64) NULL,
    payload_json NVARCHAR(MAX) NOT NULL,
    created_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_shopfloor_event_created_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_shopfloor_event_dedup_key UNIQUE (dedup_key)
  );
END
GO

IF OBJECT_ID(N'dbo.production_order', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.production_order (
    order_id NVARCHAR(128) NOT NULL CONSTRAINT PK_production_order PRIMARY KEY,
    order_type NVARCHAR(64) NULL,
    workpiece_id NVARCHAR(128) NULL,
    workpiece_type NVARCHAR(64) NULL,
    state NVARCHAR(64) NULL,
    received_at DATETIMEOFFSET NULL,
    started_at DATETIMEOFFSET NULL,
    stopped_at DATETIMEOFFSET NULL,
    updated_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_production_order_updated_at DEFAULT (SYSUTCDATETIME())
  );
END
GO

IF OBJECT_ID(N'dbo.production_step', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.production_step (
    id BIGINT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_production_step PRIMARY KEY,
    dedup_key NVARCHAR(512) NOT NULL,
    order_id NVARCHAR(128) NULL,
    step_id NVARCHAR(128) NULL,
    step_type NVARCHAR(64) NULL,
    module_type NVARCHAR(64) NULL,
    module_serial NVARCHAR(128) NULL,
    command NVARCHAR(128) NULL,
    state NVARCHAR(64) NULL,
    source NVARCHAR(128) NULL,
    target NVARCHAR(128) NULL,
    started_at DATETIMEOFFSET NULL,
    stopped_at DATETIMEOFFSET NULL,
    payload_json NVARCHAR(MAX) NOT NULL,
    created_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_production_step_created_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_production_step_dedup_key UNIQUE (dedup_key)
  );
END
GO

IF OBJECT_ID(N'dbo.workpiece', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.workpiece (
    workpiece_id NVARCHAR(128) NOT NULL CONSTRAINT PK_workpiece PRIMARY KEY,
    type NVARCHAR(64) NULL,
    current_state NVARCHAR(64) NULL,
    last_location NVARCHAR(128) NULL,
    first_seen_at DATETIMEOFFSET NULL,
    last_seen_at DATETIMEOFFSET NULL,
    updated_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_workpiece_updated_at DEFAULT (SYSUTCDATETIME())
  );
END
GO

IF OBJECT_ID(N'dbo.sensor_snapshot', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.sensor_snapshot (
    id BIGINT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_sensor_snapshot PRIMARY KEY,
    ts DATETIMEOFFSET NOT NULL,
    source NVARCHAR(64) NOT NULL,
    station_id NVARCHAR(128) NULL,
    sensor_type NVARCHAR(64) NULL,
    metric_name NVARCHAR(128) NOT NULL,
    value_numeric FLOAT NULL,
    value_text NVARCHAR(512) NULL,
    unit NVARCHAR(32) NULL,
    reason NVARCHAR(32) NOT NULL,
    related_event_id BIGINT NULL,
    order_id NVARCHAR(128) NULL,
    workpiece_id NVARCHAR(128) NULL,
    payload_json NVARCHAR(MAX) NOT NULL,
    dedup_key NVARCHAR(512) NOT NULL,
    created_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_sensor_snapshot_created_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_sensor_snapshot_dedup_key UNIQUE (dedup_key),
    CONSTRAINT CK_sensor_snapshot_reason CHECK (reason IN (N'EVENT', N'INTERVAL', N'THRESHOLD')),
    CONSTRAINT FK_sensor_snapshot_related_event
      FOREIGN KEY (related_event_id) REFERENCES dbo.shopfloor_event (id) ON DELETE SET NULL
  );
END
GO

IF OBJECT_ID(N'dbo.mqtt_raw_message', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.mqtt_raw_message (
    id BIGINT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_mqtt_raw_message PRIMARY KEY,
    received_at DATETIMEOFFSET NOT NULL,
    topic NVARCHAR(512) NOT NULL,
    qos SMALLINT NULL,
    retain BIT NULL,
    payload_json NVARCHAR(MAX) NULL,
    payload_text NVARCHAR(MAX) NULL,
    persisted_reason NVARCHAR(64) NULL,
    payload_hash NVARCHAR(128) NOT NULL,
    dedup_key NVARCHAR(512) NOT NULL,
    created_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_mqtt_raw_message_created_at DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT UQ_mqtt_raw_message_dedup_key UNIQUE (dedup_key)
  );
END
GO
