import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type { OrderActive } from '@omf3/entities';
import { getDashboardController } from '../mock-dashboard';
import { OrderCardComponent } from '../components/order-card/order-card.component';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import { map, shareReplay } from 'rxjs/operators';
import { Observable, of } from 'rxjs';
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

  private bindOrderStreams(): void {
    // Subscribe directly to dashboard streams - they already have shareReplay with startWith
    // Use refCount: false to keep streams alive even when no subscribers
    const orders$ = this.dashboard.streams.orders$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    const completed$ = this.dashboard.streams.completedOrders$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

    const orderList$ = orders$.pipe(
      map((list) => [...list]),
      map((orders) => orders.sort((a, b) => getOrderTimestamp(b) - getOrderTimestamp(a)))
    );

    const completedList$ = completed$.pipe(
      map((list) => [...list]),
      map((orders) => orders.sort((a, b) => getOrderTimestamp(b) - getOrderTimestamp(a)))
    );

    this.productionActive$ = orderList$.pipe(
      map((orders) =>
        orders.filter((order) => inferType(order) === ORDER_TYPES.PRODUCTION && !isCompleted(order))
      )
    );

    this.productionCompleted$ = completedList$.pipe(
      map((orders) => orders.filter((order) => inferType(order) === ORDER_TYPES.PRODUCTION))
    );

    this.storageActive$ = orderList$.pipe(
      map((orders) =>
        orders.filter((order) => inferType(order) === ORDER_TYPES.STORAGE && !isCompleted(order))
      )
    );

    this.storageCompleted$ = completedList$.pipe(
      map((orders) => orders.filter((order) => inferType(order) === ORDER_TYPES.STORAGE))
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

