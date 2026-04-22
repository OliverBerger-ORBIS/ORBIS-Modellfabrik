import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import type { OrderActive } from '@osf/entities';
import { getDashboardController } from '../mock-dashboard';
import { OrderCardComponent } from '../components/order-card/order-card.component';
import type { OrderFixtureName } from '@osf/testing-fixtures';
import { catchError, filter, map, shareReplay, startWith, distinctUntilChanged, take } from 'rxjs/operators';
import { BehaviorSubject, combineLatest, merge, Observable, of, Subscription } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';
import { HttpClient } from '@angular/common/http';
import { ShopfloorMappingService } from '../services/shopfloor-mapping.service';
import { AgvRouteService } from '../services/agv-route.service';
import type { ShopfloorLayoutConfig } from '../components/shopfloor-preview/shopfloor-layout.types';
import { buildFtsPreviewPositionsFromStates, type FtsPreviewPositionInput } from '../utils/build-fts-preview-positions';

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
  private readonly orderLayoutReady$ = new BehaviorSubject(false);

  readonly orderFtsPositions$: Observable<FtsPreviewPositionInput[]>;

  constructor(
    private readonly environmentService: EnvironmentService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly connectionService: ConnectionService,
    private readonly cdr: ChangeDetectorRef,
    private readonly http: HttpClient,
    private readonly mappingService: ShopfloorMappingService,
    private readonly agvRouteService: AgvRouteService
  ) {
    this.orderFtsPositions$ = combineLatest([
      this.dashboard.streams.ftsStates$,
      this.orderLayoutReady$.pipe(filter((ready) => ready)),
    ]).pipe(
      map(([ftsStates]) =>
        buildFtsPreviewPositionsFromStates(
          ftsStates,
          this.mappingService.getAgvOptions().map((o) => o.serial),
          (id) => this.getOrderTabNodePosition(id),
          (s) => this.mappingService.getAgvColor(s)
        )
      ),
      distinctUntilChanged(
        (a, b) =>
          a.length === b.length &&
          a.every(
            (it, i) =>
              b[i]?.serial === it.serial &&
              Math.abs((b[i]?.x ?? 0) - it.x) < 1 &&
              Math.abs((b[i]?.y ?? 0) - it.y) < 1 &&
              b[i]?.color === it.color
          )
      ),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.initializeStreams();
  }

  private getOrderTabNodePosition(nodeId: string): { x: number; y: number } | null {
    let pos = this.agvRouteService.getAgvMarkerCenter(nodeId);
    if (!pos) {
      const canonical = this.agvRouteService.resolveNodeRef(nodeId);
      if (canonical) pos = this.agvRouteService.getAgvMarkerCenter(canonical);
    }
    if (!pos && nodeId.match(/^\d+$/)) {
      pos =
        this.agvRouteService.getAgvMarkerCenter(`intersection:${nodeId}`) ??
        this.agvRouteService.getAgvMarkerCenter(nodeId);
    }
    return pos ? { x: pos.x, y: pos.y } : null;
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

  readonly fixtureOptions: OrderFixtureName[] = [
    'white',
    'white_step3',
    'blue',
    'red',
    'mixed',
    'mixed_pr_prnok',
    'storage',
    'storage_blue',
    'storage_blue_agv2',
    'storage_blue_parallel',
    'production_blue_dual_agv_step15',
  ];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    mixed_pr_prnok: $localize`:@@fixtureLabelMixedPrPrnok:Mixed PR Quality-Fail`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
    storage_blue: $localize`:@@fixtureLabelStorageBlue:Storage Blue`,
    storage_blue_agv2: $localize`:@@fixtureLabelStorageBlueAgv2:Storage Blue AGV-2`,
    storage_blue_parallel: $localize`:@@fixtureLabelStorageBlueParallel:Storage Blue Parallel`,
    production_blue_dual_agv_step15: $localize`:@@fixtureLabelProductionBlueDualAgv:Production Blue • Dual AGV (step 15 demo)`,
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
      this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').pipe(
        catchError((e) => {
          console.warn('[order-tab] shopfloor layout load failed', e);
          return of(null);
        })
      ).subscribe((config) => {
        if (config) {
          this.mappingService.initializeLayout(config);
          this.agvRouteService.initializeLayout(config);
          this.orderLayoutReady$.next(true);
        }
      })
    );
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
      white_step3: 'order-white-step3',
      blue: 'order-blue',
      red: 'order-red',
      mixed: 'order-mixed',
      mixed_pr_prnok: 'order-mixed-pr-prnok',
      storage: 'order-storage',
      storage_blue: 'order-storage-blue',
      storage_blue_agv2: 'order-storage-blue-agv2',
      storage_blue_parallel: 'order-storage-blue-parallel',
      production_blue_dual_agv_step15: 'order-production-blue-dual-agv-step15',
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

