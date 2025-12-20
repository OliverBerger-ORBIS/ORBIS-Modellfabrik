import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import type { PurchaseOrderData, CustomerOrderData } from '../components/erp-info-box/erp-info-box.component';

export type WorkpieceType = 'BLUE' | 'WHITE' | 'RED';

/**
 * Stored ERP data for Purchase Orders (waiting for next Storage Order)
 */
interface StoredPurchaseOrderData extends PurchaseOrderData {
  workpieceType: WorkpieceType;
  timestamp: string; // When the order was created
}

/**
 * Stored ERP data for Customer Orders (waiting for next Production Order)
 */
interface StoredCustomerOrderData extends CustomerOrderData {
  timestamp: string; // When the order was created
}

/**
 * ERP Order Data Service
 * 
 * Stores ERP business data (Purchase Orders and Customer Orders) and associates them
 * with the next Storage/Production Order for Track-Trace display.
 */
@Injectable({ providedIn: 'root' })
export class ErpOrderDataService {
  private readonly purchaseOrdersSubject = new BehaviorSubject<StoredPurchaseOrderData[]>([]);
  private readonly customerOrdersSubject = new BehaviorSubject<StoredCustomerOrderData[]>([]);

  /**
   * Observable of pending Purchase Orders (waiting for Storage Order assignment)
   */
  get purchaseOrders$() {
    return this.purchaseOrdersSubject.asObservable();
  }

  /**
   * Observable of pending Customer Orders (waiting for Production Order assignment)
   */
  get customerOrders$() {
    return this.customerOrdersSubject.asObservable();
  }

  /**
   * Store Purchase Order data with workpiece type
   * This will be associated with the next Storage Order
   */
  storePurchaseOrder(workpieceType: WorkpieceType, data: PurchaseOrderData): void {
    const stored: StoredPurchaseOrderData = {
      ...data,
      workpieceType,
      timestamp: new Date().toISOString(),
    };
    const current = this.purchaseOrdersSubject.value;
    this.purchaseOrdersSubject.next([...current, stored]);
  }

  /**
   * Store Customer Order data
   * This will be associated with the next Production Order
   */
  storeCustomerOrder(data: CustomerOrderData): void {
    const stored: StoredCustomerOrderData = {
      ...data,
      timestamp: new Date().toISOString(),
    };
    const current = this.customerOrdersSubject.value;
    this.customerOrdersSubject.next([...current, stored]);
  }

  /**
   * Get and remove the oldest Purchase Order for a specific workpiece type
   * Used when a Storage Order is created - assign the ERP data to it
   */
  popPurchaseOrderForWorkpieceType(workpieceType: WorkpieceType): PurchaseOrderData | null {
    const current = this.purchaseOrdersSubject.value;
    const index = current.findIndex(po => po.workpieceType === workpieceType);
    if (index === -1) {
      return null;
    }
    const [po] = current.splice(index, 1);
    this.purchaseOrdersSubject.next([...current]);
    return {
      purchaseOrderId: po.purchaseOrderId,
      supplierId: po.supplierId,
      orderDate: po.orderDate,
      orderAmount: po.orderAmount,
      plannedDeliveryDate: po.plannedDeliveryDate,
    };
  }

  /**
   * Get and remove the oldest Customer Order
   * Used when a Production Order is created - assign the ERP data to it
   */
  popCustomerOrder(): CustomerOrderData | null {
    const current = this.customerOrdersSubject.value;
    if (current.length === 0) {
      return null;
    }
    const [co] = current;
    this.customerOrdersSubject.next(current.slice(1));
    return {
      customerOrderId: co.customerOrderId,
      customerId: co.customerId,
      orderDate: co.orderDate,
      orderAmount: co.orderAmount,
      plannedDeliveryDate: co.plannedDeliveryDate,
    };
  }

  /**
   * Get current Purchase Orders (for display in Process Tab)
   */
  getCurrentPurchaseOrders(): StoredPurchaseOrderData[] {
    return this.purchaseOrdersSubject.value;
  }

  /**
   * Get current Customer Orders (for display in Process Tab)
   */
  getCurrentCustomerOrders(): StoredCustomerOrderData[] {
    return this.customerOrdersSubject.value;
  }

  /**
   * Get Purchase Order for a specific workpiece type (for display)
   */
  getPurchaseOrderForWorkpieceType(workpieceType: WorkpieceType): StoredPurchaseOrderData | null {
    const current = this.purchaseOrdersSubject.value;
    return current.find(po => po.workpieceType === workpieceType) || null;
  }

  /**
   * Clear all stored orders (for testing/reset)
   */
  clearAll(): void {
    this.purchaseOrdersSubject.next([]);
    this.customerOrdersSubject.next([]);
  }
}
