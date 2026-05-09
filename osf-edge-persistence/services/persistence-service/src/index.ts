import mqtt from 'mqtt';
import { loadConfig } from './config';
import { PersistenceDb } from './db';
import { Logger } from './logger';
import { normalizeMessage } from './normalizer';
import { createSensorPolicyState } from './sensorPolicy';
import { SUBSCRIBE_TOPICS } from './topics';

async function main(): Promise<void> {
  const config = loadConfig();
  const logger = new Logger(config.runtime.logLevel);
  const db = new PersistenceDb(config, logger);
  const sensorPolicyState = createSensorPolicyState();

  logger.info('Starting OSF edge persistence service', {
    mode: config.runtime.mode,
    mqttHost: config.mqtt.host,
    mqttPort: config.mqtt.port,
    pgHost: config.postgres.host,
    pgDb: config.postgres.db,
    rawEnabled: config.runtime.enableRawMessages,
    intervalSeconds: config.runtime.sensorIntervalSeconds,
  });

  await db.connect();

  const cleanupTimer = setInterval(() => {
    db.cleanupRawRetention().catch((error) => logger.error('Raw retention cleanup failed', error));
  }, 60 * 60 * 1000);

  const mqttUrl = `mqtt://${config.mqtt.host}:${config.mqtt.port}`;
  const client = mqtt.connect(mqttUrl, {
    clientId: config.mqtt.clientId,
    username: config.mqtt.username,
    password: config.mqtt.password,
    reconnectPeriod: 5000,
    connectTimeout: 30000,
    clean: true,
  });

  client.on('connect', () => {
    logger.info('Connected to MQTT broker', { mqttUrl });
    for (const topic of SUBSCRIBE_TOPICS) {
      client.subscribe(topic, { qos: 0 }, (error) => {
        if (error) {
          logger.error('Subscribe failed', { topic, error: String(error) });
        } else {
          logger.info('Subscribed', { topic });
        }
      });
    }
  });

  client.on('message', async (topic, buffer, packet) => {
    const receivedAt = new Date();
    const payloadText = buffer.toString();
    try {
      const normalized = normalizeMessage({
        config,
        topic,
        payloadText,
        qos: packet.qos ?? 0,
        retain: packet.retain ?? false,
        receivedAt,
        sensorPolicyState,
      });
      if (!normalized) {
        return;
      }
      await db.persist(normalized);
      logger.debug('Persisted MQTT message', {
        topic,
        events: normalized.shopfloorEvents.length,
        sensors: normalized.sensorSnapshots.length,
        orders: normalized.productionOrders.length,
      });
    } catch (error) {
      logger.error('Message processing failed', {
        topic,
        error: String(error),
      });
    }
  });

  client.on('error', (error) => logger.error('MQTT error', String(error)));
  client.on('offline', () => logger.warn('MQTT client offline'));
  client.on('reconnect', () => logger.info('MQTT reconnecting'));

  const shutdown = async (signal: string) => {
    logger.info('Shutting down', { signal });
    clearInterval(cleanupTimer);
    try {
      client.end(true);
      await db.close();
      process.exit(0);
    } catch (error) {
      logger.error('Shutdown failed', String(error));
      process.exit(1);
    }
  };

  process.on('SIGINT', () => void shutdown('SIGINT'));
  process.on('SIGTERM', () => void shutdown('SIGTERM'));
}

main().catch((error) => {
  console.error('Fatal startup error', error);
  process.exit(1);
});
