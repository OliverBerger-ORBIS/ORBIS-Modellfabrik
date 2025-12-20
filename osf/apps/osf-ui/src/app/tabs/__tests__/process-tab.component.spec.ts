import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { ProcessTabComponent } from '../process-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ModuleNameService } from '../../services/module-name.service';
import { ConnectionService } from '../../services/connection.service';
import { InventoryStateService } from '../../services/inventory-state.service';
import * as mockDashboard from '../../mock-dashboard';
import type { ProductionFlowMap } from '@osf/entities';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams$: of({
    flows$: of({} as ProductionFlowMap),
  }),
  streams: {
    flows$: of({} as ProductionFlowMap),
    inventoryOverview$: of({
      slots: {},
      availableCounts: {},
      reservedCounts: {},
      lastUpdated: '',
    }),
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
  let inventoryStateService: jest.Mocked<InventoryStateService>;

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

    const inventoryStateServiceMock = {
      getState$: jest.fn(() => of(null)),
      getSnapshot: jest.fn(() => null),
      setState: jest.fn(),
      clear: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ProcessTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: InventoryStateService, useValue: inventoryStateServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProcessTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    moduleNameService = TestBed.inject(ModuleNameService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    inventoryStateService = TestBed.inject(InventoryStateService) as any;
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

  it('should have production end icons', () => {
    expect(component.productionEndIcons.length).toBeGreaterThan(0);
  });

  it('should have storage end icons', () => {
    expect(component.storageEndIcons.length).toBeGreaterThan(0);
  });

  it('should resolve asset path correctly', () => {
    const path = component['resolveAssetPath']('/assets/svg/shopfloor/shared/question.svg');
    expect(path).toBe('assets/svg/shopfloor/shared/question.svg');
  });

  it('should normalize asset path without leading slash', () => {
    const path = component['resolveAssetPath']('assets/svg/shopfloor/shared/question.svg');
    expect(path).toBe('assets/svg/shopfloor/shared/question.svg');
  });

  it('should have module meta', () => {
    const moduleMeta = component['moduleMeta'];
    expect(moduleMeta).toBeDefined();
    expect(moduleMeta['HBW']).toBeDefined();
    expect(moduleMeta['HBW'].label).toBeDefined();
    expect(moduleMeta['HBW'].icon).toBeDefined();
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });

  describe('Accordion functionality', () => {
    it('should have both sections expanded by default', () => {
      expect(component.isSectionExpanded('procurement')).toBe(true);
      expect(component.isSectionExpanded('production')).toBe(true);
    });

    it('should toggle section expansion', () => {
      // Initially expanded
      expect(component.isSectionExpanded('procurement')).toBe(true);

      // Toggle to collapse
      component.toggleSection('procurement');
      expect(component.isSectionExpanded('procurement')).toBe(false);

      // Toggle to expand again
      component.toggleSection('procurement');
      expect(component.isSectionExpanded('procurement')).toBe(true);
    });

    it('should toggle production section independently', () => {
      // Initially expanded
      expect(component.isSectionExpanded('production')).toBe(true);

      // Toggle to collapse
      component.toggleSection('production');
      expect(component.isSectionExpanded('production')).toBe(false);

      // Procurement should still be expanded
      expect(component.isSectionExpanded('procurement')).toBe(true);
    });

    it('should handle unknown section IDs', () => {
      expect(component.isSectionExpanded('unknown')).toBe(false);
      
      component.toggleSection('unknown');
      expect(component.isSectionExpanded('unknown')).toBe(true);
    });
  });
});

