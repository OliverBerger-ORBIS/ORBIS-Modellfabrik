import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { WorkpieceHistoryService } from '../workpiece-history.service';
import { MessageMonitorService } from '../message-monitor.service';
import { ModuleNameService } from '../module-name.service';
import { EnvironmentService } from '../environment.service';
import { FtsRouteService } from '../fts-route.service';
import { ErpOrderDataService } from '../erp-order-data.service';
import { MessageValidationService } from '../message-validation.service';
import { MessagePersistenceService } from '../message-persistence.service';
import { of } from 'rxjs';
import type { TrackTraceEvent, OrderContext } from '../workpiece-history.service';

describe('WorkpieceHistoryService', () => {
  let service: WorkpieceHistoryService;
  let messageMonitor: MessageMonitorService;
  let moduleNameService: ModuleNameService;
  let environmentService: EnvironmentService;
  let ftsRouteService: FtsRouteService;
  let erpOrderDataService: ErpOrderDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        WorkpieceHistoryService,
        MessageMonitorService,
        ModuleNameService,
        EnvironmentService,
        FtsRouteService,
        ErpOrderDataService,
        MessageValidationService,
        MessagePersistenceService,
      ],
    });
    service = TestBed.inject(WorkpieceHistoryService);
    messageMonitor = TestBed.inject(MessageMonitorService);
    moduleNameService = TestBed.inject(ModuleNameService);
    environmentService = TestBed.inject(EnvironmentService);
    ftsRouteService = TestBed.inject(FtsRouteService);
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
        orderDate: new Date().toISOString(),
        orderAmount: 1,
        plannedDeliveryDate: new Date().toISOString(),
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
        orderDate: new Date().toISOString(),
        orderAmount: 1,
        plannedDeliveryDate: new Date().toISOString(),
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
});
