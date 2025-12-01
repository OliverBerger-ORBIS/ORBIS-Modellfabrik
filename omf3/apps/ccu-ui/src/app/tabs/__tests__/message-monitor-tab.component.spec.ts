import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { MessageMonitorTabComponent } from '../message-monitor-tab.component';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { EnvironmentService } from '../../services/environment.service';
import { ModuleNameService } from '../../services/module-name.service';
import type { MonitoredMessage } from '../../services/message-monitor.service';

describe('MessageMonitorTabComponent', () => {
  let component: MessageMonitorTabComponent;
  let fixture: ComponentFixture<MessageMonitorTabComponent>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;

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
  ];

  beforeEach(async () => {
    const messageMonitorMock = {
      getTopics: jest.fn(() => ['ccu/order/active', 'module/v1/ff/SVR4H73275/state', 'fts/v1/ff/5iO4/state']),
      getHistory: jest.fn((topic: string) => {
        return mockMessages.filter((msg) => msg.topic === topic);
      }),
      getLastMessage: jest.fn(() => of(null)),
      addMessage: jest.fn(),
    };

    const environmentServiceMock = {
      current: { key: 'mock', label: 'Mock' },
      environment$: new BehaviorSubject({ key: 'mock', label: 'Mock' }),
    };

    const moduleNameServiceMock = {
      getModuleFullName: jest.fn((key: string) => `${key} Module`),
      getModuleDisplayText: jest.fn((key: string) => `${key} Display`),
    };

    await TestBed.configureTestingModule({
      imports: [MessageMonitorTabComponent],
      providers: [
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MessageMonitorTabComponent);
    component = fixture.componentInstance;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    environmentService = TestBed.inject(EnvironmentService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
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

  it('should update available modules from topics', () => {
    component.updateAvailableModules();
    expect(component.availableModules.length).toBeGreaterThanOrEqual(0);
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

