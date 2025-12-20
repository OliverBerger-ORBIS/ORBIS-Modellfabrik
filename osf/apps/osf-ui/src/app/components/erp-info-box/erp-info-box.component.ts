import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

/**
 * ERP Business Data for Purchase Orders (Storage)
 */
export interface PurchaseOrderData {
  purchaseOrderId: string; // Format: ERP-PO-XXXXXX
  supplierId: string; // Format: SUP-XXXX
  orderDate: string; // ISO timestamp
  orderAmount: number; // Default: 1
  plannedDeliveryDate: string; // ISO timestamp
}

/**
 * ERP Business Data for Customer Orders (Production)
 */
export interface CustomerOrderData {
  customerOrderId: string; // Format: ERP-CO-XXXXXX
  customerId: string; // Format: CUST-XXXX
  orderDate: string; // ISO timestamp
  orderAmount: number; // Default: 1
  plannedDeliveryDate: string; // ISO timestamp
}

export type ErpOrderData = PurchaseOrderData | CustomerOrderData;
export type ErpOrderType = 'PURCHASE' | 'CUSTOMER';

/**
 * ERP Info Box Component
 * 
 * Displays ERP business data (Purchase Order or Customer Order) in a modal dialog.
 * Used when executing Purchase Orders or Customer Orders in the Process Tab.
 */
@Component({
  standalone: true,
  selector: 'app-erp-info-box',
  imports: [CommonModule],
  templateUrl: './erp-info-box.component.html',
  styleUrl: './erp-info-box.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ErpInfoBoxComponent {
  @Input() isOpen = false;
  @Input() orderType: ErpOrderType = 'PURCHASE';
  @Input() orderData: ErpOrderData | null = null;
  @Input() workpieceType?: string; // BLUE, WHITE, RED - for Purchase Orders
  @Output() close = new EventEmitter<void>();

  get isPurchaseOrder(): boolean {
    return this.orderType === 'PURCHASE';
  }

  get isCustomerOrder(): boolean {
    return this.orderType === 'CUSTOMER';
  }

  get purchaseData(): PurchaseOrderData | null {
    return this.isPurchaseOrder && this.orderData ? (this.orderData as PurchaseOrderData) : null;
  }

  get customerData(): CustomerOrderData | null {
    return this.isCustomerOrder && this.orderData ? (this.orderData as CustomerOrderData) : null;
  }

  get closeLabel(): string {
    return $localize`:@@commonClose:Close`;
  }

  formatDate(dateString: string): string {
    try {
      // Match Track-Trace formatTimestamp format
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  }

  onClose(): void {
    this.close.emit();
  }
}
