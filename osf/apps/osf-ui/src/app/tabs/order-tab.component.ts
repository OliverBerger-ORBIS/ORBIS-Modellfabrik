import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import type { OrderActive } from '@osf/entities';
import { getDashboardController } from '../mock-dashboard';
import { OrderCardComponent } from '../components/order-card/order-card.component';
import type { OrderFixtureName } from '@osf/testing-fixtures';
import { filter, map, shareReplay, startWith, distinctUntilChanged, take } from 'rxjs/operators';
import { combineLatest, merge, Observable, of, Subscription } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';

const ORDER_TYPES = {
  PRODUCTION: 'PRODUCTION',
  STORAGE: 'STORAGE',
};

const isCompleted = (order: OrderActive) =>
  (order.state ?? order.status ?? '').toUpperCase() === 'COMPLETED';

const inferType = (order: OrderActive) =>
  (order.orderType ?? '').toUpperCase() === ORDER_TYPES.STORAGE ? ORDER_TYPES.STORAGE : ORDER_TYPES.PRODUCTION;

const getOrderTimestamp = (order: OrderActive): number => {
  const candidates = [order.updatedAt, order.startedAt];
  for (const value of candidates) {
    if (value) {
      const date = new Date(value).getTime();
      if (!Number.isNaN(date)) {
        return date;
      }
    }
  }
  return 0;
};

