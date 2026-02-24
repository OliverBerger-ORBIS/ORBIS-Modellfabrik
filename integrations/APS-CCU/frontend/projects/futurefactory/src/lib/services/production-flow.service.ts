import { Injectable } from '@angular/core';
import { Observable, shareReplay } from 'rxjs';
import {
  ANY_SERIAL,
  CcuTopic,
  FtsTopic,
  ModuleTopic,
  getFtsTopic,
  getModuleTopic,
} from '../../common/protocol';
import { ProductionFlows } from '../../common/protocol/ccu';
import { TypedMqttService } from '../futurefactory.service';
import { getPayload } from '../utils/rx.utils';

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

/**
 * Holds the current production flows as the mqtt subscription will only send them once per page load
 */
@Injectable({
  providedIn: 'root',
})
export class ProductionFlowsService {
  /** The current flows as a replayable observable */
  readonly productionFlows$: Observable<ProductionFlows>;

  constructor(private mqttService: TypedMqttService) {
    this.productionFlows$ = this.mqttService
      .subscribe<ProductionFlows>(CcuTopic.FLOWS)
      .pipe(getPayload(), shareReplay(1));
  }
}
