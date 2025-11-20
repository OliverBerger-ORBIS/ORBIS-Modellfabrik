import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type { OrderActive } from '@omf3/entities';
import { getDashboardController } from '../mock-dashboard';
import { OrderCardComponent } from '../components/order-card/order-card.component';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import { filter, map, shareReplay, startWith } from 'rxjs/operators';
import { combineLatest, merge, Observable, of } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';

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
export class OrderTabComponent implements OnInit {
  private readonly dashboard = getDashboardController();

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService
  ) {}

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  productionActive$: Observable<OrderActive[]> = of([]);
  productionCompleted$: Observable<OrderActive[]> = of([]);
  storageActive$: Observable<OrderActive[]> = of([]);
  storageCompleted$: Observable<OrderActive[]> = of([]);

  readonly fixtureOptions: OrderFixtureName[] = ['white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  readonly fixtureLabels: Record<OrderFixtureName, string> = {
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
    
    // Combine last messages from both topics and merge with dashboard streams
    // MessageMonitor streams come first to ensure they take priority
    const lastOrders = combineLatest([lastActive, lastCompleted]).pipe(
      map(([active, completed]) => {
        // Build orders state from last messages (similar to business layer logic)
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
            // Remove from active if it's completed
            delete activeMap[order.orderId];
          }
        });
        
        return { active: activeMap, completed: completedMap };
      })
    );
    
    // Merge with dashboard streams - MessageMonitor first to ensure latest data
    // Dashboard streams are Record<string, OrderActive>, so we convert MessageMonitor data to match
    const lastActiveOrders$ = lastOrders.pipe(map((state) => state.active));
    const lastCompletedOrders$ = lastOrders.pipe(map((state) => state.completed));
    
    const ordersState$ = merge(
      lastActiveOrders$,
      this.dashboard.streams.orders$
    ).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    
    const completedState$ = merge(
      lastCompletedOrders$,
      this.dashboard.streams.completedOrders$
    ).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    
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
      map((orders: OrderActive[]) => orders.filter((order: OrderActive) => inferType(order) === ORDER_TYPES.STORAGE))
    );
  }

  ngOnInit(): void {
    this.bindOrderStreams();
    // Only load fixture in mock mode; in live/replay mode, streams are already connected
    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  async loadFixture(fixture: OrderFixtureName) {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    await this.dashboard.loadFixture(fixture);
    this.bindOrderStreams();
  }
}

