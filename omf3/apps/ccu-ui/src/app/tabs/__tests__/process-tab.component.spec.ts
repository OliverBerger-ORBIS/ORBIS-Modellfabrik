import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { ProcessTabComponent } from '../process-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ModuleNameService } from '../../services/module-name.service';
import { ConnectionService } from '../../services/connection.service';
import * as mockDashboard from '../../mock-dashboard';
import type { ProductionFlowMap } from '@omf3/entities';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    flows$: of({} as ProductionFlowMap),
  },
  loadTabFixture: jest.fn(),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('ProcessTabComponent', () => {
  let component: ProcessTabComponent;
  let fixture: ComponentFixture<ProcessTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let moduleNameService: jest.Mocked<ModuleNameService>;
  let connectionService: jest.Mocked<ConnectionService>;

  beforeEach(async () => {
    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
    };

    const moduleNameServiceMock = {
      getModuleFullName: jest.fn((key: string) => `${key} Module`),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'disconnected'>('disconnected'),
    };

    await TestBed.configureTestingModule({
      imports: [ProcessTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcessTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize streams', () => {
    expect(component.flows$).toBeDefined();
    expect(component.products$).toBeDefined();
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

  it('should have process icon', () => {
    expect(component.processIcon).toBeDefined();
  });

  it('should have start icon', () => {
    expect(component.startIcon).toBeDefined();
  });

  it('should have end icons', () => {
    expect(component.endIcons.length).toBeGreaterThan(0);
  });

  it('should resolve asset path correctly', () => {
    const path = component['resolveAssetPath']('/assets/svg/shopfloor/shared/question.svg');
    expect(path).toBe('assets/svg/shopfloor/shared/question.svg');
  });

  it('should normalize asset path without leading slash', () => {
    const path = component['resolveAssetPath']('assets/svg/shopfloor/shared/question.svg');
    expect(path).toBe('assets/svg/shopfloor/shared/question.svg');
  });

  it('should get module meta', () => {
    const meta = component['getModuleMeta']('HBW');
    expect(meta.label).toBeDefined();
    expect(meta.icon).toBeDefined();
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });
});