@Component({
  standalone: true,
  selector: 'app-order-tab',
  imports: [CommonModule, OrderCardComponent],
  templateUrl: './order-tab.component.html',
  styleUrl: './order-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrderTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly connectionService: ConnectionService,
    private readonly cdr: ChangeDetectorRef
  ) {
    this.initializeStreams();
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  productionActive$: Observable<OrderActive[]> = of([]);
  productionCompleted$: Observable<OrderActive[]> = of([]);
  storageActive$: Observable<OrderActive[]> = of([]);
  storageCompleted$: Observable<OrderActive[]> = of([]);
  
  // Cache for storage completed orders (for auto-expand functionality)
  private currentStorageCompleted: OrderActive[] = [];
  expandedStorageOrderId: string | null = null;

  readonly fixtureOptions: OrderFixtureName[] = ['white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
    startup: $localize`:@@fixtureLabelStartup:Startup`,
  };
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  productionCompletedCollapsed = true;
  storageCompletedCollapsed = true;

  toggleProductionCompleted(): void {
    this.productionCompletedCollapsed = !this.productionCompletedCollapsed;
  }

  toggleStorageCompleted(): void {
    this.storageCompletedCollapsed = !this.storageCompletedCollapsed;
    // Auto-expand first (topmost) order when expanding completed list
    if (!this.storageCompletedCollapsed) {
      // Use cached orders for immediate synchronous access
      if (this.currentStorageCompleted.length > 0) {
        const topOrder = this.currentStorageCompleted[0];
        this.expandedStorageOrderId = topOrder.orderId ?? null;
      } else {
        // Fallback: subscribe if cache is empty
        this.subscriptions.add(
          this.storageCompleted$.pipe(take(1)).subscribe((orders) => {
            if (orders.length > 0) {
              const topOrder = orders[0];
              this.expandedStorageOrderId = topOrder.orderId ?? null;
              this.cdr.markForCheck();
            }
          })
        );
      }
      this.cdr.markForCheck();
    } else {
      this.expandedStorageOrderId = null;
      this.cdr.markForCheck();
    }
  }

  get productionCompletedToggleLabel(): string {
    return this.productionCompletedCollapsed
      ? $localize`:@@orderTabExpandCompleted:Expand completed orders`
      : $localize`:@@orderTabCollapseCompleted:Collapse completed orders`;
  }

  get storageCompletedToggleLabel(): string {
    return this.storageCompletedCollapsed
      ? $localize`:@@orderTabExpandCompleted:Expand completed orders`
      : $localize`:@@orderTabCollapseCompleted:Collapse completed orders`;
  }

  requestCorrelation = async (order: { orderId: string; requestId?: string }): Promise<void> => {
    try {
      const ccuOrderId = order.orderId;
      const requestId = order.requestId;
      // Prefer requestId when available (logical: OSF-UI initiated with that ID); include ccuOrderId for DSP compatibility
      await this.dashboard.commands.requestCorrelationInfo(
        requestId ? { requestId, ccuOrderId } : { ccuOrderId }
      );
    } catch (error) {
      console.error('[order-tab] requestCorrelationInfo failed:', error);
    }
  };

  private bindOrderStreams(): void {
    // Pattern: Merge MessageMonitor last messages with dashboard streams
    // This ensures we get the latest orders even when connecting while factory is already running
    // Get last messages for both order topics
    const lastActive = this.messageMonitor.getLastMessage<OrderActive | OrderActive[]>('ccu/order/active').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => {
        const payload = msg!.payload;
        return Array.isArray(payload) ? payload : [payload];
      }),
      startWith([] as OrderActive[])
    );
    
    const lastCompleted = this.messageMonitor.getLastMessage<OrderActive | OrderActive[]>('ccu/order/completed').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => {
        const payload = msg!.payload;
        return Array.isArray(payload) ? payload : [payload];
      }),
      startWith([] as OrderActive[])
    );
    
    // Combine last messages from both topics (CCU full-snapshot semantics)
    // CCU publishes ccu/order/active and ccu/order/completed as complete arrays each time (like CCU Frontend).
    // MessageMonitor delivers the exact payload. Do NOT merge with dashboard.streams.orders$ in replay/live:
    // the gateway uses additive scan() and never clears – it does not match CCU snapshot semantics.
    const lastOrders = combineLatest([lastActive, lastCompleted]).pipe(
      map(([active, completed]) => {
        const activeMap: Record<string, OrderActive> = {};
        const completedMap: Record<string, OrderActive> = {};
        active.forEach((order) => {
          if (order && order.orderId) {
            activeMap[order.orderId] = order;
          }
        });
        completed.forEach((order) => {
          if (order && order.orderId) {
            completedMap[order.orderId] = order;
            delete activeMap[order.orderId];
          }
        });
        return { active: activeMap, completed: completedMap };
      })
    );

    const lastActiveOrders$ = lastOrders.pipe(map((state) => state.active));
    const lastCompletedOrders$ = lastOrders.pipe(map((state) => state.completed));

    // Replay/Live: use MessageMonitor only (CCU snapshot semantics).
    // Mock: use dashboard streams (fixtures).
    const ordersState$ = this.isMockMode
      ? merge(lastActiveOrders$, this.dashboard.streams.orders$).pipe(
          shareReplay({ bufferSize: 1, refCount: false })
        )
      : lastActiveOrders$.pipe(shareReplay({ bufferSize: 1, refCount: false }));

    const completedState$ = this.isMockMode
      ? merge(lastCompletedOrders$, this.dashboard.streams.completedOrders$).pipe(
          shareReplay({ bufferSize: 1, refCount: false })
        )
      : lastCompletedOrders$.pipe(shareReplay({ bufferSize: 1, refCount: false }));

    // Convert Record<string, OrderActive> to OrderActive[]
    const orderList$ = ordersState$.pipe(
      map((ordersMap) => {
        // Handle both Record and array types (merge can emit either)
        if (Array.isArray(ordersMap)) {
          return ordersMap;
        }
        return Object.values(ordersMap) as OrderActive[];
      }),
      map((orders: OrderActive[]) => orders.sort((a, b) => getOrderTimestamp(b) - getOrderTimestamp(a)))
    );

    const completedList$ = completedState$.pipe(
      map((ordersMap) => {
        // Handle both Record and array types (merge can emit either)
        if (Array.isArray(ordersMap)) {
          return ordersMap;
        }
        return Object.values(ordersMap) as OrderActive[];
      }),
      map((orders: OrderActive[]) => orders.sort((a, b) => getOrderTimestamp(b) - getOrderTimestamp(a)))
    );

    this.productionActive$ = orderList$.pipe(
      map((orders: OrderActive[]) =>
        orders.filter((order: OrderActive) => inferType(order) === ORDER_TYPES.PRODUCTION && !isCompleted(order))
      )
    );

    this.productionCompleted$ = completedList$.pipe(
      map((orders: OrderActive[]) => orders.filter((order: OrderActive) => inferType(order) === ORDER_TYPES.PRODUCTION))
    );

    this.storageActive$ = orderList$.pipe(
      map((orders: OrderActive[]) =>
        orders.filter((order: OrderActive) => inferType(order) === ORDER_TYPES.STORAGE && !isCompleted(order))
      )
    );

    this.storageCompleted$ = completedList$.pipe(
      map((orders: OrderActive[]) => orders.filter((order: OrderActive) => inferType(order) === ORDER_TYPES.STORAGE)),
      map((orders: OrderActive[]) => {
        this.currentStorageCompleted = orders;
        return orders;
      })
    );
  }

  ngOnInit(): void {
    this.subscriptions.add(
      this.connectionService.state$
        .pipe(distinctUntilChanged())
        .subscribe((state) => {
          if (state === 'connected') {
            this.initializeStreams();
          }
        })
    );

    this.subscriptions.add(
      this.environmentService.environment$
        .pipe(distinctUntilChanged((prev, next) => prev.key === next.key))
        .subscribe((environment) => {
          this.initializeStreams();
          if (environment.key === 'mock') {
            void this.loadFixture(this.activeFixture);
          }
        })
    );

    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  async loadFixture(fixture: OrderFixtureName) {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    
    // Map OrderFixtureName to tab-specific preset
    const presetMap: Partial<Record<OrderFixtureName, string>> = {
      startup: 'startup',
      white: 'order-white',
      white_step3: 'order-white-step3', // Stops at step 3
      blue: 'order-blue',
      red: 'order-red',
      mixed: 'order-mixed',
      storage: 'order-storage',
    };
    
    const preset = presetMap[fixture] || 'startup';
    await this.dashboard.loadTabFixture(preset);
    this.bindOrderStreams();
  }

  private initializeStreams(): void {
    const controller = getDashboardController();
    this.dashboard = controller;
    this.activeFixture = controller.getCurrentFixture();
    this.bindOrderStreams();
  }

  trackOrder(_index: number, order: OrderActive): string {
    return order.orderId ?? '';
  }
}

