import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { MillTabComponent } from '../mill-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ConnectionService } from '../../services/connection.service';
import { ModuleNameService } from '../../services/module-name.service';
import { ChangeDetectorRef } from '@angular/core';
import * as mockDashboard from '../../mock-dashboard';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    orders$: of({}),
  },
  loadTabFixture: jest.fn().mockResolvedValue(undefined),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('MillTabComponent', () => {
  let component: MillTabComponent;
  let fixture: ComponentFixture<MillTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;
  let cdr: jest.Mocked<ChangeDetectorRef>;

  const mockMillState = {
    serialNumber: 'SVR3QA2098',
    timestamp: '2025-12-17T18:00:00Z',
    orderId: 'test-order-123',
    orderUpdateId: 1,
    connectionState: 'ONLINE' as const,
    available: 'READY' as const,
    actionState: {
      id: 'action-1',
      command: 'MILL' as const,
      state: 'FINISHED' as const,
      timestamp: '2025-12-17T18:00:00Z',
      result: 'PASSED' as const,
      metadata: {
        millDepth: 10,
        millSpeed: 800,
        workpieceId: 'WP-345678',
      },
    },
    actionStates: [],
  };

  beforeEach(async () => {
    const environmentSubject = new BehaviorSubject({ 
      key: 'mock' as const, 
      label: 'Mock', 
      description: 'Mock', 
      connection: { mqttHost: 'localhost', mqttPort: 1883 } 
    });
    
    const environmentServiceMock = {
      get current() {
        return environmentSubject.value;
      },
      environment$: environmentSubject.asObservable(),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
      getHistory: jest.fn(() => []),
      addMessage: jest.fn(),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'connected'>('connected'),
    };

    const moduleNameServiceMock = {
      getModuleDisplayText: jest.fn((id: string) => id),
    };

    const cdrMock = {
      markForCheck: jest.fn(),
      detectChanges: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MillTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ChangeDetectorRef, useValue: cdrMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MillTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
    cdr = TestBed.inject(ChangeDetectorRef) as any;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize streams', () => {
    expect(component.millState$).toBeDefined();
    expect(component.connection$).toBeDefined();
    expect(component.millOrder$).toBeDefined();
  });

  it('should detect mock mode', () => {
    expect(component.isMockMode).toBe(true);
  });

  it('should detect replay mode', async () => {
    const replayEnvironmentSubject = new BehaviorSubject({ 
      key: 'replay' as const, 
      label: 'Replay', 
      description: 'Replay', 
      connection: { mqttHost: 'localhost', mqttPort: 1883 } 
    });
    
    const replayEnvironmentServiceMock = {
      get current() {
        return replayEnvironmentSubject.value;
      },
      environment$: replayEnvironmentSubject.asObservable(),
    };
    
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [MillTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: replayEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: ChangeDetectorRef, useValue: cdr },
      ],
    }).compileComponents();
    
    const replayFixture = TestBed.createComponent(MillTabComponent);
    const replayComponent = replayFixture.componentInstance;
    expect(replayComponent.isReplayMode).toBe(true);
  });

  it('should have fixture options', () => {
    expect(component.fixtureOptions.length).toBeGreaterThan(0);
    expect(component.activeFixture).toBeDefined();
  });

  it('should have fixture labels', () => {
    expect(component.fixtureLabels).toBeDefined();
    expect(component.fixtureLabels.startup).toBeDefined();
  });

  it('should get connection status', () => {
    expect(component.getConnectionStatus(mockMillState)).toBe('ONLINE');
    expect(component.getConnectionStatus(null)).toBe('OFFLINE');
  });

  it('should get availability', () => {
    expect(component.getAvailability(mockMillState)).toBe('READY');
    expect(component.getAvailability(null)).toBe('UNKNOWN');
  });

  it('should get current action', () => {
    const action = component.getCurrentAction(mockMillState);
    expect(action).toBeDefined();
    expect(action?.command).toBe('MILL');
  });

  it('should get recent actions', () => {
    const actions = component.getRecentActions(mockMillState);
    expect(Array.isArray(actions)).toBe(true);
  });

  it('should get mill depth', () => {
    expect(component.getMillDepth(mockMillState)).toBe(10);
    expect(component.getMillDepth(null)).toBeNull();
  });

  it('should get mill speed', () => {
    expect(component.getMillSpeed(mockMillState)).toBe(800);
    expect(component.getMillSpeed(null)).toBeNull();
  });

  it('should get workpiece ID', () => {
    expect(component.getWorkpieceId(mockMillState)).toBe('WP-345678');
    expect(component.getWorkpieceId(null)).toBeNull();
  });

  it('should get state label', () => {
    expect(component.getStateLabel('WAITING')).toBeDefined();
    expect(component.getStateLabel('FINISHED')).toBeDefined();
  });

  it('should get state class', () => {
    expect(component.getStateClass('WAITING')).toBe('waiting');
    expect(component.getStateClass('FINISHED')).toBe('finished');
  });

  it('should get result label', () => {
    expect(component.getResultLabel('PASSED')).toBeDefined();
    expect(component.getResultLabel('FAILED')).toBeDefined();
    expect(component.getResultLabel(undefined)).toBe('-');
  });

  it('should get result class', () => {
    expect(component.getResultClass('PASSED')).toBe('passed');
    expect(component.getResultClass('FAILED')).toBe('failed');
  });

  it('should format timestamp', () => {
    const formatted = component.formatTimestamp('2025-12-17T18:00:00Z');
    expect(formatted).toBeDefined();
  });

  it('should display order ID correctly', () => {
    expect(component.getOrderIdDisplay('short')).toBe('short');
    expect(component.getOrderIdDisplay('very-long-order-id-that-exceeds-12-chars')).toContain('...');
    expect(component.getOrderIdDisplay(undefined)).toBeDefined();
  });

  it('should track actions by ID', () => {
    const action = mockMillState.actionState;
    expect(component.trackByActionId(0, action)).toBe('action-1');
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });

  it('should load fixture in mock mode', async () => {
    const loadTabFixtureSpy = jest.spyOn(component['dashboard'], 'loadTabFixture').mockResolvedValue({} as any);
    
    await component.loadFixture('startup');
    expect(loadTabFixtureSpy).toHaveBeenCalled();
  });

  it('should handle fixture load in replay mode', async () => {
    const replayEnvironmentSubject = new BehaviorSubject({ 
      key: 'replay' as const, 
      label: 'Replay', 
      description: 'Replay', 
      connection: { mqttHost: 'localhost', mqttPort: 1883 } 
    });
    
    const replayEnvironmentServiceMock = {
      get current() {
        return replayEnvironmentSubject.value;
      },
      environment$: replayEnvironmentSubject.asObservable(),
    };

    const mockCdr = {
      markForCheck: jest.fn(),
      detectChanges: jest.fn(),
    };
    
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [MillTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: replayEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: ChangeDetectorRef, useValue: mockCdr },
      ],
    }).compileComponents();
    
    const replayFixture = TestBed.createComponent(MillTabComponent);
    const replayComponent = replayFixture.componentInstance;
    
    // Spy on the actual component's cdr
    const cdrSpy = jest.spyOn(replayComponent['cdr'], 'markForCheck');
    
    await replayComponent.loadFixture('production_bwr');
    
    // In replay mode, markForCheck should be called
    expect(cdrSpy).toHaveBeenCalled();
  });
});
