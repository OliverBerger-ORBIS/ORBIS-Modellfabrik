import { TestBed } from '@angular/core/testing';
import { SensorStateService } from '../sensor-state.service';
import { firstValueFrom } from 'rxjs';
import type { SensorOverviewState } from '@omf3/entities';

describe('SensorStateService', () => {
  let service: SensorStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [SensorStateService],
    });
    service = TestBed.inject(SensorStateService);
  });

  describe('Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should return null for uninitialized state', async () => {
      const state$ = service.getState$('test-env');
      const state = await firstValueFrom(state$);
      expect(state).toBeNull();
    });

    it('should return null snapshot for uninitialized state', () => {
      const snapshot = service.getSnapshot('test-env');
      expect(snapshot).toBeNull();
    });
  });

  describe('State Management', () => {
    it('should set and get state', async () => {
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      service.setState('test-env', mockState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(mockState);
    });

    it('should update state', async () => {
      const state1: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      const state2: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 30,
        humidityPercent: 60,
        pressureHpa: 1015,
        lightLux: 150,
      };

      service.setState('test-env', state1);
      service.setState('test-env', state2);

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toEqual(state2);
    });

    it('should clear state', async () => {
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      service.setState('test-env', mockState);
      service.clear('test-env');

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toBeNull();
    });

    it('should handle multiple environments independently', async () => {
      const state1: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      const state2: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 30,
        humidityPercent: 60,
        pressureHpa: 1015,
        lightLux: 150,
      };

      service.setState('env1', state1);
      service.setState('env2', state2);

      const env1State = await firstValueFrom(service.getState$('env1'));
      const env2State = await firstValueFrom(service.getState$('env2'));

      expect(env1State).toEqual(state1);
      expect(env2State).toEqual(state2);
    });
  });

  describe('Snapshot', () => {
    it('should return current snapshot', () => {
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      service.setState('test-env', mockState);
      const snapshot = service.getSnapshot('test-env');

      expect(snapshot).toEqual(mockState);
    });

    it('should return null snapshot after clear', () => {
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      service.setState('test-env', mockState);
      service.clear('test-env');
      const snapshot = service.getSnapshot('test-env');

      expect(snapshot).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty environment key', async () => {
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
      };

      service.setState('', mockState);
      const state = await firstValueFrom(service.getState$(''));

      expect(state).toEqual(mockState);
    });

    it('should handle very long environment key', async () => {
      const longKey = 'a'.repeat(1000);
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      service.setState(longKey, mockState);
      const state = await firstValueFrom(service.getState$(longKey));

      expect(state).toEqual(mockState);
    });

    it('should handle state with null sensors', async () => {
      const nullState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
      };

      service.setState('test-env', nullState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(nullState);
    });

    it('should handle state with partial sensors', async () => {
      const partialState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
      };

      service.setState('test-env', partialState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(partialState);
    });

    it('should handle rapid state changes', async () => {
      const states: SensorOverviewState[] = [
        { timestamp: new Date().toISOString(), temperatureC: 20, humidityPercent: 40, pressureHpa: 1010, lightLux: 50 },
        { timestamp: new Date().toISOString(), temperatureC: 25, humidityPercent: 50, pressureHpa: 1013, lightLux: 100 },
        { timestamp: new Date().toISOString(), temperatureC: 30, humidityPercent: 60, pressureHpa: 1015, lightLux: 150 },
      ];

      states.forEach((state) => {
        service.setState('test-env', state);
      });

      const finalState = await firstValueFrom(service.getState$('test-env'));
      expect(finalState).toEqual(states[states.length - 1]);
    });

    it('should handle clear on uninitialized environment', () => {
      expect(() => {
        service.clear('uninitialized-env');
      }).not.toThrow();

      const snapshot = service.getSnapshot('uninitialized-env');
      expect(snapshot).toBeNull();
    });

    it('should handle getSnapshot on uninitialized environment', () => {
      const snapshot = service.getSnapshot('uninitialized-env');
      expect(snapshot).toBeNull();
    });

    it('should handle multiple clears', async () => {
      const mockState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 25,
        humidityPercent: 50,
        pressureHpa: 1013,
        lightLux: 100,
      };

      service.setState('test-env', mockState);
      service.clear('test-env');
      service.clear('test-env');
      service.clear('test-env');

      const state = await firstValueFrom(service.getState$('test-env'));
      expect(state).toBeNull();
    });

    it('should handle state with extreme sensor values', async () => {
      const extremeState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: -50,
        humidityPercent: 0,
        pressureHpa: 500,
        lightLux: 0,
      };

      service.setState('test-env', extremeState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(extremeState);
    });

    it('should handle state with very high sensor values', async () => {
      const highState: SensorOverviewState = {
        timestamp: new Date().toISOString(),
        temperatureC: 150,
        humidityPercent: 100,
        pressureHpa: 2000,
        lightLux: 10000,
      };

      service.setState('test-env', highState);
      const state = await firstValueFrom(service.getState$('test-env'));

      expect(state).toEqual(highState);
    });
  });
});

