import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { BehaviorSubject, of } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { TrackTraceComponent } from '../track-trace.component';
import { WorkpieceHistoryService } from '../../../services/workpiece-history.service';
import { ModuleNameService } from '../../../services/module-name.service';
import { EnvironmentService } from '../../../services/environment.service';
import { TrackTraceEnvironmentService } from '../../../services/track-trace-environment.service';
import type { WorkpieceHistory, OrderContext, TrackTraceEvent } from '../../../services/workpiece-history.service';

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

    it('labels FTS vs Module event sources', () => {
      expect(component.getEventSourceLabel('FTS')).toBeTruthy();
      expect(component.getEventSourceLabel('MODULE')).toBeTruthy();
      expect(component.getEventSourceLabel(undefined)).toBeNull();
    });

    it('labels Color/NFC intake and shows HBW position separately', () => {
      expect(
        component.getEventLabel('INPUT_RGB', {
          timestamp: 't',
          eventType: 'INPUT_RGB',
        })
      ).toBeTruthy();
      expect(
        component.getEventLabel('RGB_NFC', {
          timestamp: 't',
          eventType: 'RGB_NFC',
        })
      ).toBeTruthy();
      expect(
        component.getEventLabel('PICK', {
          timestamp: 't',
          eventType: 'PICK',
          stationId: 'HBW',
          details: { loadPosition: 'A1' },
        })
      ).toBe('PICK');
      expect(
        component.getEventPositionLabel({
          timestamp: 't',
          eventType: 'PICK',
          stationId: 'HBW',
          details: { loadPosition: 'A1' },
        })
      ).toContain('A1');
    });
  });

  describe('groupEventsBySubOrder chronology (C1)', () => {
    it('orders groups by earliest event timestamp, not sub-order suffix', () => {
      const events = [
        {
          timestamp: '2026-05-06T12:02:00.000Z',
          eventType: 'PROCESS',
          stationId: 'AIQS',
          subOrderId: 'order-1-1',
          moduleId: 'SVR_AIQS',
        },
        {
          timestamp: '2026-05-06T12:00:00.000Z',
          eventType: 'PROCESS',
          stationId: 'AIQS',
          subOrderId: 'order-1-9',
          moduleId: 'SVR_AIQS',
        },
      ] as TrackTraceEvent[];
      const stationGroups = [
        {
          stationId: 'AIQS',
          stationName: 'AIQS',
          events,
        },
      ];
      const groups = component.groupEventsBySubOrder(events, stationGroups);
      expect(groups.map((g) => g.subOrderId)).toEqual(['order-1-9', 'order-1-1']);
    });
  });

  describe('Station | Transport timeline (B3 layout)', () => {
    it('groups consecutive DPS station events under one header and splits columns', () => {
      const order: OrderContext = {
        orderId: 'storage-1',
        orderType: 'STORAGE',
        plannedStationChain: ['DPS', 'HBW'],
      };
      const events: TrackTraceEvent[] = [
        {
          timestamp: '2026-07-28T15:00:00Z',
          eventType: 'INPUT_RGB',
          stationId: 'DPS',
          stationName: 'DPS',
          orderType: 'STORAGE',
          eventSource: 'MODULE',
        },
        {
          timestamp: '2026-07-28T15:00:10Z',
          eventType: 'RGB_NFC',
          stationId: 'DPS',
          stationName: 'DPS',
          orderType: 'STORAGE',
          eventSource: 'MODULE',
        },
        {
          timestamp: '2026-07-28T15:00:20Z',
          eventType: 'DROP',
          stationId: 'DPS',
          stationName: 'DPS',
          orderType: 'STORAGE',
          eventSource: 'MODULE',
        },
        {
          timestamp: '2026-07-28T15:00:30Z',
          eventType: 'PASS',
          orderType: 'STORAGE',
          eventSource: 'FTS',
          moduleName: 'AGV-1',
        },
        {
          timestamp: '2026-07-28T15:00:40Z',
          eventType: 'PICK',
          stationId: 'HBW',
          stationName: 'HBW',
          orderType: 'STORAGE',
          eventSource: 'MODULE',
        },
      ];

      const timeline = component.buildShopfloorTimeline(events, order);
      const headers = timeline.filter((i) => i.kind === 'station-header');
      expect(headers.map((h) => (h.kind === 'station-header' ? h.stationId : ''))).toEqual([
        'DPS',
        'HBW',
      ]);

      const dpsEvents = timeline.filter(
        (i) => i.kind === 'event' && i.column === 'station' && i.event.stationId === 'DPS'
      );
      expect(dpsEvents).toHaveLength(3);
      expect(dpsEvents[0]?.kind === 'event' && dpsEvents[0].showBusinessChip).toBe(true);
      expect(dpsEvents[1]?.kind === 'event' && dpsEvents[1].showBusinessChip).toBe(false);

      const transport = timeline.filter((i) => i.kind === 'event' && i.column === 'transport');
      expect(transport).toHaveLength(1);
    });
  });

  describe('Quality result badge', () => {
    it('returns FAILED badge for CHECK_QUALITY event with failed result', () => {
      const badge = component.getQualityResultBadge({
        timestamp: 't',
        eventType: 'CHECK_QUALITY',
        stationId: 'AIQS',
        details: { result: 'FAILED' },
      });
      expect(badge).toBe('FAILED');
      const cls = component.getQualityResultClass({
        timestamp: 't',
        eventType: 'CHECK_QUALITY',
        stationId: 'AIQS',
        details: { result: 'FAILED' },
      });
      expect(cls).toBe('quality-result--failed');
    });

    it('returns OK badge and ok class', () => {
      const badge = component.getQualityResultBadge({
        timestamp: 't',
        eventType: 'CHECK_QUALITY',
        details: { result: 'OK' },
      });
      expect(badge).toBe('OK');
      expect(
        component.getQualityResultClass({
          timestamp: 't',
          eventType: 'CHECK_QUALITY',
          details: { result: 'OK' },
        })
      ).toBe('quality-result--ok');
    });

    it('returns null for non-CHECK_QUALITY events', () => {
      expect(
        component.getQualityResultBadge({
          timestamp: 't',
          eventType: 'DRILL',
          details: { result: 'OK' },
        })
      ).toBeNull();
    });
  });

  describe('Position label for FTS transport events', () => {
    it('shows Intersection N for PASS events with intersectionNumber', () => {
      const label = component.getEventPositionLabel({
        timestamp: 't',
        eventType: 'PASS',
        eventSource: 'FTS',
        workpieceType: 'BLUE',
        details: { intersectionNumber: '2', loadPosition: '1' },
      });
      expect(label).toContain('2');
      expect(label).toContain('1');
      expect(label).toContain('BLUE');
    });

    it('shows only bucket position when no intersectionNumber for TURN', () => {
      const label = component.getEventPositionLabel({
        timestamp: 't',
        eventType: 'TURN',
        eventSource: 'FTS',
        workpieceType: 'WHITE',
        details: { loadPosition: '2' },
      });
      expect(label).toContain('2');
      expect(label).toContain('WHITE');
    });

    it('returns null for DOCK events without position', () => {
      const label = component.getEventPositionLabel({
        timestamp: 't',
        eventType: 'DOCK',
        eventSource: 'FTS',
        details: {},
      });
      expect(label).toBeNull();
    });
  });

  describe('Order flow accents', () => {
    it('activates flow chips based on matching anchor events', () => {
      const accents = component.getOrderFlowAccents(
        [
          {
            timestamp: '2026-05-06T12:00:00.000Z',
            eventType: 'DROP',
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
