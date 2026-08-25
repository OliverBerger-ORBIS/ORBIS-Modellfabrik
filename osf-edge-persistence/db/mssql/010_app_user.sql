-- App login/user for Persistence + Grafana (not sa).
-- Idempotent for principals/roles. Password set only when login is created
-- (or when sqlcmd -v OSF_EDGE_RESET_PASSWORD=1).
--
--   bash scripts/mssql-create-app-user.sh
--   bash scripts/mssql-create-app-user.sh --host .201   # see script help
--
-- Rights: db_datareader + db_datawriter + EXECUTE on schema dbo.

IF DB_ID(N'osf_edge') IS NULL
BEGIN
  CREATE DATABASE osf_edge;
END
GO

USE master;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'osf_edge')
BEGIN
  CREATE LOGIN osf_edge WITH PASSWORD = '$(OSF_EDGE_PASSWORD)', CHECK_POLICY = ON, CHECK_EXPIRATION = OFF;
END
ELSE IF '$(OSF_EDGE_RESET_PASSWORD)' = '1'
BEGIN
  ALTER LOGIN osf_edge WITH PASSWORD = '$(OSF_EDGE_PASSWORD)';
END
GO

USE osf_edge;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'osf_edge')
BEGIN
  CREATE USER osf_edge FOR LOGIN osf_edge;
END
GO

IF IS_ROLEMEMBER(N'db_datareader', N'osf_edge') <> 1
  ALTER ROLE db_datareader ADD MEMBER osf_edge;
GO
IF IS_ROLEMEMBER(N'db_datawriter', N'osf_edge') <> 1
  ALTER ROLE db_datawriter ADD MEMBER osf_edge;
GO

GRANT EXECUTE ON SCHEMA::dbo TO osf_edge;
GO
