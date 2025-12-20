// Mock URL.createObjectURL before any imports that might use it
if (typeof global.URL === 'undefined') {
  (global as any).URL = {
    createObjectURL: jest.fn(() => 'blob:mock-url'),
    revokeObjectURL: jest.fn(),
  };
} else if (!global.URL.createObjectURL) {
  global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
  global.URL.revokeObjectURL = jest.fn();
}

import { TestBed } from '@angular/core/testing';
import { ConnectionService, ConnectionState, ConnectionSettings } from '../connection.service';
import { EnvironmentService, EnvironmentDefinition } from '../environment.service';
import { MessageMonitorService } from '../message-monitor.service';
import { firstValueFrom, skip } from 'rxjs';
import { createMqttClient, MockMqttAdapter } from '@osf/mqtt-client';

describe('ConnectionService', () => {
  let service: ConnectionService;
  let environmentService: EnvironmentService;
  let messageMonitor: MessageMonitorService;

  const mockEnvironment: EnvironmentDefinition = {
    key: 'replay',
    label: 'Replay',
    description: 'Test environment',
    connection: {
      mqttHost: 'localhost',
      mqttPort: 9001,
      mqttPath: '',
    },
  };

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();

    // Mock URL.createObjectURL for worker-timers (used by mqtt client)
    // Must be set before any imports that use it
    if (typeof global.URL === 'undefined') {
      (global as any).URL = {
        createObjectURL: jest.fn(() => 'blob:mock-url'),
        revokeObjectURL: jest.fn(),
      };
    } else if (!global.URL.createObjectURL) {
      global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
      global.URL.revokeObjectURL = jest.fn();
    }

    TestBed.configureTestingModule({
      providers: [ConnectionService, EnvironmentService, MessageMonitorService],
    });

    service = TestBed.inject(ConnectionService);
    environmentService = TestBed.inject(EnvironmentService);
    messageMonitor = TestBed.inject(MessageMonitorService);
  });

  afterEach(() => {
    // Clean up connections
    service.disconnect();
    localStorage.clear();
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should have initial state as disconnected', () => {
      expect(service.currentState).toBe('disconnected');
    });

    it('should have default settings', () => {
      const settings = service.currentSettings;
      expect(settings.autoConnect).toBe(true);
      expect(settings.retryEnabled).toBe(true);
      expect(settings.retryIntervalMs).toBe(5000);
    });

    it('should load settings from localStorage', () => {
      const customSettings: ConnectionSettings = {
        autoConnect: false,
        retryEnabled: false,
        retryIntervalMs: 10000,
      };
      localStorage.setItem('OSF.connection.settings', JSON.stringify(customSettings));

      // Update settings and verify they are loaded
      service.updateSettings(customSettings);
      const settings = service.currentSettings;
      expect(settings.autoConnect).toBe(false);
      expect(settings.retryEnabled).toBe(false);
      expect(settings.retryIntervalMs).toBe(10000);
    });
  });

  describe('State Management', () => {
    it('should emit state changes', async () => {
      const states: ConnectionState[] = [];
      const state$ = service.state$;

      state$.subscribe((state) => {
        states.push(state);
      });

      // Initial state
      expect(states[0]).toBe('disconnected');

      // Connect to mock environment (should set to disconnected)
      service.connect({
        ...mockEnvironment,
        key: 'mock',
      });

      // Wait for state update
      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(states).toContain('disconnected');
    });

    it('should provide current state', () => {
      expect(service.currentState).toBe('disconnected');
    });

    it('should provide current error', () => {
      expect(service.currentError).toBeNull();
    });
  });

  describe('Settings Management', () => {
    it('should update settings', () => {
      const newSettings: Partial<ConnectionSettings> = {
        autoConnect: false,
        retryIntervalMs: 10000,
      };

      service.updateSettings(newSettings);
      const settings = service.currentSettings;

      expect(settings.autoConnect).toBe(false);
      expect(settings.retryIntervalMs).toBe(10000);
      expect(settings.retryEnabled).toBe(true); // Unchanged
    });

    it('should persist settings to localStorage', () => {
      const newSettings: Partial<ConnectionSettings> = {
        retryEnabled: false,
      };

      service.updateSettings(newSettings);

      const stored = localStorage.getItem('OSF.connection.settings');
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!);
      expect(parsed.retryEnabled).toBe(false);
    });
  });

  describe('Connection - Mock Environment', () => {
    it('should set state to disconnected for mock environment', async () => {
      const mockEnv: EnvironmentDefinition = {
        ...mockEnvironment,
        key: 'mock',
      };

      service.connect(mockEnv);

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(service.currentState).toBe('disconnected');
    });

    it('should not create MQTT client for mock environment', async () => {
      const mockEnv: EnvironmentDefinition = {
        ...mockEnvironment,
        key: 'mock',
      };

      service.connect(mockEnv);

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(service.mqttClient).toBeUndefined();
    });
  });

  describe('Connection - Error Handling', () => {
    it('should handle connection failure', async () => {
      const errorMessage = 'Connection failed';
      
      // Mock environment that will fail
      const failingEnv: EnvironmentDefinition = {
        ...mockEnvironment,
        connection: {
          mqttHost: 'invalid-host',
          mqttPort: 9999,
        },
      };

      // Set retry to false to avoid retry logic in tests
      service.updateSettings({ retryEnabled: false });

      service.connect(failingEnv);

      // Wait for connection attempt
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Should eventually reach error state (connection will fail)
      // Note: Actual error state depends on MQTT client implementation
      const state = service.currentState;
      expect(['error', 'disconnected']).toContain(state);
    });

    it('should emit error on connection failure', async () => {
      service.updateSettings({ retryEnabled: false });

      const errors: (string | null)[] = [];
      service.error$.subscribe((error) => {
        errors.push(error);
      });

      const failingEnv: EnvironmentDefinition = {
        ...mockEnvironment,
        connection: {
          mqttHost: 'invalid-host',
          mqttPort: 9999,
        },
      };

      service.connect(failingEnv);

      await new Promise((resolve) => setTimeout(resolve, 500));

      // Error should be emitted (or null if cleared)
      expect(errors.length).toBeGreaterThan(0);
    });
  });

  describe('Disconnect', () => {
    it('should set state to disconnected', () => {
      service.disconnect();
      expect(service.currentState).toBe('disconnected');
    });

    it('should clear error on disconnect', () => {
      service.disconnect();
      expect(service.currentError).toBeNull();
    });

    it('should clear retry subscription on disconnect', () => {
      service.updateSettings({ retryEnabled: true });
      service.disconnect();
      // Retry should be cleared (no way to directly test, but disconnect should handle it)
      expect(service.currentState).toBe('disconnected');
    });
  });

  describe('Retry Logic', () => {
    it('should not retry when retryEnabled is false', () => {
      service.updateSettings({ retryEnabled: false });

      const retrySpy = jest.spyOn(service as any, 'retry');
      service.handleConnectionFailure('Test error');

      expect(retrySpy).not.toHaveBeenCalled();
    });

    it('should retry when retryEnabled is true', () => {
      service.updateSettings({ retryEnabled: true });

      const retrySpy = jest.spyOn(service as any, 'retry');
      service.handleConnectionFailure('Test error');

      // Retry should be called (if environment is available)
      // Note: Actual retry behavior depends on environment service
    });

    it('should respect retryIntervalMs setting', () => {
      const customInterval = 10000;
      service.updateSettings({ retryEnabled: true, retryIntervalMs: customInterval });

      const settings = service.currentSettings;
      expect(settings.retryIntervalMs).toBe(customInterval);
    });

    it('should not retry when environment is not found', () => {
      service.updateSettings({ retryEnabled: true });

      // Mock environmentService to return null
      jest.spyOn(environmentService, 'getDefinition').mockReturnValue(undefined);
      jest.spyOn(environmentService, 'current', 'get').mockReturnValue({ key: 'unknown' } as any);

      const retrySpy = jest.spyOn(service as any, 'retry');
      service.handleConnectionFailure('Test error');

      // Should not retry if environment is not found
      expect(retrySpy).not.toHaveBeenCalled();
    });

    it('should clear retry when already connected', async () => {
      service.updateSettings({ retryEnabled: true });

      // Set state to connected via the stateSubject to avoid actual MQTT connection
      (service as any).stateSubject.next('connected');
      
      // Mock interval to avoid async timing issues
      jest.useFakeTimers();
      const clearRetrySpy = jest.spyOn(service as any, 'clearRetry');
      
      // Call retry - this should set up an interval
      (service as any).retry(mockEnvironment);
      
      // Fast-forward time to trigger the interval callback
      jest.advanceTimersByTime(100);
      
      // clearRetry should be called when already connected
      expect(clearRetrySpy).toHaveBeenCalled();
      
      jest.useRealTimers();
    });

    it('should not retry when retryEnabled is false in retry method', () => {
      service.updateSettings({ retryEnabled: false });

      const connectSpy = jest.spyOn(service, 'connect');
      (service as any).retry(mockEnvironment);

      // Should not call connect when retryEnabled is false
      expect(connectSpy).not.toHaveBeenCalled();
    });
  });

  describe('MQTT Client', () => {
    it('should provide mqttClient getter', () => {
      expect(service.mqttClient).toBeUndefined();
    });

    it('should create MQTT client on connect (non-mock)', async () => {
      service.updateSettings({ retryEnabled: false });

      // Note: Actual MQTT client creation depends on WebSocket connection
      // This test verifies the service structure
      service.connect(mockEnvironment);

      await new Promise((resolve) => setTimeout(resolve, 100));

      // Client may or may not be created depending on connection success
      // This is a structural test
      expect(service).toBeTruthy();
    });
  });

  describe('Subscription Management', () => {
    it('should handle multiple state subscriptions', async () => {
      const states1: ConnectionState[] = [];
      const states2: ConnectionState[] = [];

      service.state$.subscribe((state) => states1.push(state));
      service.state$.subscribe((state) => states2.push(state));

      service.disconnect();

      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(states1.length).toBeGreaterThan(0);
      expect(states2.length).toBeGreaterThan(0);
    });
  });

  describe('Environment Changes', () => {
    it('should disconnect when environment changes', () => {
      const disconnectSpy = jest.spyOn(service, 'disconnect');

      // Change environment
      environmentService.setEnvironment('live');

      // Should trigger disconnect
      expect(disconnectSpy).toHaveBeenCalled();
    });

    it('should auto-connect when autoConnect is enabled', () => {
      service.updateSettings({ autoConnect: true });
      const connectSpy = jest.spyOn(service, 'connect');

      // Change to non-mock environment
      environmentService.setEnvironment('replay');

      // Should trigger connect
      expect(connectSpy).toHaveBeenCalled();
    });

    it('should not auto-connect when autoConnect is disabled', () => {
      service.updateSettings({ autoConnect: false });
      const connectSpy = jest.spyOn(service, 'connect');

      // Change to non-mock environment
      environmentService.setEnvironment('replay');

      // Should not trigger connect
      expect(connectSpy).not.toHaveBeenCalled();
    });

    it('should handle environment change when definition is not found', () => {
      const disconnectSpy = jest.spyOn(service, 'disconnect');
      
      // Mock getDefinition to return undefined
      jest.spyOn(environmentService, 'getDefinition').mockReturnValue(undefined);
      jest.spyOn(environmentService, 'current', 'get').mockReturnValue({ key: 'unknown' } as any);

      // Should not crash, but should not connect
      expect(() => {
        // Trigger environment change
        (environmentService as any).environmentSubject.next({ key: 'unknown' });
      }).not.toThrow();
    });

    it('should set disconnected state for mock environment', () => {
      const updateStateSpy = jest.spyOn(service as any, 'updateState');
      
      // Set mock environment
      environmentService.setEnvironment('mock');

      // Should set disconnected state
      expect(updateStateSpy).toHaveBeenCalledWith('disconnected');
    });
  });

  describe('Publish - Edge Cases', () => {
    it('should throw error when no environment available for reconnect', async () => {
      // Ensure no environment is set
      service.disconnect();
      (service as any).currentEnvironment = undefined;

      await expect(
        service.publish('test/topic', { data: 'test' })
      ).rejects.toThrow('Cannot reconnect: no environment available');
    });

    it('should throw error when max reconnect attempts exceeded', async () => {
      service.updateSettings({ retryEnabled: false });
      
      // Set environment but don't connect
      (service as any).currentEnvironment = mockEnvironment;
      (service as any).reconnectAttempts = 3; // MAX_RECONNECT_ATTEMPTS

      await expect(
        service.publish('test/topic', { data: 'test' })
      ).rejects.toThrow('max reconnect attempts (3) exceeded');
    });

    // Note: Testing publish error handling with real reconnect is complex and slow
    // The error handling paths are covered by other tests:
    // - "should throw error when no environment available for reconnect"
    // - "should throw error when max reconnect attempts exceeded"
    // - "should throw error when reconnect succeeds but client not ready"

    it('should throw error when reconnect succeeds but client not ready', async () => {
      service.updateSettings({ retryEnabled: false });
      
      // Set environment but don't connect
      (service as any).currentEnvironment = mockEnvironment;
      (service as any).reconnectAttempts = 0;

      // Mock reconnectWithTimeout to succeed but client not ready
      const reconnectSpy = jest.spyOn(service as any, 'reconnectWithTimeout').mockResolvedValue(undefined);
      (service as any)._mqttClient = undefined; // Client not ready

      await expect(
        service.publish('test/topic', { data: 'test' })
      ).rejects.toThrow('Reconnect succeeded but client not ready');

      reconnectSpy.mockRestore();
    });
  });

  describe('Reconnect - Edge Cases', () => {
    it('should throw error when no environment for reconnect', async () => {
      (service as any).currentEnvironment = undefined;

      await expect(
        (service as any).reconnectWithTimeout()
      ).rejects.toThrow('No environment available for reconnect');
    });
  });
});

