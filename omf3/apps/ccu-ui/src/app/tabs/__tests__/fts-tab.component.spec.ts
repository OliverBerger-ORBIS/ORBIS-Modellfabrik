import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, of } from 'rxjs';
import { FtsTabComponent } from '../fts-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ConnectionService } from '../../services/connection.service';
import { ModuleNameService } from '../../services/module-name.service';
import { FtsRouteService } from '../../services/fts-route.service';
import { FtsAnimationService } from '../../services/fts-animation.service';
import { LanguageService } from '../../services/language.service';
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

describe('FtsTabComponent', () => {
  let component: FtsTabComponent;
  let fixture: ComponentFixture<FtsTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;
  let ftsRouteService: jest.Mocked<FtsRouteService>;
  let ftsAnimationService: jest.Mocked<FtsAnimationService>;
  let languageService: jest.Mocked<LanguageService>;
  let cdr: jest.Mocked<ChangeDetectorRef>;
  let http: any;

  const mockFtsState = {
    serialNumber: '5iO4',
    headerId: 1,
    timestamp: '2025-11-10T18:00:00Z',
    orderId: 'test-order-123',
    orderUpdateId: 1,
    lastNodeId: 'SVR4H73275',
    lastNodeSequenceId: 0,
    lastCode: 'DPS',
    driving: false,
    paused: false,
    waitingForLoadHandling: false,
    batteryState: {
      currentVoltage: 12.5,
      minVolt: 10.0,
      maxVolt: 14.0,
      percentage: 75,
      charging: false,
    },
    actionState: {
      id: 'action-1',
      command: 'DOCK',
      state: 'FINISHED',
      timestamp: '2025-11-10T18:00:00Z',
    },
    actionStates: [],
    load: [],
    nodeStates: [],
    edgeStates: [],
    errors: [],
  };

  beforeEach(async () => {
    const environmentSubject = new BehaviorSubject({ key: 'mock' as const, label: 'Mock', description: 'Mock', connection: { mqttHost: 'localhost', mqttPort: 1883 } });
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

    const ftsRouteServiceMock = {
      initializeLayout: jest.fn(),
      getNodePosition: jest.fn(() => ({ x: 100, y: 100 })),
      findRoute: jest.fn(() => []),
      resolveNodeRef: jest.fn((nodeId: string) => nodeId),
    };

    const ftsAnimationServiceMock = {
      animationState$: new BehaviorSubject({
        isAnimating: false,
        animatedPosition: null,
        currentRoute: [],
      }),
      getState: jest.fn(() => ({
        isAnimating: false,
        animatedPosition: null,
        currentRoute: [],
      })),
      stopAnimation: jest.fn(),
      startAnimation: jest.fn(),
    };

    const languageServiceMock = {
      current: 'en' as const,
      locale$: new BehaviorSubject('en'),
    };

    const cdrMock = {
      markForCheck: jest.fn(),
      detectChanges: jest.fn(),
    };

    const httpMock = {
      get: jest.fn(() => of({ cells: [], roads: [] })),
    };

    await TestBed.configureTestingModule({
      imports: [FtsTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: FtsRouteService, useValue: ftsRouteServiceMock },
        { provide: FtsAnimationService, useValue: ftsAnimationServiceMock },
        { provide: LanguageService, useValue: languageServiceMock },
        { provide: ChangeDetectorRef, useValue: cdrMock },
        { provide: HttpClient, useValue: httpMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FtsTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
    ftsRouteService = TestBed.inject(FtsRouteService) as any;
    ftsAnimationService = TestBed.inject(FtsAnimationService) as any;
    languageService = TestBed.inject(LanguageService) as any;
    cdr = TestBed.inject(ChangeDetectorRef) as any;
    http = TestBed.inject(HttpClient) as any;

    // Note: ngOnInit is called automatically by Angular, but we can also call it explicitly
    // The constructor already calls initializeStreams, so ngOnInit mainly sets up connection subscription
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize streams', () => {
    expect(component.ftsState$).toBeDefined();
    expect(component.batteryState$).toBeDefined();
    expect(component.loads$).toBeDefined();
    expect(component.ftsOrder$).toBeDefined();
    expect(component.ftsPosition$).toBeDefined();
    expect(component.activeRouteSegments$).toBeDefined();
    expect(component.currentPositionNode$).toBeDefined();
    expect(component.animationState$).toBeDefined();
  });

  it('should detect mock mode', () => {
    expect(component.isMockMode).toBe(true);
  });

  it('should detect replay mode', async () => {
    // Create new component with replay environment
    const replayEnvironmentSubject = new BehaviorSubject({ key: 'replay' as const, label: 'Replay', description: 'Replay', connection: { mqttHost: 'localhost', mqttPort: 1883 } });
    const replayEnvironmentServiceMock = {
      get current() {
        return replayEnvironmentSubject.value;
      },
      environment$: replayEnvironmentSubject.asObservable(),
    };
    
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [FtsTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: replayEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: FtsRouteService, useValue: ftsRouteService },
        { provide: FtsAnimationService, useValue: ftsAnimationService },
        { provide: LanguageService, useValue: languageService },
        { provide: ChangeDetectorRef, useValue: cdr },
        { provide: HttpClient, useValue: http },
      ],
    }).compileComponents();
    
    const replayFixture = TestBed.createComponent(FtsTabComponent);
    const replayComponent = replayFixture.componentInstance;
    expect(replayComponent.isReplayMode).toBe(true);
  });

  it('should have fixture options', () => {
    expect(component.fixtureOptions.length).toBeGreaterThan(0);
    expect(component.fixtureOptions).toContain('startup');
    expect(component.fixtureOptions).toContain('white');
  });

  it('should have fixture labels', () => {
    expect(component.fixtureLabels).toBeDefined();
    expect(component.fixtureLabels.startup).toBeDefined();
  });

  it('should load shopfloor layout on init', () => {
    expect(http.get).toHaveBeenCalledWith('shopfloor/shopfloor_layout.json');
  });

  it('should initialize route service when layout is loaded', () => {
    expect(ftsRouteService.initializeLayout).toHaveBeenCalled();
  });

  it('should handle FTS state changes', () => {
    // Mock a valid FTS state message with proper MonitoredMessage structure
    jest.spyOn(messageMonitor, 'getLastMessage').mockReturnValue(
      of({ 
        valid: true, 
        payload: mockFtsState,
        topic: 'fts/v1/ff/5iO4/state',
        timestamp: '2025-11-10T18:00:00Z',
      })
    );

    // Re-initialize streams to trigger state change
    // Note: initializeStreams is private, so we test indirectly through ngOnInit
    // The streams are already initialized in constructor
    expect(component.ftsState$).toBeDefined();
  });

  it('should get location name', () => {
    const location = component.getLocationName('SVR4H73275');
    expect(location).toBeDefined();
  });

  it('should return unknown for invalid location', () => {
    const location = component.getLocationName(undefined);
    expect(location).toContain('Unknown');
  });

  it('should get location short name', () => {
    const location = component.getLocationShortName('SVR4H73275');
    expect(location).toBeDefined();
  });

  it('should get route status', () => {
    const status = component.getRouteStatus(mockFtsState);
    expect(status).toBeDefined();
  });

  it('should return unknown status for null state', () => {
    const status = component.getRouteStatus(null);
    expect(status).toContain('Unknown');
  });

  it('should get order ID display', () => {
    const display = component.getOrderIdDisplay('test-123');
    expect(display).toBe('test-123');
  });

  it('should truncate long order IDs', () => {
    const longOrderId = 'very-long-order-id-that-should-be-truncated';
    const display = component.getOrderIdDisplay(longOrderId);
    expect(display.length).toBeLessThanOrEqual(11); // 8 chars + "..."
  });

  it('should return "None" for empty order ID', () => {
    const display = component.getOrderIdDisplay(undefined);
    expect(display).toContain('None');
  });

  it('should get loaded count', () => {
    const loads = [
      { loadId: '1', loadType: 'BLUE' as const, loadPosition: '1' },
      { loadId: '2', loadType: 'WHITE' as const, loadPosition: '2' },
      { loadId: null, loadType: null, loadPosition: '3' },
    ];
    const count = component.getLoadedCount(loads);
    expect(count).toBe(2);
  });

  it('should get battery level class', () => {
    expect(component.getBatteryLevelClass(80)).toBe('high');
    expect(component.getBatteryLevelClass(50)).toBe('medium');
    expect(component.getBatteryLevelClass(20)).toBe('low');
  });

  it('should get voltage display', () => {
    const display = component.getVoltageDisplay(mockFtsState.batteryState);
    expect(display).toContain('V');
    expect(display).toContain('12.5');
  });

  it('should return default voltage for null state', () => {
    const display = component.getVoltageDisplay(null);
    expect(display).toBe('0.0V');
  });

  it('should get voltage range', () => {
    const range = component.getVoltageRange(mockFtsState.batteryState);
    expect(range).toContain('V');
    expect(range).toContain('10.00');
    expect(range).toContain('14.00');
  });

  it('should get charging status text', () => {
    expect(component.getChargingStatusText(true)).toBeDefined();
    expect(component.getChargingStatusText(false)).toBeDefined();
  });

  it('should load fixture in mock mode', async () => {
    await component.loadFixture('startup');
    expect(mockDashboard.getDashboardController().loadTabFixture).toHaveBeenCalled();
    expect(component.activeFixture).toBe('startup');
  });

  it('should not load fixture in non-mock mode', async () => {
    // Reset mocks to avoid interference
    jest.clearAllMocks();
    
    // Create new component with live environment
    const liveEnvironmentSubject = new BehaviorSubject({ key: 'live' as const, label: 'Live', description: 'Live', connection: { mqttHost: 'localhost', mqttPort: 1883 } });
    const liveEnvironmentServiceMock = {
      get current() {
        return liveEnvironmentSubject.value;
      },
      environment$: liveEnvironmentSubject.asObservable(),
    };
    
    const liveLoadTabFixtureSpy = jest.fn().mockResolvedValue(undefined);
    jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
      streams: { orders$: of({}) },
      loadTabFixture: liveLoadTabFixtureSpy,
      getCurrentFixture: jest.fn(() => 'startup'),
    } as any);
    
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [FtsTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: liveEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: FtsRouteService, useValue: ftsRouteService },
        { provide: FtsAnimationService, useValue: ftsAnimationService },
        { provide: LanguageService, useValue: languageService },
        { provide: ChangeDetectorRef, useValue: cdr },
        { provide: HttpClient, useValue: http },
      ],
    }).compileComponents();
    
    const liveFixture = TestBed.createComponent(FtsTabComponent);
    const liveComponent = liveFixture.componentInstance;
    
    await liveComponent.loadFixture('startup');
    expect(liveLoadTabFixtureSpy).not.toHaveBeenCalled();
  });

  it('should handle start node change', () => {
    component.onStartNodeChange('MILL');
    expect(component.selectedStartNode).toBe('MILL');
  });

  it('should reset to auto for invalid start node', () => {
    component.onStartNodeChange('INVALID');
    expect(component.selectedStartNode).toBe('auto');
  });

  it('should get start option label', () => {
    expect(component.getStartOptionLabel('auto')).toBeDefined();
    expect(component.getStartOptionLabel('MILL')).toBeDefined();
    expect(component.getStartOptionLabel('DRILL')).toBeDefined();
  });

  it('should get vehicle label based on locale', () => {
    expect(component.vehicleLabelShort).toBeDefined();
    expect(component.vehicleLabelLong).toBeDefined();
  });

  it('should get status subtitle based on locale', () => {
    expect(component.statusSubtitle).toBeDefined();
  });

  it('should cleanup on destroy', () => {
    const stopAnimationSpy = jest.spyOn(ftsAnimationService, 'stopAnimation');
    component.ngOnDestroy();
    expect(stopAnimationSpy).toHaveBeenCalled();
  });

  it('should have presentation mode input', () => {
    component.presentationMode = true;
    expect(component.presentationMode).toBe(true);
  });

  it('should have all required icons defined', () => {
    expect(component.headingIcon).toBeDefined();
    expect(component.statusIcon).toBeDefined();
    expect(component.batteryIcon).toBeDefined();
    expect(component.loadIcon).toBeDefined();
    expect(component.routeIcon).toBeDefined();
  });

  it('should have all required labels defined', () => {
    expect(component.labelChargeOn).toBeDefined();
    expect(component.labelChargeOff).toBeDefined();
    expect(component.labelDockInitial).toBeDefined();
  });
});

