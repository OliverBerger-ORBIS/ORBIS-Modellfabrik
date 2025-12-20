import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { OverviewTabComponent } from '../overview-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ConnectionService } from '../../services/connection.service';
import { InventoryStateService } from '../../services/inventory-state.service';
import * as mockDashboard from '../../mock-dashboard';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    orders$: of([]),
    orderCounts$: of({ running: 0, queued: 0, completed: 0 }),
    ftsStates$: of({}),
    inventoryOverview$: of({
      slots: {},
      availableCounts: {},
      reservedCounts: {},
      lastUpdated: '',
    }),
  },
  commands: {
    sendCustomerOrder: jest.fn(),
  },
  loadTabFixture: jest.fn(),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('OverviewTabComponent', () => {
  let component: OverviewTabComponent;
  let fixture: ComponentFixture<OverviewTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;
  let inventoryState: jest.Mocked<InventoryStateService>;

  beforeEach(async () => {
    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
      clearTopic: jest.fn(),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'disconnected'>('disconnected'),
    };

    const inventoryStateMock = {
      getState$: jest.fn(() => of(null)),
      getSnapshot: jest.fn(() => null),
      setState: jest.fn(),
      clear: jest.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [OverviewTabComponent],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
        { provide: InventoryStateService, useValue: inventoryStateMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OverviewTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
    inventoryState = TestBed.inject(InventoryStateService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize streams', () => {
    expect(component.orders$).toBeDefined();
    expect(component.orderCounts$).toBeDefined();
    expect(component.ftsStates$).toBeDefined();
    expect(component.inventoryOverview$).toBeDefined();
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

  it('should provide workpiece types', () => {
    expect(component.workpieceTypes).toContain('BLUE');
    expect(component.workpieceTypes).toContain('WHITE');
    expect(component.workpieceTypes).toContain('RED');
  });

  it('should get slot icon for empty slot', () => {
    const slot = { location: 'A1', workpiece: null };
    const icon = component.getSlotIcon(slot);
    expect(icon).toBe(component.emptySlotIcon);
  });

  it('should get slot label for empty slot', () => {
    const slot = { location: 'A1', workpiece: null };
    const label = component.getSlotLabel(slot);
    expect(label).toContain('A1');
    expect(label).toContain('EMPTY');
  });

  it('should compute need correctly', () => {
    const counts = { BLUE: 1, WHITE: 0, RED: 2 };
    const need = component.getNeed(counts, 'BLUE');
    expect(need).toBe(2); // maxCapacity (3) - current (1)
  });

  it('should check availability', () => {
    const availableCounts = { BLUE: 1, WHITE: 0 };
    expect(component.isAvailable(availableCounts, 'BLUE')).toBe(true);
    expect(component.isAvailable(availableCounts, 'WHITE')).toBe(false);
  });

  it('should create array of specified length', () => {
    const arr = component.asArray(5);
    expect(arr.length).toBe(5);
    expect(arr).toEqual([0, 1, 2, 3, 4]);
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });
});

