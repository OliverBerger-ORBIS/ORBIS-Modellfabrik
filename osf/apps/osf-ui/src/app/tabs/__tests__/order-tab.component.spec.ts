import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { BehaviorSubject, of } from 'rxjs';
import { OrderTabComponent } from '../order-tab.component';
import { EnvironmentService } from '../../services/environment.service';
import { MessageMonitorService } from '../../services/message-monitor.service';
import { ConnectionService } from '../../services/connection.service';
import * as mockDashboard from '../../mock-dashboard';
import type { OrderActive } from '@osf/entities';

// Mock getDashboardController
jest.spyOn(mockDashboard, 'getDashboardController').mockReturnValue({
  streams: {
    orders$: of({}),
    completedOrders$: of({}),
  },
  loadTabFixture: jest.fn(),
  getCurrentFixture: jest.fn(() => 'startup'),
} as any);

describe('OrderTabComponent', () => {
  let component: OrderTabComponent;
  let fixture: ComponentFixture<OrderTabComponent>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitor: jest.Mocked<MessageMonitorService>;
  let connectionService: jest.Mocked<ConnectionService>;

  beforeEach(async () => {
    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    };

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
    };

    const connectionServiceMock = {
      state$: new BehaviorSubject<'disconnected'>('disconnected'),
    };

    await TestBed.configureTestingModule({
      imports: [OrderTabComponent, HttpClientTestingModule],
      providers: [
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ConnectionService, useValue: connectionServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OrderTabComponent);
    component = fixture.componentInstance;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitor = TestBed.inject(MessageMonitorService) as any;
    connectionService = TestBed.inject(ConnectionService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize order streams', () => {
    expect(component.productionActive$).toBeDefined();
    expect(component.productionCompleted$).toBeDefined();
    expect(component.storageActive$).toBeDefined();
    expect(component.storageCompleted$).toBeDefined();
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
    expect(component.fixtureLabels.white).toBeDefined();
  });

  it('should toggle production completed collapsed state', () => {
    const initial = component.productionCompletedCollapsed;
    component.toggleProductionCompleted();
    expect(component.productionCompletedCollapsed).toBe(!initial);
  });

  it('should toggle production completed without auto-expand', () => {
    component.productionCompletedCollapsed = true;
    component.toggleProductionCompleted();
    expect(component.productionCompletedCollapsed).toBe(false);
    // Production orders do not auto-expand
  });

  it('should toggle storage completed collapsed state', () => {
    const initial = component.storageCompletedCollapsed;
    component.toggleStorageCompleted();
    expect(component.storageCompletedCollapsed).toBe(!initial);
  });

  it('should auto-expand last order when expanding storage completed', () => {
    component.storageCompletedCollapsed = true;
    // Mock storageCompleted$ to return orders
    component.storageCompleted$ = of([
      { orderId: 'order-3' } as OrderActive,
      { orderId: 'order-4' } as OrderActive,
    ]);
    component.toggleStorageCompleted();
    expect(component.storageCompletedCollapsed).toBe(false);
    // expandedStorageOrderId should be set to the first (most recent) order
    expect(component.expandedStorageOrderId).toBe('order-3');
  });

  it('should track orders by orderId', () => {
    const order = { orderId: 'test-order-123' } as OrderActive;
    expect(component.trackOrder(0, order)).toBe('test-order-123');
  });

  it('should provide toggle labels', () => {
    expect(component.productionCompletedToggleLabel).toBeDefined();
    expect(component.storageCompletedToggleLabel).toBeDefined();
  });

  it('should unsubscribe on destroy', () => {
    const unsubscribeSpy = jest.spyOn(component['subscriptions'], 'unsubscribe');
    component.ngOnDestroy();
    expect(unsubscribeSpy).toHaveBeenCalled();
  });
});

