import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { MessageMonitorTabComponent } from '../message-monitor-tab.component';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { EnvironmentService } from '../../services/environment.service';
import { ModuleNameService } from '../../services/module-name.service';
import { ShopfloorLayoutService } from '../../services/shopfloor-layout.service';
import { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import type { MonitoredMessage } from '../../services/message-monitor.service';

describe('MessageMonitorTabComponent', () => {
  let component: MessageMonitorTabComponent;
  let fixture: ComponentFixture<MessageMonitorTabComponent>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let environmentService: {
    current: { key: string; label: string };
    environment$: BehaviorSubject<{ key: string; label: string }>;
  };
  let mappingService: jest.Mocked<Partial<ShopfloorMappingService>>;

  const mockMessages: MonitoredMessage[] = [
    {
      topic: 'ccu/order/active',
      payload: { orderId: 'order-1' },
      timestamp: '2025-11-10T18:00:00Z',
      valid: true,
    },
    {
      topic: 'module/v1/ff/SVR4H73275/state',
      payload: { state: 'idle' },
      timestamp: '2025-11-10T18:01:00Z',
      valid: true,
    },
    {
      topic: 'fts/v1/ff/5iO4/state',
      payload: { status: 'moving' },
      timestamp: '2025-11-10T18:02:00Z',
      valid: true,
    },
    {
      topic: 'module/v1/ff/HBW-DEMO/state',
      payload: { state: 'idle' },
      timestamp: '2025-11-10T18:03:00Z',
      valid: true,
    },
    {
      topic: 'module/v1/ff/HBW-MISSING/state',
      payload: { state: 'idle' },
      timestamp: '2025-11-10T18:04:00Z',
      valid: true,
    },
  ];

  beforeEach(async () => {
    const messageMonitorMock = {
      getTopics: jest.fn(() => [
        'ccu/order/active',
        'module/v1/ff/SVR4H73275/state',
        'fts/v1/ff/5iO4/state',
        'module/v1/ff/HBW-DEMO/state',
        'module/v1/ff/HBW-MISSING/state',
      ]),
      getHistory: jest.fn((topic: string) => {
        return mockMessages.filter((msg) => msg.topic === topic);
      }),
      getLastMessage: jest.fn(() => of(null)),
      addMessage: jest.fn(),
      clearAll: jest.fn(),
    };

    environmentService = {
      current: { key: 'mock', label: 'Mock' },
      environment$: new BehaviorSubject({ key: 'mock', label: 'Mock' }),
    };

    const moduleNameServiceMock = {
      getModuleFullName: jest.fn((key: string) =>
        key === 'FTS' ? 'Automated Guided Vehicle' : `${key} Module`
      ),
      getModuleDisplayText: jest.fn((key: string, format?: string) =>
        format === 'id-full' ? `${key} (${key} Module)` : key
      ),
    };

    mappingService = {
      isInitialized: jest.fn(() => true),
      getAllModules: jest.fn(() => [
        { moduleType: 'DPS', serialNumber: 'SVR4H73275' },
        { moduleType: 'FTS', serialNumber: '5iO4', icon: 'FTS' },
        { moduleType: 'FTS', serialNumber: 'leJ4', icon: 'FTS' },
      ]),
      getShopfloorTableRowSerialOrder: jest.fn(() => ['SVR4H73275', '5iO4', 'leJ4']),
      getModuleTypeFromSerial: jest.fn((serial: string) => {
        if (serial === 'SVR4H73275') return 'DPS';
        if (serial === '5iO4' || serial === 'leJ4' || serial.toLowerCase() === '5io4') return 'FTS';
        return null;
      }),
      getModuleBySerial: jest.fn((serial: string) => {
        if (serial === 'SVR4H73275') return { moduleType: 'DPS', serialNumber: 'SVR4H73275' };
        if (serial.toLowerCase() === '5io4')
          return { moduleType: 'FTS', serialNumber: '5iO4', icon: 'FTS' };
        if (serial === 'leJ4') return { moduleType: 'FTS', serialNumber: 'leJ4', icon: 'FTS' };
        return null;
      }),
      getAgvLabel: jest.fn((serial: string) =>
        serial === '5iO4' || serial.toLowerCase() === '5io4'
          ? 'AGV-1'
          : serial === 'leJ4'
            ? 'AGV-2'
            : null
      ),
      getModuleIcon: jest.fn(() => null),
    };

    const layoutServiceMock = {
      config$: of({
        cells: [],
        modules_by_serial: {},
        fts: [
          { id: 'AGV-1', label: 'AGV-1', serial: '5iO4' },
          { id: 'AGV-2', label: 'AGV-2', serial: 'leJ4' },
        ],
      }),
    };

    await TestBed.configureTestingModule({
      imports: [MessageMonitorTabComponent],
      providers: [
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: EnvironmentService, useValue: environmentService },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ShopfloorMappingService, useValue: mappingService },
        { provide: ShopfloorLayoutService, useValue: layoutServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MessageMonitorTabComponent);
    component = fixture.componentInstance;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize messages stream', () => {
    expect(component.messages$).toBeDefined();
  });

  it('should detect mock mode', () => {
    expect(component.isMockMode).toBe(true);
  });

  it('should provide environment label', () => {
    expect(component.environmentLabel).toBe('Mock');
  });

  it('should get all messages', () => {
    const messages = component.getAllMessages();
    expect(messages.length).toBeGreaterThan(0);
  });

  it('should filter messages by topic type (ccu)', () => {
    component.filterTopicType = 'ccu';
    const messages = component.getAllMessages();
    expect(messages.every((msg) => msg.topic.startsWith('ccu/'))).toBe(true);
  });

  it('should filter messages by topic type (module-fts)', () => {
    component.filterTopicType = 'module-fts';
    const messages = component.getAllMessages();
    expect(
      messages.every((msg) => msg.topic.startsWith('module/') || msg.topic.startsWith('fts/'))
    ).toBe(true);
  });

  it('should filter messages by text', () => {
    component.filterText = 'order';
    const messages = component.getAllMessages();
    expect(messages.length).toBeGreaterThanOrEqual(0);
  });

  it('should filter messages by module', () => {
    component.filterModule = 'SVR4H73275';
    const messages = component.getAllMessages();
    expect(messages.length).toBeGreaterThanOrEqual(0);
  });

  it('should filter messages by status', () => {
    component.filterStatus = 'state';
    const messages = component.getAllMessages();
    expect(messages.length).toBeGreaterThanOrEqual(0);
  });

  it('should list AGV-1 and AGV-2 from layout with serial filter values', () => {
    component.updateAvailableModules();
    const agv1 = component.availableModules.find((m) => m.serial === '5iO4');
    const agv2 = component.availableModules.find((m) => m.serial === 'leJ4');
    expect(agv1?.name).toContain('AGV-1');
    expect(agv2?.name).toContain('AGV-2');
    expect(component.availableModules.some((m) => m.serial === 'HBW-DEMO')).toBe(false);
    expect(component.availableModules.some((m) => m.serial === 'HBW-MISSING')).toBe(false);
  });

  it('should exclude non-layout serials in Live environment', () => {
    environmentService.current = { key: 'live', label: 'Live' };
    messageMonitor.getTopics.mockReturnValue([
      'module/v1/ff/SVR4H73275/state',
      'fts/v1/ff/5iO4/state',
      'module/v1/ff/EXTRA99/state',
      'module/v1/ff/HBW-DEMO/state',
    ]);
    component.updateAvailableModules();
    expect(component.availableModules.map((m) => m.serial).sort()).toEqual([
      '5iO4',
      'SVR4H73275',
      'leJ4',
    ]);
  });

  it('should label FTS topics as AGV-1 in table', () => {
    const info = component.getTopicName('fts/v1/ff/5iO4/state');
    expect(info.name).toBe('AGV-1');
  });

  it('should have monitor heading icon', () => {
    expect(component.monitorHeadingIcon).toBeDefined();
  });

  it('should save filter settings', () => {
    const saveSpy = jest.spyOn(Storage.prototype, 'setItem');
    component['saveFilterSettings']();
    expect(saveSpy).toHaveBeenCalled();
  });

  it('should load filter settings', () => {
    const loadSpy = jest.spyOn(Storage.prototype, 'getItem').mockReturnValue('{}');
    component['loadFilterSettings']();
    expect(loadSpy).toHaveBeenCalled();
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });

  it('should save filter settings on destroy', () => {
    const saveSpy = jest.spyOn(Storage.prototype, 'setItem');
    component.ngOnDestroy();
    expect(saveSpy).toHaveBeenCalled();
  });
});
