export interface ServiceConfig {
  mqtt: {
    host: string;
    port: number;
    username?: string;
    password?: string;
    clientId: string;
  };
  mssql: {
    host: string;
    port: number;
    db: string;
    user: string;
    password: string;
    encrypt: boolean;
    trustServerCertificate: boolean;
  };
  runtime: {
    mode: 'live' | 'replay';
    rawRetentionDays: number;
    sensorIntervalSeconds: number;
    sensorIdleIntervalSeconds: number;
    enableRawMessages: boolean;
    enableCameraTopic: boolean;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
  queryApi: {
    enabled: boolean;
    port: number;
    corsOrigin: string;
  };
}

function asNumber(value: string | undefined, fallback: number): number {
  if (value === undefined || value.trim() === '') {
    return fallback;
  }
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
    mssql: {
      host: process.env.MSSQL_HOST ?? 'localhost',
      port: asNumber(process.env.MSSQL_PORT, 1433),
      db: process.env.MSSQL_DB ?? 'osf_edge',
      user: process.env.MSSQL_USER ?? 'osf_edge',
      password: process.env.MSSQL_PASSWORD ?? process.env.MSSQL_SA_PASSWORD ?? 'Osf_Edge_Dev1!',
      encrypt: asBoolean(process.env.MSSQL_ENCRYPT, false),
      trustServerCertificate: asBoolean(process.env.MSSQL_TRUST_SERVER_CERTIFICATE, true),
    },
    runtime: {
      mode: asMode(process.env.PERSISTENCE_MODE),
      rawRetentionDays: asNumber(process.env.RAW_RETENTION_DAYS, 14),
      sensorIntervalSeconds: asNumber(process.env.SENSOR_INTERVAL_SECONDS, 5),
      sensorIdleIntervalSeconds: asNumber(process.env.SENSOR_IDLE_INTERVAL_SECONDS, 60),
      enableRawMessages: asBoolean(process.env.ENABLE_RAW_MESSAGES, true),
      enableCameraTopic: asBoolean(process.env.ENABLE_CAMERA_TOPIC, false),
      logLevel: (process.env.LOG_LEVEL as ServiceConfig['runtime']['logLevel']) ?? 'info',
    },
    queryApi: {
      enabled: asBoolean(process.env.QUERY_API_ENABLED, true),
      port: asNumber(process.env.QUERY_API_PORT, 3081),
      corsOrigin: process.env.QUERY_API_CORS_ORIGIN?.trim() || '*',
    },
  };
}
