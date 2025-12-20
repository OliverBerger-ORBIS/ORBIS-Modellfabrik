import { createBusiness } from '@osf/business';
import { createGateway, type RawMqttMessage, type OrderStreamPayload, type GatewayPublishFn } from '@osf/gateway';
import type {
  FtsState,
  ModuleState,
  ModuleOverviewState,
  InventoryOverviewState,
  ProductionFlowMap,
  CcuConfigSnapshot,
  SensorOverviewState,
  CameraFrame,
} from '@osf/entities';
import {
  createModulePairingFixtureStream,
  createOrderFixtureStream,
  createStockFixtureStream,
  createFlowFixtureStream,
  createConfigFixtureStream,
  createSensorFixtureStream,
  createTabFixturePreset,
  type FixtureStreamOptions,
  type ModuleFixtureName,
  type OrderFixtureName,
  type StockFixtureName,
  type FlowFixtureName,
  type ConfigFixtureName,
  type SensorFixtureName,
} from '@osf/testing-fixtures';
import { BehaviorSubject, Subject, type Observable, Subscription, merge } from 'rxjs';
import { map, scan, shareReplay, startWith, filter } from 'rxjs/operators';
import type { OrderActive } from '@osf/entities';
import type { MqttClientWrapper, MqttMessage } from '@osf/mqtt-client';
import type { MonitoredMessage } from './services/message-monitor.service';

export interface DashboardStreamSet {
  orders$: Observable<OrderActive[]>;
  completedOrders$: Observable<OrderActive[]>;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>>;
  stockByPart$: Observable<Record<string, number>>;
  moduleStates$: Observable<Record<string, ModuleState>>;
  ftsStates$: Observable<Record<string, FtsState>>;
  moduleOverview$: Observable<ModuleOverviewState>;
  inventoryOverview$: Observable<InventoryOverviewState>;
  flows$: Observable<ProductionFlowMap>;
  config$: Observable<CcuConfigSnapshot>;
  sensorOverview$: Observable<SensorOverviewState>;
  cameraFrames$: Observable<CameraFrame>;
}

export interface DashboardCommandSet {
  calibrateModule: (serialNumber: string) => Promise<void>;
  setFtsCharge: (serialNumber: string, charge: boolean) => Promise<void>;
  dockFts: (serialNumber: string, nodeId?: string) => Promise<void>;
  sendCustomerOrder: (workpieceType: string) => Promise<void>;
  requestRawMaterial: (workpieceType: string) => Promise<void>;
  moveCamera: (command: 'relmove_up' | 'relmove_down' | 'relmove_left' | 'relmove_right' | 'home' | 'stop', degree: number) => Promise<void>;
  resetFactory: (withStorage?: boolean) => Promise<void>;
}

export interface DashboardMessageMonitor {
  addMessage: (topic: string, payload: unknown, timestamp?: string) => void;
  getTopics?: () => string[];
  getHistory?: <T = unknown>(topic: string) => MonitoredMessage<T>[];
}

export interface MockDashboardController {
  streams: DashboardStreamSet;
  streams$: Observable<DashboardStreamSet>;
  commands: DashboardCommandSet;
  loadFixture: (fixture: OrderFixtureName, options?: FixtureStreamOptions) => Promise<DashboardStreamSet>;
  loadTabFixture: (presetName: string, options?: FixtureStreamOptions) => Promise<DashboardStreamSet>;
  getCurrentFixture: () => OrderFixtureName;
  updateMqttClient?: (mqttClient?: MqttClientWrapper) => void;
  injectMessage?: (message: RawMqttMessage) => void; // Inject a message into the message stream
}

const FIXTURE_DEFAULT_INTERVAL = 25;
const resolveModuleFixture = (fixture: OrderFixtureName): ModuleFixtureName => {
  if (fixture === 'white_step3') {
    return 'white';
  }
  if (
    fixture === 'white' ||
    fixture === 'blue' ||
    fixture === 'red' ||
    fixture === 'mixed' ||
    fixture === 'storage' ||
    fixture === 'startup'
  ) {
    return fixture;
  }
  return 'default';
};

