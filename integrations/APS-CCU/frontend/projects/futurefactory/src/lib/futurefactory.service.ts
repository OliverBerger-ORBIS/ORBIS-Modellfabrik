import { Injectable } from '@angular/core';
import { ControllerResponse } from '@fischertechnik/ft-api';
import {
  Observable,
  OperatorFunction,
  ReplaySubject,
  map,
  pipe,
  startWith,
} from 'rxjs';
import {
  IControllerService,
  IMqttMessage,
  IMqttService,
} from './futurefactory.external.service';

export { TypedMqttService } from './services/typed-mqtt.service';

@Injectable()
export class MqttServiceMock implements IMqttService {
  subscribe(controllerId: number, topic: string): Observable<IMqttMessage> {
    return new Observable<IMqttMessage>();
  }
  publish(controllerId: number, topic: string, message: string): void {}
}

@Injectable()
export class ControllerServiceMock implements IControllerService {
  private readonly controllers$ = new ReplaySubject<ControllerResponse[]>(1);

  onChange(): Observable<ControllerResponse[]> {
    return this.controllers$.asObservable();
  }
  loadControllers(): void {
    this.controllers$.next([
      {
        name: 'controller',
        hardwareId: '50F14AFC164C',
        hardwareModel: 'TXT',
        alarm: true,
        pushMessage: true,
        shared: true,
        mqttUser: undefined,
        softwareVersion: '1.1.9',
        softwareName: 'txt',
        controllerId: 1,
        crdate: 1560873431,
      },
    ]);
  }
}
