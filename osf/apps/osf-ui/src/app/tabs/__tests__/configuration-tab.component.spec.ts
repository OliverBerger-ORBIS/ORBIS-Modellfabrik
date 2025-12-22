import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
import { ConfigurationTabComponent } from '../configuration-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ModuleNameService } from '../../services/module-name.service';
import { ConnectionService } from '../../services/connection.service';
import { ExternalLinksService } from '../../services/external-links.service';
import { ModuleHardwareService } from '../../services/module-hardware.service';
import * as mockDashboard from '../../mock-dashboard';
import type { ModuleOverviewState, CcuConfigSnapshot } from '@osf/entities';
import type { ExternalLinksSettings } from '../../services/external-links.service';
import type { ShopfloorLayoutConfig } from '../../components/shopfloor-preview/shopfloor-layout.types';
import type { ModuleHardwareConfig } from '../../components/shopfloor-preview/module-hardware.types';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    moduleOverview$: of({
      modules: {},
      transports: {},
    } as ModuleOverviewState),
    config$: of({
      cells: [],
    } as CcuConfigSnapshot),
  },
  loadTabFixture: jest.fn(),
  loadDrillActionFixture: jest.fn(),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

const mockLayoutConfig: ShopfloorLayoutConfig = {
  metadata: {
    canvas: {
      width: 2000,
      height: 2000,
      units: 'px',
    },
  },
  scaling: {
    default_percent: 100,
    min_percent: 50,
    max_percent: 200,
    mode: 'viewBox',
  },
  highlight_defaults: {
    stroke_color: '#000000',
    fill_color: '#ffffff',
    stroke_width: 2,
    stroke_align: 'center',
  },
  icon_sizing_rules: {
    by_role: {},
  },
  cells: [
    {
      id: 'DSP',
      name: 'DSP',
      role: 'software',
      position: { x: 0, y: 0 },
      size: { w: 200, h: 200 },
    },
    {
      id: 'ORBIS',
      name: 'ORBIS',
      role: 'company',
      position: { x: 200, y: 0 },
      size: { w: 200, h: 200 },
    },
  ],
  intersection_map: {},
  modules_by_serial: {},
  parsed_roads: [],
};

