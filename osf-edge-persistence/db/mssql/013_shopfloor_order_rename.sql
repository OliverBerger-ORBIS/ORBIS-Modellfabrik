-- Rename legacy production_order → shopfloor_order (STORAGE + PRODUCTION via order_type).
USE osf_edge;
GO

IF OBJECT_ID(N'dbo.production_order', N'U') IS NOT NULL
   AND OBJECT_ID(N'dbo.shopfloor_order', N'U') IS NULL
BEGIN
  EXEC sp_rename N'dbo.production_order', N'shopfloor_order';
END
GO

IF OBJECT_ID(N'dbo.shopfloor_order', N'U') IS NOT NULL
BEGIN
  IF EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = N'PK_production_order' AND parent_object_id = OBJECT_ID(N'dbo.shopfloor_order'))
    EXEC sp_rename N'dbo.PK_production_order', N'PK_shopfloor_order', N'OBJECT';
  IF EXISTS (SELECT 1 FROM sys.default_constraints WHERE name = N'DF_production_order_updated_at' AND parent_object_id = OBJECT_ID(N'dbo.shopfloor_order'))
    EXEC sp_rename N'dbo.DF_production_order_updated_at', N'DF_shopfloor_order_updated_at', N'OBJECT';
END
GO

IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_order_state' AND object_id = OBJECT_ID(N'dbo.shopfloor_order'))
  EXEC sp_rename N'dbo.shopfloor_order.idx_production_order_state', N'idx_shopfloor_order_state', N'INDEX';
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_production_order_stopped_at' AND object_id = OBJECT_ID(N'dbo.shopfloor_order'))
  EXEC sp_rename N'dbo.shopfloor_order.idx_production_order_stopped_at', N'idx_shopfloor_order_stopped_at', N'INDEX';
GO

-- If both somehow exist, prefer shopfloor_order and drop legacy empty/duplicate.
IF OBJECT_ID(N'dbo.production_order', N'U') IS NOT NULL
   AND OBJECT_ID(N'dbo.shopfloor_order', N'U') IS NOT NULL
BEGIN
  DROP TABLE dbo.production_order;
END
GO
