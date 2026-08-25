-- Local replay idempotency: sessions already ingested are skipped on re-run.
-- Cleared by scripts/reset-replay-db.sh (full truncate). Live (.201) does not use this.
USE osf_edge;
GO

IF OBJECT_ID(N'dbo.replay_session_ingest', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.replay_session_ingest (
    session_id NVARCHAR(256) NOT NULL CONSTRAINT PK_replay_session_ingest PRIMARY KEY,
    ingested_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_replay_session_ingest_ingested_at DEFAULT (SYSUTCDATETIME())
  );
END
GO
