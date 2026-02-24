import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatSelectionListChange } from '@angular/material/list';
import { map } from 'rxjs/operators';
import { OrderResponse, OrderState } from '../../../common/protocol/ccu';
import { OrderListState } from './order-list.state';
import { shareReplay } from 'rxjs/internal/operators/shareReplay';

@Component({
  selector: 'ff-order-list',
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.scss'],
  providers: [OrderListState],
})
export class OrderListComponent {
  readonly stepTypeIcon: { [t in 'MANUFACTURE' | 'NAVIGATION']: string } = {
    MANUFACTURE: 'precision_manufacturing',
    NAVIGATION: 'forklift',
  };
  readonly stateIcons: { [t in OrderState]: string } = {
    [OrderState.ENQUEUED]: 'hourglass_empty',
    [OrderState.IN_PROGRESS]: 'play_circle',
    [OrderState.FINISHED]: 'check_circle',
    [OrderState.ERROR]: 'error',
    [OrderState.CANCELLED]: 'hourglass_disabled',
  };

  @Input() multiple = false;
  @Input() withCompleted = false;
  @Input() canRemove = true;
  @Input() set selectedOrder(order: OrderResponse | undefined) {
    this.state.setSelectedOrder(order);
  }
  /** Used to filter for orders of a specific simulation. */
  @Input() simulationId: string | undefined;
  @Output() public readonly orderSelect = new EventEmitter<OrderResponse[]>();

  activeOrders$ = this.state.activeOrders$.pipe(
    map((orders: OrderResponse[]) => orders.filter(o => this.simulationId === undefined || o.simulationId == this.simulationId)),
    shareReplay(1)
  );
  completedOrders$ = this.state.completedOrders$.pipe(
    map((orders: OrderResponse[]) => orders.filter(o => this.simulationId === undefined || o.simulationId == this.simulationId)),
    shareReplay(1)
  );

  constructor(public readonly state: OrderListState) {}

  selectOrder($event: MatSelectionListChange): void {
    const selectedOrders = $event.options.map(
      (o) => o.value
    ) as OrderResponse[];
    this.orderSelect.emit(selectedOrders);
  }
}
