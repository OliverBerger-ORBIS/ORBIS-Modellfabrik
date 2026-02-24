import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { ReplaySubject } from 'rxjs';
import { OrderResponse } from '../../../common/protocol';
import { OrderState } from '../../../common/protocol/ccu';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { OrderStatesService } from '../../services/order-states.service';
import { OrderListComponent } from './order-list.component';

describe('OrderListComponent', () => {
  const mockDate = new Date('2023-06-27T08:00:00.000Z');
  let activeOrders$: ReplaySubject<OrderResponse[]>;
  let completedOrders$: ReplaySubject<OrderResponse[]>;
  let component: OrderListComponent;
  let fixture: ComponentFixture<OrderListComponent>;

  beforeEach(async () => {
    jest.useFakeTimers();
    jest.setSystemTime(mockDate);

    activeOrders$ = new ReplaySubject<OrderResponse[]>(1);
    completedOrders$ = new ReplaySubject<OrderResponse[]>(1);

    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [OrderListComponent],
      providers: [
        MockProvider(TypedMqttService, {
          publish: jest.fn(),
        }),
        MockProvider(OrderStatesService, {
          activeOrders$,
          completedOrders$,
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OrderListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });

  it('should show active orders without completed', () => {
    activeOrders$.next([
      {
        orderType: 'PRODUCTION',
        type: 'BLUE',
        timestamp: mockDate,
        orderId: '471243d7-5ac2-4fe5-959a-04708e783629',
        productionSteps: [],
        receivedAt: mockDate,
        state: OrderState.ENQUEUED,
      },
    ]);
    completedOrders$.next([]);
    component.withCompleted = false;
    fixture.detectChanges();
    expect(fixture).toMatchSnapshot();
  });

  it('should show both active and completed orders if withCompleted equals true', () => {
    activeOrders$.next([
      {
        orderType: 'PRODUCTION',
        type: 'BLUE',
        timestamp: mockDate,
        orderId: '471243d7-5ac2-4fe5-959a-04708e783629',
        productionSteps: [],
        receivedAt: mockDate,
        state: OrderState.ENQUEUED,
      },
    ]);
    completedOrders$.next([
      {
        orderType: 'PRODUCTION',
        type: 'BLUE',
        timestamp: mockDate,
        orderId: '471243d7-5ac2-4fe5-959a-04708e369124',
        productionSteps: [],
        receivedAt: mockDate,
        state: OrderState.FINISHED,
      },
    ]);
    component.withCompleted = true;
    fixture.detectChanges();
    expect(fixture).toMatchSnapshot();
  });

  it('should show active orders and hide completed orders if withCompleted equals false', () => {
    activeOrders$.next([
      {
        orderType: 'PRODUCTION',
        type: 'BLUE',
        timestamp: mockDate,
        orderId: '471243d7-5ac2-4fe5-959a-04708e783629',
        productionSteps: [],
        receivedAt: mockDate,
        state: OrderState.ENQUEUED,
      },
    ]);
    completedOrders$.next([
      {
        orderType: 'PRODUCTION',
        type: 'BLUE',
        timestamp: mockDate,
        orderId: '471243d7-5ac2-4fe5-959a-04708e369124',
        productionSteps: [],
        receivedAt: mockDate,
        state: OrderState.FINISHED,
      },
    ]);
    component.withCompleted = false;
    fixture.detectChanges();
    expect(fixture).toMatchSnapshot();
  });

  it('should show completed orders if withCompleted equals true', () => {
    activeOrders$.next([]);
    completedOrders$.next([
      {
        orderType: 'PRODUCTION',
        type: 'BLUE',
        timestamp: mockDate,
        orderId: '471243d7-5ac2-4fe5-959a-04708e369124',
        productionSteps: [],
        receivedAt: mockDate,
        state: OrderState.FINISHED,
      },
    ]);
    component.withCompleted = true;
    fixture.detectChanges();
    expect(fixture).toMatchSnapshot();
  });
});
