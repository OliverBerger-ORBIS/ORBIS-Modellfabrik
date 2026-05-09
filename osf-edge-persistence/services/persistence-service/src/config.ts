export interface ServiceConfig {
  mqtt: {
    host: string;
    port: number;
    username?: string;
    password?: string;
    clientId: string;
  };
  postgres: {
    host: string;
    port: number;
    db: string;
    user: string;
    password: string;
  };
  runtime: {
    mode: 'live' | 'replay';
    rawRetentionDays: number;
    sensorIntervalSeconds: number;
    enableRawMessages: boolean;
    enableCameraTopic: boolean;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
}

function asNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function asBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }
  return value.toLowerCase() === 'true';
}

function asMode(value: string | undefined): 'live' | 'replay' {
  const normalized = (value ?? '').trim().toLowerCase();
  return normalized === 'replay' ? 'replay' : 'live';
}

export function loadConfig(): ServiceConfig {
  return {
    mqtt: {
      host: process.env.MQTT_HOST ?? 'host.docker.internal',
      port: asNumber(process.env.MQTT_PORT, 1883),
      username: process.env.MQTT_USERNAME || undefined,
      password: process.env.MQTT_PASSWORD || undefined,
      clientId: process.env.MQTT_CLIENT_ID ?? 'osf-persistence-edge',
    },
    postgres: {
      host: process.env.POSTGRES_HOST ?? 'localhost',
      port: asNumber(process.env.POSTGRES_PORT, 5432),
      db: process.env.POSTGRES_DB ?? 'osf',
      user: process.env.POSTGRES_USER ?? 'osf',
      password: process.env.POSTGRES_PASSWORD ?? 'osf_dev',
    },
    runtime: {
      mode: asMode(process.env.PERSISTENCE_MODE),
      rawRetentionDays: asNumber(process.env.RAW_RETENTION_DAYS, 14),
      sensorIntervalSeconds: asNumber(process.env.SENSOR_INTERVAL_SECONDS, 3600),
      enableRawMessages: asBoolean(process.env.ENABLE_RAW_MESSAGES, true),
      enableCameraTopic: asBoolean(process.env.ENABLE_CAMERA_TOPIC, false),
      logLevel: (process.env.LOG_LEVEL as ServiceConfig['runtime']['logLevel']) ?? 'info',
    },
  };
}
