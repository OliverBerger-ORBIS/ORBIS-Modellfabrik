import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import type { OrderActive } from '@omf3/entities';
import { getDashboardController } from '../mock-dashboard';
import { OrderCardComponent } from '../components/order-card/order-card.component';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import { map, shareReplay } from 'rxjs/operators';
import { Observable, of } from 'rxjs';

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

  productionActive$: Observable<OrderActive[]> = of([]);
  productionCompleted$: Observable<OrderActive[]> = of([]);
  storageActive$: Observable<OrderActive[]> = of([]);
  storageCompleted$: Observable<OrderActive[]> = of([]);

  readonly fixtureOptions: OrderFixtureName[] = ['white', 'blue', 'red', 'mixed', 'storage'];
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  private bindOrderStreams(): void {
    const orders$ = this.dashboard.streams.orders$.pipe(shareReplay({ bufferSize: 1, refCount: true }));
    const completed$ = this.dashboard.streams.completedOrders$.pipe(shareReplay({ bufferSize: 1, refCount: true }));

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
    void this.loadFixture(this.activeFixture);
  }

  async loadFixture(fixture: OrderFixtureName) {
    this.activeFixture = fixture;
    await this.dashboard.loadFixture(fixture);
    this.bindOrderStreams();
  }
}