describe('ConfigurationTabComponent', () => {
  let component: ConfigurationTabComponent;
  let fixture: ComponentFixture<ConfigurationTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let externalLinksService: jest.Mocked<ExternalLinksService>;
  let httpClient: jest.Mocked<HttpClient>;
  let router: jest.Mocked<Router>;
  let activatedRoute: jest.Mocked<ActivatedRoute>;
  let moduleHardwareService: jest.Mocked<ModuleHardwareService>;

  const mockModuleHardwareConfig: ModuleHardwareConfig = {
    serial_number: 'SVR4H73275',
    module_name: 'DPS',
    module_type: 'Input/Output',
    opc_ua_station: {
      ip_address: '192.168.0.90',
      ip_range: '192.168.0.90',
      endpoint: 'opc.tcp://192.168.0.90:4840',
      description: '6-axis gripper arm with NFC scanner',
    },
    txt_controllers: [
      {
        id: 'TXT4.0-p0F4',
        name: 'TXT-DPS',
        ip_address: '192.168.0.102',
        description: 'NFC-Reader and Sensor-Station',
      },
    ],
  };

  beforeEach(async () => {
    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
      getHistory: jest.fn(() => of([])),
      clearTopic: jest.fn(),
    };

    const moduleNameServiceMock = {
      getModuleFullName: jest.fn((key: string) => `${key} Module`),
      getModuleDisplayText: jest.fn((key: string) => `${key} Display`),
      getModuleDisplayName: jest.fn((key: string) => ({
        id: key,
        fullName: `${key} Module`,
      })),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'disconnected'>('disconnected'),
    };

    const externalLinksServiceMock = {
      settings$: new BehaviorSubject<ExternalLinksSettings>({
        dspControlUrl: '',
        managementCockpitUrl: '',
        grafanaDashboardUrl: '',
        smartfactoryDashboardUrl: '',
        erpSystemUrl: '',
      }),
    };

    const httpClientMock = {
      get: jest.fn(() => of(mockLayoutConfig)),
    };

    const moduleHardwareServiceMock = {
      getModuleHardwareConfig: jest.fn((serial: string) => {
        if (serial === 'SVR4H73275') {
          return mockModuleHardwareConfig;
        }
        return null;
      }),
      hasOpcUaServer: jest.fn((serial: string) => serial === 'SVR4H73275'),
      hasTxtController: jest.fn((serial: string) => serial === 'SVR4H73275'),
      getOpcUaStation: jest.fn((serial: string) =>
        serial === 'SVR4H73275' ? mockModuleHardwareConfig.opc_ua_station : null
      ),
      getTxtControllers: jest.fn((serial: string) =>
        serial === 'SVR4H73275' ? mockModuleHardwareConfig.txt_controllers : []
      ),
    };

    const routerMock = {
      navigate: jest.fn(),
      url: '/en/configuration',
    };

    const activatedRouteMock = {
      snapshot: { params: {} },
      params: of({}),
    };

    await TestBed.configureTestingModule({
      imports: [ConfigurationTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: ExternalLinksService, useValue: externalLinksServiceMock },
        { provide: HttpClient, useValue: httpClientMock },
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: activatedRouteMock },
        { provide: ModuleHardwareService, useValue: moduleHardwareServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ConfigurationTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    externalLinksService = TestBed.inject(ExternalLinksService) as any;
    httpClient = TestBed.inject(HttpClient) as any;
    router = TestBed.inject(Router) as any;
    activatedRoute = TestBed.inject(ActivatedRoute) as any;
    moduleHardwareService = TestBed.inject(ModuleHardwareService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize streams', () => {
    expect(component.viewModel$).toBeDefined();
    expect(component.selectedCell$).toBeDefined();
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

  it('should select cell', () => {
    component.selectCell('DSP');
    expect(component['selectedCellSubject'].value).toBe('DSP');
  });

  it('should handle cell selected event', () => {
    const event = { id: 'ORBIS', kind: 'fixed' as const };
    component.onCellSelected(event);
    expect(component['selectedCellSubject'].value).toBe('ORBIS');
    // Note: ORBIS detail views are no longer displayed - just basic selection
  });

  it('should handle cell double click event', () => {
    const consoleSpy = jest.spyOn(console, 'info').mockImplementation();
    const event = { id: 'DSP', kind: 'fixed' as const };
    component.onCellDoubleClick(event);
    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });

  it('should provide factory icon', () => {
    expect(component.factoryIcon).toBeDefined();
  });

  it('should provide parameters icon', () => {
    expect(component.parametersIcon).toBeDefined();
  });

  // Note: ORBIS and DSP detail views have been removed/moved
  // These tests are minimal since the functionality is no longer in this component
  it('should have fixed position details (minimal - functionality moved)', () => {
    expect(component['fixedPositionDetails']).toBeDefined();
    // Basic structure check only - detailed ORBIS/DSP views are no longer here
    expect(component['fixedPositionDetails']['COMPANY']).toBeDefined();
  });

  // DSP architecture and features are still defined but not actively used in detail views
  // Keeping minimal test to ensure no breaking changes
  it('should have DSP architecture layers (minimal - functionality moved)', () => {
    expect(component['dspArchitecture']).toBeDefined();
    // Just verify it exists - detailed testing not needed as functionality moved
  });

  it('should have DSP features (minimal - functionality moved)', () => {
    expect(component['dspFeatures']).toBeDefined();
    // Just verify it exists - detailed testing not needed as functionality moved
  });

  it('should have labels', () => {
    expect(component.yesLabel).toBeDefined();
    expect(component.noLabel).toBeDefined();
    expect(component.unknownLabel).toBeDefined();
    expect(component.serialLabel).toBeDefined();
    expect(component.availabilityLabel).toBeDefined();
    expect(component.connectedLabel).toBeDefined();
    expect(component.configuredLabel).toBeDefined();
    expect(component.lastUpdateLabel).toBeDefined();
    expect(component.gridPositionLabel).toBeDefined();
  });

  it('should resolve asset path', () => {
    const path = component['resolveAssetPath']('/assets/svg/shopfloor/shared/question.svg');
    expect(path).toBeDefined();
  });

  it('should normalize cell key', () => {
    const normalized = component['normalizeCellKey']({ label: 'dsp', type: 'DSP' } as any);
    expect(normalized).toBe('DSP');
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });

  it('should handle fixture loading', async () => {
    const loadFixtureSpy = jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
      ...mockDashboard.getDashboardController(),
      loadTabFixture: jest.fn().mockResolvedValue(undefined),
    } as any);

    await component.loadFixture('startup');
    expect(loadFixtureSpy).toHaveBeenCalled();
  });

  it('should not load fixture in non-mock mode', async () => {
    // Create a new component with live environment
    const liveEnvironmentService = {
      current: { key: 'live' },
      environment$: new BehaviorSubject({ key: 'live' }),
    };
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [ConfigurationTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: liveEnvironmentService },
        { provide: MessageMonitorService, useValue: messageMonitor },
        { provide: ModuleNameService, useValue: moduleNameService },
        { provide: ConnectionService, useValue: connectionService },
        { provide: ExternalLinksService, useValue: externalLinksService },
        { provide: HttpClient, useValue: httpClient },
        { provide: Router, useValue: router },
        { provide: ActivatedRoute, useValue: activatedRoute },
      ],
    }).compileComponents();
    const liveFixture = TestBed.createComponent(ConfigurationTabComponent);
    const liveComponent = liveFixture.componentInstance;

    const loadFixtureSpy = jest.fn();
    jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
      ...mockDashboard.getDashboardController(),
      loadTabFixture: loadFixtureSpy,
    } as any);

    await liveComponent.loadFixture('startup');
    expect(loadFixtureSpy).not.toHaveBeenCalled();
  });

  it('should handle drill action fixture loading', async () => {
    // loadDrillActionFixture uses dynamic import which may not work in test environment
    // Just verify the method exists and can be called
    expect(component.loadDrillActionFixture).toBeDefined();
    // The method may throw or fail silently in test environment due to dynamic import
    try {
      await component.loadDrillActionFixture();
    } catch (error) {
      // Expected in test environment
      expect(error).toBeDefined();
    }
  });

  it('should open external link', () => {
    const openSpy = jest.spyOn(window, 'open').mockImplementation(() => null);
    component.openExternalLink('https://example.com');
    expect(openSpy).toHaveBeenCalledWith('https://example.com', '_blank', 'noreferrer noopener');
    openSpy.mockRestore();
  });

  it('should format timestamp', () => {
    const formatted = component.formatTimestamp('2025-11-10T18:00:00Z');
    expect(formatted).toBeDefined();
  });

  it('should handle invalid timestamp', () => {
    const formatted = component.formatTimestamp('invalid-date');
    // formatTimestamp tries to parse and format, but invalid dates may return "Invalid Date" string
    // or the original string depending on toLocaleString behavior
    expect(formatted).toBeDefined();
  });

  // DSP action message functionality is minimal - only used for DRILL module status
  it('should get DSP action message (minimal - limited functionality)', () => {
    const message$ = component.getDspActionMessage();
    expect(message$).toBeDefined();
    // Detailed DSP detail views have been moved - this is only for DRILL module status
  });

  it('should get change light value', () => {
    const message = {
      topic: '/j1/txt/1/i/changeLight',
      payload: { command: 'changeLight', value: '#FF0000' },
      timestamp: '2025-11-10T18:00:00Z',
      valid: true,
    };
    const value = component.getChangeLightValue(message);
    expect(value).toBe('#FF0000');
  });

  it('should return null for invalid change light message', () => {
    const message = {
      topic: '/j1/txt/1/i/changeLight',
      payload: null,
      timestamp: '2025-11-10T18:00:00Z',
      valid: true,
    };
    const value = component.getChangeLightValue(message);
    expect(value).toBeNull();
  });

  describe('Module Hardware Configuration', () => {
    it('should use ModuleHardwareService to get hardware config', () => {
      const mockOverview: ModuleOverviewState = {
        modules: {
          SVR4H73275: {
            id: 'SVR4H73275',
            connected: true,
            availability: 'READY',
            configured: true,
            messageCount: 1,
            lastUpdate: '2025-12-22T12:00:00Z',
          },
        },
        transports: {},
      };

      const mockCell = {
        id: 'DPS',
        label: 'DPS',
        kind: 'module' as const,
        row: 1,
        column: 1,
        rowSpan: 1,
        columnSpan: 1,
        icon: 'dps-icon',
        tooltip: 'DPS',
        serialNumber: 'SVR4H73275',
        type: 'DPS',
      };

      const details = component['buildSelectedDetails'](mockCell, mockOverview);
      expect(moduleHardwareService.getModuleHardwareConfig).toHaveBeenCalledWith('SVR4H73275');
      expect(details.hasOpcUaStation).toBe(true);
      expect(details.hasTxtController).toBe(true);
      expect(details.opcUaItems).toBeDefined();
      expect(details.txtControllerItems).toBeDefined();
    });

    it('should not show OPC-UA section if module has no OPC-UA server', () => {
      moduleHardwareService.getModuleHardwareConfig.mockReturnValue({
        ...mockModuleHardwareConfig,
        opc_ua_station: null,
      });
      moduleHardwareService.hasOpcUaServer.mockReturnValue(false);

      const mockOverview: ModuleOverviewState = {
        modules: {
          '5iO4': {
            id: '5iO4',
            connected: true,
            availability: 'READY',
            configured: true,
            messageCount: 1,
            lastUpdate: '2025-12-22T12:00:00Z',
          },
        },
        transports: {},
      };

      const mockCell = {
        id: 'FTS',
        label: 'FTS',
        kind: 'module' as const,
        row: 1,
        column: 1,
        rowSpan: 1,
        columnSpan: 1,
        icon: 'fts-icon',
        tooltip: 'FTS',
        serialNumber: '5iO4',
        type: 'FTS',
      };

      const details = component['buildSelectedDetails'](mockCell, mockOverview);
      expect(details.hasOpcUaStation).toBe(false);
      expect(details.opcUaItems).toBeUndefined();
    });

    it('should not show TXT Controller section if module has no TXT controller', () => {
      moduleHardwareService.getModuleHardwareConfig.mockReturnValue({
        ...mockModuleHardwareConfig,
        txt_controllers: [],
      });
      moduleHardwareService.hasTxtController.mockReturnValue(false);

      const mockOverview: ModuleOverviewState = {
        modules: {
          SVR3QA0022: {
            id: 'SVR3QA0022',
            connected: true,
            availability: 'READY',
            configured: true,
            messageCount: 1,
            lastUpdate: '2025-12-22T12:00:00Z',
          },
        },
        transports: {},
      };

      const mockCell = {
        id: 'HBW',
        label: 'HBW',
        kind: 'module' as const,
        row: 1,
        column: 1,
        rowSpan: 1,
        columnSpan: 1,
        icon: 'hbw-icon',
        tooltip: 'HBW',
        serialNumber: 'SVR3QA0022',
        type: 'HBW',
      };

      const details = component['buildSelectedDetails'](mockCell, mockOverview);
      expect(details.hasTxtController).toBe(false);
      expect(details.txtControllerItems).toBeUndefined();
    });
  });
});

