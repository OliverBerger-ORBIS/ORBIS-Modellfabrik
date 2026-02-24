import { Inject, Injectable, Optional } from '@angular/core';
import { Observable } from 'rxjs';
import { filter, map, shareReplay, switchMap } from 'rxjs/operators';
import { jsonIsoDateReviver } from '../../common/util/json.revivers';
import {
  IMqttMessage,
  IMqttService,
  IPublishOptions,
  MqttClientService, MqttPrefixRequired,
} from '../futurefactory.external.service';
import { SelectedControllerService } from './selected-controller.service';

export type MqttMessage<T> = Omit<IMqttMessage, 'payload'> & { payload: T };

/**
 * This service provides a typed interface to the MQTT service.
 *  - It subscribes to a topic and parses the payload as JSON
 *  - It publishes a message and stringifies the payload as JSON
 */
@Injectable()
export class TypedMqttService {
  constructor(
    @Inject(MqttClientService) private mqttService: IMqttService,
    @Optional() @Inject(MqttPrefixRequired) private readonly requirePrefix: boolean,
    private selectedControllerService: SelectedControllerService
  ) {
    // treat missing injection token as required prefix
    this.requirePrefix = requirePrefix ?? true;
  }

  /**
   * Prepend the prefix if it is required.
   * @param controllerId
   * @param topic
   * @private
   */
  private prependPrefix(controllerId: number, topic: string): string {
    return this.requirePrefix ? `/j1/txt/${controllerId}/${topic}` : topic;
  }

  /**
   * This method subscribes to a topic and parses the payload as JSON.
   * The observable is shared and replayed with a buffer size of 1.
   *
   * @param topic The topic from which the messages should be received
   * @returns An observable of messages with the payload parsed as JSON
   */
  subscribe<T>(topic: string): Observable<MqttMessage<T>> {
    return this.selectedControllerService.selectedController$.pipe(
      filter((c) => !!c?.controllerId),
      map((c) => c?.controllerId as number),
      switchMap((controllerId) =>
        this.mqttService.subscribe(controllerId, this.prependPrefix(controllerId, topic))
      ),
      map((msg) => this.parsePayload(msg.topic, msg) as MqttMessage<T>),
      shareReplay(1)
    );
  }

  /**
   * This method parses the payload of a message as JSON.
   * @param topic The topic to which the message was published
   * @param msg The message from which the payload should be parsed
   * @returns The message with the payload parsed as JSON
   */
  private parsePayload<T>(topic: string, msg: IMqttMessage): MqttMessage<T> {
    try {
      return {
        ...msg,
        payload: JSON.parse(msg.payload?.toString(), jsonIsoDateReviver) as T,
      };
    } catch (error) {
      console.error(
        'Unable to parse message payload in topic "%s" as JSON',
        topic,
        error
      );
      return {
        ...msg,
        payload: {} as T,
      };
    }
  }

  publish<T>(topic: string, message: T, options?: IPublishOptions): void {
    const controllerId =
      this.selectedControllerService.selectedController$.value?.controllerId;
    if (!controllerId) {
      throw new Error('No controller selected');
    }
    this.mqttService.publish(
      controllerId,
      this.prependPrefix(controllerId, topic),
      JSON.stringify(message),
      // Expand default options with provided options
      { retain: false, qos: 2, ...(options ?? {}) }
    );
  }
}
