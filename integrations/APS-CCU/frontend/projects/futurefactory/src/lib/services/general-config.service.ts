import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import {
  CcuTopic
} from '../../common/protocol';
import { GeneralConfig } from '../../common/protocol/ccu';
import { getPayload } from '../utils/rx.utils';
import { TypedMqttService } from './typed-mqtt.service';

@Injectable({
  providedIn: 'root',
})
export class GeneralConfigService {
  readonly config$: Observable<GeneralConfig> = this.mqttService
    .subscribe<GeneralConfig>(CcuTopic.CONFIG)
    .pipe(getPayload(), shareReplay(1));

  constructor(private mqttService: TypedMqttService) {}

  public saveConfig(config: GeneralConfig) {
    this.mqttService.publish(CcuTopic.SET_CONFIG, config, { qos: 1 });
  }
}