const resolveStockFixture = (fixture: OrderFixtureName): StockFixtureName => {
  if (fixture === 'startup') {
    return 'startup';
  }
  return 'default';
};

const resolveFlowFixture = (fixture: OrderFixtureName): FlowFixtureName => {
  if (fixture === 'startup') {
    return 'startup';
  }
  return 'default';
};

const resolveConfigFixture = (fixture: OrderFixtureName): ConfigFixtureName => {
  if (fixture === 'startup') {
    return 'startup';
  }
  return 'default';
};

const resolveSensorFixture = (fixture: OrderFixtureName): SensorFixtureName => {
  if (fixture === 'startup') {
    return 'startup';
  }
  return 'default';
};

interface OrdersAccumulator {
  active: Record<string, OrderActive>;
  completed: Record<string, OrderActive>;
}

const COMPLETION_STATES = new Set(['COMPLETED', 'FINISHED']);

const normalizeOrder = (order: OrderActive): OrderActive => {
  const normalizedState = (order.state ?? order.status ?? '').toUpperCase();
  return {
    ...order,
    state: normalizedState,
    status: order.status ?? order.state ?? normalizedState.toLowerCase(),
  };
};

const accumulateOrders = (acc: OrdersAccumulator, payload: OrderStreamPayload): OrdersAccumulator => {
  const { order } = payload;
  if (!order.orderId) {
    return acc;
  }

  const harmonized = normalizeOrder(order);
  const state = harmonized.state ?? '';

  const nextActive = { ...acc.active };
  const nextCompleted = { ...acc.completed };

  if (COMPLETION_STATES.has(state) || payload.topic.includes('/completed')) {
    nextCompleted[harmonized.orderId] = harmonized;
    delete nextActive[harmonized.orderId];
  } else {
    nextActive[harmonized.orderId] = harmonized;
    if (nextCompleted[harmonized.orderId]) {
      delete nextCompleted[harmonized.orderId];
    }
  }

  return {
    active: nextActive,
    completed: nextCompleted,
  };
};

