-- Environment at Ist events (query-time, no Grafana, no related_event_id write).
--
-- As-of join: latest sensor_snapshot per metric with ts <= event.ts + grace,
-- inside [event.ts - window, event.ts + grace]. Same idea as Track & Trace
-- (last known ENV at an event), not a spatial sensor-to-station map.
--
-- TXT BME680 snapshots often store only metric `iaq`; t/h live in payload_json.
-- LDR is usually absent from sensor_snapshot — last mqtt_raw_message is used.
--
-- psql variables (set by scripts/sensor-around-ist.sh, or by hand):
--   window_seconds  default 30
--   grace_seconds   default 5
--   lookback_hours  default 6     (0 = no time filter)
--   nfc_regex       default .*
--   row_limit       default 200
--   anchors_only    default 0     (1 = T&T ENV anchors only)

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
  LEFT JOIN production_order po ON po.order_id = i.order_id
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
),
nearest AS (
  SELECT DISTINCT ON (e.id, s.source, s.station_id, s.sensor_type, s.metric_name)
    e.id AS event_id,
    s.source,
    s.station_id,
    s.sensor_type,
    s.metric_name,
    s.value_numeric,
    s.value_text,
    s.ts AS sensor_ts,
    EXTRACT(EPOCH FROM (e.ts - s.ts))::int AS lag_s,
    s.payload_json
  FROM ist_f e
  CROSS JOIN params p
  INNER JOIN sensor_snapshot s
    ON s.ts <= e.ts + make_interval(secs => p.grace_seconds)
   AND s.ts >= e.ts - make_interval(secs => p.window_seconds)
  ORDER BY e.id, s.source, s.station_id, s.sensor_type, s.metric_name, s.ts DESC
)
SELECT
  e.ts AS event_ts,
  e.workpiece_id AS nfc,
  e.workpiece_type AS color,
  e.station,
  e.action,
  COALESCE(e.order_type, '') AS order_type,
  MAX(n.value_numeric) FILTER (
    WHERE n.sensor_type = 'temperature' AND n.metric_name = 'temperature'
  ) AS dht11_temp_c,
  MAX(n.value_numeric) FILTER (
    WHERE n.sensor_type = 'temperature' AND n.metric_name = 'humidity'
  ) AS dht11_rh,
  MAX(n.value_numeric) FILTER (
    WHERE n.sensor_type = 'vibration' AND n.station_id = 'mpu6050-1' AND n.metric_name = 'magnitude'
  ) AS mpu_magnitude,
  MAX(n.value_text) FILTER (
    WHERE n.sensor_type = 'vibration' AND n.station_id = 'mpu6050-1' AND n.metric_name = 'vibrationDetected'
  ) AS mpu_detected,
  MAX(n.value_text) FILTER (
    WHERE n.sensor_type = 'flame' AND n.metric_name = 'flameDetected'
  ) AS flame_detected,
  MAX(n.value_numeric) FILTER (
    WHERE n.sensor_type = 'gas' AND n.metric_name = 'gasLevel'
  ) AS gas_level,
  MAX(n.value_numeric) FILTER (
    WHERE n.sensor_type = 'bme680' AND n.metric_name = 'iaq'
  ) AS bme_iaq,
  MAX((n.payload_json->>'t')::double precision) FILTER (WHERE n.sensor_type = 'bme680') AS bme_t_c,
  MAX((n.payload_json->>'h')::double precision) FILTER (WHERE n.sensor_type = 'bme680') AS bme_rh,
  (SELECT (r.payload_json->>'br')::double precision
     FROM mqtt_raw_message r, params p
    WHERE r.topic = '/j1/txt/1/i/ldr'
      AND r.received_at <= e.ts + make_interval(secs => p.grace_seconds)
      AND r.received_at >= e.ts - make_interval(secs => p.window_seconds)
    ORDER BY r.received_at DESC
    LIMIT 1) AS ldr_br,
  MAX(n.lag_s) AS max_sensor_lag_s
FROM ist_f e
LEFT JOIN nearest n ON n.event_id = e.id
CROSS JOIN params p
GROUP BY e.id, e.ts, e.workpiece_id, e.workpiece_type, e.station, e.action, e.order_type
ORDER BY e.ts, e.workpiece_id
LIMIT (SELECT row_limit FROM params);
