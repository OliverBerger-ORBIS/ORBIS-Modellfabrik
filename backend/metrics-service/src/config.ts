/**
 * Configuration management via environment variables
 * Defaults are set for local development on localhost
 */

export interface Config {
  mqtt: {
    url: string;
    clientId: string;
  };
  influx: {
    url: string;
    token: string;
    org: string;
    bucket: string;
  };
}

/**
 * Load configuration from environment variables with sensible defaults
 */
export function loadConfig(): Config {
  return {
    mqtt: {
      // MQTT broker URL - default to localhost, easily switchable to trade fair IP
      url: process.env.MQTT_URL || 'mqtt://localhost:1883',
      clientId: process.env.MQTT_CLIENT_ID || 'omf-metrics-service',
    },
    influx: {
      // InfluxDB connection settings
      url: process.env.INFLUX_URL || 'http://localhost:8086',
      // Token should be set via environment variable for security
      token: process.env.INFLUX_TOKEN || 'dev-token-please-change',
      org: process.env.INFLUX_ORG || 'orbis',
      bucket: process.env.INFLUX_BUCKET || 'omf-metrics',
    },
  };
}
