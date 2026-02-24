import { Injectable } from '@angular/core';
import { Observable, shareReplay } from 'rxjs';
import { OrderResponse, Workpiece } from '../../common/protocol';
import { generateOrderRequestForProduction } from '../../common/protocol/ccu';
import { getPayload } from '../utils/rx.utils';
import { TypedMqttService } from './typed-mqtt.service';

export const orderRequest = 'ccu/order/request';
export const activeOrders = 'ccu/order/active';

@Injectable({
  providedIn: 'root',
})
export class OrderService {
  constructor(private mqttService: TypedMqttService) {}

  sendProductionOrder(type: Workpiece = 'WHITE') {
    this.mqttService.publish(
      orderRequest,
      generateOrderRequestForProduction(type)
    );
  }

  getActiveOrders(): Observable<OrderResponse[]> {
    return this.mqttService
      .subscribe<OrderResponse[]>(activeOrders)
      .pipe(getPayload(), shareReplay(1));
  }
}
