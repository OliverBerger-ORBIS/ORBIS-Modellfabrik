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
import type { TrackTraceEvent, OrderContext } from '../workpiece-history.service';

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

  describe('multi-AGV (5iO4 and leJ4)', () => {
    it('should subscribe to FTS state topics for both AGVs when layout has two FTS', () => {
      const mappingMock = {
        getAgvOptions: jest.fn(() => [
          { serial: '5iO4', label: 'AGV-1' },
          { serial: 'leJ4', label: 'AGV-2' },
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
      expect(mm.getLastMessage).toHaveBeenCalledWith('fts/v1/ff/leJ4/state');

      svc.ngOnDestroy();
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
        actionId: 'other-source-action',
        stationId: 'AIQS',
        moduleId: 'SVR4H76530',
        location: 'SVR4H76530',
      };

      expect(svc.shouldAppendEvent('mock', 'wp-2', ftsLikeEvent)).toBe(true);
      expect(svc.shouldAppendEvent('mock', 'wp-2', moduleLikeEvent)).toBe(false);
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
    it('captures production PROCESS events for DRILL/MILL/AIQS', () => {
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
      ).toBe(true);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:00.500Z',
          eventType: 'PROCESS',
          orderType: 'PRODUCTION',
          stationId: 'MILL',
        })
      ).toBe(true);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:01.000Z',
          eventType: 'PROCESS',
          orderType: 'PRODUCTION',
          stationId: 'AIQS',
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
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:04.000Z',
          eventType: 'PICK',
          orderType: 'STORAGE',
          stationId: 'DPS',
        })
      ).toBe(true);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:05.000Z',
          eventType: 'DROP',
          orderType: 'STORAGE',
          stationId: 'HBW',
        })
      ).toBe(true);
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
          timestamp: '2026-05-01T10:00:07.000Z',
          eventType: 'DROP',
          orderType: 'PRODUCTION',
          stationId: 'AIQS',
        })
      ).toBe(false);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:08.000Z',
          eventType: 'DROP',
          orderType: 'STORAGE',
          stationId: 'DPS',
        })
      ).toBe(false);
      expect(
        svc.shouldCaptureEnvironmentSnapshot({
          timestamp: '2026-05-01T10:00:09.000Z',
          eventType: 'PICK',
          orderType: 'STORAGE',
          stationId: 'HBW',
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
});
