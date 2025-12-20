import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type EnvironmentKey = 'mock' | 'replay' | 'live';

interface EnvironmentConnection {
  mqttHost: string;
  mqttPort: number;
  mqttPath?: string;
  mqttUsername?: string;
  mqttPassword?: string;
}

export interface EnvironmentDefinition {
  key: EnvironmentKey;
  label: string;
  description: string;
  connection: EnvironmentConnection;
  readOnly?: boolean;
}

const STORAGE_KEY = 'OSF.environment';
const CONNECTION_STORAGE_KEY = 'OSF.environment.connections';

const DEFAULT_CONNECTIONS: Record<EnvironmentKey, EnvironmentConnection> = {
  mock: {
    mqttHost: 'mock://fixtures',
    mqttPort: 0,
  },
  replay: {
    mqttHost: 'localhost',
    mqttPort: 9001, // WebSocket MQTT port (Browser requires WebSocket, not TCP)
    mqttPath: '',
    mqttUsername: undefined,
    mqttPassword: undefined,
  },
  live: {
    mqttHost: '192.168.0.100',
    mqttPort: 9001, // WebSocket MQTT port (Browser requires WebSocket, not TCP MQTT on 1883)
    mqttPath: '',
    mqttUsername: 'default',
    mqttPassword: 'default',
  },
};

@Injectable({ providedIn: 'root' })
export class EnvironmentService {
  private readonly definitions: Record<EnvironmentKey, EnvironmentDefinition>;
  private readonly environmentSubject: BehaviorSubject<EnvironmentDefinition>;

  constructor() {
    const storedConnections = this.loadConnections();
    this.definitions = {
      mock: {
        key: 'mock',
        label: $localize`:@@environmentMock:Mock environment`,
        description: $localize`:@@environmentMockDescription:Local fixtures and simulated data streams for development.`,
        connection: storedConnections.mock,
        readOnly: true,
      },
      replay: {
        key: 'replay',
        label: $localize`:@@environmentReplay:Replay environment`,
        description: $localize`:@@environmentReplayDescription:Connect to local MQTT gateway and replay recorded sessions.`,
        connection: storedConnections.replay,
      },
      live: {
        key: 'live',
        label: $localize`:@@environmentLive:Live environment`,
        description: $localize`:@@environmentLiveDescription:Connect to production MQTT gateway with live shopfloor data.`,
        connection: storedConnections.live,
      },
    } satisfies Record<EnvironmentKey, EnvironmentDefinition>;

    // Migrate old TCP port (1883) to WebSocket port (9001) if needed
    this.migratePortsIfNeeded();

    const initial = this.loadInitialEnvironment();
    this.environmentSubject = new BehaviorSubject<EnvironmentDefinition>({ ...this.definitions[initial] });
  }

  get environments(): EnvironmentDefinition[] {
    return Object.values(this.definitions).map((definition) => ({ ...definition }));
  }

  get environment$() {
    return this.environmentSubject.asObservable();
  }

  get current(): EnvironmentDefinition {
    return { ...this.environmentSubject.value };
  }

  setEnvironment(key: EnvironmentKey): void {
    const definition = this.definitions[key];
    if (!definition) {
      return;
    }
    localStorage?.setItem(STORAGE_KEY, key);
    this.environmentSubject.next({ ...definition });
  }

  getDefinition(key: EnvironmentKey): EnvironmentDefinition | undefined {
    const definition = this.definitions[key];
    return definition ? { ...definition } : undefined;
  }

  updateConnection(key: EnvironmentKey, connection: EnvironmentConnection): void {
    const definition = this.definitions[key];
    if (!definition || definition.readOnly) {
      return;
    }
    definition.connection = { ...connection };
    this.persistConnections();
    if (this.current.key === key) {
      this.environmentSubject.next({ ...definition });
    }
  }

  private loadInitialEnvironment(): EnvironmentKey {
    const stored = localStorage?.getItem(STORAGE_KEY) as EnvironmentKey | null;
    if (stored && this.definitions?.[stored]) {
      return stored;
    }
    return 'mock';
  }

  private loadConnections(): Record<EnvironmentKey, EnvironmentConnection> {
    try {
      const stored = localStorage?.getItem(CONNECTION_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<Record<EnvironmentKey, EnvironmentConnection>>;
        return {
          mock: { ...DEFAULT_CONNECTIONS.mock, ...(parsed.mock ?? {}) },
          replay: { ...DEFAULT_CONNECTIONS.replay, ...(parsed.replay ?? {}) },
          live: { ...DEFAULT_CONNECTIONS.live, ...(parsed.live ?? {}) },
        };
      }
    } catch (error) {
      console.warn('[environment] Failed to parse stored connections', error);
    }
    return { ...DEFAULT_CONNECTIONS };
  }

  private migratePortsIfNeeded(): void {
    let needsMigration = false;
    
    // Migrate old TCP port (1883) to WebSocket port (9001) for browser compatibility
    if (this.definitions.replay.connection.mqttPort === 1883) {
      console.log('[environment] Migrating replay port from 1883 to 9001 (WebSocket)');
      this.definitions.replay.connection.mqttPort = 9001;
      needsMigration = true;
    }
    if (this.definitions.live.connection.mqttPort === 1883) {
      console.log('[environment] Migrating live port from 1883 to 9001 (WebSocket)');
      this.definitions.live.connection.mqttPort = 9001;
      needsMigration = true;
    }
    
    // Persist migrated connections if any changes were made
    if (needsMigration) {
      this.persistConnections();
    }
  }

  private persistConnections(): void {
    const snapshot: Record<EnvironmentKey, EnvironmentConnection> = {
      mock: this.definitions.mock.connection,
      replay: this.definitions.replay.connection,
      live: this.definitions.live.connection,
    };
    localStorage?.setItem(CONNECTION_STORAGE_KEY, JSON.stringify(snapshot));
  }
}
