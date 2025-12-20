import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { SensorTabComponent } from '../sensor-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ConnectionService } from '../../services/connection.service';
import { SensorStateService } from '../../services/sensor-state.service';
import * as mockDashboard from '../../mock-dashboard';
import type { SensorOverviewState, CameraFrame } from '@osf/entities';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    sensorOverview$: of({
      timestamp: '',
      temperatureC: undefined,
      humidityPercent: undefined,
      pressureHpa: undefined,
      lightLux: undefined,
      iaq: undefined,
      airQualityScore: undefined,
      airQualityClassification: undefined,
    } as SensorOverviewState),
    cameraFrames$: of(null as CameraFrame | null),
  },
  commands: {
    moveCamera: jest.fn(),
  },
  loadTabFixture: jest.fn(),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('SensorTabComponent', () => {
  let component: SensorTabComponent;
  let fixture: ComponentFixture<SensorTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let sensorState: jest.Mocked<SensorStateService>;

  beforeEach(async () => {
    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'disconnected'>('disconnected'),
    };

    const sensorStateMock = {
      getState$: jest.fn(() => of(null)),
      getSnapshot: jest.fn(() => null),
      setState: jest.fn(),
      clear: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [SensorTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: SensorStateService, useValue: sensorStateMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SensorTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    sensorState = TestBed.inject(SensorStateService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize streams', () => {
    expect(component.sensorOverview$).toBeDefined();
    expect(component.cameraFrame$).toBeDefined();
  });

  it('should detect mock mode', () => {
    expect(component.isMockMode).toBe(true);
  });

  it('should have fixture options', () => {
    expect(component.fixtureOptions.length).toBeGreaterThan(0);
    expect(component.activeFixture).toBeDefined();
  });

  it('should have fixture labels', () => {
    expect(component.fixtureLabels).toBeDefined();
    expect(component.fixtureLabels.startup).toBeDefined();
  });

  it('should compute gauge ratio', () => {
    const ratio = component.gaugeRatio(50, 0, 100);
    expect(ratio).toBe(0.5);
  });

  it('should compute gauge dash offset', () => {
    const offset = component.gaugeDashOffset(50, 0, 100);
    expect(offset).toBeGreaterThan(0);
  });

  it('should format timestamp', () => {
    const formatted = component.formatTimestamp('2025-11-10T18:00:00Z');
    expect(formatted).toBeDefined();
  });

  it('should handle missing timestamp', () => {
    const formatted = component.formatTimestamp(undefined);
    expect(formatted).toBeDefined();
  });

  it('should get air quality status', () => {
    const sensor = {
      airQualityClassification: 'good',
    } as SensorOverviewState;
    const status = component.airQualityStatus(sensor);
    expect(status).toBe('good');
  });

  it('should handle missing air quality classification', () => {
    const status = component.airQualityStatus(null);
    expect(status).toBeDefined();
  });

  it('should format large numbers', () => {
    expect(component.formatLarge(1000000)).toContain('M');
    expect(component.formatLarge(1000)).toContain('k');
    expect(component.formatLarge(100)).toBe('100');
  });

  it('should format exponent', () => {
    const formatted = component.formatExponent(1000);
    expect(formatted).toContain('10^');
  });

  it('should get aria label for camera control', () => {
    expect(component.getAriaLabel('up')).toBeDefined();
    expect(component.getAriaLabel('down')).toBeDefined();
    expect(component.getAriaLabel('left')).toBeDefined();
    expect(component.getAriaLabel('right')).toBeDefined();
    expect(component.getAriaLabel('center')).toBeDefined();
  });

  it('should handle step size change', () => {
    const event = {
      target: { value: '15' },
    } as unknown as Event;
    component.onStepSizeChange(event);
    expect(component.stepSize).toBe(15);
  });

  it('should clamp step size to valid range', () => {
    const event = {
      target: { value: '100' },
    } as unknown as Event;
    component.onStepSizeChange(event);
    expect(component.stepSize).toBeLessThanOrEqual(90);
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });
});

