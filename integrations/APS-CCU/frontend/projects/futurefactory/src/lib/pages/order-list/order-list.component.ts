import { Component, OnDestroy, ViewChild } from '@angular/core';
import { MatSelectionList } from '@angular/material/list';
import { ActivatedRoute, Router } from '@angular/router';
import {
  Observable,
  Subject,
  combineLatest,
  firstValueFrom,
  map,
  shareReplay,
  takeUntil,
} from 'rxjs';
import { CcuTopic, OrderResponse } from '../../../common/protocol';
import { OrderManufactureStep, OrderState } from '../../../common/protocol/ccu';
import { TypedMqttService } from '../../futurefactory.service';
import { OrderStatesService } from '../../services/order-states.service';

@Component({
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.scss'],
})
export class FutureFactoryOrderListComponent implements OnDestroy {
  @ViewChild('selectionList')
  selectionList!: MatSelectionList;

  readonly activeOrders$: Observable<OrderResponse[]>;
  private readonly destroyed$ = new Subject<void>();
  readonly selectedOrder$: Observable<OrderResponse | undefined>;
  readonly activeStepId$: Observable<string | undefined>;
  private readonly paramOrderId$: Observable<string | null>;

  constructor(
    private mqttService: TypedMqttService,
    private orderStatesService: OrderStatesService,
    private activatedRoute: ActivatedRoute,
    private router: Router
  ) {
    this.paramOrderId$ = this.activatedRoute.paramMap.pipe(
      takeUntil(this.destroyed$),
      map((params) => params.get('orderId'))
    );

    this.activeOrders$ = this.orderStatesService.activeOrders$.pipe(
      map((orders) => orders.filter((o) => o.orderType === 'PRODUCTION'))
    );
    this.selectedOrder$ = combineLatest([
      this.paramOrderId$,
      this.activeOrders$,
    ]).pipe(
      map(([selectedOrderId, activeOrders]) => {
        const selectedOrder = selectedOrderId
          ? activeOrders.find((o) => selectedOrderId === o.orderId)
          : undefined;
        return (
          selectedOrder ?? (activeOrders.length ? activeOrders[0] : undefined)
        );
      }),
      shareReplay(1)
    );
    this.activeStepId$ = this.selectedOrder$.pipe(
      map((orderResponse) => {
        if (!orderResponse) {
          return undefined;
        }
        const usedProductionSteps: OrderManufactureStep[] =
          this.getUsedProductionSteps(orderResponse);
        return usedProductionSteps?.length
          ? usedProductionSteps.reverse()[0].serialNumber
          : undefined;
      })
    );
  }

  ngOnDestroy() {
    this.destroyed$.next();
    this.destroyed$.complete();
  }

  async selectOrder($event: OrderResponse[]): Promise<void> {
    const lastOrderIdParam = await firstValueFrom(this.paramOrderId$);
    const route = [lastOrderIdParam != null ? '..' : '.', $event[0].orderId];
    await this.router.navigate(route, { relativeTo: this.activatedRoute });
  }

  private getUsedProductionSteps(
    orderResponse: OrderResponse
  ): OrderManufactureStep[] {
    return orderResponse.productionSteps.filter(
      (s): s is OrderManufactureStep => {
        if (s.type !== 'MANUFACTURE') {
          return false;
        }
        // skip production steps that have not been started or were never started
        return (
          s.state !== OrderState.ENQUEUED && s.state !== OrderState.CANCELLED
        );
      }
    );
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
}
