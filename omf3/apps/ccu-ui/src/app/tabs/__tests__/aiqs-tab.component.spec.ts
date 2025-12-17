import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { AiqsTabComponent } from '../aiqs-tab.component';
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

describe('AiqsTabComponent', () => {
  let component: AiqsTabComponent;
  let fixture: ComponentFixture<AiqsTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;
  let cdr: jest.Mocked<ChangeDetectorRef>;

  const mockAiqsState = {
    serialNumber: 'SVR4H76530',
    timestamp: '2025-11-10T18:00:00Z',
    orderId: 'test-order-123',
    orderUpdateId: 1,
    connectionState: 'ONLINE' as const,
    available: 'READY' as const,
    actionState: {
      id: 'action-1',
      command: 'CHECK_QUALITY' as const,
      state: 'FINISHED' as const,
      timestamp: '2025-11-10T18:00:00Z',
      result: 'PASSED' as const,
    },
    actionStates: [
      {
        id: 'action-1',
        command: 'CHECK_QUALITY' as const,
        state: 'FINISHED' as const,
        timestamp: '2025-11-10T18:00:00Z',
        result: 'PASSED' as const,
      },
      {
        id: 'action-2',
        command: 'CHECK_QUALITY' as const,
        state: 'FINISHED' as const,
        timestamp: '2025-11-10T18:01:00Z',
        result: 'FAILED' as const,
      },
    ],
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
      imports: [AiqsTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ChangeDetectorRef, useValue: cdrMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AiqsTabComponent);
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
    expect(component.aiqsState$).toBeDefined();
    expect(component.connection$).toBeDefined();
    expect(component.aiqsOrder$).toBeDefined();
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
      imports: [AiqsTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: replayEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: ChangeDetectorRef, useValue: cdr },
      ],
    }).compileComponents();
    
    const replayFixture = TestBed.createComponent(AiqsTabComponent);
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
    expect(component.getConnectionStatus(mockAiqsState)).toBe('ONLINE');
    expect(component.getConnectionStatus(null)).toBe('OFFLINE');
  });

  it('should get availability', () => {
    expect(component.getAvailability(mockAiqsState)).toBe('READY');
    expect(component.getAvailability(null)).toBe('UNKNOWN');
  });

  it('should get current action', () => {
    const action = component.getCurrentAction(mockAiqsState);
    expect(action).toBeDefined();
    expect(action?.command).toBe('CHECK_QUALITY');
  });

  it('should get recent actions', () => {
    const actions = component.getRecentActions(mockAiqsState);
    expect(Array.isArray(actions)).toBe(true);
  });

  it('should get quality checks', () => {
    const checks = component.getQualityChecks(mockAiqsState);
    expect(checks.length).toBe(2);
    expect(checks.every(c => c.command === 'CHECK_QUALITY')).toBe(true);
  });

  it('should get total checks count', () => {
    expect(component.getTotalChecks(mockAiqsState)).toBe(2);
  });

  it('should get passed count', () => {
    expect(component.getPassedCount(mockAiqsState)).toBe(1);
  });

  it('should get failed count', () => {
    expect(component.getFailedCount(mockAiqsState)).toBe(1);
  });

  it('should calculate success rate', () => {
    expect(component.getSuccessRate(mockAiqsState)).toBe(50);
  });

  it('should handle zero checks for success rate', () => {
    expect(component.getSuccessRate(null)).toBe(0);
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
    const formatted = component.formatTimestamp('2025-11-10T18:00:00Z');
    expect(formatted).toBeDefined();
  });

  it('should display order ID correctly', () => {
    expect(component.getOrderIdDisplay('short')).toBe('short');
    expect(component.getOrderIdDisplay('very-long-order-id-that-exceeds-12-chars')).toContain('...');
    expect(component.getOrderIdDisplay(undefined)).toBeDefined();
  });

  it('should track actions by ID', () => {
    const action = mockAiqsState.actionState;
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
      imports: [AiqsTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: replayEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: ChangeDetectorRef, useValue: mockCdr },
      ],
    }).compileComponents();
    
    const replayFixture = TestBed.createComponent(AiqsTabComponent);
    const replayComponent = replayFixture.componentInstance;
    
    // Spy on the actual component's cdr
    const cdrSpy = jest.spyOn(replayComponent['cdr'], 'markForCheck');
    
    await replayComponent.loadFixture('production_bwr');
    
    // In replay mode, markForCheck should be called
    expect(cdrSpy).toHaveBeenCalled();
  });
});
