import { Injectable } from '@angular/core';
import {
  BehaviorSubject,
  MonoTypeOperatorFunction,
  Observable,
  pipe,
} from 'rxjs';
import { map, shareReplay, startWith } from 'rxjs/operators';
import { CcuTopic } from '../../../common/protocol';
import { OrderResponse, OrderType } from '../../../common/protocol/ccu';
import { TypedMqttService } from '../../futurefactory.service';
import { OrderStatesService } from '../../services/order-states.service';

@Injectable()
export class OrderListState {
  readonly selectedOrder = new BehaviorSubject<OrderResponse | undefined>(
    undefined
  );
  readonly activeOrders$: Observable<OrderResponse[]>;
  readonly completedOrders$: Observable<OrderResponse[]>;

  constructor(
    private mqttService: TypedMqttService,
    private orderStatesService: OrderStatesService
  ) {
    this.activeOrders$ = this.orderStatesService.activeOrders$.pipe(
      this.filterOrdersByType(),
      shareReplay(1)
    );
    this.completedOrders$ = this.orderStatesService.completedOrders$.pipe(
      this.filterOrdersByType(),
      shareReplay(1)
    );
  }

  public setSelectedOrder(order: OrderResponse | undefined) {
    this.selectedOrder.next(order);
  }

  isOrderSelected(order: OrderResponse): boolean {
    return this.selectedOrder.value?.orderId === order.orderId;
  }

  /**
   * Request the deletion of an order, only ENQUEUED orders can be deleted.
   * Cancelling of active orders is not possible.
   * @param $event
   * @param orderId
   */
  public deleteOrder($event: MouseEvent, orderId: string) {
    $event.stopPropagation();
    this.mqttService.publish(CcuTopic.CANCEL_ORDERS, [orderId]);
  }

  /**
   * OperatorFunction to filter orders by type.
   * It is used in the constructor to filter the active and completed orders
   * by the order type.
   *
   * @param orderType the type of orders to filter
   * @returns {MonoTypeOperatorFunction<OrderResponse[]>}
   */
  private filterOrdersByType(): MonoTypeOperatorFunction<OrderResponse[]> {
    return pipe(
      map((orders) => orders ?? []),
      map((orders) =>
        orders.filter((o) => o.orderType === OrderType.PRODUCTION)
      ),
      startWith([])
    );
  }
}
