import { TestBed } from '@angular/core/testing';
import { ErpOrderDataService } from '../erp-order-data.service';
import { firstValueFrom } from 'rxjs';

describe('ErpOrderDataService', () => {
  let service: ErpOrderDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ErpOrderDataService],
    });
    service = TestBed.inject(ErpOrderDataService);
  });

  describe('Service Creation', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('Purchase Orders', () => {
    it('should store purchase order data', () => {
      service.storePurchaseOrder('BLUE', {
        purchaseOrderId: 'ERP-PO-TEST123',
        supplierId: 'SUP-ABC',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const orders = firstValueFrom(service.purchaseOrders$);
      expect(orders).toBeTruthy();
    });

    it('should pop purchase order for workpiece type', () => {
      service.storePurchaseOrder('BLUE', {
        purchaseOrderId: 'ERP-PO-TEST123',
        supplierId: 'SUP-ABC',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const result = service.popPurchaseOrderForWorkpieceType('BLUE');
      
      expect(result).toBeTruthy();
      expect(result?.purchaseOrderId).toBe('ERP-PO-TEST123');
      expect(result?.supplierId).toBe('SUP-ABC');
    });

    it('should return null when no purchase order available', () => {
      const result = service.popPurchaseOrderForWorkpieceType('BLUE');
      expect(result).toBeNull();
    });

    it('should only pop matching workpiece type', () => {
      service.storePurchaseOrder('BLUE', {
        purchaseOrderId: 'ERP-PO-BLUE',
        supplierId: 'SUP-ABC',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      service.storePurchaseOrder('WHITE', {
        purchaseOrderId: 'ERP-PO-WHITE',
        supplierId: 'SUP-XYZ',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const blueResult = service.popPurchaseOrderForWorkpieceType('BLUE');
      expect(blueResult?.purchaseOrderId).toBe('ERP-PO-BLUE');

      const whiteResult = service.popPurchaseOrderForWorkpieceType('WHITE');
      expect(whiteResult?.purchaseOrderId).toBe('ERP-PO-WHITE');
    });
  });

  describe('Customer Orders', () => {
    it('should store customer order data', () => {
      service.storeCustomerOrder({
        customerOrderId: 'ERP-CO-TEST123',
        customerId: 'CUST-ABC',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const orders = firstValueFrom(service.customerOrders$);
      expect(orders).toBeTruthy();
    });

    it('should pop customer order', () => {
      service.storeCustomerOrder({
        customerOrderId: 'ERP-CO-TEST123',
        customerId: 'CUST-ABC',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const result = service.popCustomerOrder();
      
      expect(result).toBeTruthy();
      expect(result?.customerOrderId).toBe('ERP-CO-TEST123');
      expect(result?.customerId).toBe('CUST-ABC');
    });

    it('should return null when no customer order available', () => {
      const result = service.popCustomerOrder();
      expect(result).toBeNull();
    });

    it('should pop orders in FIFO order', () => {
      service.storeCustomerOrder({
        customerOrderId: 'ERP-CO-FIRST',
        customerId: 'CUST-1',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      service.storeCustomerOrder({
        customerOrderId: 'ERP-CO-SECOND',
        customerId: 'CUST-2',
        orderDate: '2025-12-20T11:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T11:00:00Z',
      });

      const first = service.popCustomerOrder();
      expect(first?.customerOrderId).toBe('ERP-CO-FIRST');

      const second = service.popCustomerOrder();
      expect(second?.customerOrderId).toBe('ERP-CO-SECOND');
    });
  });

  describe('Observables', () => {
    it('should emit purchase orders', async () => {
      service.storePurchaseOrder('BLUE', {
        purchaseOrderId: 'ERP-PO-TEST',
        supplierId: 'SUP-TEST',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const orders = await firstValueFrom(service.purchaseOrders$);
      expect(orders.length).toBeGreaterThan(0);
    });

    it('should emit customer orders', async () => {
      service.storeCustomerOrder({
        customerOrderId: 'ERP-CO-TEST',
        customerId: 'CUST-TEST',
        orderDate: '2025-12-20T10:00:00Z',
        orderAmount: 1,
        plannedDeliveryDate: '2025-12-25T10:00:00Z',
      });

      const orders = await firstValueFrom(service.customerOrders$);
      expect(orders.length).toBeGreaterThan(0);
    });
  });
});
