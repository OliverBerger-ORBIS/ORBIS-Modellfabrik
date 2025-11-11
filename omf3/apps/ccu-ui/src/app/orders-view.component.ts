import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';
import type { OrderActive } from '@omf3/entities';
import type { Observable } from 'rxjs';

@Component({
  selector: 'app-orders-view',
  standalone: true,
  template: `
    <section class="panel">
      <header>
        <h2>Orders</h2>
        <div class="status-badges" *ngIf="counts$ | async as counts">
          <span class="badge running">Running: {{ counts.running }}</span>
          <span class="badge queued">Queued: {{ counts.queued }}</span>
          <span class="badge completed">Completed: {{ counts.completed }}</span>
        </div>
      </header>

      <p class="empty" *ngIf="(orders$ | async)?.length === 0">
        No active orders.
      </p>

      <ul *ngIf="orders$ | async as orders">
        <li *ngFor="let order of orders">
          <div class="order-id">{{ order.orderId }}</div>
          <div class="order-meta">
            <span>{{ order.productId }}</span>
            <span>Qty {{ order.quantity }}</span>
          </div>
          <span class="pill" [class]="order.status">{{ order.status }}</span>
        </li>
      </ul>
    </section>
  `,
  styleUrls: ['./orders-view.component.scss'],
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrdersViewComponent {
  @Input({ required: true }) orders$!: Observable<OrderActive[]>;
  @Input({ required: true })
  counts$!: Observable<Record<'running' | 'queued' | 'completed', number>>;
}

