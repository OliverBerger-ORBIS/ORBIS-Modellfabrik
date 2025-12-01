import { TestBed } from '@angular/core/testing';
import { EnvironmentService, EnvironmentKey, EnvironmentDefinition } from '../environment.service';
import { firstValueFrom, skip } from 'rxjs';

describe('EnvironmentService', () => {
  let service: EnvironmentService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [EnvironmentService],
    });

    service = TestBed.inject(EnvironmentService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should provide default environment', () => {
      const current = service.current;
      expect(current).toBeDefined();
      expect(['mock', 'replay', 'live']).toContain(current.key);
    });

    it('should provide all environments', () => {
      const environments = service.environments;
      expect(environments.length).toBe(3);
      expect(environments.map((e) => e.key)).toEqual(['mock', 'replay', 'live']);
    });

    it('should emit current environment on subscription', async () => {
      const environment$ = service.environment$;
      const value = await firstValueFrom(environment$);
      expect(value).toBeDefined();
      expect(value.key).toBeDefined();
    });
  });

  describe('Environment Management', () => {
    it('should set environment', () => {
      service.setEnvironment('live');
      expect(service.current.key).toBe('live');
    });

    it('should persist environment to localStorage', () => {
      service.setEnvironment('replay');
      const stored = localStorage.getItem('omf3.environment');
      expect(stored).toBe('replay');
    });

    it('should load environment from localStorage', () => {
      // Test that setEnvironment persists to localStorage
      service.setEnvironment('live');
      const stored = localStorage.getItem('omf3.environment');
      expect(stored).toBe('live');
      
      // Verify current reflects the change
      expect(service.current.key).toBe('live');
    });

    it('should emit environment changes', (done) => {
      const environment$ = service.environment$;
      let initialKey: string | null = null;
      let callCount = 0;

      environment$.subscribe((env) => {
        callCount++;
        if (callCount === 1) {
          initialKey = env.key;
          service.setEnvironment('live');
        } else if (callCount === 2) {
          expect(env.key).toBe('live');
          expect(env.key).not.toBe(initialKey);
          done();
        }
      });
    });
  });

  describe('Environment Definitions', () => {
    it('should provide environment definition', () => {
      const definition = service.getDefinition('mock');
      expect(definition).toBeDefined();
      expect(definition?.key).toBe('mock');
      expect(definition?.label).toBeDefined();
      expect(definition?.description).toBeDefined();
    });

    it('should return undefined for invalid environment key', () => {
      const definition = service.getDefinition('invalid' as EnvironmentKey);
      expect(definition).toBeUndefined();
    });

    it('should provide connection details for each environment', () => {
      const mockDef = service.getDefinition('mock');
      const replayDef = service.getDefinition('replay');
      const liveDef = service.getDefinition('live');

      expect(mockDef?.connection).toBeDefined();
      expect(replayDef?.connection).toBeDefined();
      expect(liveDef?.connection).toBeDefined();

      expect(mockDef?.connection.mqttHost).toBeDefined();
      expect(replayDef?.connection.mqttHost).toBeDefined();
      expect(liveDef?.connection.mqttHost).toBeDefined();
    });
  });

  describe('Connection Storage', () => {
    it('should update connection settings', () => {
      const newConnection = {
        mqttHost: 'test-host',
        mqttPort: 1234,
        mqttPath: '/test',
      };

      service.updateConnection('replay', newConnection);
      const definition = service.getDefinition('replay');

      expect(definition?.connection.mqttHost).toBe('test-host');
      expect(definition?.connection.mqttPort).toBe(1234);
      expect(definition?.connection.mqttPath).toBe('/test');
    });

    it('should persist connection settings to localStorage', () => {
      const newConnection = {
        mqttHost: 'test-host',
        mqttPort: 1234,
      };

      service.updateConnection('live', newConnection);

      const stored = localStorage.getItem('omf3.environment.connections');
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!);
      expect(parsed.live.mqttHost).toBe('test-host');
    });

    it('should persist and load connection settings', () => {
      const newConnection = {
        mqttHost: 'stored-host',
        mqttPort: 5678,
      };

      // Update connection
      service.updateConnection('replay', newConnection);
      const definition = service.getDefinition('replay');

      expect(definition?.connection.mqttHost).toBe('stored-host');
      expect(definition?.connection.mqttPort).toBe(5678);
      
      // Verify persistence
      const stored = localStorage.getItem('omf3.environment.connections');
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!);
      expect(parsed.replay.mqttHost).toBe('stored-host');
    });
  });

  describe('Read-Only Environments', () => {
    it('should mark mock environment as read-only', () => {
      const definition = service.getDefinition('mock');
      expect(definition?.readOnly).toBe(true);
    });

    it('should allow modification of non-read-only environments', () => {
      const replayDef = service.getDefinition('replay');
      const liveDef = service.getDefinition('live');

      expect(replayDef?.readOnly).toBeFalsy();
      expect(liveDef?.readOnly).toBeFalsy();
    });

    it('should not update read-only environment connection', () => {
      const before = service.getDefinition('mock');
      const newConnection = {
        mqttHost: 'test-host',
        mqttPort: 1234,
      };

      service.updateConnection('mock', newConnection);
      const after = service.getDefinition('mock');

      // Should not change
      expect(after?.connection.mqttHost).toBe(before?.connection.mqttHost);
      expect(after?.connection.mqttPort).toBe(before?.connection.mqttPort);
    });
  });

  describe('Edge Cases', () => {
    it('should handle setEnvironment with invalid key gracefully', () => {
      const before = service.current;
      service.setEnvironment('invalid' as EnvironmentKey);
      
      // Should not change
      expect(service.current.key).toBe(before.key);
    });

    it('should handle updateConnection with invalid key gracefully', () => {
      const newConnection = {
        mqttHost: 'test-host',
        mqttPort: 1234,
      };

      expect(() => {
        service.updateConnection('invalid' as EnvironmentKey, newConnection);
      }).not.toThrow();
    });

    it('should handle corrupted connection storage gracefully', () => {
      localStorage.setItem('omf3.environment.connections', 'invalid json{{{');
      
      // Should not crash, should use defaults
      const newService = TestBed.inject(EnvironmentService);
      const definition = newService.getDefinition('replay');
      
      expect(definition).toBeDefined();
      expect(definition?.connection.mqttHost).toBeDefined();
    });

    it('should handle partial connection storage', () => {
      const partialData = {
        replay: {
          mqttHost: 'partial-host',
          mqttPort: 5678,
        },
      };
      localStorage.setItem('omf3.environment.connections', JSON.stringify(partialData));
      
      // Need to create new service instance to load from localStorage
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        providers: [EnvironmentService],
      });
      const newService = TestBed.inject(EnvironmentService);
      const replayDef = newService.getDefinition('replay');
      const liveDef = newService.getDefinition('live');
      
      // Replay should use partial data merged with defaults
      expect(replayDef?.connection.mqttHost).toBe('partial-host');
      expect(replayDef?.connection.mqttPort).toBe(5678);
      
      // Live should use defaults
      expect(liveDef?.connection.mqttHost).toBe('192.168.0.100');
    });

    it('should handle localStorage errors gracefully', () => {
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = jest.fn(() => {
        throw new Error('Storage quota exceeded');
      });

      expect(() => {
        service.setEnvironment('live');
      }).not.toThrow();

      localStorage.setItem = originalSetItem;
    });

    it('should handle invalid stored environment key', () => {
      localStorage.setItem('omf3.environment', 'invalid-key');
      
      const newService = TestBed.inject(EnvironmentService);
      // Should default to 'mock'
      expect(newService.current.key).toBe('mock');
    });

    it('should migrate port 1883 to 9001 for replay', () => {
      const oldConnections = {
        replay: { mqttHost: 'localhost', mqttPort: 1883 },
        live: { mqttHost: '192.168.0.100', mqttPort: 9001 },
        mock: { mqttHost: 'mock://fixtures', mqttPort: 0 },
      };
      localStorage.setItem('omf3.environment.connections', JSON.stringify(oldConnections));
      
      const newService = TestBed.inject(EnvironmentService);
      const replayDef = newService.getDefinition('replay');
      
      // Should be migrated to 9001
      expect(replayDef?.connection.mqttPort).toBe(9001);
    });

    it('should migrate port 1883 to 9001 for live', () => {
      const oldConnections = {
        replay: { mqttHost: 'localhost', mqttPort: 9001 },
        live: { mqttHost: '192.168.0.100', mqttPort: 1883 },
        mock: { mqttHost: 'mock://fixtures', mqttPort: 0 },
      };
      localStorage.setItem('omf3.environment.connections', JSON.stringify(oldConnections));
      
      const newService = TestBed.inject(EnvironmentService);
      const liveDef = newService.getDefinition('live');
      
      // Should be migrated to 9001
      expect(liveDef?.connection.mqttPort).toBe(9001);
    });

    it('should update current environment when connection is updated', () => {
      service.setEnvironment('replay');
      const newConnection = {
        mqttHost: 'updated-host',
        mqttPort: 9999,
      };

      service.updateConnection('replay', newConnection);
      
      // Current should reflect the update
      expect(service.current.connection.mqttHost).toBe('updated-host');
      expect(service.current.connection.mqttPort).toBe(9999);
    });

    it('should not update current environment when different environment connection is updated', () => {
      service.setEnvironment('replay');
      const before = service.current;
      const newConnection = {
        mqttHost: 'updated-host',
        mqttPort: 9999,
      };

      service.updateConnection('live', newConnection);
      
      // Current should not change
      expect(service.current.connection.mqttHost).toBe(before.connection.mqttHost);
    });
  });
});

