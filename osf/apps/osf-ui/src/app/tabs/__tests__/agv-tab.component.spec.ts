import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { AgvTabComponent } from '../agv-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ConnectionService } from '../../services/connection.service';
import { ModuleNameService } from '../../services/module-name.service';
import { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import { AgvRouteService } from '../../services/agv-route.service';
import { AgvAnimationService } from '../../services/agv-animation.service';
import { LanguageService } from '../../services/language.service';
import { ShopfloorLayoutService } from '../../services/shopfloor-layout.service';
import { ChangeDetectorRef } from '@angular/core';
import * as mockDashboard from '../../mock-dashboard';
import { ORBIS_COLORS } from '../../assets/color-palette';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    orders$: of({}),
    ftsStates$: of({}),
  },
  commands: {
    setFtsCharge: jest.fn(),
    dockFts: jest.fn(),
    clearLoadHandlerFts: jest.fn().mockResolvedValue(undefined),
  },
  loadTabFixture: jest.fn().mockResolvedValue(undefined),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('AgvTabComponent', () => {
  let component: AgvTabComponent;
  let fixture: ComponentFixture<AgvTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;
  let ftsRouteService: jest.Mocked<AgvRouteService>;
  let ftsAnimationService: jest.Mocked<AgvAnimationService>;
  let languageService: jest.Mocked<LanguageService>;
  let cdr: jest.Mocked<ChangeDetectorRef>;
  let layoutService: jest.Mocked<ShopfloorLayoutService>;

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

    /** Mirrors `shopfloor_layout.json` fts[]: first serial = AGV-1 (orange), second = AGV-2 (warm yellow). */
    const mappingServiceMock = {
      getAgvOptions: jest.fn(() =>
        [
          { serial: '5iO4', label: 'AGV-1' },
          { serial: 'leJ4', label: 'AGV-2' },
        ] as const
      ),
      getAgvLabel: jest.fn((serial: string) =>
        serial === '5iO4' ? 'AGV-1' : serial === 'leJ4' ? 'AGV-2' : null
      ),
      getAgvColor: jest.fn((serial: string) =>
        serial === '5iO4'
          ? ORBIS_COLORS.agv.agv1
          : serial === 'leJ4'
            ? ORBIS_COLORS.agv.agv2
            : ORBIS_COLORS.orbisGrey.medium
      ),
    };

    const ftsRouteServiceMock = {
      initializeLayout: jest.fn(),
      getNodePosition: jest.fn(() => ({ x: 100, y: 100 })),
      findRoute: jest.fn(() => []),
      findRoutePath: jest.fn(() => null),
      findRoadBetween: jest.fn(() => null),
      pathToRouteSegments: jest.fn(() => []),
      resolveNodeRef: jest.fn((nodeId: string) => nodeId),
    };

    const ftsAnimationServiceMock = {
      animationState$: new BehaviorSubject({
        isAnimating: false,
        animatedPosition: null,
        animationPath: [] as string[],
        activeRouteSegments: [] as Array<{ x1: number; y1: number; x2: number; y2: number }>,
      }),
      getState: jest.fn(() => ({
        isAnimating: false,
        animatedPosition: null,
        animationPath: [] as string[],
        activeRouteSegments: [] as Array<{ x1: number; y1: number; x2: number; y2: number }>,
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

    const layoutServiceMock = {
      snapshot$: of({
        config: { cells: [], roads: [], fts: [] } as any,
        hash: '0123456789abcdef',
        url: '/shopfloor/shopfloor_layout.json',
      }),
      config$: of({ cells: [], roads: [], fts: [] } as any),
      hash$: of('0123456789abcdef'),
    };

    await TestBed.configureTestingModule({
      imports: [AgvTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ShopfloorMappingService, useValue: mappingServiceMock },
        { provide: AgvRouteService, useValue: ftsRouteServiceMock },
        { provide: AgvAnimationService, useValue: ftsAnimationServiceMock },
        { provide: LanguageService, useValue: languageServiceMock },
        { provide: ChangeDetectorRef, useValue: cdrMock },
        { provide: ShopfloorLayoutService, useValue: layoutServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AgvTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
    ftsRouteService = TestBed.inject(AgvRouteService) as any;
    ftsAnimationService = TestBed.inject(AgvAnimationService) as any;
    languageService = TestBed.inject(LanguageService) as any;
    cdr = TestBed.inject(ChangeDetectorRef) as any;
    layoutService = TestBed.inject(ShopfloorLayoutService) as any;

    // Note: ngOnInit is called automatically by Angular, but we can also call it explicitly
    // The constructor already calls initializeStreams, so ngOnInit mainly sets up connection subscription
    fixture.detectChanges();
  });

  afterEach(() => {
    (ftsRouteService.findRoutePath as jest.Mock).mockReset();
    (ftsRouteService.findRoutePath as jest.Mock).mockReturnValue(null);
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
    expect(component.combinedAgvRouteSegments$).toBeDefined();
    expect(component.currentPositionNode$).toBeDefined();
    expect(component.animationState$).toBeDefined();
  });

  it('should detect mock mode', () => {
    expect(component.isMockMode).toBe(true);
  });

  describe('Dual AGV labels (shopfloor fts[] order)', () => {
    it('maps MQTT serials to AGV-1 and AGV-2', () => {
      expect(component.getAgvLabel('5iO4')).toBe('AGV-1');
      expect(component.getAgvLabel('leJ4')).toBe('AGV-2');
      expect(component.getAgvLabel('unknown-serial')).toBeNull();
    });

    it('exposes both AGVs in layout order (AGV-1 first)', () => {
      expect(component.agvOptions.map((o) => o.serial)).toEqual(['5iO4', 'leJ4']);
      expect(component.agvOptions.map((o) => o.label)).toEqual(['AGV-1', 'AGV-2']);
    });

    it('maps AGV colors by serial like ShopfloorMappingService', () => {
      const mapping = TestBed.inject(ShopfloorMappingService);
      expect(mapping.getAgvColor('5iO4')).toBe(ORBIS_COLORS.agv.agv1);
      expect(mapping.getAgvColor('leJ4')).toBe(ORBIS_COLORS.agv.agv2);
      expect(mapping.getAgvColor('other')).toBe(ORBIS_COLORS.orbisGrey.medium);
    });
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
    
    const mappingMock = {
      getAgvOptions: () => [{ serial: '5iO4', label: 'AGV-1' }],
      getAgvLabel: () => null,
      getAgvColor: () => '#f97316',
    };
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [AgvTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: replayEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: ShopfloorMappingService, useValue: mappingMock },
        { provide: AgvRouteService, useValue: ftsRouteService },
        { provide: AgvAnimationService, useValue: ftsAnimationService },
        { provide: LanguageService, useValue: languageService },
        { provide: ChangeDetectorRef, useValue: cdr },
        {
          provide: ShopfloorLayoutService,
          useValue: {
            snapshot$: of({
              config: { cells: [], roads: [], fts: [] } as any,
              hash: '0123456789abcdef',
              url: '/shopfloor/shopfloor_layout.json',
            }),
            config$: of({ cells: [], roads: [], fts: [] } as any),
            hash$: of('0123456789abcdef'),
          },
        },
      ],
    }).compileComponents();
    
    const replayFixture = TestBed.createComponent(AgvTabComponent);
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
    expect(layoutService.snapshot$).toBeDefined();
    expect(component.layoutHashShort).toBe('01234567');
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
      imports: [AgvTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: liveEnvironmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: AgvRouteService, useValue: ftsRouteService },
        { provide: AgvAnimationService, useValue: ftsAnimationService },
        { provide: LanguageService, useValue: languageService },
        { provide: ChangeDetectorRef, useValue: cdr },
        {
          provide: ShopfloorLayoutService,
          useValue: {
            snapshot$: of({
              config: { cells: [], roads: [], fts: [] } as any,
              hash: '0123456789abcdef',
              url: '/shopfloor/shopfloor_layout.json',
            }),
            config$: of({ cells: [], roads: [], fts: [] } as any),
            hash$: of('0123456789abcdef'),
          },
        },
      ],
    }).compileComponents();
    
    const liveFixture = TestBed.createComponent(AgvTabComponent);
    const liveComponent = liveFixture.componentInstance;
    
    await liveComponent.loadFixture('startup');
    expect(liveLoadTabFixtureSpy).not.toHaveBeenCalled();
  });

  it('should handle nav target module change', () => {
    component.onNavTargetModuleChange('MILL');
    expect(component.selectedNavTargetModule).toBe('MILL');
  });

  it('should reset nav target to HBW for invalid value', () => {
    component.onNavTargetModuleChange('INVALID');
    expect(component.selectedNavTargetModule).toBe('HBW');
  });

  it('should get nav target module label', () => {
    expect(component.getNavTargetModuleLabel('MILL')).toBeDefined();
    expect(component.getNavTargetModuleLabel('DRILL')).toBeDefined();
    expect(component.getNavTargetModuleLabel('HBW')).toBeDefined();
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
    expect(component.getNavigateToTargetButtonLabel()).toContain('HBW');
  });

  it('should enable drive to selected target when route exists from reported node (default HBW)', () => {
    component.selectedNavTargetModule = 'HBW';
    (ftsRouteService.findRoutePath as jest.Mock).mockImplementation(
      (start: string, target: string) => {
        if (start === 'SVR4H73275' && target === 'SVR3QA0022') {
          return ['SVR4H73275', '2', '1', 'SVR3QA0022'];
        }
        return null;
      }
    );
    expect(component.canDriveToSelectedNavTarget(mockFtsState as never)).toBe(true);
  });

  it('should enable drive to DRILL from DPS when route exists', () => {
    component.selectedNavTargetModule = 'DRILL';
    (ftsRouteService.findRoutePath as jest.Mock).mockImplementation(
      (start: string, target: string) => {
        if (start === 'SVR4H73275' && target === 'SVR4H76449') {
          return ['SVR4H73275', 'SVR4H76449'];
        }
        return null;
      }
    );
    expect(component.canDriveToSelectedNavTarget(mockFtsState as never)).toBe(true);
  });

  it('should enable drive to Intersection 2 when IX2 selected and path exists', () => {
    component.selectedNavTargetModule = 'IX2';
    (ftsRouteService.findRoutePath as jest.Mock).mockImplementation(
      (start: string, target: string) => {
        if (start === 'SVR4H73275' && target === '2') {
          return ['SVR4H73275', '2'];
        }
        return null;
      }
    );
    expect(component.canDriveToSelectedNavTarget(mockFtsState as never)).toBe(true);
    expect(component.getNavigateToTargetButtonLabel()).toContain('Intersection');
  });

  it('should disable drive to target when FTS state is null', () => {
    (ftsRouteService.findRoutePath as jest.Mock).mockReturnValue(['SVR4H76449', 'SVR3QA0022']);
    expect(component.canDriveToSelectedNavTarget(null)).toBe(false);
    expect(component.getNavigateToTargetDisabledReason(null)).toBe(component.labelNavigateNoFtsState);
  });

  it('should disable drive to target when lastNodeId is UNKNOWN', () => {
    const unknown = { ...mockFtsState, lastNodeId: 'UNKNOWN' };
    expect(component.canDriveToSelectedNavTarget(unknown as never)).toBe(false);
    expect(component.getNavigateToTargetDisabledReason(unknown as never)).toBe(component.labelNavigatePositionUnclear);
  });

  it('should disable drive to target when already at selected target (HBW)', () => {
    (ftsRouteService.findRoutePath as jest.Mock).mockReturnValue(['SVR3QA0022']);
    component.selectedNavTargetModule = 'HBW';
    const atHbw = { ...mockFtsState, lastNodeId: 'SVR3QA0022' };
    expect(component.canDriveToSelectedNavTarget(atHbw as never)).toBe(false);
  });

  it('buildOrderFromTo should emit CCU-style node and edge ids for DPS → HBW', () => {
    const layoutPath = ['serial:SVR4H73275', 'intersection:2', 'intersection:1', 'serial:SVR3QA0022'];
    (ftsRouteService.findRoutePath as jest.Mock).mockReturnValue(layoutPath);
    (ftsRouteService.findRoadBetween as jest.Mock).mockImplementation((a: string, b: string) => {
      const segs: Record<string, { length: number; direction: 'NORTH' | 'SOUTH' | 'EAST' | 'WEST' }> = {
        'serial:SVR4H73275|intersection:2': { length: 380, direction: 'WEST' },
        'intersection:2|intersection:1': { length: 360, direction: 'WEST' },
        'intersection:1|serial:SVR3QA0022': { length: 380, direction: 'WEST' },
      };
      const key = `${a}|${b}`;
      const rev = `${b}|${a}`;
      if (segs[key]) {
        const sd = segs[key];
        return { id: 'omit', length: sd.length, direction: sd.direction, from: { ref: a }, to: { ref: b } };
      }
      if (segs[rev]) {
        const sd = segs[rev];
        return { id: 'omit', length: sd.length, direction: sd.direction, from: { ref: b }, to: { ref: a } };
      }
      return null;
    });

    const { payload, pathUsed } = (component as unknown as { buildOrderFromTo: (s: string, t: string) => unknown }).buildOrderFromTo(
      'SVR4H73275',
      'SVR3QA0022',
    ) as { payload: Record<string, unknown>; pathUsed: string[] | null };

    expect(pathUsed).toEqual(layoutPath);
    expect(payload['serialNumber']).toBe('5iO4');
    expect(payload['metadata']).toBeUndefined();
    expect(payload['orderUpdateId']).toBe(0);
    expect(payload['edges']).toEqual([
      { id: 'SVR4H73275-2', length: 380, linkedNodes: ['SVR4H73275', '2'] },
      { id: '2-1', length: 360, linkedNodes: ['2', '1'] },
      { id: '1-SVR3QA0022', length: 380, linkedNodes: ['1', 'SVR3QA0022'] },
    ]);
    const orderNodes = payload['nodes'] as Array<Record<string, unknown>>;
    expect(orderNodes.map((n) => n['id'])).toEqual(['SVR4H73275', '2', '1', 'SVR3QA0022']);
    expect(orderNodes[0]).toEqual(
      expect.objectContaining({ id: 'SVR4H73275', linkedEdges: ['SVR4H73275-2'] }),
    );
    expect(orderNodes[1]).toEqual(
      expect.objectContaining({ id: '2', linkedEdges: ['SVR4H73275-2', '2-1'], action: expect.objectContaining({ type: 'PASS' }) }),
    );
    expect(orderNodes[2]).toEqual(
      expect.objectContaining({ id: '1', linkedEdges: ['2-1', '1-SVR3QA0022'], action: expect.objectContaining({ type: 'PASS' }) }),
    );
    expect(orderNodes[3]).toEqual(
      expect.objectContaining({
        id: 'SVR3QA0022',
        linkedEdges: ['1-SVR3QA0022'],
        action: expect.objectContaining({ type: 'DOCK' }),
      }),
    );
  });

  it('buildOrderFromTo should emit TURN at intersections for DRILL → HBW (layout-accurate directions)', () => {
    const layoutPath = ['serial:SVR4H76449', 'intersection:3', 'intersection:1', 'serial:SVR3QA0022'];
    (ftsRouteService.findRoutePath as jest.Mock).mockReturnValue(layoutPath);
    (ftsRouteService.findRoadBetween as jest.Mock).mockImplementation((a: string, b: string) => {
      const segs: Record<string, { length: number; direction: 'NORTH' | 'SOUTH' | 'EAST' | 'WEST' }> = {
        'serial:SVR4H76449|intersection:3': { length: 380, direction: 'EAST' },
        'intersection:3|intersection:1': { length: 360, direction: 'NORTH' },
        'intersection:1|serial:SVR3QA0022': { length: 380, direction: 'WEST' },
      };
      const key = `${a}|${b}`;
      const rev = `${b}|${a}`;
      if (segs[key]) {
        const sd = segs[key];
        return { id: 'omit', length: sd.length, direction: sd.direction, from: { ref: a }, to: { ref: b } };
      }
      if (segs[rev]) {
        const sd = segs[rev];
        return { id: 'omit', length: sd.length, direction: sd.direction, from: { ref: b }, to: { ref: a } };
      }
      return null;
    });

    const { payload } = (component as unknown as { buildOrderFromTo: (s: string, t: string) => unknown }).buildOrderFromTo(
      'SVR4H76449',
      'SVR3QA0022',
    ) as { payload: Record<string, unknown> };
    const orderNodes = payload['nodes'] as Array<{ id?: string; action?: { type?: string; metadata?: { direction?: string } } }>;
    expect(orderNodes[1].action?.type).toBe('TURN');
    expect(orderNodes[1].action?.metadata?.direction).toBe('LEFT');
    expect(orderNodes[2].action?.type).toBe('TURN');
    expect(orderNodes[2].action?.metadata?.direction).toBe('LEFT');
  });

  describe('getSupervisorCcuReadiness', () => {
    it('returns unknown when FTS state is null', () => {
      expect(component.getSupervisorCcuReadiness(null).kind).toBe('unknown');
    });

    it('returns busy when driving', () => {
      const s = { ...mockFtsState, driving: true };
      expect(component.getSupervisorCcuReadiness(s as never).kind).toBe('busy');
    });

    it('returns busy when waiting for load handling', () => {
      const s = { ...mockFtsState, waitingForLoadHandling: true };
      expect(component.getSupervisorCcuReadiness(s as never).kind).toBe('busy');
    });

    it('returns blocked when paused', () => {
      const s = { ...mockFtsState, paused: true };
      const r = component.getSupervisorCcuReadiness(s as never);
      expect(r.kind).toBe('blocked');
      expect(r.detail).toContain('Paused');
    });

    it('returns blocked when lastNodeId is UNKNOWN', () => {
      const s = { ...mockFtsState, lastNodeId: 'UNKNOWN' };
      const r = component.getSupervisorCcuReadiness(s as never);
      expect(r.kind).toBe('blocked');
      expect(r.detail).toContain('Last node UNKNOWN');
    });

    it('returns blocked with FATAL error summary when errors include FATAL', () => {
      const s = {
        ...mockFtsState,
        errors: [{ errorLevel: 'FATAL', errorType: 'NAV_FAULT' }],
      };
      const r = component.getSupervisorCcuReadiness(s as never);
      expect(r.kind).toBe('blocked');
      expect(r.detail).toContain('NAV_FAULT');
      expect(r.detail).toContain('FATAL');
    });

    it('returns busy when primary action is not FINISHED', () => {
      const s = {
        ...mockFtsState,
        actionState: { ...mockFtsState.actionState, state: 'RUNNING' },
      };
      expect(component.getSupervisorCcuReadiness(s as never).kind).toBe('busy');
    });

    it('returns ready when stopped and action FINISHED', () => {
      const s = {
        ...mockFtsState,
        driving: false,
        waitingForLoadHandling: false,
        actionState: { ...mockFtsState.actionState, state: 'FINISHED' },
      };
      expect(component.getSupervisorCcuReadiness(s as never).kind).toBe('ready');
    });
  });

  describe('filterCcuActiveOrdersForAgv', () => {
    const serial = '5iO4';

    it('matches by FTS state orderId', () => {
      const fts = { ...mockFtsState, orderId: 'order-a' };
      const orders = [
        { orderId: 'order-a', productionSteps: [] },
        { orderId: 'order-b', productionSteps: [] },
      ];
      const r = component.filterCcuActiveOrdersForAgv(orders as never, serial, fts as never);
      expect(r).toHaveLength(1);
      expect(r[0].orderId).toBe('order-a');
    });

    it('matches by productionSteps serialNumber', () => {
      const fts = { ...mockFtsState, orderId: '' };
      const orders = [
        {
          orderId: 'x1',
          productionSteps: [{ id: '1', type: 'MANUFACTURE', state: 'RUNNING', serialNumber: 'leJ4' }],
        },
      ];
      const r = component.filterCcuActiveOrdersForAgv(orders as never, 'leJ4', fts as never);
      expect(r).toHaveLength(1);
      expect(r[0].orderId).toBe('x1');
    });

    it('dedupes when orderId and step both match', () => {
      const fts = { ...mockFtsState, orderId: 'order-a' };
      const orders = [
        {
          orderId: 'order-a',
          productionSteps: [{ id: 's', type: 'MANUFACTURE', state: 'RUNNING', serialNumber: serial }],
        },
      ];
      const r = component.filterCcuActiveOrdersForAgv(orders as never, serial, fts as never);
      expect(r).toHaveLength(1);
    });
  });

  describe('formatSupervisorCcuOrderSummary', () => {
    it('includes id state and orderType', () => {
      const line = component.formatSupervisorCcuOrderSummary({
        orderId: 'abc',
        state: 'IN_PROGRESS',
        orderType: 'PRODUCTION',
      } as never);
      expect(line).toContain('abc');
      expect(line).toContain('IN_PROGRESS');
      expect(line).toContain('PRODUCTION');
    });
  });

  it('canClearLoadHandling is true when waitingForLoadHandling', () => {
    const s = { ...mockFtsState, waitingForLoadHandling: true };
    expect(component.canClearLoadHandling(s as never)).toBe(true);
    expect(component.canClearLoadHandling(mockFtsState as never)).toBe(false);
  });

  it('sendClearLoadHandlerSupervisor calls dashboard command', async () => {
    const clearLoad = jest.fn().mockResolvedValue(undefined);
    (component as unknown as { dashboard: { commands: Record<string, jest.Mock> } }).dashboard = {
      ...((component as unknown as { dashboard: object }).dashboard ?? {}),
      commands: {
        setFtsCharge: jest.fn(),
        dockFts: jest.fn(),
        clearLoadHandlerFts: clearLoad,
      },
    };
    await component.sendClearLoadHandlerSupervisor();
    expect(clearLoad).toHaveBeenCalledWith('5iO4', { loadDropped: false });
  });

  describe('planned route overlay (driving + destination)', () => {
    const orderThreeNodes = {
      nodes: [{ id: 'A' }, { id: 'B' }, { id: 'DEST' }],
    };

    const asOverlay = (s: unknown, o: unknown) =>
      (
        component as unknown as {
          shouldShowPlannedRouteOverlay: (state: unknown, order: unknown) => boolean;
        }
      ).shouldShowPlannedRouteOverlay(s, o);

    it('shows when driving even if reported at destination node', () => {
      expect(
        asOverlay({ ...mockFtsState, lastNodeId: 'DEST', driving: true }, orderThreeNodes),
      ).toBe(true);
    });

    it('hides when stationary at last order node (C)', () => {
      expect(
        asOverlay({ ...mockFtsState, lastNodeId: 'DEST', driving: false }, orderThreeNodes),
      ).toBe(false);
    });

    it('shows when stationary but not yet at last node', () => {
      expect(
        asOverlay({ ...mockFtsState, lastNodeId: 'B', driving: false }, orderThreeNodes),
      ).toBe(true);
    });

    it('shows when lastNodeId missing and not driving', () => {
      expect(
        asOverlay({ ...mockFtsState, lastNodeId: '', driving: false }, orderThreeNodes),
      ).toBe(true);
    });
  });
});

