-- Create OSF edge database (idempotent).
-- Run against master. Application tables live in osf_edge.
IF DB_ID(N'osf_edge') IS NULL
BEGIN
  CREATE DATABASE osf_edge;
END
GO
