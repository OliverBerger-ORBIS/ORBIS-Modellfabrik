import { Injectable, OnDestroy } from '@angular/core';
import {
  IMqttMessage,
  IMqttService,
  IPublishOptions,
} from '@ft/futurefactory';
import { MqttService as NgxMqttService } from 'ngx-mqtt';
import { Observable, ReplaySubject, takeUntil } from 'rxjs';

/**
 * This is a wrapper around the ngx-mqtt service to make it compatible with the
 * IMqttService interface. This is necessary, because the mqtt service is provided
 * by the fischertechnik Cloud for the cloud and this service is provided for the
 * local mqtt broker, running on the raspberry pi.
 */
@Injectable({
  providedIn: 'root',
})
export class MqttService implements IMqttService, OnDestroy {
  private readonly destroy = new ReplaySubject<boolean>(1);

  constructor(private mqttService: NgxMqttService) {}

  public publish(
    _: number,
    topic: string,
    message: string,
    options?: IPublishOptions
  ): void {
    this.mqttService.unsafePublish(topic, message, options);
  }

  public subscribe(_: number, topic: string): Observable<IMqttMessage> {
    console.debug('Subscribing to topic : %s', topic);
    return this.mqttService.observe(topic).pipe(takeUntil(this.destroy));
  }

  ngOnDestroy(): void {
    this.destroy.next(true);
    this.destroy.complete();
    this.mqttService.disconnect();
  }
}
