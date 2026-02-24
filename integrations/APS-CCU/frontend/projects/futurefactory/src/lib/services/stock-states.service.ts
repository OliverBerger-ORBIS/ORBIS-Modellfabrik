import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import {
  CcuTopic
} from '../../common/protocol';
import { CloudStock } from '../../common/protocol/ccu';
import { getPayload } from '../utils/rx.utils';
import { TypedMqttService } from './typed-mqtt.service';

@Injectable({
  providedIn: 'root',
})
export class StockStatesService {
  readonly stock$: Observable<CloudStock> = this.mqttService.subscribe<CloudStock>(CcuTopic.STOCK).pipe(getPayload(), shareReplay(1));

  constructor(private mqttService: TypedMqttService) {}
}
