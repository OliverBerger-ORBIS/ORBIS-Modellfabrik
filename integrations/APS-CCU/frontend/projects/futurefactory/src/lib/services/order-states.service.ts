import { Injectable } from '@angular/core';
import { MqttService } from 'ngx-mqtt';
import { Observable, merge } from 'rxjs';
import { map, scan, shareReplay, startWith } from 'rxjs/operators';
import {
  ANY_SERIAL,
  CcuTopic,
  FtsTopic,
  ModuleTopic,
  OrderResponse,
  getFtsTopic,
  getModuleTopic,
} from '../../common/protocol';
import { FtsState } from '../../common/protocol/fts';
import { ModuleState } from '../../common/protocol/module';
import { getPayload } from '../utils/rx.utils';
import { MqttMessage, TypedMqttService } from './typed-mqtt.service';

export interface OrderStatus {
  [order: string]: {
    current: string;
    log: string[];
    lastTimestamp: Date;
  };
}

export const STATE_TOPICS = {
  fts: getFtsTopic(ANY_SERIAL, FtsTopic.STATE),
  module: getModuleTopic(ANY_SERIAL, ModuleTopic.STATE),
  order: CcuTopic.ORDER_RESPONSE,
};

@Injectable({
  providedIn: 'root',
})
export class OrderStatesService {
  readonly orderStatus$: Observable<OrderStatus>;
  readonly activeOrders$: Observable<OrderResponse[]>;
  readonly completedOrders$: Observable<OrderResponse[]>;
  readonly hasRunningOrders$: Observable<boolean>;

  constructor(private mqttService: TypedMqttService) {
    const ftsState$ = this.mqttService.subscribe<FtsState>(STATE_TOPICS.fts);
    const moduleState$ = this.mqttService.subscribe<ModuleState>(
      STATE_TOPICS.module
    );
    const orderState$ = this.mqttService.subscribe<OrderResponse>(
      STATE_TOPICS.order
    );

    this.orderStatus$ = merge(ftsState$, moduleState$, orderState$).pipe(
      scan(this.buildOrderStatus, {} as OrderStatus),
      shareReplay(1)
    );

    this.activeOrders$ = this.listenForActiveOrders();
    this.completedOrders$ = this.listenForCompletedOrders();
    this.hasRunningOrders$ = this.setupHasRunningOrders(this.activeOrders$);
  }

  buildOrderStatus = (
    status: OrderStatus,
    message: MqttMessage<FtsState | ModuleState | OrderResponse>
  ): OrderStatus => {
    const newStatus = { ...status };
    let orderId, newMessage, timestamp;
    if (message) {
      if (MqttService.filterMatchesTopic(STATE_TOPICS.fts, message.topic)) {
        const ftsResponse = message.payload as FtsState;
        orderId = ftsResponse.orderId;
        if (ftsResponse.actionState) {
          timestamp = new Date(ftsResponse.actionState.timestamp);
          newMessage = `FTS ${ftsResponse.serialNumber}: ${ftsResponse.actionState.state}`;
        }
      } else if (
        MqttService.filterMatchesTopic(STATE_TOPICS.module, message.topic)
      ) {
        const moduleResponse = message.payload as ModuleState;
        orderId = moduleResponse.orderId;
        if (moduleResponse.actionState) {
          timestamp = new Date(moduleResponse.actionState.timestamp);
          newMessage = `Module ${moduleResponse.serialNumber}: ${moduleResponse.actionState.command} ${moduleResponse.actionState.state}`;
        }
      } else if (
        MqttService.filterMatchesTopic(STATE_TOPICS.order, message.topic)
      ) {
        const orderResponse = message.payload as OrderResponse;
        orderId = orderResponse.orderId;
        timestamp = new Date(orderResponse.timestamp);
        newMessage = `Order created: ${orderResponse.orderId} ${orderResponse.type}`;
      }
      if (orderId) {
        const prev = status[orderId]?.current;
        const log = prev
          ? [prev, ...status[orderId]?.log]
          : status[orderId]?.log || [];
        newStatus[orderId] = {
          current: newMessage || 'Unknown',
          lastTimestamp: timestamp || new Date(),
          log: log,
        };
      }
    }
    return newStatus;
  };

  private listenForActiveOrders(): Observable<OrderResponse[]> {
    return this.mqttService
      .subscribe<OrderResponse[]>(CcuTopic.ACTIVE_ORDERS)
      .pipe(getPayload(), shareReplay(1));
  }

  private listenForCompletedOrders(): Observable<OrderResponse[]> {
    return this.mqttService
      .subscribe<OrderResponse[]>(CcuTopic.COMPLETED_ORDERS)
      .pipe(getPayload(), shareReplay(1));
  }

  private setupHasRunningOrders(
    activeOrders$: Observable<OrderResponse[]>
  ): Observable<boolean> {
    return activeOrders$.pipe(
      startWith([]),
      map((activeOrders) => (activeOrders ?? []).length > 0),
      shareReplay(1)
    );
  }
}
