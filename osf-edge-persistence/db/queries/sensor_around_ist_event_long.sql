-- LEGACY (Postgres). Active DB is MSSQL table env_sensor_snapshot.
-- Not executed by current tooling; keep until T-SQL port.
-- Long format: one row per Ist event × sensor metric (as-of).
-- Same join rules as sensor_around_ist_event.sql.

WITH params AS (
  SELECT
    :window_seconds::int AS window_seconds,
    :grace_seconds::int AS grace_seconds,
    :lookback_hours::int AS lookback_hours,
    :'nfc_regex' AS nfc_regex,
    :row_limit::int AS row_limit,
    :anchors_only::int AS anchors_only
),
ist AS (
  SELECT
    e.id,
    e.ts,
    e.workpiece_id,
    e.workpiece_type,
    e.action,
    e.order_id,
    CASE
      WHEN e.topic LIKE 'fts/%' OR e.module_type = 'FTS' THEN
        CASE e.payload_json->>'lastNodeId'
          WHEN 'SVR4H73275' THEN 'DPS'
          WHEN 'SVR3QA0022' THEN 'HBW'
          WHEN 'SVR4H76449' THEN 'DRILL'
          WHEN 'SVR3QA2098' THEN 'MILL'
          WHEN 'SVR4H76530' THEN 'AIQS'
          ELSE 'FTS'
        END
      WHEN e.module_serial = 'SVR4H73275' OR e.module_type = 'DPS' THEN 'DPS'
      WHEN e.module_serial = 'SVR3QA0022' OR e.module_type = 'HBW' THEN 'HBW'
      WHEN e.module_serial = 'SVR4H76449' OR e.module_type = 'DRILL' THEN 'DRILL'
      WHEN e.module_serial = 'SVR3QA2098' OR e.module_type = 'MILL' THEN 'MILL'
      WHEN e.module_serial = 'SVR4H76530' OR e.module_type IN ('AIQS', 'QUALITY') THEN 'AIQS'
      ELSE COALESCE(e.module_type, '—')
    END AS station
  FROM shopfloor_event e
  CROSS JOIN params p
  WHERE e.workpiece_id IS NOT NULL
    AND (p.lookback_hours = 0 OR e.ts >= NOW() - make_interval(hours => p.lookback_hours))
    AND e.action_state = 'FINISHED'
    AND (
      e.topic LIKE 'module/%'
      OR e.topic LIKE 'fts/%'
      OR (e.topic = 'ccu/order/completed' AND e.action IN ('MANUFACTURE', 'completed'))
    )
    AND e.workpiece_id ~ p.nfc_regex
),
ist_f AS (
  SELECT i.*, po.order_type
  FROM ist i
  LEFT JOIN shopfloor_order po ON po.order_id = i.order_id
  CROSS JOIN params p
  WHERE p.anchors_only = 0
    OR CASE
      WHEN COALESCE(po.order_type, 'PRODUCTION') IN ('PRODUCTION', 'PROD') THEN
        (
          (i.station IN ('DRILL', 'MILL', 'AIQS') AND i.action IN ('DOCK', 'CHECK_QUALITY'))
          OR (i.station IN ('HBW', 'DPS') AND i.action IN ('PICK', 'DROP'))
        )
      WHEN po.order_type = 'STORAGE' THEN
        (
          (i.station = 'DPS' AND i.action = 'DROP')
          OR (i.station = 'HBW' AND i.action = 'PICK')
        )
      ELSE FALSE
    END
)
SELECT
  e.ts AS event_ts,
  e.workpiece_id AS nfc,
  e.workpiece_type AS color,
  e.station,
  e.action,
  s.source,
  s.station_id AS sensor_device,
  s.sensor_type,
  s.metric_name,
  s.value_numeric,
  s.value_text,
  s.unit,
  s.ts AS sensor_ts,
  EXTRACT(EPOCH FROM (e.ts - s.ts))::int AS lag_s
FROM ist_f e
CROSS JOIN params p
INNER JOIN LATERAL (
  SELECT DISTINCT ON (sn.source, sn.station_id, sn.sensor_type, sn.metric_name)
    sn.source,
    sn.station_id,
    sn.sensor_type,
    sn.metric_name,
    sn.value_numeric,
    sn.value_text,
    sn.unit,
    sn.ts
  FROM env_sensor_snapshot sn
  WHERE sn.ts <= e.ts + make_interval(secs => p.grace_seconds)
    AND sn.ts >= e.ts - make_interval(secs => p.window_seconds)
  ORDER BY sn.source, sn.station_id, sn.sensor_type, sn.metric_name, sn.ts DESC
) s ON TRUE
ORDER BY e.ts, e.workpiece_id, s.source, s.sensor_type, s.metric_name
LIMIT (SELECT row_limit FROM params);
