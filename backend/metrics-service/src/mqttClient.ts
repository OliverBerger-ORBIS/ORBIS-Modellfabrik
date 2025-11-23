/**
 * MQTT Client for subscribing to OMF topics and processing messages
 */

import mqtt, { MqttClient } from 'mqtt';
import { Config } from './config';
import { logger } from './logger';
import { InfluxWriter } from './influxWriter';

// Import handlers
import { handleOrderCompleted } from './handlers/orderCompletedHandler';
import { handleFtsState } from './handlers/ftsStateHandler';
import { handleFtsConnection } from './handlers/ftsConnectionHandler';
import { handleFtsOrder } from './handlers/ftsOrderHandler';
import { handleFtsInstantAction } from './handlers/ftsInstantActionHandler';
import { handleModuleState } from './handlers/moduleStateHandler';
import { handleEnvironment } from './handlers/environmentHandler';
import { handleStock } from './handlers/stockHandler';

/**
 * MQTT topics to subscribe to
 */
const TOPICS = [
  // CCU topics
  'ccu/order/completed',
  'ccu/order/active',
  
  // FTS topics (generic subscription with wildcard)
  'fts/v1/ff/+/state',
  'fts/v1/ff/+/connection',
  'fts/v1/ff/+/factsheet',
  'fts/v1/ff/+/order',
  'fts/v1/ff/+/instantAction',
  
  // Module topics (generic subscription with wildcard)
  'module/v1/ff/+/state',
  'module/v1/ff/NodeRed/+/state',
  
  // TXT topics (environment and stock)
  '/j1/txt/1/i/bme680',
  '/j1/txt/1/f/i/stock',
];

export class OmfMqttClient {
  private client: MqttClient;
  private influxWriter: InfluxWriter;
  private config: Config;

  constructor(config: Config, influxWriter: InfluxWriter) {
    this.config = config;
    this.influxWriter = influxWriter;

    // Initialize MQTT client
    this.client = mqtt.connect(config.mqtt.url, {
      clientId: config.mqtt.clientId,
      clean: true,
      reconnectPeriod: 5000, // Auto-reconnect every 5 seconds
      connectTimeout: 30000,
    });

    this.setupEventHandlers();
  }

  /**
   * Setup MQTT event handlers
   */
  private setupEventHandlers(): void {
    this.client.on('connect', () => {
      logger.info(`Connected to MQTT broker at ${this.config.mqtt.url}`);
      this.subscribe();
    });

    this.client.on('message', (topic, payload) => {
      this.handleMessage(topic, payload);
    });

    this.client.on('error', (error) => {
      logger.error('MQTT client error', error);
    });

    this.client.on('reconnect', () => {
      logger.info('Reconnecting to MQTT broker...');
    });

    this.client.on('offline', () => {
      logger.warn('MQTT client is offline');
    });

    this.client.on('close', () => {
      logger.warn('MQTT connection closed');
    });
  }

  /**
   * Subscribe to all configured topics
   */
  private subscribe(): void {
    for (const topic of TOPICS) {
      this.client.subscribe(topic, { qos: 0 }, (err) => {
        if (err) {
          logger.error(`Failed to subscribe to ${topic}`, err);
        } else {
          logger.info(`Subscribed to topic: ${topic}`);
        }
      });
    }
  }

  /**
   * Handle incoming MQTT messages and route to appropriate handlers
   */
  private handleMessage(topic: string, payload: Buffer): void {
    const payloadStr = payload.toString();
    
    try {
      // Route message to appropriate handler based on topic
      let points = [];

      // CCU topics
      if (topic === 'ccu/order/completed') {
        points = handleOrderCompleted(topic, payloadStr);
      }
      // FTS topics
      else if (topic.match(/^fts\/v1\/ff\/[^/]+\/state$/)) {
        points = handleFtsState(topic, payloadStr);
      }
      else if (topic.match(/^fts\/v1\/ff\/[^/]+\/connection$/)) {
        points = handleFtsConnection(topic, payloadStr);
      }
      else if (topic.match(/^fts\/v1\/ff\/[^/]+\/order$/)) {
        points = handleFtsOrder(topic, payloadStr);
      }
      else if (topic.match(/^fts\/v1\/ff\/[^/]+\/instantAction$/)) {
        points = handleFtsInstantAction(topic, payloadStr);
      }
      else if (topic.match(/^fts\/v1\/ff\/[^/]+\/factsheet$/)) {
        // Factsheets are informational, could be stored but not as time-series
        logger.debug(`Received FTS factsheet on ${topic}`);
        return;
      }
      // Module topics
      else if (topic.match(/^module\/v1\/ff\/(NodeRed\/)?[^/]+\/state$/)) {
        points = handleModuleState(topic, payloadStr);
      }
      // Environment topics
      else if (topic === '/j1/txt/1/i/bme680') {
        points = handleEnvironment(topic, payloadStr);
      }
      // Stock topics
      else if (topic === '/j1/txt/1/f/i/stock') {
        points = handleStock(topic, payloadStr);
      }
      // CCU order active - could be handled similarly to completed
      else if (topic === 'ccu/order/active') {
        // Log but don't process yet - could be added if needed
        logger.debug(`Received active order on ${topic}`);
        return;
      }
      else {
        logger.warn(`No handler for topic: ${topic}`);
        return;
      }

      // Write points to InfluxDB
      if (points.length > 0) {
        this.influxWriter.writePoints(points);
        logger.info(`Processed ${points.length} point(s) from topic: ${topic}`);
      }
    } catch (error) {
      logger.error(`Error processing message from ${topic}`, error);
    }
  }

  /**
   * Gracefully close the MQTT client
   */
  async close(): Promise<void> {
    return new Promise((resolve) => {
      this.client.end(false, {}, () => {
        logger.info('MQTT client closed');
        resolve();
      });
    });
  }
}
