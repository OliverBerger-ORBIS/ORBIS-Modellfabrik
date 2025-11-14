import { BehaviorSubject, Observable, Subject } from 'rxjs';

export type ConnState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface SubscribeOptions {
  qos?: 0 | 1 | 2;
}

export interface PublishOptions {
  qos?: 0 | 1 | 2;
  retain?: boolean;
}

export interface MqttMessage<T = unknown> {
  topic: string;
  payload: T;
  timestamp: string;
  options?: PublishOptions;
}

export interface MqttAdapter {
  connect(wsUrl: string, options?: Record<string, unknown>): Promise<void>;
  disconnect(): Promise<void>;
  publish(topic: string, payload: unknown, options?: PublishOptions): Promise<void>;
  subscribe(topic: string, options?: SubscribeOptions): Promise<void>;
  readonly messages$: Observable<MqttMessage>;
  readonly connectionState$: Observable<ConnState>;
}

export class MqttClientWrapper {
  constructor(private readonly adapter: MqttAdapter) {}

  connect(wsUrl: string, options?: Record<string, unknown>): Promise<void> {
    return this.adapter.connect(wsUrl, options);
  }

  disconnect(): Promise<void> {
    return this.adapter.disconnect();
  }

  publish(topic: string, payload: unknown, options?: PublishOptions): Promise<void> {
    return this.adapter.publish(topic, payload, options);
  }

  subscribe(topic: string, options?: SubscribeOptions): Promise<void> {
    return this.adapter.subscribe(topic, options);
  }

  get messages$(): Observable<MqttMessage> {
    return this.adapter.messages$;
  }

  get connectionState$(): Observable<ConnState> {
    return this.adapter.connectionState$;
  }
}

export class SubjectMqttAdapter implements MqttAdapter {
  private readonly messagesSubject = new Subject<MqttMessage>();
  private readonly stateSubject = new BehaviorSubject<ConnState>('disconnected');

  readonly messages$ = this.messagesSubject.asObservable();
  readonly connectionState$ = this.stateSubject.asObservable();

  connect(wsUrl: string, _options?: Record<string, unknown>): Promise<void> {
    this.updateState('connecting');
    return Promise.resolve(wsUrl).then(() => this.updateState('connected'));
  }

  disconnect(): Promise<void> {
    this.updateState('disconnected');
    return Promise.resolve();
  }

  publish(topic: string, payload: unknown, options?: PublishOptions): Promise<void> {
    this.messagesSubject.next({
      topic,
      payload,
      options,
      timestamp: new Date().toISOString(),
    });
    return Promise.resolve();
  }

  subscribe(_topic: string, _options?: SubscribeOptions): Promise<void> {
    return Promise.resolve();
  }

  protected updateState(next: ConnState) {
    this.stateSubject.next(next);
  }
}

export const createMqttClient = (adapter: MqttAdapter) =>
  new MqttClientWrapper(adapter);

export { MockMqttAdapter } from './mock-adapter';
export { WebSocketMqttAdapter } from './websocket-adapter';
