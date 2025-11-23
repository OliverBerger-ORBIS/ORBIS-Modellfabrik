/**
 * OMF Metrics Service
 * 
 * MQTT to InfluxDB bridge for ORBIS Modellfabrik metrics collection
 * Subscribes to MQTT topics from the factory floor and writes time-series data to InfluxDB
 */

import { loadConfig } from './config';
import { logger } from './logger';
import { InfluxWriter } from './influxWriter';
import { OmfMqttClient } from './mqttClient';

/**
 * Main entry point
 */
async function main() {
  logger.info('=== OMF Metrics Service Starting ===');

  // Load configuration
  const config = loadConfig();
  logger.info('Configuration loaded', {
    mqttUrl: config.mqtt.url,
    influxUrl: config.influx.url,
    influxOrg: config.influx.org,
    influxBucket: config.influx.bucket,
  });

  // Initialize InfluxDB writer
  const influxWriter = new InfluxWriter(config);
  logger.info('InfluxDB writer initialized');

  // Initialize MQTT client
  const mqttClient = new OmfMqttClient(config, influxWriter);
  logger.info('MQTT client initialized');

  // Setup graceful shutdown
  const shutdown = async (signal: string) => {
    logger.info(`Received ${signal}, shutting down gracefully...`);
    
    try {
      await mqttClient.close();
      await influxWriter.close();
      logger.info('Shutdown complete');
      process.exit(0);
    } catch (error) {
      logger.error('Error during shutdown', error);
      process.exit(1);
    }
  };

  // Handle shutdown signals
  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  // Handle uncaught errors
  process.on('uncaughtException', (error) => {
    logger.error('Uncaught exception', error);
    shutdown('uncaughtException');
  });

  process.on('unhandledRejection', (reason) => {
    logger.error('Unhandled rejection', reason);
    shutdown('unhandledRejection');
  });

  logger.info('=== OMF Metrics Service Running ===');
  logger.info('Press Ctrl+C to stop');
}

// Start the service
main().catch((error) => {
  logger.error('Fatal error starting service', error);
  process.exit(1);
});
