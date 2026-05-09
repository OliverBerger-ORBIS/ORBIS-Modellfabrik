-- Default retention policies.
-- RAW_RETENTION_DAYS can be additionally enforced by application-side cleanup job.
SELECT add_retention_policy('mqtt_raw_message', INTERVAL '14 days', if_not_exists => TRUE);

-- Keep normalized sensor history longer for trend analysis.
SELECT add_retention_policy('sensor_snapshot', INTERVAL '365 days', if_not_exists => TRUE);

