import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { OrderResponse } from '../../../common/protocol';

@Injectable()
export class FutureFactorySimulationLayoutState {
  public readonly selectedOrder = new BehaviorSubject<
    OrderResponse | undefined
  >(undefined);

  public setSelectedOrder(order: OrderResponse[] | OrderResponse | undefined) {
    if (Array.isArray(order)) {
      this.selectedOrder.next(order[0]);
    } else {
      this.selectedOrder.next(order);
    }
  }
}
