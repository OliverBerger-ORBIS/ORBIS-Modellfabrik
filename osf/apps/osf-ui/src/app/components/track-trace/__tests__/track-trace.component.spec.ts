import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { BehaviorSubject, of } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { TrackTraceComponent } from '../track-trace.component';
import { WorkpieceHistoryService } from '../../../services/workpiece-history.service';
import { ModuleNameService } from '../../../services/module-name.service';
import { EnvironmentService } from '../../../services/environment.service';
import { TrackTraceEnvironmentService } from '../../../services/track-trace-environment.service';
import type { WorkpieceHistory, OrderContext } from '../../../services/workpiece-history.service';

describe('TrackTraceComponent', () => {
  let component: TrackTraceComponent;
  let fixture: ComponentFixture<TrackTraceComponent>;
  let historyMap$: BehaviorSubject<Map<string, WorkpieceHistory>>;

  const createHistoryWithOrderStatus = (status: OrderContext['status']): WorkpieceHistory => ({
    workpieceId: 'wp-failed-test',
    workpieceType: 'RED',
    events: [],
    currentLocation: 'SVR4H73275',
    orders: [
      {
        orderId: 'order-1',
        orderType: 'PRODUCTION',
        status,
        customerOrderId: 'ERP-CO-X',
        customerId: 'CUST-1',
      },
    ],
  });

  beforeEach(async () => {
    historyMap$ = new BehaviorSubject(new Map<string, WorkpieceHistory>());

    const workpieceHistoryServiceMock = {
      initialize: jest.fn(),
      getHistory$: jest.fn(() => historyMap$.asObservable()),
    };

    const environmentServiceMock = {
      get current() {
        return { key: 'mock' as const };
      },
      environment$: new BehaviorSubject({ key: 'mock' as const, label: 'Mock', description: '', connection: { mqttHost: 'localhost', mqttPort: 1883 } }),
    };

    const trackTraceEnvironmentMock = {
      snapshot$: of({
        rows: [{ id: 'empty', label: '', value: '', variant: 'normal' as const }],
        hasAlarm: false,
        updatedAt: '2020-01-01T00:00:00.000Z',
      }),
    };

    await TestBed.configureTestingModule({
      imports: [TrackTraceComponent, FormsModule, HttpClientTestingModule],
      providers: [
        ModuleNameService,
        { provide: WorkpieceHistoryService, useValue: workpieceHistoryServiceMock },
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: TrackTraceEnvironmentService, useValue: trackTraceEnvironmentMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TrackTraceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Order Status FAILED/ERROR display', () => {
    it('should display Failed status when order has status ERROR', () => {
      const history = createHistoryWithOrderStatus('ERROR');
      historyMap$.next(new Map([['wp-failed-test', history]]));
      component.selectWorkpiece('wp-failed-test');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      const failedLabel = el.querySelector('.status-failed');
      expect(failedLabel).toBeTruthy();
      expect(failedLabel?.textContent?.trim()).toMatch(/Failed|Fehlgeschlagen|Échoué/);
    });

    it('should display Failed status when order has status FAILED', () => {
      const history = createHistoryWithOrderStatus('FAILED');
      historyMap$.next(new Map([['wp-failed-test', history]]));
      component.selectWorkpiece('wp-failed-test');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      const failedLabel = el.querySelector('.status-failed');
      expect(failedLabel).toBeTruthy();
    });
  });

  describe('Sampled event environment snapshot', () => {
    it('renders sampled sensor rows on event entries', () => {
      const history: WorkpieceHistory = {
        workpieceId: 'wp-env-1',
        workpieceType: 'BLUE',
        currentLocation: 'SVR4H76449',
        events: [
          {
            timestamp: '2026-05-06T09:00:00.000Z',
            eventType: 'PROCESS',
            orderType: 'PRODUCTION',
            moduleName: 'DRILL',
            stationId: 'DRILL',
            details: {
              environmentSnapshot: {
                rows: [{ id: 'bme680', label: 'BME680', value: '22.3°C · 48% RH', variant: 'normal' }],
                hasAlarm: false,
                updatedAt: '2026-05-06T09:00:00.000Z',
              },
            },
          },
        ],
        orders: [
          {
            orderId: 'order-env-1',
            orderType: 'PRODUCTION',
          },
        ],
      };

      historyMap$.next(new Map([['wp-env-1', history]]));
      component.selectColor('BLUE');
      component.selectWorkpiece('wp-env-1');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      expect(el.textContent).toContain('Environment @ event');
      expect(el.textContent).toContain('BME680');
      expect(el.textContent).toContain('22.3°C · 48% RH');
    });

    it('does not render sampled environment block when snapshot is missing', () => {
      const history: WorkpieceHistory = {
        workpieceId: 'wp-env-2',
        workpieceType: 'BLUE',
        currentLocation: 'SVR4H76449',
        events: [
          {
            timestamp: '2026-05-06T09:05:00.000Z',
            eventType: 'PROCESS',
            orderType: 'PRODUCTION',
            moduleName: 'DRILL',
            stationId: 'DRILL',
            details: {},
          },
        ],
        orders: [
          {
            orderId: 'order-env-2',
            orderType: 'PRODUCTION',
          },
        ],
      };

      historyMap$.next(new Map([['wp-env-2', history]]));
      component.selectColor('BLUE');
      component.selectWorkpiece('wp-env-2');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      expect(el.textContent).not.toContain('Environment @ event');
      expect(el.textContent).not.toContain('No sampled sensor snapshot for this event.');
    });
  });

  describe('Event actor labeling', () => {
    it('prefers station id for bracket actions', () => {
      expect(
        component.getEventPrimaryActor({
          timestamp: '2026-05-06T12:00:00.000Z',
          eventType: 'PROCESS',
          stationId: 'AIQS',
          moduleName: 'AGV-1',
        })
      ).toBe('AIQS');
    });

    it('keeps AGV transport context for bracket actions', () => {
      expect(
        component.getEventTransportContext({
          timestamp: '2026-05-06T12:00:00.000Z',
          eventType: 'PROCESS',
          stationId: 'AIQS',
          moduleName: 'AGV-1',
        })
      ).toBe('AGV-1');
    });

    it('maps AGV labels to accent classes', () => {
      expect(component.getAgvAccentClass('AGV-1')).toBe('agv-accent--1');
      expect(component.getAgvAccentClass('AGV-2')).toBe('agv-accent--2');
      expect(component.getAgvAccentClass('DRILL')).toBe('');
    });
  });

  describe('Order flow accents', () => {
    it('activates flow chips based on matching anchor events', () => {
      const accents = component.getOrderFlowAccents(
        [
          {
            timestamp: '2026-05-06T12:00:00.000Z',
            eventType: 'PICK',
            stationId: 'HBW',
            orderId: 'order-prod-1',
            orderType: 'PRODUCTION',
          },
          {
            timestamp: '2026-05-06T12:01:00.000Z',
            eventType: 'PROCESS',
            stationId: 'DRILL',
            orderId: 'order-prod-1',
            orderType: 'PRODUCTION',
          },
        ],
        {
          orderId: 'order-prod-1',
          orderType: 'PRODUCTION',
          plannedStationChain: ['HBW', 'DRILL', 'MILL', 'AIQS', 'DPS'],
        }
      );

      expect(accents).toHaveLength(5);
      expect(accents[0]?.active).toBe(true);
      expect(accents[1]?.active).toBe(true);
      expect(accents[2]?.active).toBe(false);
    });

    it('builds per-event business flow accent for timeline lane', () => {
      const accent = component.getBusinessFlowAccent(
        {
          timestamp: '2026-05-06T12:01:00.000Z',
          eventType: 'PROCESS',
          stationId: 'DRILL',
          orderId: 'order-prod-1',
          orderType: 'PRODUCTION',
        },
        {
          orderId: 'order-prod-1',
          orderType: 'PRODUCTION',
          plannedStationChain: ['HBW', 'DRILL', 'MILL', 'AIQS', 'DPS'],
        }
      );

      expect(accent).toEqual({ station: 'DRILL', index: 2, total: 5 });
    });
  });
});