const createStreamSet = (
  messages$: Subject<RawMqttMessage>,
  mqttClient?: MqttClientWrapper
): {
  streams: DashboardStreamSet;
  commands: DashboardCommandSet;
} => {
  const publish: GatewayPublishFn = async (topic, payload, options) => {
    if (mqttClient) {
      // Use real MQTT client for live/replay mode
      try {
        console.info('[mock-dashboard] Publishing to MQTT:', topic, payload, options);
        await mqttClient.publish(topic, payload, {
          qos: options?.qos ?? 0,
          retain: options?.retain ?? false,
        });
        console.info('[mock-dashboard] Published to MQTT successfully:', topic);
      } catch (error) {
        console.error('[mock-dashboard] Failed to publish to MQTT:', topic, error);
        throw error;
      }
    } else {
      // Mock mode - just log
      console.info('[mock-dashboard] publish (mock)', topic, payload, options);
    }
  };

  const gateway = createGateway(messages$.asObservable(), { publish });
  const business = createBusiness(gateway);

  const ordersState$ = gateway.orders$.pipe(
    scan(accumulateOrders, { active: {}, completed: {} } as OrdersAccumulator),
    startWith({ active: {}, completed: {} } as OrdersAccumulator),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orders$ = ordersState$.pipe(
    map((state) => Object.values(state.active)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const completedOrders$ = ordersState$.pipe(
    map((state) => Object.values(state.completed)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orderCounts$ = ordersState$.pipe(
    map((state) => {
      const counts = {
        running: 0,
        queued: 0,
        completed: Object.keys(state.completed).length,
      };

      Object.values(state.active).forEach((order) => {
        const stateValue = (order.state ?? '').toUpperCase();
        if (stateValue === 'RUNNING' || stateValue === 'IN_PROGRESS') {
          counts.running += 1;
        } else {
          counts.queued += 1;
        }
      });

      return counts;
    }),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  return {
    streams: {
      orders$,
      completedOrders$,
      orderCounts$,
      stockByPart$: business.stockByPart$,
      moduleStates$: business.moduleStates$,
      ftsStates$: business.ftsStates$,
      moduleOverview$: business.moduleOverview$,
      inventoryOverview$: business.inventoryOverview$,
      flows$: business.flows$,
      config$: business.config$,
      sensorOverview$: business.sensorOverview$,
      cameraFrames$: business.cameraFrames$,
    },
    commands: {
      calibrateModule: business.calibrateModule,
      setFtsCharge: business.setFtsCharge,
      dockFts: business.dockFts,
      sendCustomerOrder: business.sendCustomerOrder,
      requestRawMaterial: business.requestRawMaterial,
      moveCamera: business.moveCamera,
      resetFactory: business.resetFactory,
    },
  };
};

const REPLAY_TOPIC_MATCHERS: RegExp[] = [
  /^module\/v1\//,
  /^ccu\/pairing\/state$/,
  /^ccu\/state\//,
  /^fts\/v1\//,
  /^warehouse\/stock/,
];

const shouldReplayTopic = (topic: string): boolean => REPLAY_TOPIC_MATCHERS.some((matcher) => matcher.test(topic));

export const createMockDashboardController = (options?: {
  mqttClient?: MqttClientWrapper;
  messageMonitor?: DashboardMessageMonitor;
}): MockDashboardController => {
  let messageSubject = new Subject<RawMqttMessage>();
  let mqttClient = options?.mqttClient; // Store in closure (mutable)
  const messageMonitor = options?.messageMonitor; // Store in closure
  let bundle = createStreamSet(messageSubject, mqttClient);
  let messageMonitorSubscription: Subscription | undefined;
  
  // Helper function to setup MessageMonitor forwarding
  // This ensures messages from fixtures are forwarded to MessageMonitorService
  const setupMessageMonitorForwarding = () => {
    // Unsubscribe existing subscription if any
    if (messageMonitorSubscription) {
      messageMonitorSubscription.unsubscribe();
      messageMonitorSubscription = undefined;
    }
    
    // In mock mode (no MQTT client), forward fixture messages to MessageMonitor
    if (!mqttClient && messageMonitor) {
      console.log('[mock-dashboard] Setting up MessageMonitor forwarding for fixture messages');
      messageMonitorSubscription = messageSubject.subscribe((message: RawMqttMessage) => {
        try {
          let payload: unknown = message.payload;
          if (typeof payload === 'string') {
            try {
              payload = JSON.parse(payload);
            } catch {
              // Keep as string if not valid JSON
            }
          }
          messageMonitor.addMessage(message.topic, payload, message.timestamp);
        } catch (error) {
          console.error('[mock-dashboard] Failed to forward message to MessageMonitor:', error);
        }
      });
    }
  };
  
  // Initial setup of MessageMonitor forwarding
  setupMessageMonitorForwarding();
  const shouldReplayPersistedMessages = (): boolean =>
    Boolean(mqttClient && messageMonitor?.getTopics && messageMonitor.getHistory);

  const replayPersistedMessages = () => {
    if (!shouldReplayPersistedMessages()) {
      return;
    }
    try {
      const topics = messageMonitor!.getTopics!();
      topics.forEach((topic) => {
        if (!shouldReplayTopic(topic)) {
          return;
        }
        const history = messageMonitor!.getHistory!(topic);
        if (!history || history.length === 0) {
          return;
        }
        const lastMessage = history[history.length - 1];
        messageSubject.next({
          topic,
          payload: lastMessage.payload,
          timestamp: lastMessage.timestamp,
        });
      });
    } catch (error) {
      console.warn('[mock-dashboard] Failed to replay persisted messages', error);
    }
  };

  if (shouldReplayPersistedMessages()) {
    replayPersistedMessages();
  }

  let currentReplays: Subscription[] = [];
  let currentFixture: OrderFixtureName = 'startup';
  const streamsSubject = new BehaviorSubject<DashboardStreamSet>(bundle.streams);
  let mqttSubscription: Subscription | undefined;

  // If MQTT client is provided (live/replay mode), subscribe to its messages
  if (mqttClient) {
    console.log('[mock-dashboard] Using real MQTT client for live/replay mode');
    mqttSubscription = mqttClient.messages$.subscribe((mqttMsg: MqttMessage) => {
      // Convert MqttMessage to RawMqttMessage format
      const rawMessage: RawMqttMessage = {
        topic: mqttMsg.topic,
        payload: mqttMsg.payload,
        timestamp: mqttMsg.timestamp,
        qos: mqttMsg.options?.qos,
        retain: mqttMsg.options?.retain,
      };
      messageSubject.next(rawMessage);
    });
  }

  const unsubscribeReplays = () => {
    currentReplays.forEach((sub) => sub.unsubscribe());
    currentReplays = [];
    // Don't unsubscribe from MQTT client - it's managed by ConnectionService
  };

  const resetStreams = () => {
    unsubscribeReplays();
    // Only complete messageSubject if we're not using MQTT client (mock mode)
    if (!mqttClient) {
      messageSubject.complete();
      messageSubject = new Subject<RawMqttMessage>();
      // CRITICAL FIX: Reconnect MessageMonitor forwarding after creating new subject
      setupMessageMonitorForwarding();
    } else {
      // In live/replay mode, keep the same messageSubject and reconnect MQTT subscription
      messageSubject = new Subject<RawMqttMessage>();
      if (mqttSubscription) {
        mqttSubscription.unsubscribe();
      }
      mqttSubscription = mqttClient.messages$.subscribe((mqttMsg: MqttMessage) => {
        const rawMessage: RawMqttMessage = {
          topic: mqttMsg.topic,
          payload: mqttMsg.payload,
          timestamp: mqttMsg.timestamp,
          qos: mqttMsg.options?.qos,
          retain: mqttMsg.options?.retain,
        };
        messageSubject.next(rawMessage);
      });
    }
    bundle = createStreamSet(messageSubject, mqttClient);
    if (shouldReplayPersistedMessages()) {
      replayPersistedMessages();
    }
    streamsSubject.next(bundle.streams);
  };

  const loadFixture = async (
    fixture: OrderFixtureName,
    options?: FixtureStreamOptions
  ): Promise<DashboardStreamSet> => {
    unsubscribeReplays();
    resetStreams();

    const replay$ = createOrderFixtureStream(fixture, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      baseUrl: options?.baseUrl,
      loader: options?.loader,
      loop: options?.loop,
    });

    currentReplays.push(replay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const moduleFixtureName = resolveModuleFixture(fixture);
    const moduleReplay$ = createModulePairingFixtureStream(moduleFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(moduleReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const stockFixtureName = resolveStockFixture(fixture);
    const stockReplay$ = createStockFixtureStream(stockFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(stockReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const flowFixtureName = resolveFlowFixture(fixture);
    const flowReplay$ = createFlowFixtureStream(flowFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(flowReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const configFixtureName = resolveConfigFixture(fixture);
    const configReplay$ = createConfigFixtureStream(configFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(configReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    // Add DSP action fixtures
    const { createDspActionFixtureStream } = await import('@osf/testing-fixtures');
    const dspActionReplay$ = createDspActionFixtureStream({
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loop: options?.loop,
    });
    currentReplays.push(dspActionReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const sensorFixtureName = resolveSensorFixture(fixture);
    const sensorReplay$ = createSensorFixtureStream(sensorFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(sensorReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    currentFixture = fixture;
    streamsSubject.next(bundle.streams);
    return bundle.streams;
  };

  /**
   * Load tab-specific fixture preset
   * Allows independent fixture loading per tab with relevant topics
   */
  const loadTabFixture = async (
    presetName: string,
    options?: FixtureStreamOptions
  ): Promise<DashboardStreamSet> => {
    unsubscribeReplays();
    resetStreams();

    console.log(`[mock-dashboard] Loading tab fixture preset: ${presetName}`);

    // Use the tab-specific fixture preset stream
    const tabFixtureStream$ = createTabFixturePreset(presetName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      baseUrl: options?.baseUrl,
      loader: options?.loader,
      loop: options?.loop,
    });

    // Subscribe to the combined tab fixture stream
    currentReplays.push(
      tabFixtureStream$.subscribe((message: RawMqttMessage) => messageSubject.next(message))
    );

    // Update current fixture name for backwards compatibility
    // Map preset name to OrderFixtureName if possible
    const presetToFixture: Record<string, OrderFixtureName> = {
      startup: 'startup',
      'order-white': 'white',
      'order-blue': 'blue',
      'order-red': 'red',
      'order-mixed': 'mixed',
      'order-storage': 'storage',
      'track-trace': 'track-trace',
      'track-trace-production-bwr': 'track-trace-production-bwr',
      'order-production-bwr': 'production_bwr',
      'order-production-white': 'production_white',
      'order-storage-blue': 'storage_blue',
      'order-white-step3': 'white_step3',
    };
    currentFixture = presetToFixture[presetName] || 'startup';

    streamsSubject.next(bundle.streams);
    return bundle.streams;
  };

  // Update bundle when MQTT client changes (for live/replay mode)
  const updateMqttClient = (newMqttClient?: MqttClientWrapper) => {
    if (newMqttClient !== mqttClient) {
      mqttClient = newMqttClient;
      // Recreate bundle with new MQTT client
      bundle = createStreamSet(messageSubject, mqttClient);
      if (shouldReplayPersistedMessages()) {
        replayPersistedMessages();
      }
      // Update MQTT subscription if needed
      if (mqttSubscription) {
        mqttSubscription.unsubscribe();
      }
      if (mqttClient) {
        mqttSubscription = mqttClient.messages$.subscribe((mqttMsg: MqttMessage) => {
          const rawMessage: RawMqttMessage = {
            topic: mqttMsg.topic,
            payload: mqttMsg.payload,
            timestamp: mqttMsg.timestamp,
            qos: mqttMsg.options?.qos,
            retain: mqttMsg.options?.retain,
          };
          messageSubject.next(rawMessage);
        });
      }
    }
  };

  const injectMessage = (message: RawMqttMessage): void => {
    messageSubject.next(message);
  };

  return {
    get streams() {
      return bundle.streams;
    },
    get streams$() {
      return streamsSubject.asObservable();
    },
    get commands() {
      // Always return fresh bundle.commands to ensure we have the latest MQTT client
      return bundle.commands;
    },
    loadFixture,
    loadTabFixture, // New: tab-specific fixture loading
    getCurrentFixture() {
      return currentFixture;
    },
    updateMqttClient, // Expose method to update MQTT client
    injectMessage, // Expose method to inject messages into the stream
  };
};

let sharedController: MockDashboardController | null = null;
let mqttClientRef: MqttClientWrapper | undefined;
let messageMonitorRef: DashboardMessageMonitor | undefined;

export const getDashboardController = (
  mqttClient?: MqttClientWrapper,
  messageMonitor?: DashboardMessageMonitor
): MockDashboardController => {
  // Create controller once
  if (!sharedController) {
    mqttClientRef = mqttClient;
    messageMonitorRef = messageMonitor;
    sharedController = createMockDashboardController({ mqttClient, messageMonitor });
    return sharedController;
  }

  // Update MQTT client for existing controller without recreating streams
  if (mqttClient && mqttClient !== mqttClientRef) {
    mqttClientRef = mqttClient;
    if (sharedController.updateMqttClient) {
      sharedController.updateMqttClient(mqttClient);
    }
  }

  // MessageMonitor is only relevant in mock mode; if it changes recreate controller
  if (messageMonitor && messageMonitor !== messageMonitorRef) {
    messageMonitorRef = messageMonitor;
    sharedController = createMockDashboardController({ mqttClient: mqttClientRef, messageMonitor });
  }

  return sharedController;
};

