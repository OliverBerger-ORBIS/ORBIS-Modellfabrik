import { Injectable } from '@angular/core';
import { BehaviorSubject, interval, Subscription } from 'rxjs';
import { EnvironmentDefinition, EnvironmentService } from './environment.service';

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

    // TODO: integrate real MQTT client. For now simulate async connection.
    setTimeout(() => {
      const success = true;
      if (success) {
        this.updateState('connected');
        this.clearRetry();
      } else {
        this.handleConnectionFailure('Unable to connect');
      }
    }, 300);
  }

  disconnect(): void {
    this.clearRetry();
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
