import { Injectable } from '@angular/core';
import { BehaviorSubject, interval, Subscription } from 'rxjs';
import { EnvironmentDefinition, EnvironmentService } from './environment.service';
import { createMqttClient, MockMqttAdapter, WebSocketMqttAdapter, MqttClientWrapper } from '@osf/mqtt-client';
import { MessageMonitorService } from './message-monitor.service';

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface ConnectionSettings {
  autoConnect: boolean;
  retryEnabled: boolean;
  retryIntervalMs: number;
}

const SETTINGS_STORAGE_KEY = 'OSF.connection.settings';

const DEFAULT_SETTINGS: ConnectionSettings = {
  autoConnect: true,
  retryEnabled: true,
  retryIntervalMs: 5000,
};

@Injectable({ providedIn: 'root' })
export class ConnectionService {
  private readonly stateSubject = new BehaviorSubject<ConnectionState>('disconnected');
  private readonly errorSubject = new BehaviorSubject<string | null>(null);
  private settings: ConnectionSettings = this.loadSettings();
  private retrySub?: Subscription;
  private _mqttClient?: MqttClientWrapper;
  private connectionStateSub?: Subscription;
  private messagesSub?: Subscription;
  private currentEnvironment?: EnvironmentDefinition;
  private reconnectAttempts = 0;
  private readonly RECONNECT_TIMEOUT_MS = 10000;
  private readonly MAX_RECONNECT_ATTEMPTS = 3;

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService
  ) {
    this.environmentService.environment$.subscribe((environment) => {
      const definition = this.environmentService.getDefinition(environment.key);
      if (!definition) {
        return;
      }
      this.disconnect();
      if (definition.key === 'mock') {
        this.updateState('disconnected');
        return;
      }
      if (this.settings.autoConnect) {
        this.connect(definition);
      }
    });
  }

  get state$() {
    return this.stateSubject.asObservable();
  }

  get error$() {
    return this.errorSubject.asObservable();
  }

  get currentState(): ConnectionState {
    return this.stateSubject.value;
  }

  get currentError(): string | null {
    return this.errorSubject.value;
  }

  get currentSettings(): ConnectionSettings {
    return { ...this.settings };
  }

  get mqttClient(): MqttClientWrapper | undefined {
    return this._mqttClient;
  }

  updateSettings(partial: Partial<ConnectionSettings>): void {
    this.settings = { ...this.settings, ...partial };
    localStorage?.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(this.settings));
  }

  connect(environment: EnvironmentDefinition): void {
    if (environment.key === 'mock') {
      this.updateState('disconnected');
      return;
    }

    if (this.currentState === 'connecting' || this.currentState === 'connected') {
      return;
    }

    // Store environment for potential reconnect attempts
    this.currentEnvironment = environment;

    this.updateState('connecting');
    this.errorSubject.next(null);

    // Create WebSocket MQTT client for replay/live environments
    const adapter = new WebSocketMqttAdapter();
    this._mqttClient = createMqttClient(adapter);

    // Subscribe to connection state changes
    if (this.connectionStateSub) {
      this.connectionStateSub.unsubscribe();
    }
    this.connectionStateSub = this._mqttClient.connectionState$.subscribe((state) => {
      this.updateState(state as ConnectionState);
      
      // Reset reconnect attempts on successful connection
      if (state === 'connected') {
        this.reconnectAttempts = 0;
        console.log('[connection] Connected successfully, reset reconnect attempts');
      }
    });

    // Build connection URL
    const { mqttHost, mqttPort, mqttPath, mqttUsername, mqttPassword } = environment.connection;
    const wsUrl = `${mqttHost}:${mqttPort}${mqttPath || ''}`;
    const options: Record<string, unknown> = {};
    
    if (mqttUsername) {
      options['username'] = mqttUsername;
    }
    if (mqttPassword) {
      options['password'] = mqttPassword;
    }

    // Attempt connection
    this._mqttClient.connect(wsUrl, options)
      .then(() => {
        this.clearRetry();
        // Start monitoring MQTT messages FIRST to ensure all messages are captured
        // This must be done before subscribing to topics to avoid missing any messages
        this.startMessageMonitoring();
        // Subscribe to all required topics after message monitoring is set up
        this.subscribeToRequiredTopics();
      })
      .catch((error) => {
        console.error('[connection] Failed to connect:', error);
        this.handleConnectionFailure(error?.message || 'Unable to connect');
      });
  }

  disconnect(): void {
    this.clearRetry();
    if (this.connectionStateSub) {
      this.connectionStateSub.unsubscribe();
      this.connectionStateSub = undefined;
    }
    if (this.messagesSub) {
      this.messagesSub.unsubscribe();
      this.messagesSub = undefined;
    }
    if (this._mqttClient) {
      this._mqttClient.disconnect().catch((error) => {
        console.error('[connection] Failed to disconnect:', error);
      });
      this._mqttClient = undefined;
    }
    this.updateState('disconnected');
    this.errorSubject.next(null);
  }

  private subscribeToRequiredTopics(): void {
    if (!this._mqttClient) {
      return;
    }

    // List of all topics that need to be subscribed
    // MQTT wildcards: + = single level, # = multi-level
    const topics = [
      'ccu/order/#',           // Capture all order-related topics (active, completed, future)
      'ccu/state/stock',       // Stock snapshots
      'ccu/state/flows',       // Process flows
      'ccu/state/config',      // Configuration
      'ccu/pairing/state',     // Module pairing state
      'module/v1/#',           // All module topics (states, factsheets, etc.)
      'fts/v1/#',              // All FTS topics (fts/v1/ff/<serial>/...)
      'dsp/#',                 // DSP topics (dsp/drill/action, dsp/correlation/info, etc.)
      '/j1/txt/1/i/bme680',    // Sensor: BME680
      '/j1/txt/1/i/ldr',       // Sensor: LDR
      '/j1/txt/1/i/cam',       // Sensor: Camera
      '/j1/txt/1/i/quality_check', // AIQS: Quality check images
    ];

    console.log('[connection] Subscribing to MQTT topics...');
    Promise.all(
      topics.map((topic) =>
        this._mqttClient!.subscribe(topic, { qos: 0 }).then(() => {
          console.log(`[connection] Subscribed to: ${topic}`);
        })
      )
    ).catch((error) => {
      console.error('[connection] Failed to subscribe to topics:', error);
    });
  }

  retry(environment: EnvironmentDefinition): void {
    if (!this.settings.retryEnabled) {
      return;
    }
    this.clearRetry();
    this.retrySub = interval(this.settings.retryIntervalMs).subscribe(() => {
      if (this.stateSubject.value !== 'connected') {
        this.connect(environment);
      } else {
        this.clearRetry();
      }
    });
  }

  handleConnectionFailure(message: string): void {
    this.updateState('error');
    this.errorSubject.next(message);
    if (this.settings.retryEnabled) {
      const environment = this.environmentService.getDefinition(this.environmentService.current.key);
      if (environment) {
        this.retry(environment);
      }
    }
  }

  private updateState(state: ConnectionState): void {
    this.stateSubject.next(state);
  }

  private clearRetry(): void {
    if (this.retrySub) {
      this.retrySub.unsubscribe();
      this.retrySub = undefined;
    }
  }

  /**
   * Publish a message with automatic reconnect on disconnect
   * If disconnected, triggers immediate reconnect attempt and retries publish
   */
  async publish(topic: string, payload: unknown, options?: { qos?: 0 | 1 | 2; retain?: boolean }): Promise<void> {
    // If connected, publish immediately
    if (this.currentState === 'connected' && this._mqttClient) {
      try {
        await this._mqttClient.publish(topic, payload, options);
        console.log(`[connection] Published to ${topic}`);
        // Reset reconnect attempts on successful publish
        this.reconnectAttempts = 0;
        return;
      } catch (error) {
        console.error('[connection] Publish failed:', error);
        // Fall through to reconnect logic
      }
    }

    // Not connected or publish failed - attempt reconnect
    if (!this.currentEnvironment) {
      throw new Error('Cannot reconnect: no environment available');
    }

    if (this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
      // Reset counter so next publish operation can try again
      this.reconnectAttempts = 0;
      throw new Error(`Publish failed: max reconnect attempts (${this.MAX_RECONNECT_ATTEMPTS}) exceeded`);
    }

    console.warn(`[connection] Publish called while disconnected (attempt ${this.reconnectAttempts + 1}/${this.MAX_RECONNECT_ATTEMPTS}), triggering reconnect...`);
    this.reconnectAttempts++;

    // Attempt immediate reconnect
    try {
      await this.reconnectWithTimeout();
      
      // Retry publish after successful reconnect
      if (this._mqttClient && this.currentState === 'connected') {
        await this._mqttClient.publish(topic, payload, options);
        console.log(`[connection] Published to ${topic} after reconnect`);
        // Reset reconnect attempts on successful publish
        this.reconnectAttempts = 0;
        return;
      } else {
        throw new Error('Reconnect succeeded but client not ready');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      console.error('[connection] Reconnect and publish failed:', errorMsg);
      throw new Error(`Publish failed after reconnect attempt: ${errorMsg}`);
    }
  }

  /**
   * Attempt to reconnect with a timeout
   */
  private async reconnectWithTimeout(): Promise<void> {
    if (!this.currentEnvironment) {
      throw new Error('No environment available for reconnect');
    }

    return new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error(`Reconnect timeout after ${this.RECONNECT_TIMEOUT_MS}ms`));
      }, this.RECONNECT_TIMEOUT_MS);

      // Subscribe to state changes to detect successful connection
      const stateSub = this.stateSubject.subscribe((state) => {
        if (state === 'connected') {
          clearTimeout(timeout);
          stateSub.unsubscribe();
          resolve();
        } else if (state === 'error') {
          clearTimeout(timeout);
          stateSub.unsubscribe();
          reject(new Error('Reconnect failed with error state'));
        }
      });

      // Trigger reconnect
      this.connect(this.currentEnvironment!);
    });
  }

  private startMessageMonitoring(): void {
    if (!this._mqttClient) {
      return;
    }

    // Subscribe to all MQTT messages and feed them to MessageMonitorService
    if (this.messagesSub) {
      this.messagesSub.unsubscribe();
    }

    this.messagesSub = this._mqttClient.messages$.subscribe((message) => {
      try {
        // Parse JSON payload if it's a string
        let payload = message.payload;
        if (typeof payload === 'string') {
          try {
            payload = JSON.parse(payload);
          } catch {
            // Keep as string if not valid JSON
          }
        }
        
        // Feed message to monitor service
        this.messageMonitor.addMessage(message.topic, payload, message.timestamp);
      } catch (error) {
        console.error('[connection] Failed to process message:', error);
      }
    });

    console.log('[connection] Started message monitoring');
  }

  private loadSettings(): ConnectionSettings {
    try {
      const stored = localStorage?.getItem(SETTINGS_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<ConnectionSettings>;
        return { ...DEFAULT_SETTINGS, ...parsed };
      }
    } catch (error) {
      console.warn('[connection] Failed to parse stored settings', error);
    }
    return { ...DEFAULT_SETTINGS };
  }
}
