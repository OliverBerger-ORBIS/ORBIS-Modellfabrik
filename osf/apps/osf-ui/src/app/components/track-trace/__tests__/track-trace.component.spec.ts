import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { BehaviorSubject, of } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { TrackTraceComponent } from '../track-trace.component';
import { WorkpieceHistoryService } from '../../../services/workpiece-history.service';
import { ModuleNameService } from '../../../services/module-name.service';
import { EnvironmentService } from '../../../services/environment.service';
import { TrackTraceEnvironmentService } from '../../../services/track-trace-environment.service';
import { AgvRouteService } from '../../../services/agv-route.service';
import { ShopfloorLayoutService } from '../../../services/shopfloor-layout.service';
import { ShopfloorMappingService } from '../../../services/shopfloor-mapping.service';
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

    const agvRouteServiceMock = {
      initializeLayout: jest.fn(),
      getAgvMarkerCenter: jest.fn(() => ({ x: 220, y: 120 })),
      getNodePosition: jest.fn(() => ({ x: 220, y: 120 })),
      resolveNodeRef: jest.fn((id: string | undefined) => id ?? null),
    };

    const shopfloorLayoutMock = {
      config$: of(null),
    };

    const shopfloorMappingMock = {
      getAgvColor: jest.fn(() => '#f97316'),
      getAgvOptions: jest.fn(() => [{ serial: '5iO4', label: 'AGV-1' }]),
      initializeLayout: jest.fn(),
      isInitialized: jest.fn(() => true),
      getModuleTypeFromSerial: jest.fn(() => null),
    };

    await TestBed.configureTestingModule({
      imports: [TrackTraceComponent, FormsModule, HttpClientTestingModule],
      providers: [
        ModuleNameService,
        { provide: WorkpieceHistoryService, useValue: workpieceHistoryServiceMock },
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: TrackTraceEnvironmentService, useValue: trackTraceEnvironmentMock },
        { provide: AgvRouteService, useValue: agvRouteServiceMock },
        { provide: ShopfloorLayoutService, useValue: shopfloorLayoutMock },
        { provide: ShopfloorMappingService, useValue: shopfloorMappingMock },
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
    const envSnapshot = {
      rows: [{ id: 'bme680', label: 'BME680', value: '22.3°C · 48% RH', variant: 'normal' as const }],
      hasAlarm: false,
      updatedAt: '2026-05-06T09:00:00.000Z',
    };

    it('shows collapsed Env summary on anchor events (default)', () => {
      const history: WorkpieceHistory = {
        workpieceId: 'wp-env-1',
        workpieceType: 'BLUE',
        currentLocation: 'SVR4H76449',
        events: [
          {
            timestamp: '2026-05-06T09:00:00.000Z',
            eventType: 'DOCK',
            eventSource: 'FTS',
            orderType: 'PRODUCTION',
            moduleName: 'AGV-1',
            stationId: 'DRILL',
            location: 'SVR4H76449',
            details: { environmentSnapshot: envSnapshot },
          },
        ],
        orders: [{ orderId: 'order-env-1', orderType: 'PRODUCTION' }],
      };

      historyMap$.next(new Map([['wp-env-1', history]]));
      component.selectColor('BLUE');
      component.selectWorkpiece('wp-env-1');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      expect(el.textContent).toMatch(/Env/i);
      expect(el.textContent).toMatch(/OK/i);
      expect(el.textContent).not.toContain('BME680');
    });

    it('expands sensor rows on toggle', () => {
      const event = {
        timestamp: '2026-05-06T09:00:00.000Z',
        eventType: 'DROP',
        eventSource: 'MODULE' as const,
        orderType: 'PRODUCTION',
        moduleName: 'HBW',
        stationId: 'HBW',
        location: 'SVR3QA0022',
        details: { environmentSnapshot: envSnapshot },
      };
      const history: WorkpieceHistory = {
        workpieceId: 'wp-env-1b',
        workpieceType: 'BLUE',
        currentLocation: 'SVR3QA0022',
        events: [event],
        orders: [{ orderId: 'order-env-1b', orderType: 'PRODUCTION' }],
      };

      historyMap$.next(new Map([['wp-env-1b', history]]));
      component.selectColor('BLUE');
      component.selectWorkpiece('wp-env-1b');
      fixture.detectChanges();

      component.toggleEnvironmentExpanded(event);
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      expect(el.textContent).toContain('BME680');
      expect(el.textContent).toContain('22.3°C · 48% RH');
    });

    it('hides env on non-anchor events even if snapshot exists', () => {
      expect(
        component.shouldDisplayEnvironmentSnapshot({
          timestamp: 't',
          eventType: 'PASS',
          eventSource: 'FTS',
          details: { environmentSnapshot: envSnapshot },
        })
      ).toBe(false);
      expect(
        component.shouldDisplayEnvironmentSnapshot({
          timestamp: 't',
          eventType: 'PROCESS',
          eventSource: 'MODULE',
          stationId: 'DRILL',
          details: { environmentSnapshot: envSnapshot },
        })
      ).toBe(false);
    });

    it('does not render sampled environment block when snapshot is missing', () => {
      const history: WorkpieceHistory = {
        workpieceId: 'wp-env-2',
        workpieceType: 'BLUE',
        currentLocation: 'SVR4H76449',
        events: [
          {
            timestamp: '2026-05-06T09:05:00.000Z',
            eventType: 'DOCK',
            eventSource: 'FTS',
            orderType: 'PRODUCTION',
            moduleName: 'AGV-1',
            stationId: 'DRILL',
            details: {},
          },
        ],
        orders: [{ orderId: 'order-env-2', orderType: 'PRODUCTION' }],
      };

      historyMap$.next(new Map([['wp-env-2', history]]));
      component.selectColor('BLUE');
      component.selectWorkpiece('wp-env-2');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      expect(el.querySelector('.event-environment')).toBeNull();
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

    it('labels FTS vs Module event sources (API retained; badges hidden in dense UI)', () => {
      expect(component.getEventSourceLabel('FTS')).toBeTruthy();
      expect(component.getEventSourceLabel('MODULE')).toBeTruthy();
      expect(component.getEventSourceLabel(undefined)).toBeNull();
    });

    it('puts module serial on station group header', () => {
      const items = component.buildShopfloorTimeline(
        [
          {
            timestamp: '2026-08-06T10:00:00.000Z',
            eventType: 'PICK',
            eventSource: 'MODULE',
            stationId: 'DRILL',
            stationName: 'DRILL (Drill Station)',
            location: 'SVR4H76449',
            orderType: 'PRODUCTION',
          },
        ],
        { orderId: 'o1', orderType: 'PRODUCTION' }
      );
      const header = items.find((i) => i.kind === 'station-header');
      expect(header?.kind).toBe('station-header');
      if (header?.kind === 'station-header') {
        expect(header.serialNumber).toBe('SVR4H76449');
      }
    });

    it('builds compact FTS position line without serial', () => {
      jest.spyOn(component, 'getLocationInfo').mockReturnValue({
        moduleType: '2',
        fullName: 'Intersection 2',
        serialNumber: null,
      });
      expect(
        component.getFtsPositionLine({
          timestamp: 't',
          eventType: 'TURN',
          eventSource: 'FTS',
          location: '2',
        })
      ).toBe('2 (Intersection 2)');
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
      expect(transport).toHaveLength(0);
      const transportGroups = timeline.filter((i) => i.kind === 'transport-group');
      expect(transportGroups).toHaveLength(1);
      if (transportGroups[0]?.kind === 'transport-group') {
        expect(transportGroups[0].events).toHaveLength(1);
        expect(transportGroups[0].fromStation).toBe('DPS');
        expect(transportGroups[0].toStation).toBe('HBW');
      }
    });

    it('groups consecutive FTS events and collects Ist stations as dashed chips', () => {
      const order: OrderContext = {
        orderId: 'ord-red',
        orderType: 'PRODUCTION',
        plannedStationChain: ['HBW', 'MILL', 'AIQS', 'DPS'],
      };
      const events: TrackTraceEvent[] = [
        {
          timestamp: 't1',
          eventType: 'DROP',
          stationId: 'HBW',
          stationName: 'HBW',
          orderType: 'PRODUCTION',
          eventSource: 'MODULE',
        },
        {
          timestamp: 't2',
          eventType: 'TURN',
          orderType: 'PRODUCTION',
          eventSource: 'FTS',
          moduleName: 'AGV-1',
          location: '1',
        },
        {
          timestamp: 't3',
          eventType: 'DOCK',
          orderType: 'PRODUCTION',
          eventSource: 'FTS',
          moduleName: 'AGV-1',
          stationId: 'DRILL',
          details: { visitKind: 'IST_ONLY', coPassenger: true },
        },
        {
          timestamp: 't4',
          eventType: 'DOCK',
          orderType: 'PRODUCTION',
          eventSource: 'FTS',
          moduleName: 'AGV-1',
          stationId: 'MILL',
          details: { visitKind: 'PLANNED' },
        },
        {
          timestamp: 't5',
          eventType: 'PICK',
          stationId: 'MILL',
          stationName: 'MILL',
          orderType: 'PRODUCTION',
          eventSource: 'MODULE',
        },
      ];

      const timeline = component.buildShopfloorTimeline(events, order);
      const groups = timeline.filter((i) => i.kind === 'transport-group');
      expect(groups).toHaveLength(1);
      if (groups[0]?.kind === 'transport-group') {
        expect(groups[0].events).toHaveLength(3);
        expect(groups[0].fromStation).toBe('HBW');
        expect(groups[0].toStation).toBe('MILL');
        expect(groups[0].istStations).toEqual(['DRILL']);
      }
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
    it('shows Intersection N meta for PASS events', () => {
      const meta = component.getTransportMetaLabel({
        timestamp: 't',
        eventType: 'PASS',
        eventSource: 'FTS',
        workpieceType: 'BLUE',
        details: { intersectionNumber: '2', loadPosition: '1' },
      });
      expect(meta).toContain('2');
    });

    it('shows 3 AGV buckets for single-load TURN (missing slots EMPTY)', () => {
      const rows = component.getTransportLoadRows({
        timestamp: 't',
        eventType: 'TURN',
        eventSource: 'FTS',
        workpieceType: 'WHITE',
        details: { loadPosition: '2' },
      });
      expect(rows).toHaveLength(3);
      expect(rows[0].empty).toBe(true);
      expect(rows[1].empty).toBe(false);
      expect(rows[1].label).toContain('2');
      expect(rows[1].label).toContain('WHITE');
      expect(rows[1].icon).toBeTruthy();
      expect(rows[2].empty).toBe(true);
    });

    it('returns no load rows for DOCK without agvLoads/position', () => {
      expect(
        component.getTransportLoadRows({
          timestamp: 't',
          eventType: 'DOCK',
          eventSource: 'FTS',
          details: {},
        })
      ).toEqual([]);
      expect(
        component.getEventPositionLabel({
          timestamp: 't',
          eventType: 'DOCK',
          eventSource: 'FTS',
          details: {},
        })
      ).toBeNull();
    });

    it('shows 3 AGV buckets for multi-load DOCK (Pos3 EMPTY)', () => {
      const rows = component.getTransportLoadRows({
        timestamp: 't',
        eventType: 'DOCK',
        eventSource: 'FTS',
        workpieceType: 'BLUE',
        details: {
          loadPosition: '1',
          agvLoads: [
            { loadId: 'a', loadType: 'BLUE', loadPosition: '1' },
            { loadId: 'b', loadType: 'RED', loadPosition: '2' },
          ],
        },
      });
      expect(rows).toHaveLength(3);
      expect(rows[0].empty).toBe(false);
      expect(rows[0].label).toContain('1');
      expect(rows[0].label).toContain('BLUE');
      expect(rows[0].icon).toBeTruthy();
      expect(rows[1].empty).toBe(false);
      expect(rows[1].label).toContain('2');
      expect(rows[1].label).toContain('RED');
      expect(rows[2].empty).toBe(true);
      expect(rows[2].label).toContain('EMPTY');
    });
  });

  describe('HBW mini grid', () => {
    it('builds 3×3 cells with active PICK slot highlighted', () => {
      const grid = component.getHbwMiniGrid({
        timestamp: 't',
        eventType: 'PICK',
        eventSource: 'MODULE',
        stationId: 'HBW',
        workpieceType: 'WHITE',
        workpieceId: 'nfc-w',
        details: {
          loadPosition: 'A2',
          hbwShelf: [
            { loadPosition: 'A1', loadType: 'BLUE', loadId: 'b' },
            { loadPosition: 'A2', loadType: 'WHITE', loadId: 'nfc-w' },
            { loadPosition: 'B1', loadType: null, loadId: null },
          ],
        },
      });
      expect(grid).not.toBeNull();
      expect(grid!.cells).toHaveLength(9);
      const a2 = grid!.cells.find((c) => c.loadPosition === 'A2');
      expect(a2?.active).toBe(true);
      expect(a2?.empty).toBe(false);
      expect(a2?.loadType).toBe('WHITE');
      const a1 = grid!.cells.find((c) => c.loadPosition === 'A1');
      expect(a1?.loadType).toBe('BLUE');
      expect(a1?.active).toBe(false);
      expect(component.getEventPositionLabel({
        timestamp: 't',
        eventType: 'PICK',
        eventSource: 'MODULE',
        stationId: 'HBW',
        details: { loadPosition: 'A2', hbwShelf: [] },
      })).toBeNull();
    });

    it('returns null for non-HBW stations', () => {
      expect(
        component.getHbwMiniGrid({
          timestamp: 't',
          eventType: 'PICK',
          eventSource: 'MODULE',
          stationId: 'DRILL',
          details: { loadPosition: '1' },
        })
      ).toBeNull();
    });
  });

  describe('AGV shopfloor mini map', () => {
    it('builds roads + AGV-colored marker for FTS events when layout is set', () => {
      (component as unknown as { layoutConfig: unknown }).layoutConfig = {
        metadata: { canvas: { width: 400, height: 300 } },
        parsed_roads: [
          {
            from: { center: { x: 100, y: 100 } },
            to: { center: { x: 200, y: 100 } },
          },
        ],
      };
      const mini = component.getAgvEventShopfloorMiniMap({
        timestamp: 't',
        eventType: 'PASS',
        eventSource: 'FTS',
        location: '1',
        moduleId: '5iO4',
        details: {},
      });
      expect(mini).not.toBeNull();
      expect(mini!.viewBox).toBe('0 0 400 300');
      expect(mini!.roads).toHaveLength(1);
      expect(mini!.marker.color).toBe('#f97316');
      expect(mini!.marker.x).toBe(220);
      expect(mini!.marker.y).toBe(120);
      expect(mini!.marker.r).toBeGreaterThanOrEqual(24);
    });

    it('returns null for MODULE events', () => {
      expect(
        component.getAgvEventShopfloorMiniMap({
          timestamp: 't',
          eventType: 'PICK',
          eventSource: 'MODULE',
          location: 'SVR3QA0022',
        })
      ).toBeNull();
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

    it('builds planned-station checklist with visited flags', () => {
      const checklist = component.getPlannedStationChecklist(
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
            eventType: 'DRILL',
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

      expect(checklist.map((s) => s.station)).toEqual(['HBW', 'DRILL', 'MILL', 'AIQS', 'DPS']);
      expect(checklist.find((s) => s.station === 'HBW')?.visited).toBe(true);
      expect(checklist.find((s) => s.station === 'DRILL')?.visited).toBe(true);
      expect(checklist.find((s) => s.station === 'MILL')?.visited).toBe(false);
    });

    it('marks PRODUCTION AIQS visited from FTS DOCK Mitfahrt (no MODULE quality)', () => {
      const checklist = component.getPlannedStationChecklist(
        [
          {
            timestamp: '2026-08-04T09:50:50.000Z',
            eventType: 'DROP',
            eventSource: 'MODULE',
            stationId: 'HBW',
            orderId: 'order-blue-prod',
            orderType: 'PRODUCTION',
          },
          {
            timestamp: '2026-08-04T09:54:34.000Z',
            eventType: 'DOCK',
            eventSource: 'FTS',
            stationId: 'AIQS',
            orderId: 'order-white-foreign',
            orderType: 'PRODUCTION',
            details: { coPassenger: true, visitKind: 'IST_ONLY' },
          },
        ],
        {
          orderId: 'order-blue-prod',
          orderType: 'PRODUCTION',
          plannedStationChain: ['HBW', 'DRILL', 'MILL', 'AIQS', 'DPS'],
        }
      );

      expect(checklist.find((s) => s.station === 'HBW')?.visited).toBe(true);
      expect(checklist.find((s) => s.station === 'AIQS')?.visited).toBe(true);
      expect(checklist.find((s) => s.station === 'DPS')?.visited).toBe(false);
    });

    it('does not mark STORAGE HBW from unrelated FTS DOCK (no speculative storage complete)', () => {
      const checklist = component.getPlannedStationChecklist(
        [
          {
            timestamp: '2026-08-04T09:46:00.000Z',
            eventType: 'DROP',
            eventSource: 'MODULE',
            stationId: 'DPS',
            orderId: 'order-blue-storage',
            orderType: 'STORAGE',
          },
          {
            timestamp: '2026-08-04T09:50:50.000Z',
            eventType: 'DOCK',
            eventSource: 'FTS',
            stationId: 'HBW',
            orderId: 'order-other',
            orderType: 'PRODUCTION',
            details: { coPassenger: true },
          },
        ],
        {
          orderId: 'order-blue-storage',
          orderType: 'STORAGE',
          plannedStationChain: ['DPS', 'HBW'],
        }
      );

      expect(checklist.find((s) => s.station === 'DPS')?.visited).toBe(true);
      expect(checklist.find((s) => s.station === 'HBW')?.visited).toBe(false);
    });
  });

  describe('Ist visit badge', () => {
    it('shows Ist stop badge for FTS DOCK with visitKind IST_ONLY', () => {
      expect(
        component.getIstVisitBadge({
          timestamp: 't',
          eventType: 'DOCK',
          eventSource: 'FTS',
          details: { visitKind: 'IST_ONLY', coPassenger: true },
        })
      ).toBeTruthy();
    });

    it('hides badge for planned FTS DOCK', () => {
      expect(
        component.getIstVisitBadge({
          timestamp: 't',
          eventType: 'DOCK',
          eventSource: 'FTS',
          details: { visitKind: 'PLANNED' },
        })
      ).toBeNull();
    });
  });
});
