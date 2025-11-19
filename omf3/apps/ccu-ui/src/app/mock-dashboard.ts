import { createBusiness } from '@omf3/business';
import { createGateway, type RawMqttMessage, type OrderStreamPayload, type GatewayPublishFn } from '@omf3/gateway';
import type {
  FtsState,
  ModuleState,
  ModuleOverviewState,
  InventoryOverviewState,
  ProductionFlowMap,
  CcuConfigSnapshot,
  SensorOverviewState,
  CameraFrame,
} from '@omf3/entities';
import {
  createModulePairingFixtureStream,
  createOrderFixtureStream,
  createStockFixtureStream,
  createFlowFixtureStream,
  createConfigFixtureStream,
  createSensorFixtureStream,
  type FixtureStreamOptions,
  type ModuleFixtureName,
  type OrderFixtureName,
  type StockFixtureName,
  type FlowFixtureName,
  type ConfigFixtureName,
  type SensorFixtureName,
} from '@omf3/testing-fixtures';
import { BehaviorSubject, Subject, type Observable, Subscription, merge } from 'rxjs';
import { map, scan, shareReplay, startWith, filter } from 'rxjs/operators';
import type { OrderActive } from '@omf3/entities';
import type { MqttClientWrapper, MqttMessage } from '@omf3/mqtt-client';

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

export interface MockDashboardController {
  streams: DashboardStreamSet;
  streams$: Observable<DashboardStreamSet>;
  commands: DashboardCommandSet;
  loadFixture: (fixture: OrderFixtureName, options?: FixtureStreamOptions) => Promise<DashboardStreamSet>;
  getCurrentFixture: () => OrderFixtureName;
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
        await mqttClient.publish(topic, payload, {
          qos: options?.qos ?? 0,
          retain: options?.retain ?? false,
        });
        console.info('[mock-dashboard] Published to MQTT:', topic, payload);
      } catch (error) {
        console.error('[mock-dashboard] Failed to publish to MQTT:', error);
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

export const createMockDashboardController = (options?: {
  mqttClient?: MqttClientWrapper;
  messageMonitor?: { addMessage: (topic: string, payload: unknown, timestamp?: string) => void };
}): MockDashboardController => {
  let messageSubject = new Subject<RawMqttMessage>();
  const mqttClient = options?.mqttClient; // Store in closure
  const messageMonitor = options?.messageMonitor; // Store in closure
  let bundle = createStreamSet(messageSubject, mqttClient);
  
  // In mock mode (no MQTT client), forward fixture messages to MessageMonitor
  if (!mqttClient && messageMonitor) {
    messageSubject.subscribe((message: RawMqttMessage) => {
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

  return {
    get streams() {
      return bundle.streams;
    },
    get streams$() {
      return streamsSubject.asObservable();
    },
    get commands() {
      return bundle.commands;
    },
    loadFixture,
    getCurrentFixture() {
      return currentFixture;
    },
  };
};

let sharedController: MockDashboardController | null = null;
let mqttClientRef: MqttClientWrapper | undefined;
let messageMonitorRef: { addMessage: (topic: string, payload: unknown, timestamp?: string) => void } | undefined;

export const getDashboardController = (
  mqttClient?: MqttClientWrapper,
  messageMonitor?: { addMessage: (topic: string, payload: unknown, timestamp?: string) => void }
): MockDashboardController => {
  // If MQTT client changed or controller doesn't exist, recreate it
  if (!sharedController || (mqttClient && mqttClient !== mqttClientRef) || (messageMonitor && messageMonitor !== messageMonitorRef)) {
    mqttClientRef = mqttClient;
    messageMonitorRef = messageMonitor;
    sharedController = createMockDashboardController({ mqttClient, messageMonitor });
  }
  return sharedController;
};

