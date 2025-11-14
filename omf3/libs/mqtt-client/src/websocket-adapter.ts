import { BehaviorSubject, Observable, Subject } from 'rxjs';

import {
  ConnState,
  MqttAdapter,
  MqttMessage,
  PublishOptions,
  SubscribeOptions,
} from './index';

/**
 * WebSocket-based MQTT adapter for browser environments.
 * Connects to MQTT brokers via WebSocket protocol (ws:// or wss://).
 */
export class WebSocketMqttAdapter implements MqttAdapter {
  private readonly stateSubject = new BehaviorSubject<ConnState>('disconnected');
  private readonly messagesSubject = new Subject<MqttMessage>();
  private socket: WebSocket | null = null;
  private readonly subscriptions = new Set<string>();
  private reconnectTimeout?: ReturnType<typeof setTimeout>;

  readonly connectionState$ = this.stateSubject.asObservable();
  readonly messages$ = this.messagesSubject.asObservable();

  async connect(wsUrl: string, options?: Record<string, unknown>): Promise<void> {
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
      return;
    }

    this.transition('connecting');

    return new Promise<void>((resolve, reject) => {
      try {
        // Build WebSocket URL with optional auth parameters
        let url = wsUrl;
        if (options?.['username'] && options?.['password']) {
          const urlObj = new URL(url.startsWith('ws') ? url : `ws://${url}`);
          urlObj.searchParams.set('username', String(options['username']));
          urlObj.searchParams.set('password', String(options['password']));
          url = urlObj.toString();
        } else if (!url.startsWith('ws')) {
          url = `ws://${url}`;
        }

        this.socket = new WebSocket(url, ['mqtt']);

        const timeout = setTimeout(() => {
          this.handleConnectionError('Connection timeout');
          reject(new Error('Connection timeout'));
        }, 10000);

        this.socket.onopen = () => {
          clearTimeout(timeout);
          this.transition('connected');
          resolve();
        };

        this.socket.onerror = (error) => {
          clearTimeout(timeout);
          console.error('[WebSocketMqttAdapter] Connection error:', error);
          this.handleConnectionError('WebSocket error');
          reject(error);
        };

        this.socket.onclose = () => {
          this.transition('disconnected');
        };

        this.socket.onmessage = (event) => {
          this.handleMessage(event);
        };
      } catch (error) {
        this.handleConnectionError('Failed to create WebSocket');
        reject(error);
      }
    });
  }

  async disconnect(): Promise<void> {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = undefined;
    }

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    this.subscriptions.clear();
    this.transition('disconnected');
  }

  async publish(topic: string, payload: unknown, options?: PublishOptions): Promise<void> {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('Not connected');
    }

    // Create a simple MQTT-like message format
    const message = {
      type: 'publish',
      topic,
      payload,
      qos: options?.qos ?? 0,
      retain: options?.retain ?? false,
    };

    this.socket.send(JSON.stringify(message));
  }

  async subscribe(topic: string, options?: SubscribeOptions): Promise<void> {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('Not connected');
    }

    this.subscriptions.add(topic);

    const message = {
      type: 'subscribe',
      topic,
      qos: options?.qos ?? 0,
    };

    this.socket.send(JSON.stringify(message));
  }

  private transition(next: ConnState) {
    this.stateSubject.next(next);
  }

  private handleConnectionError(message: string) {
    console.error('[WebSocketMqttAdapter]', message);
    this.transition('error');
  }

  private handleMessage(event: MessageEvent) {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'message' && data.topic) {
        this.messagesSubject.next({
          topic: data.topic,
          payload: data.payload,
          timestamp: data.timestamp || new Date().toISOString(),
          options: {
            qos: data.qos,
            retain: data.retain,
          },
        });
      }
    } catch (error) {
      console.warn('[WebSocketMqttAdapter] Failed to parse message:', error);
    }
  }
}
