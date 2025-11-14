import { Injectable } from '@angular/core';
import { BehaviorSubject, interval, Subscription } from 'rxjs';
import { EnvironmentDefinition, EnvironmentService } from './environment.service';
import { createMqttClient, MockMqttAdapter, WebSocketMqttAdapter, MqttClientWrapper } from '@omf3/mqtt-client';

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface ConnectionSettings {
  autoConnect: boolean;
  retryEnabled: boolean;
  retryIntervalMs: number;
}

const SETTINGS_STORAGE_KEY = 'omf3.connection.settings';

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
  private mqttClient?: MqttClientWrapper;
  private connectionStateSub?: Subscription;

  constructor(private readonly environmentService: EnvironmentService) {
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

    this.updateState('connecting');
    this.errorSubject.next(null);

    // Create WebSocket MQTT client for replay/live environments
    const adapter = new WebSocketMqttAdapter();
    this.mqttClient = createMqttClient(adapter);

    // Subscribe to connection state changes
    if (this.connectionStateSub) {
      this.connectionStateSub.unsubscribe();
    }
    this.connectionStateSub = this.mqttClient.connectionState$.subscribe((state) => {
      this.updateState(state as ConnectionState);
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
    this.mqttClient.connect(wsUrl, options)
      .then(() => {
        this.clearRetry();
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
    if (this.mqttClient) {
      this.mqttClient.disconnect().catch((error) => {
        console.error('[connection] Failed to disconnect:', error);
      });
      this.mqttClient = undefined;
    }
    this.updateState('disconnected');
    this.errorSubject.next(null);
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
