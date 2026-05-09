SELECT create_hypertable('sensor_snapshot', by_range('ts'), if_not_exists => TRUE);
SELECT create_hypertable('mqtt_raw_message', by_range('received_at'), if_not_exists => TRUE);

ALTER TABLE sensor_snapshot SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'source,station_id,sensor_type,metric_name'
);

ALTER TABLE mqtt_raw_message SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'topic'
);

SELECT add_compression_policy('sensor_snapshot', INTERVAL '7 days', if_not_exists => TRUE);
SELECT add_compression_policy('mqtt_raw_message', INTERVAL '3 days', if_not_exists => TRUE);

