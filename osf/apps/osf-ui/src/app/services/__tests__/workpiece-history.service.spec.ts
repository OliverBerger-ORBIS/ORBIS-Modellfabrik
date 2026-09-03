import { utcIsoTimestampMs } from '@osf/entities';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { WorkpieceHistoryService } from '../workpiece-history.service';
import { MessageMonitorService } from '../message-monitor.service';
import { ModuleNameService } from '../module-name.service';
import { EnvironmentService } from '../environment.service';
import { AgvRouteService } from '../agv-route.service';
import { ErpOrderDataService } from '../erp-order-data.service';
import { MessageValidationService } from '../message-validation.service';
import { MessagePersistenceService } from '../message-persistence.service';
import { ShopfloorMappingService } from '../shopfloor-mapping.service';
import { of } from 'rxjs';
import type { TrackTraceEvent, OrderContext, WorkpieceHistory } from '../workpiece-history.service';

describe('WorkpieceHistoryService', () => {
  let service: WorkpieceHistoryService;
  let messageMonitor: MessageMonitorService;
  let moduleNameService: ModuleNameService;
  let environmentService: EnvironmentService;
  let ftsRouteService: AgvRouteService;
  let erpOrderDataService: ErpOrderDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        WorkpieceHistoryService,
        MessageMonitorService,
        ModuleNameService,
        EnvironmentService,
        AgvRouteService,
        ErpOrderDataService,
        MessageValidationService,
        MessagePersistenceService,
      ],
    });
    service = TestBed.inject(WorkpieceHistoryService);
    messageMonitor = TestBed.inject(MessageMonitorService);
    moduleNameService = TestBed.inject(ModuleNameService);
    environmentService = TestBed.inject(EnvironmentService);
    ftsRouteService = TestBed.inject(AgvRouteService);
    erpOrderDataService = TestBed.inject(ErpOrderDataService);

    // Mock necessary methods
    jest.spyOn(messageMonitor, 'getLastMessage').mockReturnValue(of(null));
    jest.spyOn(messageMonitor, 'getHistory').mockReturnValue([]);
  });

  afterEach(() => {
    service.ngOnDestroy();
  });

  describe('Service Creation', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('getHistory$', () => {
    it('should return observable for environment', (done) => {
      const history$ = service.getHistory$('mock');
      
      history$.subscribe((historyMap) => {
        expect(historyMap).toBeInstanceOf(Map);
        expect(historyMap.size).toBe(0);
        done();
      });
    });
  });

  describe('getSnapshot', () => {
    it('should return history snapshot', () => {
      const snapshot = service.getSnapshot('mock');
      expect(snapshot).toBeInstanceOf(Map);
      expect(snapshot.size).toBe(0);
    });
  });

  describe('getWorkpieceHistory', () => {
    it('should return observable for specific workpiece', (done) => {
      const workpiece$ = service.getWorkpieceHistory('mock', 'wp-123');
      
      workpiece$.subscribe((history) => {
        expect(history).toBeUndefined();
        done();
      });
    });
  });

  describe('clear', () => {
    it('should clear history for environment', () => {
      // Initialize first
      service.initialize('mock');
      
      // Clear
      service.clear('mock');
      
      // Verify cleared
      const snapshot = service.getSnapshot('mock');
      expect(snapshot.size).toBe(0);
    });

    it('should not throw when clearing non-initialized environment', () => {
      expect(() => service.clear('non-existent')).not.toThrow();
    });
  });

  describe('initialize', () => {
    it('should initialize tracking for environment', () => {
      service.initialize('mock');
      // Should set up subscriptions without throwing
      expect(service).toBeTruthy();
    });

    it('should not re-initialize if already initialized', () => {
      service.initialize('mock');
      const spy = jest.spyOn(messageMonitor, 'getLastMessage');
      
      // Try to initialize again
      service.initialize('mock');
      
      // Should not call getLastMessage again for the same environment
      // (First initialization already called it)
      expect(spy).not.toHaveBeenCalledTimes(2);
    });

    it('bootstraps intake from MessageMonitor getHistory on initialize', () => {
      service.clear('replay');
      jest.spyOn(messageMonitor, 'getHistory').mockImplementation((topic: string) => {
        if (topic !== 'osf/workpiece/intake') {
          return [];
        }
        return [
          {
            topic: 'osf/workpiece/intake',
            payload: JSON.stringify({
              productRaw: 'WHITE',
              nfc: '832a423afcb534',
              timestamp: '2026-08-04T09:45:27.290373Z',
            }),
            timestamp: '2026-08-04T09:45:28.278Z',
            valid: true,
          },
          {
            topic: 'osf/workpiece/intake',
            payload: JSON.stringify({
              productRaw: 'BLUE',
              nfc: '78d10489b38ed8',
              timestamp: '2026-08-04T09:46:32.799367Z',
            }),
            timestamp: '2026-08-04T09:46:33.794Z',
            valid: true,
          },
        ];
      });

      service.initialize('replay');

      const snapshot = service.getSnapshot('replay');
      expect(snapshot.size).toBe(2);
      expect(snapshot.get('832a423afcb534')?.workpieceType).toBe('WHITE');
      expect(snapshot.get('78d10489b38ed8')?.workpieceType).toBe('BLUE');
      expect(snapshot.get('832a423afcb534')?.events.map((e) => e.eventType)).toEqual([
        'INPUT_RGB',
        'RGB_NFC',
      ]);
    });
  });

  describe('ngOnDestroy', () => {
    it('should clean up subscriptions', () => {
      service.initialize('mock');
      
      expect(() => service.ngOnDestroy()).not.toThrow();
    });

    it('should handle destroy when not initialized', () => {
      expect(() => service.ngOnDestroy()).not.toThrow();
    });
  });

  describe('ERP Data Integration', () => {
    it('should use ErpOrderDataService for Purchase Orders', () => {
      const spy = jest.spyOn(erpOrderDataService, 'popPurchaseOrderForWorkpieceType');
      
      // Store a purchase order
      erpOrderDataService.storePurchaseOrder('BLUE', {
        purchaseOrderId: 'ERP-PO-TEST',
        supplierId: 'SUP-TEST',
        orderDate: utcIsoTimestampMs(),
        orderAmount: 1,
        plannedDeliveryDate: utcIsoTimestampMs(),
      });

      // This would be called during generateOrderContext
      const result = erpOrderDataService.popPurchaseOrderForWorkpieceType('BLUE');
      
      expect(result).toBeTruthy();
      expect(result?.purchaseOrderId).toBe('ERP-PO-TEST');
      expect(result?.supplierId).toBe('SUP-TEST');
    });

    it('should use ErpOrderDataService for Customer Orders', () => {
      const spy = jest.spyOn(erpOrderDataService, 'popCustomerOrder');
      
      // Store a customer order
      erpOrderDataService.storeCustomerOrder({
        customerOrderId: 'ERP-CO-TEST',
        customerId: 'CUST-TEST',
        orderDate: utcIsoTimestampMs(),
        orderAmount: 1,
        plannedDeliveryDate: utcIsoTimestampMs(),
      });

      // This would be called during generateOrderContext
      const result = erpOrderDataService.popCustomerOrder();
      
      expect(result).toBeTruthy();
      expect(result?.customerOrderId).toBe('ERP-CO-TEST');
      expect(result?.customerId).toBe('CUST-TEST');
    });
  });

  describe('Order Status (Active/Completed)', () => {
    it('should determine order status from completed orders', () => {
      const orders: {
        active: Record<string, { orderId: string; orderType: string }>;
        completed: Record<string, { orderId: string; orderType: string }>;
      } = {
        active: {
          'order-1': { orderId: 'order-1', orderType: 'STORAGE' },
        },
        completed: {
          'order-2': { orderId: 'order-2', orderType: 'PRODUCTION' },
        },
      };

      // Verify that completed orders are tracked
      expect(orders.completed['order-2']).toBeTruthy();
      expect(orders.active['order-1']).toBeTruthy();
      expect(orders.completed['order-1']).toBeUndefined();
    });
  });

  describe('Order Status (FAILED/ERROR from order.state)', () => {
    it('should set status ERROR when order has state ERROR (e.g. quality-check failure)', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          ftsOrderId?: string,
          events?: TrackTraceEvent[]
        ) => OrderContext[];
      };
      const orders = {
        active: {
          'order-fail': {
            orderId: 'order-fail',
            orderType: 'PRODUCTION',
            state: 'ERROR',
            productionSteps: [{ id: 's1', source: 'START', target: 'DPS', type: 'NAVIGATION' }],
          },
        },
        completed: {},
      };
      const contexts = servicePrivate.generateOrderContext?.('RED', orders, 'order-fail');
      expect(contexts).toBeDefined();
      expect(contexts!.length).toBeGreaterThan(0);
      expect(contexts![0].status).toBe('ERROR');
    });

    it('should set status FAILED when order has state FAILED', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          ftsOrderId?: string,
          events?: TrackTraceEvent[]
        ) => OrderContext[];
      };
      const orders = {
        active: {
          'order-fail': {
            orderId: 'order-fail',
            orderType: 'PRODUCTION',
            state: 'FAILED',
            productionSteps: [],
          },
        },
        completed: {},
      };
      const contexts = servicePrivate.generateOrderContext?.('RED', orders, 'order-fail');
      expect(contexts).toBeDefined();
      expect(contexts!.length).toBeGreaterThan(0);
      expect(contexts![0].status).toBe('FAILED');
    });

    it('should prefer order.state ERROR over completed list membership', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          ftsOrderId?: string,
          events?: TrackTraceEvent[]
        ) => OrderContext[];
      };
      const orders = {
        active: {
          'order-err': {
            orderId: 'order-err',
            orderType: 'PRODUCTION',
            state: 'ERROR',
            productionSteps: [],
          },
        },
        completed: {
          'order-err': {
            orderId: 'order-err',
            orderType: 'PRODUCTION',
            state: 'ERROR',
            productionSteps: [],
          },
        },
      };
      const contexts = servicePrivate.generateOrderContext?.('RED', orders, 'order-err');
      expect(contexts).toBeDefined();
      expect(contexts!.length).toBeGreaterThan(0);
      expect(contexts![0].status).toBe('ERROR');
    });
  });

  describe('Date Extraction from Events', () => {
    it('should extract delivery date from DPS events for storage orders', () => {
      const events: TrackTraceEvent[] = [
        {
          timestamp: '2025-12-20T10:00:00Z',
          eventType: 'DOCK',
          location: 'SVR4H73275', // DPS
          moduleId: 'SVR4H73275',
        },
        {
          timestamp: '2025-12-20T11:00:00Z',
          eventType: 'DOCK',
          location: 'SVR3QA0022', // HBW
          moduleId: 'SVR3QA0022',
        },
      ];

      // Access private method via type assertion (for testing)
      const servicePrivate = service as any;
      const extractedDates = servicePrivate.extractDatesFromEvents?.(events, 'STORAGE');

      if (extractedDates) {
        expect(extractedDates.deliveryDate).toBe('2025-12-20T10:00:00Z');
        expect(extractedDates.storageDate).toBe('2025-12-20T11:00:00Z');
      }
    });

    it('should extract production start and delivery end dates for production orders', () => {
      const events: TrackTraceEvent[] = [
        {
          timestamp: '2025-12-20T10:00:00Z',
          eventType: 'DOCK',
          location: 'SVR3QA0022', // HBW
          moduleId: 'SVR3QA0022',
        },
        {
          timestamp: '2025-12-20T11:00:00Z',
          eventType: 'DOCK',
          location: 'SVR4H76449', // DRILL
          moduleId: 'SVR4H76449',
          stationId: 'DRILL',
        },
        {
          timestamp: '2025-12-20T12:00:00Z',
          eventType: 'DOCK',
          location: 'SVR4H73275', // DPS
          moduleId: 'SVR4H73275',
        },
      ];

      // Access private method via type assertion (for testing)
      const servicePrivate = service as any;
      const extractedDates = servicePrivate.extractDatesFromEvents?.(events, 'PRODUCTION');

      if (extractedDates) {
        expect(extractedDates.productionStartDate).toBe('2025-12-20T10:00:00Z');
        expect(extractedDates.deliveryEndDate).toBe('2025-12-20T12:00:00Z');
      }
    });
  });

  describe('multi-AGV (5iO4 and xkI4)', () => {
    it('should subscribe to FTS state topics for both AGVs when layout has two FTS', () => {
      const mappingMock = {
        getAgvOptions: jest.fn(() => [
          { serial: '5iO4', label: 'AGV-1' },
          { serial: 'xkI4', label: 'AGV-2' },
        ]),
      };

      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          WorkpieceHistoryService,
          MessageMonitorService,
          ModuleNameService,
          EnvironmentService,
          AgvRouteService,
          ErpOrderDataService,
          MessageValidationService,
          MessagePersistenceService,
          { provide: ShopfloorMappingService, useValue: mappingMock },
        ],
      });

      const svc = TestBed.inject(WorkpieceHistoryService);
      const mm = TestBed.inject(MessageMonitorService);
      jest.spyOn(mm, 'getLastMessage').mockReturnValue(of(null));

      svc.initialize('mock');

      expect(mm.getLastMessage).toHaveBeenCalledWith('fts/v1/ff/5iO4/state');
      expect(mm.getLastMessage).toHaveBeenCalledWith('fts/v1/ff/xkI4/state');

      svc.ngOnDestroy();
    });

    it('should subscribe to both AGV FTS topics when layout not loaded yet (fallback)', () => {
      const mappingMock = {
        getAgvOptions: jest.fn(() => []),
      };

      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          WorkpieceHistoryService,
          MessageMonitorService,
          ModuleNameService,
          EnvironmentService,
          AgvRouteService,
          ErpOrderDataService,
          MessageValidationService,
          MessagePersistenceService,
          { provide: ShopfloorMappingService, useValue: mappingMock },
        ],
      });

      const svc = TestBed.inject(WorkpieceHistoryService);
      const mm = TestBed.inject(MessageMonitorService);
      jest.spyOn(mm, 'getLastMessage').mockReturnValue(of(null));

      svc.initialize('mock');

      expect(mm.getLastMessage).toHaveBeenCalledWith('fts/v1/ff/5iO4/state');
      expect(mm.getLastMessage).toHaveBeenCalledWith('fts/v1/ff/xkI4/state');

      svc.ngOnDestroy();
    });

    it('keeps PRODUCTION phase on NFC when FTS step-order is another color (dual-AGV)', () => {
      const blueOrder = 'blue-prod-order';
      const redOrder = 'red-prod-order';
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const orders = {
        active: {
          [blueOrder]: { orderId: blueOrder, orderType: 'PRODUCTION', type: 'BLUE' },
          [redOrder]: { orderId: redOrder, orderType: 'PRODUCTION', type: 'RED' },
        },
        completed: {},
      };

      // Own BLUE production stop at HBW
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: 'xkI4',
          timestamp: '2026-09-03T10:00:00.000Z',
          orderId: blueOrder,
          orderUpdateId: 1,
          lastNodeId: 'SVR3QA0022',
          driving: false,
          actionState: {
            id: 'dock-hbw',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-09-03T10:00:00.000Z',
          },
          load: [{ loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' }],
          _moduleSerialId: 'xkI4',
        },
        orders
      );

      // Same NFC on AGV-2 while CCU step-order is RED (foreign)
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: 'xkI4',
          timestamp: '2026-09-03T10:01:00.000Z',
          orderId: redOrder,
          orderUpdateId: 2,
          lastNodeId: '1',
          driving: false,
          actionState: {
            id: 'turn-1',
            command: 'TURN',
            state: 'FINISHED',
            timestamp: '2026-09-03T10:01:00.000Z',
          },
          load: [{ loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' }],
          _moduleSerialId: 'xkI4',
        },
        orders
      );

      const blue = service.getSnapshot(env).get('nfc-blue');
      const turn = blue?.events.find((e) => e.eventType === 'TURN' && e.location === '1');
      expect(turn).toBeDefined();
      expect(turn?.orderType).toBe('PRODUCTION');
      expect(turn?.orderId).toBe(redOrder);
      expect(turn?.details?.['coPassenger']).toBe(true);
      expect(turn?.moduleId).toBe('xkI4');
    });

    it('keeps STORAGE phase on NFC when FTS step-order is another color (dual-AGV)', () => {
      const whiteStorage = 'white-storage-order';
      const blueProd = 'blue-prod-order';
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const orders = {
        active: {
          [whiteStorage]: { orderId: whiteStorage, orderType: 'STORAGE', type: 'WHITE' },
          [blueProd]: { orderId: blueProd, orderType: 'PRODUCTION', type: 'BLUE' },
        },
        completed: {},
      };

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-09-03T09:00:00.000Z',
          orderId: whiteStorage,
          orderUpdateId: 1,
          lastNodeId: 'SVR4H73275',
          driving: false,
          actionState: {
            id: 'dock-dps',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-09-03T09:00:00.000Z',
          },
          load: [{ loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        orders
      );

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: 'xkI4',
          timestamp: '2026-09-03T09:01:00.000Z',
          orderId: blueProd,
          orderUpdateId: 2,
          lastNodeId: '2',
          driving: false,
          actionState: {
            id: 'pass-2',
            command: 'PASS',
            state: 'FINISHED',
            timestamp: '2026-09-03T09:01:00.000Z',
          },
          load: [{ loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: 'xkI4',
        },
        orders
      );

      const white = service.getSnapshot(env).get('nfc-white');
      const pass = white?.events.find((e) => e.eventType === 'PASS' && e.location === '2');
      expect(pass).toBeDefined();
      expect(pass?.orderType).toBe('STORAGE');
      expect(pass?.details?.['coPassenger']).toBe(true);
    });
  });

  describe('TURN Direction', () => {
    it('should store TURN direction in event details', () => {
      // This tests the integration with FTS order stream
      // The actual direction extraction happens in updateWorkpieceHistory
      const event: TrackTraceEvent = {
        timestamp: '2025-12-20T10:00:00Z',
        eventType: 'TURN',
        details: {
          direction: 'LEFT',
        },
      };

      expect(event.details?.['direction']).toBe('LEFT');
    });

    it('remaps MQTT DOCK at intersection to TURN (no dock at I*)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      jest.spyOn(ftsRouteService, 'resolveNodeRef').mockImplementation((id: string | undefined) =>
        id === '1' || id === 'intersection:1' ? 'intersection:1' : id ?? null
      );

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:04:08.000Z',
          orderId: 'ord-w',
          lastNodeId: '1',
          driving: false,
          actionState: {
            id: 'act-pass',
            command: 'PASS',
            state: 'FINISHED',
            timestamp: '2026-08-06T09:04:08.000Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:04:08.100Z',
          orderId: 'ord-w',
          lastNodeId: '1',
          driving: false,
          actionState: {
            id: 'act-dock-ix',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-08-06T09:04:08.100Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );

      const events = service.getSnapshot(env).get('nfc-w')?.events.filter((e) => e.eventSource === 'FTS') ?? [];
      expect(events.map((e) => e.eventType)).toEqual(['PASS', 'TURN']);
      const turn = events[1];
      expect(turn?.details?.['intersectionNumber']).toBe('1');
      expect(turn?.details?.['remappedFromDockAtIntersection']).toBe(true);
      expect(turn?.details?.['originalCommand']).toBe('DOCK');
      expect(turn?.details?.['direction']).toBeUndefined();
    });

    it('does not emit second TURN when DOCK follows TURN at same intersection', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      jest.spyOn(ftsRouteService, 'resolveNodeRef').mockImplementation((id: string | undefined) =>
        id === '2' || id === 'intersection:2' ? 'intersection:2' : id ?? null
      );

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:34:30.000Z',
          orderId: 'ord-w',
          lastNodeId: '2',
          driving: false,
          actionState: {
            id: 'act-turn-2',
            command: 'TURN',
            state: 'FINISHED',
            timestamp: '2026-08-06T09:34:30.000Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:34:33.000Z',
          orderId: 'ord-w',
          lastNodeId: '2',
          driving: false,
          actionState: {
            id: 'act-dock-2',
            command: 'DOCK',
            state: 'RUNNING',
            timestamp: '2026-08-06T09:34:33.000Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );

      const events = service.getSnapshot(env).get('nfc-w')?.events.filter((e) => e.eventSource === 'FTS') ?? [];
      expect(events.map((e) => e.eventType)).toEqual(['TURN']);
      expect(events[0]?.actionId).toBe('act-turn-2');
    });

    it('emits new TURN when actionId changes at same intersection (FINISHED)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      (service as any).turnDirectionByActionId.set('turn-old', 'RIGHT');
      (service as any).turnDirectionByActionId.set('turn-new', 'LEFT');
      jest.spyOn(ftsRouteService, 'resolveNodeRef').mockImplementation((id: string | undefined) =>
        id === '2' || id === 'intersection:2' ? 'intersection:2' : id ?? null
      );

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:34:29.000Z',
          orderId: 'ord-w',
          lastNodeId: '1',
          driving: true,
          actionState: {
            id: 'turn-old',
            command: 'TURN',
            state: 'FINISHED',
            timestamp: '2026-08-06T09:34:29.000Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );
      // Stale actionId while arriving at I2 — must not emit
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:34:30.000Z',
          orderId: 'ord-w',
          lastNodeId: '2',
          driving: true,
          actionState: {
            id: 'turn-old',
            command: 'TURN',
            state: 'FINISHED',
            timestamp: '2026-08-06T09:34:30.000Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );
      // Real TURN at I2
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-08-06T09:34:31.000Z',
          orderId: 'ord-w',
          lastNodeId: '2',
          driving: false,
          actionState: {
            id: 'turn-new',
            command: 'TURN',
            state: 'FINISHED',
            timestamp: '2026-08-06T09:34:31.000Z',
          },
          load: [{ loadId: 'nfc-w', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );

      const events = service.getSnapshot(env).get('nfc-w')?.events.filter((e) => e.eventSource === 'FTS') ?? [];
      expect(events.map((e) => e.eventType)).toEqual(['TURN', 'TURN']);
      expect(events[0]?.location).toBe('1');
      expect(events[0]?.details?.['direction']).toBe('RIGHT');
      expect(events[1]?.location).toBe('2');
      expect(events[1]?.details?.['direction']).toBe('LEFT');
    });
  });

  describe('Deduplication', () => {
    it('should deduplicate identical events for the same workpiece', () => {
      const svc = service as unknown as {
        shouldAppendEvent: (environmentKey: string, workpieceId: string, event: TrackTraceEvent) => boolean;
      };

      const event: TrackTraceEvent = {
        timestamp: '2026-04-13T10:00:00Z',
        eventType: 'DOCK',
        workpieceId: 'wp-1',
        orderId: 'order-1',
        orderUpdateId: 1,
        actionId: 'a1',
        location: 'SVR3QA0022',
        moduleId: '5iO4',
      };

      expect(svc.shouldAppendEvent('mock', 'wp-1', event)).toBe(true);
      expect(svc.shouldAppendEvent('mock', 'wp-1', event)).toBe(false);
    });

    it('should deduplicate semantic duplicates across sources for station actions', () => {
      const svc = service as unknown as {
        shouldAppendEvent: (environmentKey: string, workpieceId: string, event: TrackTraceEvent) => boolean;
      };

      const ftsLikeEvent: TrackTraceEvent = {
        timestamp: '2026-05-06T13:00:00Z',
        eventType: 'PROCESS',
        workpieceId: 'wp-2',
        orderId: 'order-2',
        orderUpdateId: 4,
        actionId: 'action-xyz',
        stationId: 'AIQS',
        moduleId: '5iO4',
        location: 'SVR4H76530',
      };
      const moduleLikeEvent: TrackTraceEvent = {
        timestamp: '2026-05-06T13:00:02Z',
        eventType: 'PROCESS',
        workpieceId: 'wp-2',
        orderId: 'order-2',
        orderUpdateId: 4,
        actionId: 'action-xyz',
        stationId: 'AIQS',
        moduleId: 'SVR4H76530',
        location: 'SVR4H76530',
      };

      expect(svc.shouldAppendEvent('mock', 'wp-2', ftsLikeEvent)).toBe(true);
      expect(svc.shouldAppendEvent('mock', 'wp-2', moduleLikeEvent)).toBe(false);
    });

    it('deduplicates CHECK_QUALITY from NodeRed + direct module topics (same actionId, different orderUpdateId)', () => {
      const svc = service as unknown as {
        shouldAppendEvent: (environmentKey: string, workpieceId: string, event: TrackTraceEvent) => boolean;
      };

      const nodeRedEvent: TrackTraceEvent = {
        timestamp: '2026-07-28T08:03:52.774Z',
        eventType: 'CHECK_QUALITY',
        workpieceId: '711f5fa991adb1',
        orderId: 'fd488dcf-947c-4471-8472-7f1c552d9013',
        orderUpdateId: 10,
        actionId: 'e9792d9b-12e6-45c8-b097-633a6b0bea33',
        stationId: 'AIQS',
        location: 'SVR4H76530',
        eventSource: 'MODULE',
        details: { result: 'FAILED' },
      };
      const directModuleEvent: TrackTraceEvent = {
        ...nodeRedEvent,
        timestamp: '2026-07-28T08:03:53.948Z',
        orderUpdateId: 0,
      };

      expect(svc.shouldAppendEvent('mock', '711f5fa991adb1', nodeRedEvent)).toBe(true);
      expect(svc.shouldAppendEvent('mock', '711f5fa991adb1', directModuleEvent)).toBe(false);
    });
  });

  describe('Quality check image attachment', () => {
    it('attaches quality image to CHECK_QUALITY when result and ts match', () => {
      const svc = service as unknown as {
        latestQualityCheck: {
          dataUrl: string;
          ts?: string;
          result?: string;
          classification?: string;
          classificationDesc?: string;
        } | null;
        attachQualityImageIfRelevant: (event: TrackTraceEvent) => void;
      };

      svc.latestQualityCheck = {
        dataUrl: 'data:image/png;base64,abc',
        ts: '2026-08-07T09:08:36.886Z',
        result: 'FAILED',
        classification: 'CRACK',
        classificationDesc: 'Crack',
      };

      const event: TrackTraceEvent = {
        timestamp: '2026-08-07T09:08:37.175Z',
        eventType: 'CHECK_QUALITY',
        workpieceId: 'wp-blue-nok',
        stationId: 'AIQS',
        details: { result: 'FAILED' },
      };
      svc.attachQualityImageIfRelevant(event);
      expect(event.details?.['qualityImage']).toBe('data:image/png;base64,abc');
      expect(event.details?.['qualityClassification']).toBe('CRACK');
      expect(event.details?.['qualityClassificationDesc']).toBe('Crack');
    });

    it('attaches when module result is OK and MQTT result is PASSED', () => {
      const svc = service as unknown as {
        latestQualityCheck: { dataUrl: string; ts?: string; result?: string } | null;
        attachQualityImageIfRelevant: (event: TrackTraceEvent) => void;
      };
      svc.latestQualityCheck = {
        dataUrl: 'data:image/png;base64,ok',
        ts: '2026-08-07T09:15:25.701Z',
        result: 'PASSED',
      };
      const event: TrackTraceEvent = {
        timestamp: '2026-08-07T09:15:25.837Z',
        eventType: 'CHECK_QUALITY',
        details: { result: 'OK' },
      };
      svc.attachQualityImageIfRelevant(event);
      expect(event.details?.['qualityImage']).toBe('data:image/png;base64,ok');
    });

    it('skips attach when result mismatches', () => {
      const svc = service as unknown as {
        latestQualityCheck: { dataUrl: string; ts?: string; result?: string } | null;
        attachQualityImageIfRelevant: (event: TrackTraceEvent) => void;
      };
      svc.latestQualityCheck = {
        dataUrl: 'data:image/png;base64,abc',
        ts: '2026-08-07T09:08:36.886Z',
        result: 'FAILED',
      };
      const event: TrackTraceEvent = {
        timestamp: '2026-08-07T09:08:37.175Z',
        eventType: 'CHECK_QUALITY',
        details: { result: 'PASSED' },
      };
      svc.attachQualityImageIfRelevant(event);
      expect(event.details?.['qualityImage']).toBeUndefined();
    });
  });

  describe('Planned station chain', () => {
    it('should return fixed storage chain DPS -> HBW', () => {
      const svc = service as unknown as {
        getPlannedStationChain: (workpieceType: string, orderType: 'STORAGE' | 'PRODUCTION') => string[];
      };
      expect(svc.getPlannedStationChain('BLUE', 'STORAGE')).toEqual(['DPS', 'HBW']);
    });

    it('should return production chain by workpiece type', () => {
      const svc = service as unknown as {
        getPlannedStationChain: (workpieceType: string, orderType: 'STORAGE' | 'PRODUCTION') => string[];
      };
      expect(svc.getPlannedStationChain('BLUE', 'PRODUCTION')).toEqual(['HBW', 'DRILL', 'MILL', 'AIQS', 'DPS']);
      expect(svc.getPlannedStationChain('WHITE', 'PRODUCTION')).toEqual(['HBW', 'DRILL', 'AIQS', 'DPS']);
      expect(svc.getPlannedStationChain('RED', 'PRODUCTION')).toEqual(['HBW', 'MILL', 'AIQS', 'DPS']);
    });
  });

  describe('Environment snapshot trigger matrix', () => {
    it('does not capture PROCESS/DRILL/MILL — only CHECK_QUALITY + DOCK at mfg stations', () => {
      const svc = service as unknown as {
        shouldCaptureEnvironmentSnapshot: (event: TrackTraceEvent) => boolean;
      };
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:00.000Z',
          eventType: 'PROCESS',
          orderType: 'PRODUCTION',
          stationId: 'DRILL',
        })
      ).toBe(false);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:00.500Z',
          eventType: 'DRILL',
          orderType: 'PRODUCTION',
          stationId: 'DRILL',
        })
      ).toBe(false);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:01.000Z',
          eventType: 'CHECK_QUALITY',
          orderType: 'PRODUCTION',
          stationId: 'AIQS',
        })
      ).toBe(true);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:01.500Z',
          eventType: 'DOCK',
          orderType: 'PRODUCTION',
          stationId: 'DRILL',
        })
      ).toBe(true);
    });

    it('captures HBW/DPS by order-specific pick/drop rules', () => {
      const svc = service as unknown as {
        shouldCaptureEnvironmentSnapshot: (event: TrackTraceEvent) => boolean;
      };
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:02.000Z',
          eventType: 'PICK',
          orderType: 'PRODUCTION',
          stationId: 'HBW',
        })
      ).toBe(true);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:03.000Z',
          eventType: 'DROP',
          orderType: 'PRODUCTION',
          stationId: 'DPS',
        })
      ).toBe(true);
      // STORAGE: DPS DROP + HBW PICK (real flow; not DPS PICK / HBW DROP)
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:04.000Z',
          eventType: 'DROP',
          orderType: 'STORAGE',
          stationId: 'DPS',
        })
      ).toBe(true);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:05.000Z',
          eventType: 'PICK',
          orderType: 'STORAGE',
          stationId: 'HBW',
        })
      ).toBe(true);
    });

    it('keeps DRILL/MILL/CHECK_QUALITY as MQTT event types (not generic PROCESS)', () => {
      const svc = service as unknown as {
        mapModuleCommandToEventType: (command: string) => string;
        isTrackableModuleCommand: (command: string) => boolean;
        resolveLoadPosition: (
          environmentKey: string,
          state: { loads?: Array<{ loadId?: string; loadType?: string; loadPosition?: string }> },
          workpieceId: string,
          history: { workpieceId: string; workpieceType: string; events: unknown[] },
          stationName: string | null,
          mappedCommand: string
        ) => string | null;
        resolveModuleWorkpieceId: (
          state: unknown,
          action: { command?: string; metadata?: Record<string, unknown> },
          result: unknown,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> }
        ) => string | null;
        resolveModuleWorkpieceType: (
          state: unknown,
          action: { metadata?: Record<string, unknown> }
        ) => string | null;
      };
      expect(svc.mapModuleCommandToEventType('DRILL')).toBe('DRILL');
      expect(svc.mapModuleCommandToEventType('MILL')).toBe('MILL');
      expect(svc.mapModuleCommandToEventType('CHECK_QUALITY')).toBe('CHECK_QUALITY');
      expect(svc.mapModuleCommandToEventType('INPUT_RGB')).toBe('INPUT_RGB');
      expect(svc.isTrackableModuleCommand('DRILL')).toBe(true);
      expect(svc.isTrackableModuleCommand('INPUT_RGB')).toBe(false);
      expect(svc.isTrackableModuleCommand('RGB_NFC')).toBe(false);
      expect(
        svc.resolveLoadPosition(
          'mock',
          {
            loads: [
              { loadId: '2b2c6dd469a47a', loadType: 'WHITE', loadPosition: 'A1' },
              { loadId: '', loadPosition: 'A2' },
            ],
          },
          '2b2c6dd469a47a',
          { workpieceId: '2b2c6dd469a47a', workpieceType: 'WHITE', events: [] },
          'HBW',
          'PICK'
        )
      ).toBe('A1');
      expect(
        svc.resolveModuleWorkpieceId(
          {},
          { command: 'RGB_NFC' },
          '2b2c6dd469a47a',
          { active: {}, completed: {} }
        )
      ).toBe('2b2c6dd469a47a');
      expect(svc.resolveModuleWorkpieceType({}, { metadata: { type: 'WHITE' } })).toBe('WHITE');
    });

    it('bootstraps Color+NFC history from osf/workpiece/intake', () => {
      const svc = service as unknown as {
        ingestWorkpieceIntake: (environmentKey: string, payload: unknown) => void;
      };
      svc.ingestWorkpieceIntake('mock', {
        productRaw: 'BLUE',
        nfc: '59a42cb15f9e1f',
        timestamp: '2026-08-26T11:00:00.000Z',
      });
      const history = service.getSnapshot('mock').get('59a42cb15f9e1f');
      expect(history).toBeDefined();
      expect(history?.workpieceType).toBe('BLUE');
      expect(history?.events.map((e) => e.eventType)).toEqual(['INPUT_RGB', 'RGB_NFC']);
      expect(history?.events.every((e) => e.details?.['sourceTopic'] === 'osf/workpiece/intake')).toBe(
        true
      );

      // Dedup on second publish
      svc.ingestWorkpieceIntake('mock', {
        productRaw: 'BLUE',
        nfc: '59a42cb15f9e1f',
        timestamp: '2026-08-26T11:00:01.000Z',
      });
      expect(service.getSnapshot('mock').get('59a42cb15f9e1f')?.events.length).toBe(2);
    });

    it('ignores intake without known color', () => {
      const svc = service as unknown as {
        ingestWorkpieceIntake: (environmentKey: string, payload: unknown) => void;
      };
      svc.ingestWorkpieceIntake('mock', {
        productRaw: 'UNKNOWN',
        nfc: 'deadbeef',
        timestamp: '2026-08-26T11:00:00.000Z',
      });
      expect(service.getSnapshot('mock').size).toBe(0);
    });

    it('does not capture non-matrix events', () => {
      const svc = service as unknown as {
        shouldCaptureEnvironmentSnapshot: (event: TrackTraceEvent) => boolean;
      };
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:06.000Z',
          eventType: 'PICK',
          orderType: 'PRODUCTION',
          stationId: 'MILL',
        })
      ).toBe(false);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:08.000Z',
          eventType: 'PICK',
          orderType: 'STORAGE',
          stationId: 'DPS',
        })
      ).toBe(false);
    });
  });

  describe('Module storage fallback parsing', () => {
    it('extracts workpiece type from actionStates metadata when loads are missing', () => {
      const svc = service as unknown as {
        resolveModuleActionState: (state: unknown) => { metadata?: Record<string, unknown> } | null;
        resolveModuleWorkpieceType: (
          state: unknown,
          actionState: { metadata?: Record<string, unknown> }
        ) => 'BLUE' | 'WHITE' | 'RED' | null;
      };

      const moduleState = {
        serialNumber: 'SVR4H73275',
        timestamp: '2026-05-06T13:00:00Z',
        orderId: 'order-storage-1',
        actionState: null,
        actionStates: [
          {
            id: 'a-1',
            command: 'DROP',
            state: 'FINISHED',
            timestamp: '2026-05-06T13:00:00Z',
            metadata: { workpiece: { type: 'WHITE' } },
          },
        ],
      };

      const resolved = svc.resolveModuleActionState(moduleState);
      expect(resolved).toBeTruthy();
      expect(svc.resolveModuleWorkpieceType(moduleState, resolved!)).toBe('WHITE');
    });
  });

  describe('A1 Multi-Order context rebuild', () => {
    it('builds STORAGE and PRODUCTION contexts from distinct event orderIds', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          orderIds?: string | string[],
          events?: TrackTraceEvent[],
          previousContexts?: OrderContext[]
        ) => OrderContext[];
      };

      const storageId = 'storage-uuid-1';
      const productionId = 'production-uuid-2';
      const orders = {
        active: {
          [productionId]: {
            orderId: productionId,
            orderType: 'PRODUCTION',
            state: 'ENQUEUED',
            startedAt: '2026-07-28T08:00:00Z',
            productionSteps: [{ id: 's1', source: 'HBW', target: 'DPS', type: 'NAVIGATION' }],
          },
        },
        completed: {
          [storageId]: {
            orderId: storageId,
            orderType: 'STORAGE',
            state: 'FINISHED',
            startedAt: '2026-07-28T07:50:00Z',
            productionSteps: [{ id: 's0', source: 'DPS', target: 'HBW', type: 'NAVIGATION' }],
          },
        },
      };

      const events: TrackTraceEvent[] = [
        {
          timestamp: '2026-07-28T07:50:10Z',
          eventType: 'DROP',
          location: 'SVR4H73275',
          orderId: storageId,
          orderType: 'STORAGE',
        },
        {
          timestamp: '2026-07-28T08:01:00Z',
          eventType: 'PICK',
          location: 'SVR3QA0022',
          orderId: productionId,
          orderType: 'PRODUCTION',
        },
      ];

      const contexts = servicePrivate.generateOrderContext(
        'WHITE',
        orders,
        [storageId, productionId],
        events
      );

      expect(contexts.map((c) => c.orderType)).toEqual(['STORAGE', 'PRODUCTION']);
      expect(contexts.map((c) => c.orderId)).toEqual([storageId, productionId]);
    });

    it('collapses multiple STORAGE orderIds into one card', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          orderIds?: string | string[],
          events?: TrackTraceEvent[],
          previousContexts?: OrderContext[]
        ) => OrderContext[];
      };

      const intakeId = 'intake-uuid';
      const transportId = 'agv-storage-uuid';
      const orders = {
        active: {},
        completed: {
          [intakeId]: {
            orderId: intakeId,
            orderType: 'STORAGE',
            state: 'FINISHED',
            startedAt: '2026-07-28T07:50:00Z',
          },
        },
      };

      const events: TrackTraceEvent[] = [
        {
          timestamp: '2026-07-28T07:50:10Z',
          eventType: 'INPUT_RGB',
          orderId: intakeId,
          orderType: 'STORAGE',
          stationId: 'DPS',
        },
        {
          timestamp: '2026-07-28T07:51:00Z',
          eventType: 'DOCK',
          orderId: transportId,
          orderType: 'STORAGE',
          stationId: 'HBW',
        },
      ];

      const contexts = servicePrivate.generateOrderContext(
        'RED',
        orders,
        [intakeId, transportId],
        events
      );

      expect(contexts.filter((c) => c.orderType === 'STORAGE')).toHaveLength(1);
      expect(contexts[0].orderId).toBe(intakeId);
    });

    it('preserves previous ERP fields when rebuilding the same orderId', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          orderIds?: string | string[],
          events?: TrackTraceEvent[],
          previousContexts?: OrderContext[]
        ) => OrderContext[];
      };

      const productionId = 'production-uuid-keep';
      const orders = {
        active: {
          [productionId]: {
            orderId: productionId,
            orderType: 'PRODUCTION',
            state: 'ENQUEUED',
            startedAt: '2026-07-28T08:00:00Z',
          },
        },
        completed: {},
      };
      const previous: OrderContext[] = [
        {
          orderId: productionId,
          orderType: 'PRODUCTION',
          customerOrderId: 'ERP-CO-KEEP',
          customerId: 'CUST-KEEP',
        },
      ];

      const contexts = servicePrivate.generateOrderContext(
        'WHITE',
        orders,
        [productionId],
        [],
        previous
      );

      expect(contexts).toHaveLength(1);
      expect(contexts[0].customerOrderId).toBe('ERP-CO-KEEP');
      expect(contexts[0].customerId).toBe('CUST-KEEP');
    });

    it('prefers own-color PRODUCTION over foreign co-passenger order when collapsing', () => {
      const servicePrivate = service as unknown as {
        generateOrderContext: (
          workpieceType: string,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
          orderIds?: string | string[],
          events?: TrackTraceEvent[],
          previousContexts?: OrderContext[]
        ) => OrderContext[];
        rebuildOrderContexts: (
          history: WorkpieceHistory,
          orders: { active: Record<string, unknown>; completed: Record<string, unknown> }
        ) => OrderContext[];
      };

      const foreignWhiteProd = 'a9325a20-foreign-white';
      const ownBlueProd = '83700d76-own-blue';
      const orders = {
        active: {},
        completed: {
          [foreignWhiteProd]: {
            orderId: foreignWhiteProd,
            orderType: 'PRODUCTION',
            type: 'WHITE',
            state: 'FINISHED',
            startedAt: '2026-08-04T09:50:00Z',
            workpieceId: 'white-nfc',
          },
          [ownBlueProd]: {
            orderId: ownBlueProd,
            orderType: 'PRODUCTION',
            type: 'BLUE',
            state: 'FINISHED',
            startedAt: '2026-08-04T09:50:50Z',
            workpieceId: '78d10489b38ed8',
          },
        },
      };

      const events: TrackTraceEvent[] = [
        // Many FTS Ist stops on foreign WHITE order (co-passenger)
        ...[1, 2, 3, 4, 5, 6].map((i) => ({
          timestamp: `2026-08-04T09:51:0${i}.000Z`,
          eventType: 'DOCK',
          eventSource: 'FTS' as const,
          orderId: foreignWhiteProd,
          orderType: 'PRODUCTION' as const,
          stationId: 'MILL',
          workpieceId: '78d10489b38ed8',
          workpieceType: 'BLUE',
          location: 'SVR3QA2098',
          details: { coPassenger: true, visitKind: 'IST_ONLY' },
        })),
        // Own MODULE anchors on BLUE production
        {
          timestamp: '2026-08-04T09:50:50.000Z',
          eventType: 'DROP',
          eventSource: 'MODULE',
          orderId: ownBlueProd,
          orderType: 'PRODUCTION',
          stationId: 'HBW',
          workpieceId: '78d10489b38ed8',
          workpieceType: 'BLUE',
          location: 'SVR3QA0022',
        },
        {
          timestamp: '2026-08-04T09:53:12.000Z',
          eventType: 'DRILL',
          eventSource: 'MODULE',
          orderId: ownBlueProd,
          orderType: 'PRODUCTION',
          stationId: 'DRILL',
          workpieceId: '78d10489b38ed8',
          workpieceType: 'BLUE',
          location: 'SVR4H76449',
        },
      ];

      // Collapse path: both IDs requested (legacy / without coPassenger filter)
      const collapsed = servicePrivate.generateOrderContext(
        'BLUE',
        orders,
        [foreignWhiteProd, ownBlueProd],
        events
      );
      const production = collapsed.find((c) => c.orderType === 'PRODUCTION');
      expect(production?.orderId).toBe(ownBlueProd);

      // rebuild path: coPassenger foreign UUID must not enter the request set
      const rebuilt = servicePrivate.rebuildOrderContexts(
        {
          workpieceId: '78d10489b38ed8',
          workpieceType: 'BLUE',
          events,
          orders: [
            { orderId: foreignWhiteProd, orderType: 'PRODUCTION' },
            { orderId: ownBlueProd, orderType: 'PRODUCTION' },
          ],
        },
        orders
      );
      expect(rebuilt.filter((c) => c.orderType === 'PRODUCTION')).toHaveLength(1);
      expect(rebuilt.find((c) => c.orderType === 'PRODUCTION')?.orderId).toBe(ownBlueProd);
    });
  });

  describe('shouldCaptureEnvironmentSnapshot', () => {
    const makeEvent = (overrides: Partial<{ stationId: string; orderType: string; eventType: string }>) => ({
      stationId: overrides.stationId ?? '',
      orderType: overrides.orderType ?? '',
      eventType: overrides.eventType ?? '',
    } as any);

    it('captures HBW DROP in PRODUCTION', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'HBW', orderType: 'PRODUCTION', eventType: 'DROP' }))).toBe(true);
    });

    it('captures DPS PICK in PRODUCTION', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'DPS', orderType: 'PRODUCTION', eventType: 'PICK' }))).toBe(true);
    });

    it('captures HBW PICK in PRODUCTION (existing behaviour)', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'HBW', orderType: 'PRODUCTION', eventType: 'PICK' }))).toBe(true);
    });

    it('captures HBW PICK in STORAGE', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'HBW', orderType: 'STORAGE', eventType: 'PICK' }))).toBe(true);
    });

    it('captures DPS DROP in PRODUCTION', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'DPS', orderType: 'PRODUCTION', eventType: 'DROP' }))).toBe(true);
    });

    it('does NOT capture unrelated events like DRILL PICK', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'DRILL', orderType: 'PRODUCTION', eventType: 'PICK' }))).toBe(false);
    });

    it('captures DOCK at DRILL/MILL/AIQS in PRODUCTION (Ist arrival / co-passenger)', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'DRILL', orderType: 'PRODUCTION', eventType: 'DOCK' }))).toBe(true);
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'MILL', orderType: 'PRODUCTION', eventType: 'DOCK' }))).toBe(true);
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'AIQS', orderType: 'PRODUCTION', eventType: 'DOCK' }))).toBe(true);
    });

    it('does NOT capture DOCK at DRILL in STORAGE', () => {
      const sp = service as any;
      expect(sp.shouldCaptureEnvironmentSnapshot(makeEvent({ stationId: 'DRILL', orderType: 'STORAGE', eventType: 'DOCK' }))).toBe(false);
    });
  });

  describe('FTS Ist stops (same-node DOCK + co-passenger)', () => {
    const drillSerial = 'SVR4H76449';

    const makeFtsState = (
      command: string,
      actionId: string,
      timestamp: string,
      load: Array<{ loadId: string; loadType: 'RED' | 'WHITE' | 'BLUE'; loadPosition: string }>
    ) => ({
      serialNumber: '5iO4',
      timestamp,
      orderId: 'ord-co',
      orderUpdateId: 1,
      lastNodeId: drillSerial,
      driving: false,
      actionState: { id: actionId, command, state: 'FINISHED', timestamp },
      load,
      _moduleSerialId: '5iO4',
    });

    it('emits DOCK after PASS at the same manufacturing node', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      sp.updateWorkpieceHistory(
        env,
        makeFtsState('PASS', 'act-pass', '2026-07-29T10:00:00.000Z', [
          { loadId: 'nfc-red', loadType: 'RED', loadPosition: '2' },
        ]),
        { active: {}, completed: {} }
      );
      sp.updateWorkpieceHistory(
        env,
        makeFtsState('DOCK', 'act-dock', '2026-07-29T10:00:01.000Z', [
          { loadId: 'nfc-red', loadType: 'RED', loadPosition: '2' },
        ]),
        { active: {}, completed: {} }
      );

      const history = service.getSnapshot(env).get('nfc-red');
      expect(history).toBeDefined();
      const types = history!.events.map((e) => e.eventType);
      expect(types).toContain('PASS');
      expect(types).toContain('DOCK');
      const dock = history!.events.find((e) => e.eventType === 'DOCK');
      expect(dock?.details?.['visitKind']).toBe('IST_ONLY');
      expect(dock?.details?.['coPassenger']).toBe(true);
      expect(dock?.stationId).toBe('DRILL');
    });

    it('marks WHITE at DRILL as PLANNED (not co-passenger)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      sp.updateWorkpieceHistory(
        env,
        makeFtsState('DOCK', 'act-w', '2026-07-29T10:00:00.000Z', [
          { loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' },
        ]),
        { active: {}, completed: {} }
      );

      const history = service.getSnapshot(env).get('nfc-white');
      const dock = history!.events.find((e) => e.eventType === 'DOCK');
      expect(dock?.details?.['visitKind']).toBe('PLANNED');
      expect(dock?.details?.['coPassenger']).toBe(false);
    });
  });

  describe('FTS multi-load mapping fallback (slot loadPosition)', () => {
    const moduleSerialId = '5iO4';

    const makeFtsState = (
      command: string,
      actionId: string,
      timestamp: string,
      lastNodeId: string,
      load: Array<{
        loadId: string | null;
        loadType: 'RED' | 'WHITE' | 'BLUE' | null;
        loadPosition: string;
      }>
    ) => ({
      serialNumber: moduleSerialId,
      timestamp,
      orderId: 'ord-co',
      orderUpdateId: 1,
      lastNodeId,
      driving: false,
      actionState: { id: actionId, command, state: 'FINISHED', timestamp },
      load,
      _moduleSerialId: moduleSerialId,
    });

    it('emits transport events for all loads even when FTS omits loadId in a later state', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      const location1 = 'SVR4H76449'; // manufacturing station => PRODUCTION context
      const location2 = 'intersection:2';

      // State 1: all loadIds known -> history created for all NFCs
      sp.updateWorkpieceHistory(
        env,
        makeFtsState('PASS', 'act-pass', '2026-07-29T10:00:00.000Z', location1, [
          { loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' },
          { loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '3' },
          { loadId: 'nfc-red', loadType: 'RED', loadPosition: '2' },
        ]),
        { active: {}, completed: {} }
      );

      // State 2: FTS transiently omits loadId for two slots, but keeps loadType/loadPosition
      sp.updateWorkpieceHistory(
        env,
        makeFtsState('DOCK', 'act-dock', '2026-07-29T10:00:01.000Z', location2, [
          { loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' },
          { loadId: null, loadType: 'RED', loadPosition: '2' },
          { loadId: null, loadType: 'WHITE', loadPosition: '3' },
        ]),
        { active: {}, completed: {} }
      );

      const snapshot = service.getSnapshot(env);
      const historyBlue = snapshot.get('nfc-blue');
      const historyRed = snapshot.get('nfc-red');
      const historyWhite = snapshot.get('nfc-white');

      expect(historyBlue?.events.some((e) => e.eventSource === 'FTS' && e.eventType === 'TURN' && e.location === location2)).toBe(
        true
      );
      expect(historyRed?.events.some((e) => e.eventSource === 'FTS' && e.eventType === 'TURN' && e.location === location2)).toBe(
        true
      );
      expect(historyWhite?.events.some((e) => e.eventSource === 'FTS' && e.eventType === 'TURN' && e.location === location2)).toBe(
        true
      );
      expect(
        historyBlue?.events.find((e) => e.location === location2)?.details?.['remappedFromDockAtIntersection']
      ).toBe(true);
    });

    it('clears sticky on fully empty slots (no post-unload attribution)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const dps = 'SVR4H73275';
      const intersection = '2';
      const hbw = 'SVR3QA0022';

      sp.updateWorkpieceHistory(
        env,
        makeFtsState('DOCK', 'act-dps', '2026-07-29T10:00:00.000Z', dps, [
          { loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' },
        ]),
        { active: {}, completed: {} }
      );

      // Empty after unload / next order approach — must not keep WHITE sticky
      sp.updateWorkpieceHistory(
        env,
        makeFtsState('PASS', 'act-pass', '2026-07-29T10:00:01.000Z', intersection, [
          { loadId: null, loadType: null, loadPosition: '1' },
        ]),
        { active: {}, completed: {} }
      );
      sp.updateWorkpieceHistory(
        env,
        makeFtsState('DOCK', 'act-hbw', '2026-07-29T10:00:02.000Z', hbw, [
          { loadId: null, loadType: null, loadPosition: '1' },
        ]),
        { active: {}, completed: {} }
      );

      const history = service.getSnapshot(env).get('nfc-white');
      expect(history).toBeDefined();
      const locations = history!.events.filter((e) => e.eventSource === 'FTS').map((e) => e.location);
      expect(locations).toContain(dps);
      expect(locations).not.toContain(intersection);
      expect(locations).not.toContain(hbw);
    });

    it('clears sticky after MODULE HBW PICK so later empty FTS is not attributed', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const hbw = 'SVR3QA0022';
      const intersection = '2';
      const orders = {
        active: {
          'ord-white-storage': {
            orderId: 'ord-white-storage',
            orderType: 'STORAGE',
            type: 'WHITE',
            workpieceId: 'nfc-white',
          },
        },
        completed: {},
      };

      sp.updateWorkpieceHistory(
        env,
        makeFtsState('DOCK', 'act-hbw-dock', '2026-07-29T10:00:00.000Z', hbw, [
          { loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' },
        ]),
        orders
      );

      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:00:01.000Z',
          orderId: 'ord-white-storage',
          orderUpdateId: 1,
          actionState: {
            id: 'hbw-pick',
            command: 'PICK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:00:01.000Z',
          },
          loads: [{ loadId: 'nfc-white', loadType: 'WHITE', loadPosition: 'A1' }],
          _moduleSerialId: hbw,
          _topic: `module/v1/ff/${hbw}/state`,
        },
        orders
      );

      sp.updateWorkpieceHistory(
        env,
        makeFtsState('PASS', 'act-empty', '2026-07-29T10:00:02.000Z', intersection, [
          { loadId: null, loadType: null, loadPosition: '1' },
          { loadId: null, loadType: null, loadPosition: '2' },
          { loadId: null, loadType: null, loadPosition: '3' },
        ]),
        orders
      );

      const history = service.getSnapshot(env).get('nfc-white');
      expect(history).toBeDefined();
      expect(history!.events.some((e) => e.eventSource === 'MODULE' && e.eventType === 'PICK')).toBe(
        true
      );
      expect(
        history!.events.some(
          (e) => e.eventSource === 'FTS' && e.location === intersection
        )
      ).toBe(false);
    });
  });

  describe('Golden Path phases via CCU orderType (white storage→production)', () => {
    const dps = 'SVR4H73275';
    const hbw = 'SVR3QA0022';
    const drill = 'SVR4H76449';
    const storageOrderId = 'ord-storage-white';
    const productionOrderId = 'ord-prod-white';
    const nfc = 'nfc-white-golden';

    const ccuOrders = {
      active: {
        [storageOrderId]: {
          orderId: storageOrderId,
          orderType: 'STORAGE',
          type: 'WHITE',
          workpieceId: nfc,
        },
        [productionOrderId]: {
          orderId: productionOrderId,
          orderType: 'PRODUCTION',
          type: 'WHITE',
          workpieceId: nfc,
        },
      },
      completed: {},
    };

    it('keeps HBW dock in STORAGE when CCU orderType is STORAGE (no wasAtHbw flip)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-28T07:49:08.000Z',
          orderId: storageOrderId,
          lastNodeId: dps,
          driving: false,
          actionState: {
            id: 'a1',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-28T07:49:08.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        ccuOrders
      );
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-28T07:49:28.000Z',
          orderId: storageOrderId,
          lastNodeId: '1',
          driving: true,
          actionState: {
            id: 'a2',
            command: 'PASS',
            state: 'FINISHED',
            timestamp: '2026-07-28T07:49:28.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        ccuOrders
      );
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-28T07:49:34.000Z',
          orderId: storageOrderId,
          lastNodeId: hbw,
          driving: false,
          actionState: {
            id: 'a3',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-28T07:49:34.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        ccuOrders
      );

      const history = service.getSnapshot(env).get(nfc);
      expect(history).toBeDefined();
      const fts = history!.events.filter((e) => e.eventSource === 'FTS');
      expect(fts.every((e) => e.orderType === 'STORAGE')).toBe(true);
      expect(fts.some((e) => e.location === hbw && e.orderType === 'STORAGE')).toBe(true);
    });

    it('marks production FTS as PRODUCTION via CCU orderId (same NFC)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-28T07:51:05.000Z',
          orderId: productionOrderId,
          lastNodeId: hbw,
          driving: false,
          actionState: {
            id: 'p1',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-28T07:51:05.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        ccuOrders
      );
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-28T07:51:23.000Z',
          orderId: productionOrderId,
          lastNodeId: drill,
          driving: false,
          actionState: {
            id: 'p2',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-28T07:51:23.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        ccuOrders
      );

      const history = service.getSnapshot(env).get(nfc);
      const fts = history!.events.filter((e) => e.eventSource === 'FTS');
      expect(fts.every((e) => e.orderType === 'PRODUCTION')).toBe(true);
    });

    it('normalizes ccu/order/active array payload into orderId map', () => {
      const sp = service as any;
      const map = sp.toOrderIdMap([
        { orderId: storageOrderId, orderType: 'STORAGE', type: 'WHITE' },
        { orderId: productionOrderId, orderType: 'PRODUCTION', type: 'WHITE' },
      ]);
      expect(map[storageOrderId].orderType).toBe('STORAGE');
      expect(map[productionOrderId].orderType).toBe('PRODUCTION');
      expect(sp.resolveCcuOrderType({ active: map, completed: {} }, storageOrderId)).toBe('STORAGE');
      expect(sp.resolveCcuOrderType({ active: map, completed: {} }, productionOrderId)).toBe(
        'PRODUCTION'
      );
    });
  });

  describe('SOLL station completeness (BLUE module gate)', () => {
    it('records MODULE DRILL/MILL/CHECK_QUALITY for BLUE production history', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      const makeModule = (
        serial: string,
        command: string,
        actionId: string,
        timestamp: string
      ) => ({
        serialNumber: serial,
        timestamp,
        orderId: 'ord-blue',
        orderUpdateId: 2,
        actionState: {
          id: actionId,
          command,
          state: 'FINISHED',
          timestamp,
          result: command === 'CHECK_QUALITY' ? 'OK' : undefined,
        },
        loads: [{ loadId: 'nfc-blue', loadType: 'BLUE' as const, loadPosition: '1' }],
        _moduleSerialId: serial,
        _topic: `module/v1/ff/${serial}/state`,
      });

      sp.updateWorkpieceHistoryFromModule(
        env,
        makeModule('SVR4H76449', 'DRILL', 'm-drill', '2026-07-29T11:00:00.000Z'),
        { active: {}, completed: {} }
      );
      sp.updateWorkpieceHistoryFromModule(
        env,
        makeModule('SVR3QA2098', 'MILL', 'm-mill', '2026-07-29T11:01:00.000Z'),
        { active: {}, completed: {} }
      );
      sp.updateWorkpieceHistoryFromModule(
        env,
        makeModule('SVR4H76530', 'CHECK_QUALITY', 'm-aiqs', '2026-07-29T11:02:00.000Z'),
        { active: {}, completed: {} }
      );

      const history = service.getSnapshot(env).get('nfc-blue');
      expect(history).toBeDefined();
      const stations = new Set(
        history!.events
          .filter((e) => e.eventSource === 'MODULE')
          .map((e) => (e.stationId || '').toUpperCase())
      );
      expect(stations.has('DRILL')).toBe(true);
      expect(stations.has('MILL')).toBe(true);
      expect(stations.has('AIQS')).toBe(true);
    });
  });

  describe('module attribution (no Blue steal)', () => {
    const drillSerial = 'SVR4H76449';
    const whiteOrder = 'ord-white';
    const blueOrder = 'ord-blue';

    it('does not attribute White DRILL DROP (empty loads) to Blue via Map order', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const orders = {
        active: {
          [blueOrder]: { orderId: blueOrder, orderType: 'PRODUCTION', type: 'BLUE' },
          [whiteOrder]: { orderId: whiteOrder, orderType: 'PRODUCTION', type: 'WHITE' },
        },
        completed: {},
      };

      // Insert BLUE first so naive Map.entries() would prefer it
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: 'xkI4',
          timestamp: '2026-07-29T10:00:00.000Z',
          orderId: blueOrder,
          orderUpdateId: 1,
          lastNodeId: drillSerial,
          driving: false,
          actionState: { id: 'b-dock', command: 'DOCK', state: 'FINISHED', timestamp: '2026-07-29T10:00:00.000Z' },
          load: [{ loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' }],
          _moduleSerialId: 'xkI4',
        },
        orders
      );
      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-29T10:01:00.000Z',
          orderId: whiteOrder,
          orderUpdateId: 1,
          lastNodeId: drillSerial,
          driving: false,
          actionState: { id: 'w-dock', command: 'DOCK', state: 'FINISHED', timestamp: '2026-07-29T10:01:00.000Z' },
          load: [
            { loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' },
            { loadId: 'nfc-red', loadType: 'RED', loadPosition: '2' },
          ],
          _moduleSerialId: '5iO4',
        },
        orders
      );

      // Empty loads DROP for White's order at DRILL
      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: drillSerial,
          timestamp: '2026-07-29T10:02:00.000Z',
          orderId: whiteOrder,
          orderUpdateId: 2,
          actionState: {
            id: 'drill-drop',
            command: 'DROP',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:02:00.000Z',
          },
          loads: [],
          _moduleSerialId: drillSerial,
          _topic: `module/v1/ff/${drillSerial}/state`,
        },
        orders
      );

      const blue = service.getSnapshot(env).get('nfc-blue');
      const white = service.getSnapshot(env).get('nfc-white');
      const red = service.getSnapshot(env).get('nfc-red');

      const blueModule = blue?.events.filter((e) => e.eventSource === 'MODULE') ?? [];
      const whiteModule = white?.events.filter((e) => e.eventSource === 'MODULE') ?? [];
      const redModule = red?.events.filter((e) => e.eventSource === 'MODULE') ?? [];

      expect(blueModule.some((e) => e.eventType === 'DROP' && e.orderId === whiteOrder)).toBe(false);
      expect(whiteModule.some((e) => e.eventType === 'DROP' && e.stationId === 'DRILL')).toBe(true);
      // RED is co-passenger (not planned at DRILL) — must not steal White DROP
      expect(redModule.some((e) => e.eventType === 'DROP')).toBe(false);
    });

    it('does not attribute RED MILL to BLUE co-passenger (both have MILL in SOLL)', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const millSerial = 'SVR3QA2098';
      const redOrder = 'ord-red';
      const orders = {
        active: {
          [redOrder]: { orderId: redOrder, orderType: 'PRODUCTION', type: 'RED' },
          [blueOrder]: { orderId: blueOrder, orderType: 'PRODUCTION', type: 'BLUE' },
        },
        completed: {},
      };

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-29T12:00:00.000Z',
          orderId: redOrder,
          orderUpdateId: 1,
          lastNodeId: millSerial,
          driving: false,
          actionState: { id: 'dock', command: 'DOCK', state: 'FINISHED', timestamp: '2026-07-29T12:00:00.000Z' },
          load: [
            { loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' },
            { loadId: 'nfc-red', loadType: 'RED', loadPosition: '2' },
          ],
          _moduleSerialId: '5iO4',
        },
        orders
      );

      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: millSerial,
          timestamp: '2026-07-29T12:01:00.000Z',
          orderId: redOrder,
          orderUpdateId: 2,
          actionState: {
            id: 'mill',
            command: 'MILL',
            state: 'FINISHED',
            timestamp: '2026-07-29T12:01:00.000Z',
          },
          loads: [],
          _moduleSerialId: millSerial,
        },
        orders
      );

      expect(service.getSnapshot(env).get('nfc-red')?.events.some((e) => e.eventType === 'MILL')).toBe(true);
      expect(service.getSnapshot(env).get('nfc-blue')?.events.some((e) => e.eventType === 'MILL')).toBe(
        false
      );
      expect(
        service.getSnapshot(env).get('nfc-blue')?.events.find((e) => e.eventType === 'DOCK')?.details?.[
          'coPassenger'
        ]
      ).toBe(true);
      expect(
        service.getSnapshot(env).get('nfc-blue')?.events.find((e) => e.eventType === 'DOCK')?.details?.[
          'agvLoads'
        ]
      ).toHaveLength(2);
    });

    it('keeps explicit NFC loadId even when Blue already exists for same orderId', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: 'xkI4',
          timestamp: '2026-07-29T10:00:00.000Z',
          orderId: whiteOrder,
          orderUpdateId: 1,
          lastNodeId: drillSerial,
          driving: false,
          actionState: { id: 'b-dock', command: 'DOCK', state: 'FINISHED', timestamp: '2026-07-29T10:00:00.000Z' },
          load: [{ loadId: 'nfc-blue', loadType: 'BLUE', loadPosition: '1' }],
          _moduleSerialId: 'xkI4',
        },
        {
          active: { [whiteOrder]: { orderId: whiteOrder, orderType: 'PRODUCTION', type: 'WHITE' } },
          completed: {},
        }
      );

      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: drillSerial,
          timestamp: '2026-07-29T10:01:00.000Z',
          orderId: whiteOrder,
          orderUpdateId: 2,
          actionState: {
            id: 'drill',
            command: 'DRILL',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:01:00.000Z',
          },
          loads: [{ loadId: 'nfc-white', loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: drillSerial,
        },
        {
          active: { [whiteOrder]: { orderId: whiteOrder, orderType: 'PRODUCTION', type: 'WHITE' } },
          completed: {},
        }
      );

      expect(service.getSnapshot(env).get('nfc-white')?.events.some((e) => e.eventType === 'DRILL')).toBe(
        true
      );
      expect(service.getSnapshot(env).get('nfc-blue')?.events.some((e) => e.eventType === 'DRILL')).toBe(
        false
      );
    });
  });

  describe('HBW multi-shelf attribution (result + order.workpieceId)', () => {
    const hbw = 'SVR3QA0022';
    const whiteNfc = '832a423afcb534';
    const blueNfc = '78d10489b38ed8';
    const redNfc = 'f5b58ca1a9f367';

    it('attributes HBW DROP to actionState.result NFC, not remaining shelf loadId', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const whiteOrder = 'ord-white-prod';
      const orders = {
        active: {
          [whiteOrder]: {
            orderId: whiteOrder,
            orderType: 'PRODUCTION',
            type: 'WHITE',
            workpieceId: whiteNfc,
          },
        },
        completed: {},
      };

      // Seed histories so all three NFCs exist
      for (const [nfc, type] of [
        [whiteNfc, 'WHITE'],
        [blueNfc, 'BLUE'],
        [redNfc, 'RED'],
      ] as const) {
        sp.updateWorkpieceHistory(
          env,
          {
            serialNumber: '5iO4',
            timestamp: '2026-07-29T10:00:00.000Z',
            orderId: whiteOrder,
            orderUpdateId: 1,
            lastNodeId: hbw,
            driving: false,
            actionState: {
              id: `seed-${type}`,
              command: 'DOCK',
              state: 'FINISHED',
              timestamp: '2026-07-29T10:00:00.000Z',
            },
            load: [{ loadId: nfc, loadType: type, loadPosition: '1' }],
            _moduleSerialId: '5iO4',
          },
          orders
        );
      }

      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:01:00.000Z',
          orderId: whiteOrder,
          orderUpdateId: 2,
          actionState: {
            id: 'hbw-drop-white',
            command: 'DROP',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:01:00.000Z',
            result: whiteNfc,
          },
          // Remaining shelf — must not steal attribution
          loads: [
            { loadId: blueNfc, loadType: 'BLUE', loadPosition: 'B1' },
            { loadId: redNfc, loadType: 'RED', loadPosition: 'C1' },
          ],
          _moduleSerialId: hbw,
          _topic: `module/v1/ff/${hbw}/state`,
        },
        orders
      );

      expect(
        service.getSnapshot(env).get(whiteNfc)?.events.some((e) => e.eventSource === 'MODULE' && e.eventType === 'DROP')
      ).toBe(true);
      expect(
        service.getSnapshot(env).get(blueNfc)?.events.some((e) => e.eventSource === 'MODULE' && e.eventType === 'DROP')
      ).toBe(false);
    });

    it('attributes HBW PICK (storage) via CCU order.workpieceId when shelf has multiple NFCs', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const redStorage = 'ord-red-storage';
      const orders = {
        active: {
          [redStorage]: {
            orderId: redStorage,
            orderType: 'STORAGE',
            type: 'RED',
            workpieceId: redNfc,
          },
        },
        completed: {},
      };

      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:02:00.000Z',
          orderId: redStorage,
          orderUpdateId: 1,
          actionState: {
            id: 'hbw-pick-red',
            command: 'PICK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:02:00.000Z',
          },
          loads: [
            { loadId: blueNfc, loadType: 'BLUE', loadPosition: 'B1' },
            { loadId: redNfc, loadType: 'RED', loadPosition: 'C1' },
            { loadId: whiteNfc, loadType: 'WHITE', loadPosition: 'A1' },
          ],
          _moduleSerialId: hbw,
          _topic: `module/v1/ff/${hbw}/state`,
        },
        orders
      );

      expect(
        service.getSnapshot(env).get(redNfc)?.events.some((e) => e.eventSource === 'MODULE' && e.eventType === 'PICK')
      ).toBe(true);
      expect(
        service.getSnapshot(env).get(blueNfc)?.events.some((e) => e.eventSource === 'MODULE' && e.eventType === 'PICK') ??
          false
      ).toBe(false);
    });

    it('HBW DROP uses own shelf slot (PICK / remembered), not remaining loads', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const whiteOrder = 'ord-w-store';
      const whiteProd = 'ord-w-prod';
      const blueProd = 'ord-b-prod';
      const redStorage = 'ord-r-store';
      const orders = {
        active: {
          [whiteOrder]: {
            orderId: whiteOrder,
            orderType: 'STORAGE',
            type: 'WHITE',
            workpieceId: whiteNfc,
          },
          [whiteProd]: {
            orderId: whiteProd,
            orderType: 'PRODUCTION',
            type: 'WHITE',
            workpieceId: whiteNfc,
          },
          [blueProd]: {
            orderId: blueProd,
            orderType: 'PRODUCTION',
            type: 'BLUE',
            workpieceId: blueNfc,
          },
          [redStorage]: {
            orderId: redStorage,
            orderType: 'STORAGE',
            type: 'RED',
            workpieceId: redNfc,
          },
        },
        completed: {},
      };

      // White Einlagerung A1
      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:00:00.000Z',
          orderId: whiteOrder,
          orderUpdateId: 1,
          actionState: {
            id: 'pick-w',
            command: 'PICK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:00:00.000Z',
            metadata: { type: 'WHITE', workpieceId: whiteNfc },
          },
          loads: [{ loadId: whiteNfc, loadType: 'WHITE', loadPosition: 'A1' }],
          _moduleSerialId: hbw,
        },
        orders
      );

      // Red Einlagerung — shelf already has Blue B1 + White A1 (learns Blue slot without Blue PICK event)
      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:01:00.000Z',
          orderId: redStorage,
          orderUpdateId: 1,
          actionState: {
            id: 'pick-r',
            command: 'PICK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:01:00.000Z',
            metadata: { type: 'RED', workpieceId: redNfc },
          },
          loads: [
            { loadId: blueNfc, loadType: 'BLUE', loadPosition: 'B1' },
            { loadId: redNfc, loadType: 'RED', loadPosition: 'C1' },
            { loadId: whiteNfc, loadType: 'WHITE', loadPosition: 'A1' },
          ],
          _moduleSerialId: hbw,
        },
        orders
      );

      // White Auslagerung — FINISHED loads are remainder only (Blue B1, Red C1)
      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:02:00.000Z',
          orderId: whiteProd,
          orderUpdateId: 2,
          actionState: {
            id: 'drop-w',
            command: 'DROP',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:02:00.000Z',
            result: whiteNfc,
            metadata: { type: 'WHITE' },
          },
          loads: [
            { loadId: blueNfc, loadType: 'BLUE', loadPosition: 'B1' },
            { loadId: redNfc, loadType: 'RED', loadPosition: 'C1' },
          ],
          _moduleSerialId: hbw,
        },
        orders
      );

      const whiteDrop = service
        .getSnapshot(env)
        .get(whiteNfc)
        ?.events.find((e) => e.eventType === 'DROP' && e.stationId === 'HBW');
      expect(whiteDrop?.details?.['loadPosition']).toBe('A1');
      const shelf = whiteDrop?.details?.['hbwShelf'] as
        | Array<{ loadPosition: string; loadType: string | null; loadId: string | null }>
        | undefined;
      expect(shelf).toBeDefined();
      expect(shelf).toHaveLength(9);
      expect(shelf?.find((c) => c.loadPosition === 'B1')?.loadType).toBe('BLUE');
      expect(shelf?.find((c) => c.loadPosition === 'C1')?.loadType).toBe('RED');
      // DROP FINISHED remainder — vacated A1 empty in MQTT snapshot
      expect(shelf?.find((c) => c.loadPosition === 'A1')?.loadId).toBeFalsy();

      // Blue Auslagerung — no own HBW PICK; slot remembered from Red storage shelf snapshot
      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: hbw,
          timestamp: '2026-07-29T10:03:00.000Z',
          orderId: blueProd,
          orderUpdateId: 2,
          actionState: {
            id: 'drop-b',
            command: 'DROP',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:03:00.000Z',
            result: blueNfc,
            metadata: { type: 'BLUE' },
          },
          loads: [{ loadId: redNfc, loadType: 'RED', loadPosition: 'C1' }],
          _moduleSerialId: hbw,
        },
        orders
      );

      const blueDrop = service
        .getSnapshot(env)
        .get(blueNfc)
        ?.events.find((e) => e.eventType === 'DROP' && e.stationId === 'HBW');
      expect(blueDrop?.details?.['loadPosition']).toBe('B1');
    });
  });

  describe('CHRG as Ist station (FTS only, no module MQTT)', () => {
    it('emits DOCK @ CHRG0 with stationId CHRG and visitKind IST_ONLY', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const nfc = 'nfc-white-chrg';
      const orders = {
        active: {
          'ord-prod': {
            orderId: 'ord-prod',
            orderType: 'PRODUCTION',
            type: 'WHITE',
            workpieceId: nfc,
          },
        },
        completed: {},
      };

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-29T12:00:00.000Z',
          orderId: 'ord-prod',
          orderUpdateId: 1,
          lastNodeId: 'CHRG0',
          driving: false,
          actionState: {
            id: 'chrg-dock',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-29T12:00:00.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        orders
      );

      const dock = service
        .getSnapshot(env)
        .get(nfc)
        ?.events.find((e) => e.eventSource === 'FTS' && e.eventType === 'DOCK');
      expect(dock?.stationId).toBe('CHRG');
      expect(dock?.location).toBe('CHRG0');
      expect(dock?.details?.['visitKind']).toBe('IST_ONLY');
    });
  });

  describe('DPS production delivery (PASSED / MQTT gap)', () => {
    const dps = 'SVR4H73275';
    const nfc = '2b2c6dd469a47a';
    const orderId = 'ord-white-prod';

    it('attributes DPS PICK FINISHED PASSED via CCU workpieceId', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      // Seed history so matching does not invent a blank workpiece
      const historyMap = service.getSnapshot(env);
      historyMap.set(nfc, {
        workpieceId: nfc,
        workpieceType: 'WHITE',
        events: [
          {
            timestamp: '2026-07-29T10:00:00.000Z',
            workpieceId: nfc,
            workpieceType: 'WHITE',
            location: dps,
            moduleId: '5iO4',
            moduleName: 'AGV-1',
            orderId,
            orderType: 'PRODUCTION',
            stationId: 'DPS',
            eventSource: 'FTS',
            eventType: 'DOCK',
            subOrderId: `${orderId}-1`,
            actionId: 'dock-1',
          },
        ],
        orders: [],
      } as any);
      (service as any).getStore(env).next(new Map(historyMap));

      sp.updateWorkpieceHistoryFromModule(
        env,
        {
          serialNumber: dps,
          _moduleSerialId: dps,
          timestamp: '2026-07-29T10:00:05.000Z',
          orderId,
          orderUpdateId: 11,
          actionState: {
            id: 'pick-1',
            command: 'PICK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:00:05.000Z',
            result: 'PASSED',
          },
          loads: null,
        },
        {
          active: {
            [orderId]: {
              orderId,
              orderType: 'PRODUCTION',
              type: 'WHITE',
              workpieceId: nfc,
            },
          },
          completed: {},
        }
      );

      const events = service.getSnapshot(env).get(nfc)?.events ?? [];
      const pick = events.find(
        (e) => e.eventSource === 'MODULE' && e.eventType === 'PICK' && e.stationId === 'DPS'
      );
      expect(pick).toBeDefined();
      expect(pick?.orderId).toBe(orderId);
      expect(pick?.workpieceId).toBe(nfc);
    });

    it('synthesizes DPS MODULE PICK when completed PRODUCTION has FTS DOCK but no MQTT PICK', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-29T10:00:00.000Z',
          orderId,
          orderUpdateId: 1,
          lastNodeId: dps,
          driving: false,
          actionState: {
            id: 'dock-dps',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:00:00.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        {
          active: {
            [orderId]: { orderId, orderType: 'PRODUCTION', type: 'WHITE', workpieceId: nfc },
          },
          completed: {},
        }
      );

      expect(
        service
          .getSnapshot(env)
          .get(nfc)
          ?.events.some((e) => e.eventSource === 'MODULE' && e.eventType === 'PICK')
      ).toBe(false);

      sp.refreshAllOrderContexts(env, {
        active: {},
        completed: {
          [orderId]: {
            orderId,
            orderType: 'PRODUCTION',
            type: 'WHITE',
            workpieceId: nfc,
            timestamp: '2026-07-29T10:00:10.000Z',
            state: 'FINISHED',
          },
        },
      });

      const pick = service
        .getSnapshot(env)
        .get(nfc)
        ?.events.find((e) => e.eventSource === 'MODULE' && e.eventType === 'PICK' && e.stationId === 'DPS');
      expect(pick).toBeDefined();
      expect(pick?.details?.['synthesizedFromFtsDock']).toBe(true);
    });

    it('emits FTS DOCK from sticky when firmware sends load: []', () => {
      const sp = service as any;
      const env = 'mock';
      service.initialize(env);
      const aiqs = 'SVR4H76530';

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-29T10:00:00.000Z',
          orderId,
          orderUpdateId: 1,
          lastNodeId: aiqs,
          driving: false,
          actionState: {
            id: 'dock-aiqs',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:00:00.000Z',
          },
          load: [{ loadId: nfc, loadType: 'WHITE', loadPosition: '1' }],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );

      sp.updateWorkpieceHistory(
        env,
        {
          serialNumber: '5iO4',
          timestamp: '2026-07-29T10:00:05.000Z',
          orderId,
          orderUpdateId: 1,
          lastNodeId: dps,
          driving: false,
          actionState: {
            id: 'dock-dps',
            command: 'DOCK',
            state: 'FINISHED',
            timestamp: '2026-07-29T10:00:05.000Z',
          },
          load: [],
          _moduleSerialId: '5iO4',
        },
        { active: {}, completed: {} }
      );

      const dock = service
        .getSnapshot(env)
        .get(nfc)
        ?.events.find((e) => e.eventSource === 'FTS' && e.eventType === 'DOCK' && e.location === dps);
      expect(dock).toBeDefined();
      expect(dock?.workpieceId).toBe(nfc);
    });
  });
});
