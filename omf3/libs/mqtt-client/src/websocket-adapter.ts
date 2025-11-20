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

// Extend Window interface to include diagnostic flag
declare global {
  interface Window {
    __MQTT_RAW_WEBSOCKET_DIAGNOSTIC?: boolean;
  }
}

/**
 * WebSocket-based MQTT adapter for browser environments using mqtt.js.
 * Connects to MQTT brokers via WebSocket protocol (ws:// or wss://).
 * 
 * Diagnostic Mode:
 * Set window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true before loading the app
 * to enable detailed connection diagnostics including raw WebSocket testing.
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

    // Check if diagnostic mode is enabled
    const diagnosticMode = typeof window !== 'undefined' && window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC;

    return new Promise<void>((resolve, reject) => {
      try {
        // Build WebSocket URL
        let url = wsUrl;
        if (!url.startsWith('ws://') && !url.startsWith('wss://')) {
          url = `ws://${url}`;
        }

        console.log('[WebSocketMqttAdapter] Attempting to connect to:', url);
        console.log('[WebSocketMqttAdapter] Original wsUrl parameter:', wsUrl);

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

        // Diagnostic mode: Log detailed connection info
        if (diagnosticMode) {
          console.log('[WebSocketMqttAdapter] === DIAGNOSTIC MODE ENABLED ===');
          console.log('[WebSocketMqttAdapter] Final mqtt.connect URL:', url);
          console.log('[WebSocketMqttAdapter] mqtt.connect options:', JSON.stringify({
            ...mqttOptions,
            password: mqttOptions.password ? '***' : undefined
          }, null, 2));
          console.log('[WebSocketMqttAdapter] Browser:', navigator.userAgent);
          console.log('[WebSocketMqttAdapter] Current page protocol:', window.location.protocol);
          console.log('[WebSocketMqttAdapter] Current page host:', window.location.host);
          console.log('[WebSocketMqttAdapter] Timestamp:', new Date().toISOString());

          // Test raw WebSocket connection first in diagnostic mode
          this.testRawWebSocket(url).then((result) => {
            console.log('[WebSocketMqttAdapter] Raw WebSocket test result:', result);
          }).catch((error) => {
            console.error('[WebSocketMqttAdapter] Raw WebSocket test failed:', error);
          });
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
          if (diagnosticMode) {
            console.error('[WebSocketMqttAdapter] Error details:', {
              message: error.message,
              stack: error.stack,
              name: error.name
            });
          }
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
            console.error('[WebSocketMqttAdapter] Connection timeout');
            this.handleConnectionError('Connection timeout');
            reject(new Error('Connection timeout'));
          }
        }, 10000);

        this.client.on('connect', () => {
          clearTimeout(timeout);
        });

      } catch (error) {
        console.error('[WebSocketMqttAdapter] Failed to create MQTT client:', error);
        this.handleConnectionError('Failed to create MQTT client');
        reject(error);
      }
    });
  }

  /**
   * Test raw WebSocket connection in diagnostic mode
   * This helps identify if the issue is with the WebSocket connection itself
   * or with MQTT.js library behavior
   */
  private testRawWebSocket(url: string): Promise<{ success: boolean; details: string }> {
    return new Promise((resolve) => {
      console.log('[WebSocketMqttAdapter] Testing raw WebSocket connection to:', url);
      
      try {
        const ws = new WebSocket(url);
        const startTime = Date.now();

        const cleanup = () => {
          ws.onopen = null;
          ws.onerror = null;
          ws.onclose = null;
        };

        const timeout = setTimeout(() => {
          cleanup();
          ws.close();
          resolve({
            success: false,
            details: `Timeout after ${Date.now() - startTime}ms`
          });
        }, 5000);

        ws.onopen = () => {
          clearTimeout(timeout);
          cleanup();
          const duration = Date.now() - startTime;
          console.log('[WebSocketMqttAdapter] Raw WebSocket opened successfully in', duration, 'ms');
          ws.close();
          resolve({
            success: true,
            details: `Connected in ${duration}ms`
          });
        };

        ws.onerror = (event) => {
          clearTimeout(timeout);
          cleanup();
          console.error('[WebSocketMqttAdapter] Raw WebSocket error:', event);
          resolve({
            success: false,
            details: 'WebSocket error event fired'
          });
        };

        ws.onclose = (event) => {
          clearTimeout(timeout);
          cleanup();
          console.log('[WebSocketMqttAdapter] Raw WebSocket closed:', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
          });
          if (!event.wasClean) {
            resolve({
              success: false,
              details: `Closed uncleanly: code ${event.code}, reason: ${event.reason || 'none'}`
            });
          }
        };

      } catch (error) {
        console.error('[WebSocketMqttAdapter] Raw WebSocket test exception:', error);
        resolve({
          success: false,
          details: `Exception: ${error instanceof Error ? error.message : String(error)}`
        });
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
