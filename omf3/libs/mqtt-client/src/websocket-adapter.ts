import { BehaviorSubject, Observable, Subject } from 'rxjs';
import mqtt from 'mqtt';
import type { IClientOptions, MqttClient } from 'mqtt';

import {
  ConnState,
  MqttAdapter,
  MqttMessage,
  PublishOptions,
  SubscribeOptions,
} from './index';

/**
 * WebSocket-based MQTT adapter for browser environments using mqtt.js.
 * Connects to MQTT brokers via WebSocket protocol (ws:// or wss://).
 */
export class WebSocketMqttAdapter implements MqttAdapter {
  private readonly stateSubject = new BehaviorSubject<ConnState>('disconnected');
  private readonly messagesSubject = new Subject<MqttMessage>();
  private client: MqttClient | null = null;

  readonly connectionState$ = this.stateSubject.asObservable();
  readonly messages$ = this.messagesSubject.asObservable();

  async connect(wsUrl: string, options?: Record<string, unknown>): Promise<void> {
    if (this.client?.connected) {
      return;
    }

    this.transition('connecting');

    return new Promise<void>((resolve, reject) => {
      try {
        // Build WebSocket URL
        let url = wsUrl;
        if (!url.startsWith('ws://') && !url.startsWith('wss://')) {
          url = `ws://${url}`;
        }

        console.log('[WebSocketMqttAdapter] Attempting to connect to:', url);

        // Prepare MQTT.js connection options
        const mqttOptions: IClientOptions = {
          connectTimeout: 10000,
          reconnectPeriod: 0, // Disable auto-reconnect, we handle it ourselves
        };

        // Add authentication if provided
        if (options?.['username']) {
          mqttOptions.username = String(options['username']);
          console.log('[WebSocketMqttAdapter] Using authentication with username:', mqttOptions.username);
        }
        if (options?.['password']) {
          mqttOptions.password = String(options['password']);
        }

        // Create MQTT client
        this.client = mqtt.connect(url, mqttOptions);
        console.log('[WebSocketMqttAdapter] MQTT client created, waiting for connection...');

        // Set up event handlers
        this.client.on('connect', () => {
          console.log('[WebSocketMqttAdapter] Successfully connected!');
          this.transition('connected');
          resolve();
        });

        this.client.on('error', (error) => {
          console.error('[WebSocketMqttAdapter] Connection error:', error);
          this.handleConnectionError(error.message || 'Connection failed');
          reject(error);
        });

        this.client.on('close', () => {
          console.log('[WebSocketMqttAdapter] Connection closed');
          this.transition('disconnected');
        });

        this.client.on('message', (topic, payload) => {
          this.messagesSubject.next({
            topic,
            payload: payload.toString(),
            timestamp: new Date().toISOString(),
          });
        });

        // Set a timeout for connection
        const timeout = setTimeout(() => {
          if (this.client && !this.client.connected) {
            this.client.end(true);
            this.handleConnectionError('Connection timeout');
            reject(new Error('Connection timeout'));
          }
        }, 10000);

        this.client.on('connect', () => {
          clearTimeout(timeout);
        });

      } catch (error) {
        this.handleConnectionError('Failed to create MQTT client');
        reject(error);
      }
    });
  }

  async disconnect(): Promise<void> {
    if (this.client) {
      return new Promise<void>((resolve) => {
        this.client!.end(false, {}, () => {
          this.client = null;
          this.transition('disconnected');
          resolve();
        });
      });
    }
    this.transition('disconnected');
  }

  async publish(topic: string, payload: unknown, options?: PublishOptions): Promise<void> {
    if (!this.client?.connected) {
      throw new Error('Not connected');
    }

    return new Promise<void>((resolve, reject) => {
      this.client!.publish(
        topic,
        typeof payload === 'string' ? payload : JSON.stringify(payload),
        {
          qos: options?.qos ?? 0,
          retain: options?.retain ?? false,
        },
        (error) => {
          if (error) {
            reject(error);
          } else {
            resolve();
          }
        }
      );
    });
  }

  async subscribe(topic: string, options?: SubscribeOptions): Promise<void> {
    if (!this.client?.connected) {
      throw new Error('Not connected');
    }

    return new Promise<void>((resolve, reject) => {
      this.client!.subscribe(
        topic,
        {
          qos: options?.qos ?? 0,
        },
        (error) => {
          if (error) {
            reject(error);
          } else {
            resolve();
          }
        }
      );
    });
  }

  private transition(next: ConnState) {
    this.stateSubject.next(next);
  }

  private handleConnectionError(message: string) {
    console.error('[WebSocketMqttAdapter]', message);
    this.transition('error');
  }
}
