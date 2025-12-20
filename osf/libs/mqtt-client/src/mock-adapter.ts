import { BehaviorSubject, Observable, Subject } from 'rxjs';

import {
  ConnState,
  MqttAdapter,
  MqttMessage,
  PublishOptions,
  SubscribeOptions,
} from './index';

type PublishedPayload = {
  topic: string;
  payload: unknown;
  options?: PublishOptions;
};

/**
 * Simple mock adapter to use in tests or replay mode.
 * All operations resolve immediately and no actual network connection is opened.
 */
export class MockMqttAdapter implements MqttAdapter {
  private readonly stateSubject = new BehaviorSubject<ConnState>('disconnected');
  private readonly messagesSubject = new Subject<MqttMessage>();
  private readonly subscriptions = new Set<string>();

  readonly connectionState$ = this.stateSubject.asObservable();
  readonly messages$ = this.messagesSubject.asObservable();

  async connect(wsUrl: string, _options?: Record<string, unknown>): Promise<void> {
    this.transition('connecting');
    await Promise.resolve(wsUrl);
    this.transition('connected');
  }

  async disconnect(): Promise<void> {
    this.transition('disconnected');
  }

  async publish(topic: string, payload: unknown, options?: PublishOptions): Promise<void> {
    if (!this.subscriptions.has(topic)) {
      return;
    }

    this.emit({ topic, payload, options });
  }

  async subscribe(topic: string, _options?: SubscribeOptions): Promise<void> {
    this.subscriptions.add(topic);
  }

  private transition(next: ConnState) {
    this.stateSubject.next(next);
  }

  private emit({ topic, payload, options }: PublishedPayload) {
    this.messagesSubject.next({
      topic,
      payload,
      options,
      timestamp: new Date().toISOString(),
    });
  }
}

