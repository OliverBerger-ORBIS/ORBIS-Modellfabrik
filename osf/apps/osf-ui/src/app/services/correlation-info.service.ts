import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, type Observable, Subscription } from 'rxjs';
import { distinctUntilChanged, map } from 'rxjs/operators';
import { MessageMonitorService } from './message-monitor.service';

const CORRELATION_TOPIC = 'dsp/correlation/info';

/**
 * Correlation info payload from DSP (dsp/correlation/info).
 * Aligned with ErpInfoBox CustomerOrderData / PurchaseOrderData.
 */
export interface CorrelationInfo {
  ccuOrderId?: string;
  requestId?: string;
  orderType: 'CUSTOMER' | 'PURCHASE';
  customerOrderId?: string;
  customerId?: string;
  orderDate?: string;
  orderAmount?: number;
  plannedDeliveryDate?: string;
  purchaseOrderId?: string;
  supplierId?: string;
  timestamp?: string;
}

function parseCorrelationPayload(payload: unknown): CorrelationInfo | null {
  if (!payload || typeof payload !== 'object') {
    return null;
  }
  const obj = payload as Record<string, unknown>;
  const orderType = String(obj['orderType'] ?? '').toUpperCase();
  if (orderType !== 'CUSTOMER' && orderType !== 'PURCHASE') {
    return null;
  }
  const ccuOrderId = typeof obj['ccuOrderId'] === 'string' ? obj['ccuOrderId'] : undefined;
  const requestId = typeof obj['requestId'] === 'string' ? obj['requestId'] : undefined;
  if (!ccuOrderId && !requestId) {
    return null; // Need at least one for lookup
  }
  return {
    ccuOrderId,
    requestId,
    orderType: orderType as 'CUSTOMER' | 'PURCHASE',
    customerOrderId: typeof obj['customerOrderId'] === 'string' ? obj['customerOrderId'] : undefined,
    customerId: typeof obj['customerId'] === 'string' ? obj['customerId'] : undefined,
    orderDate: typeof obj['orderDate'] === 'string' ? obj['orderDate'] : undefined,
    orderAmount: typeof obj['orderAmount'] === 'number' ? obj['orderAmount'] : undefined,
    plannedDeliveryDate: typeof obj['plannedDeliveryDate'] === 'string' ? obj['plannedDeliveryDate'] : undefined,
    purchaseOrderId: typeof obj['purchaseOrderId'] === 'string' ? obj['purchaseOrderId'] : undefined,
    supplierId: typeof obj['supplierId'] === 'string' ? obj['supplierId'] : undefined,
    timestamp: typeof obj['timestamp'] === 'string' ? obj['timestamp'] : undefined,
  };
}

/**
 * Stores correlation infos from dsp/correlation/info (Unsolicited or Request/Response).
 * Indexed by ccuOrderId for display in Order Cards / Track & Trace.
 */
@Injectable({ providedIn: 'root' })
export class CorrelationInfoService implements OnDestroy {
  private readonly mapSubject = new BehaviorSubject<Map<string, CorrelationInfo>>(new Map());
  private subscription?: Subscription;

  constructor(private readonly messageMonitor: MessageMonitorService) {
    this.initializeSubscription();
    this.processHistory();
  }

  private initializeSubscription(): void {
    this.subscription = this.messageMonitor
      .getLastMessage<unknown>(CORRELATION_TOPIC)
      .pipe(
        distinctUntilChanged((a, b) => a?.timestamp === b?.timestamp),
        map((msg) => (msg?.payload ? parseCorrelationPayload(msg.payload) : null))
      )
      .subscribe((info) => {
        if (!info) {
          return;
        }
        const key = info.ccuOrderId ?? info.requestId;
        if (!key) {
          return;
        }
        const current = new Map(this.mapSubject.value);
        current.set(key, info);
        if (info.ccuOrderId && info.requestId && info.ccuOrderId !== info.requestId) {
          current.set(info.requestId, info);
        }
        this.mapSubject.next(current);
      });
  }

  private processHistory(): void {
    const history = this.messageMonitor.getHistory<unknown>(CORRELATION_TOPIC);
    const current = new Map(this.mapSubject.value);
    for (const msg of history) {
      const info = parseCorrelationPayload(msg.payload);
      if (!info) continue;
      const key = info.ccuOrderId ?? info.requestId;
      if (key) {
        current.set(key, info);
        if (info.ccuOrderId && info.requestId && info.ccuOrderId !== info.requestId) {
          current.set(info.requestId, info);
        }
      }
    }
    if (current.size > 0) {
      this.mapSubject.next(current);
    }
  }

  /**
   * Observable of correlation info for a given ccuOrderId (or requestId as fallback).
   */
  getCorrelationInfo$(ccuOrderId: string): Observable<CorrelationInfo | null> {
    return this.mapSubject.pipe(
      map((m) => m.get(ccuOrderId) ?? null),
      distinctUntilChanged((a, b) => {
        if (a === b) return true;
        if (!a || !b) return false;
        return a.timestamp === b.timestamp && a.ccuOrderId === b.ccuOrderId;
      })
    );
  }

  /**
   * Get current correlation info for a ccuOrderId (synchronous).
   */
  getCorrelationInfo(ccuOrderId: string): CorrelationInfo | null {
    return this.mapSubject.value.get(ccuOrderId) ?? null;
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }
}
