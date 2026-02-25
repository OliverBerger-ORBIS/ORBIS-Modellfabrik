import { combineLatest, merge, Observable } from 'rxjs';
import { map, scan, shareReplay, startWith } from 'rxjs/operators';

import type {
  FtsState,
  ModuleState,
  OrderActive,
  StockMessage,
  ModulePairingState,
  ModuleOverviewState,
  ModuleAvailabilityStatus,
  ModuleFactsheetSnapshot,
  StockSnapshot,
  InventoryOverviewState,
  InventorySlotState,
  StockWorkpiece,
  WorkpieceType,
  ProductionFlowMap,
  CcuConfigSnapshot,
  Bme680Snapshot,
  LdrSnapshot,
  SensorOverviewState,
  CameraFrame,
} from '@osf/entities';
import { OrderStreamPayload, type GatewayPublishFn } from '@osf/gateway';

const DEFAULT_WORKPIECE_TYPES: WorkpieceType[] = ['BLUE', 'WHITE', 'RED'];

export interface GatewayStreams {
  orders$: Observable<OrderStreamPayload>;
  stock$: Observable<StockMessage>;
  modules$: Observable<ModuleState>;
  fts$: Observable<FtsState>;
  pairing$: Observable<ModulePairingState>;
  moduleFactsheets$: Observable<ModuleFactsheetSnapshot>;
  stockSnapshots$: Observable<StockSnapshot>;
  flows$: Observable<ProductionFlowMap>;
  config$: Observable<CcuConfigSnapshot>;
  sensorBme680$: Observable<Bme680Snapshot>;
  sensorLdr$: Observable<LdrSnapshot>;
  cameraFrames$: Observable<CameraFrame>;
  publish: GatewayPublishFn;
}

export interface BusinessStreams {
  orders$: Observable<Record<string, OrderActive>>;
  completedOrders$: Observable<Record<string, OrderActive>>;
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

export interface BusinessCommands {
  calibrateModule: (serialNumber: string) => Promise<void>;
  setFtsCharge: (serialNumber: string, charge: boolean) => Promise<void>;
  dockFts: (serialNumber: string, nodeId?: string) => Promise<void>;
  sendCustomerOrder: (workpieceType: WorkpieceType) => Promise<void>;
  requestRawMaterial: (workpieceType: WorkpieceType) => Promise<void>;
  requestCorrelationInfo: (params: { ccuOrderId?: string; requestId?: string }) => Promise<void>;
  moveCamera: (command: 'relmove_up' | 'relmove_down' | 'relmove_left' | 'relmove_right' | 'home' | 'stop', degree: number) => Promise<void>;
  resetFactory: (withStorage?: boolean) => Promise<void>;
}

export type BusinessFacade = BusinessStreams & BusinessCommands;

const COMPLETION_STATES = new Set(['COMPLETED', 'FINISHED']);

interface OrdersAccumulator {
  active: Record<string, OrderActive>;
  completed: Record<string, OrderActive>;
}

const normalizeState = (order: OrderActive): string => (order.state ?? order.status ?? '').toUpperCase();

const harmonizeOrder = (order: OrderActive): OrderActive => ({
  ...order,
  state: normalizeState(order),
});

const formatTimestamp = (value?: string): string => {
  if (!value) {
    return 'N/A';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
};

const initializeModuleOverview = (): ModuleOverviewState => ({
  modules: {},
  transports: {},
});

const INVENTORY_LOCATIONS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];

const createEmptyInventory = (): Record<string, InventorySlotState> => {
  return INVENTORY_LOCATIONS.reduce<Record<string, InventorySlotState>>((acc, location) => {
    acc[location] = { location, workpiece: null };
    return acc;
  }, {});
};

const createCountRecord = (): Record<WorkpieceType, number> => {
  const counts: Record<string, number> = {};
  DEFAULT_WORKPIECE_TYPES.forEach((type) => {
    counts[type] = 0;
  });
  return counts as Record<WorkpieceType, number>;
};

const classifyAirQuality = (score?: number): string => {
  if (score == null || Number.isNaN(score)) {
    return 'Unknown';
  }
  if (score < 1) {
    return 'Excellent';
  }
  if (score < 2) {
    return 'Good';
  }
  if (score < 3) {
    return 'Moderate';
  }
  if (score < 4) {
    return 'Poor';
  }
  return 'Critical';
};

const buildSensorOverviewState = (
  bme680: Bme680Snapshot | null,
  ldr: LdrSnapshot | null
): SensorOverviewState => {
  const temperatureC = bme680?.t ?? undefined;
  const humidityPercent = bme680?.h ?? undefined;
  const pressureHpa = bme680?.p ?? undefined;
  const lightLux = ldr?.ldr ?? ldr?.br ?? undefined;
  const iaq = bme680?.iaq ?? undefined;
  const airQualityScore = bme680?.aq ?? undefined;
  const airQualityClassification = classifyAirQuality(airQualityScore);

  return {
    timestamp: bme680?.ts ?? ldr?.ts,
    temperatureC,
    humidityPercent,
    pressureHpa,
    lightLux,
    iaq,
    airQualityScore,
    airQualityClassification,
  };
};

const normalizeWorkpiece = (workpiece?: StockWorkpiece | null): StockWorkpiece | null => {
  if (!workpiece) {
    return null;
  }

  return {
    id: workpiece.id ?? undefined,
    type: workpiece.type ? (workpiece.type.toUpperCase() as WorkpieceType) : undefined,
    state: workpiece.state ? workpiece.state.toUpperCase() : undefined,
  };
};

const buildInventoryOverview = (snapshot: StockSnapshot | null | undefined): InventoryOverviewState => {
  const slots = createEmptyInventory();
  const availableCounts = createCountRecord();
  const reservedCounts = createCountRecord();

  if (snapshot && Array.isArray(snapshot.stockItems)) {
    snapshot.stockItems.forEach((item) => {
      const location = item.location?.toUpperCase();
      if (!location || !slots[location]) {
        return;
      }

      const normalized = normalizeWorkpiece(item.workpiece ?? null);
      slots[location] = {
        location,
        workpiece: normalized,
      };

      if (normalized?.type) {
        const workpieceType = normalized.type;
        const state = normalized.state?.toUpperCase();
        if (state === 'RAW') {
          availableCounts[workpieceType] = (availableCounts[workpieceType] ?? 0) + 1;
        } else if (state === 'RESERVED') {
          reservedCounts[workpieceType] = (reservedCounts[workpieceType] ?? 0) + 1;
        }
      }
    });
  }

  return {
    slots,
    availableCounts,
    reservedCounts,
    lastUpdated: snapshot?.ts ?? new Date().toISOString(),
  };
};

const applyPairingSnapshot = (state: ModuleOverviewState, snapshot: ModulePairingState): ModuleOverviewState => {
  const timestamp = snapshot.timestamp ?? new Date().toISOString();
  const nextModules = { ...state.modules };
  const nextTransports = { ...state.transports };

  snapshot.modules.forEach((module) => {
    const prev = nextModules[module.serialNumber];
    if (!module.serialNumber) {
      return;
    }

    nextModules[module.serialNumber] = {
      id: module.serialNumber,
      subType: module.subType ?? prev?.subType,
      connected: Boolean(module.connected),
      availability: (module.available ?? prev?.availability ?? 'Unknown') as ModuleAvailabilityStatus,
      hasCalibration: module.hasCalibration ?? prev?.hasCalibration ?? false,
      assigned: module.assigned ?? prev?.assigned ?? false,
      ip: module.ip ?? prev?.ip,
      version: module.version ?? prev?.version,
      pairedSince: module.pairedSince ?? prev?.pairedSince,
      lastSeen: module.lastSeen ?? prev?.lastSeen,
      configured: prev?.configured ?? false,
      factsheetTimestamp: prev?.factsheetTimestamp,
      messageCount: (prev?.messageCount ?? 0) + 1,
      lastUpdate: formatTimestamp(timestamp),
    };
  });

  snapshot.transports.forEach((transport) => {
    const prev = nextTransports[transport.serialNumber];
    if (!transport.serialNumber) {
      return;
    }

    nextTransports[transport.serialNumber] = {
      id: transport.serialNumber,
      connected: Boolean(transport.connected),
      availability: (transport.available ?? prev?.availability ?? 'Unknown') as ModuleAvailabilityStatus,
      ip: transport.ip ?? prev?.ip,
      version: transport.version ?? prev?.version,
      lastSeen: transport.lastSeen ?? prev?.lastSeen,
      charging: transport.charging ?? prev?.charging ?? false,
      batteryVoltage: transport.batteryVoltage ?? prev?.batteryVoltage,
      batteryPercentage: transport.batteryPercentage ?? prev?.batteryPercentage,
      lastNodeId: transport.lastNodeId ?? prev?.lastNodeId,
      lastModuleSerialNumber: transport.lastModuleSerialNumber ?? prev?.lastModuleSerialNumber,
      lastLoadPosition: transport.lastLoadPosition ?? prev?.lastLoadPosition,
      messageCount: (prev?.messageCount ?? 0) + 1,
      lastUpdate: formatTimestamp(timestamp),
    };
  });

  return {
    modules: nextModules,
    transports: nextTransports,
  };
};

const applyFactsheetSnapshot = (
  state: ModuleOverviewState,
  snapshot: ModuleFactsheetSnapshot
): ModuleOverviewState => {
  const serial = snapshot.serialNumber;
  if (!serial) {
    return state;
  }

  const nextModules = { ...state.modules };
  const prev = nextModules[serial] ?? {
    id: serial,
    connected: false,
    availability: 'Unknown' as ModuleAvailabilityStatus,
    hasCalibration: false,
    assigned: false,
    messageCount: 0,
    configured: false,
    lastUpdate: 'N/A',
  };

  nextModules[serial] = {
    ...prev,
    configured: true,
    factsheetTimestamp: formatTimestamp(snapshot.timestamp ?? new Date().toISOString()),
    messageCount: (prev.messageCount ?? 0) + 1,
    lastUpdate: formatTimestamp(snapshot.timestamp ?? prev.lastUpdate),
  };

  return {
    ...state,
    modules: nextModules,
  };
};

const accumulateOrders = (acc: OrdersAccumulator, payload: OrderStreamPayload): OrdersAccumulator => {
  const { order } = payload;
  if (!order.orderId) {
    return acc;
  }

  const harmonized = harmonizeOrder(order);
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

export const createBusiness = (gateway: GatewayStreams): BusinessStreams & BusinessCommands => {
  const publish = gateway.publish;
  const ordersState$ = gateway.orders$.pipe(
    scan(accumulateOrders, { active: {}, completed: {} } as OrdersAccumulator),
    startWith({ active: {}, completed: {} } as OrdersAccumulator),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orders$ = ordersState$.pipe(
    map((state) => state.active),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const completedOrders$ = ordersState$.pipe(
    map((state) => state.completed),
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
        const normalized = normalizeState(order);
        if (normalized === 'QUEUED' || normalized === 'PENDING' || normalized === '') {
          counts.queued += 1;
        } else if (['RUNNING', 'IN_PROGRESS'].includes(normalized)) {
          counts.running += 1;
        }
      });

      return counts;
    }),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const stockByPart$ = gateway.stock$.pipe(
    scan(
      (acc, msg) => {
        if (!msg.partId) {
          return acc;
        }

        const next = { ...acc };
        next[msg.partId] = (next[msg.partId] ?? 0) + (msg.amount ?? 0);
        return next;
      },
      {} as Record<string, number>
    ),
    startWith({} as Record<string, number>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const moduleStates$ = gateway.modules$.pipe(
    scan(
      (acc, module) => {
        if (!module.moduleId) {
          return acc;
        }

        return { ...acc, [module.moduleId]: module };
      },
      {} as Record<string, ModuleState>
    ),
    startWith({} as Record<string, ModuleState>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const ftsStates$ = gateway.fts$.pipe(
    scan(
      (acc, fts) => {
        const id = fts.ftsId ?? 'unknown';
        return { ...acc, [id]: fts };
      },
      {} as Record<string, FtsState>
    ),
    startWith({} as Record<string, FtsState>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const moduleOverview$ = merge(
    gateway.pairing$.pipe(
      map(
        (snapshot) =>
          (state: ModuleOverviewState): ModuleOverviewState =>
            applyPairingSnapshot(state, snapshot)
      )
    ),
    gateway.moduleFactsheets$.pipe(
      map(
        (factsheet) =>
          (state: ModuleOverviewState): ModuleOverviewState =>
            applyFactsheetSnapshot(state, factsheet)
      )
    )
  ).pipe(
    scan(
      (acc, reducer) => reducer(acc),
      initializeModuleOverview()
    ),
    startWith(initializeModuleOverview()),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const inventoryOverview$ = gateway.stockSnapshots$.pipe(
    map((snapshot) => buildInventoryOverview(snapshot)),
    startWith(buildInventoryOverview(null)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const sensorOverview$ = combineLatest([
    gateway.sensorBme680$.pipe(startWith(null)),
    gateway.sensorLdr$.pipe(startWith(null)),
  ]).pipe(
    map(([bme, ldr]) => buildSensorOverviewState(bme, ldr)),
    startWith(buildSensorOverviewState(null, null)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const cameraFrames$ = gateway.cameraFrames$.pipe(shareReplay({ bufferSize: 1, refCount: true }));

  const config$ = gateway.config$.pipe(shareReplay({ bufferSize: 1, refCount: true }));

  const calibrateModule: BusinessCommands['calibrateModule'] = async (serialNumber) => {
    if (!serialNumber) {
      return;
    }

    const payload = {
      timestamp: new Date().toISOString(),
      serialNumber,
      command: 'startCalibration',
    };

    await publish('ccu/set/calibration', payload, { qos: 1, retain: false });
  };

  const setFtsCharge: BusinessCommands['setFtsCharge'] = async (serialNumber, charge) => {
    if (!serialNumber) {
      return;
    }

    // Note: ccu/set/charge does NOT include timestamp in payload (based on session logs)
    const payload = {
      serialNumber,
      charge,
    };

    await publish('ccu/set/charge', payload, { qos: 1, retain: false });
  };

  const dockFts: BusinessCommands['dockFts'] = async (serialNumber, nodeId) => {
    if (!serialNumber) {
      return;
    }

    const targetNodeId = nodeId && nodeId !== 'UNKNOWN' ? nodeId : 'SVR4H73275';

    const payload = {
      timestamp: new Date().toISOString(),
      serialNumber,
      actions: [
        {
          actionType: 'findInitialDockPosition',
          actionId: `dock-${Date.now()}`,
          metadata: {
            nodeId: targetNodeId,
          },
        },
      ],
    };

    await publish(`fts/v1/ff/${serialNumber}/instantAction`, payload, { qos: 1, retain: false });
  };

  const generateRequestId = (): string =>
    `OSF-UI_${'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    })}`;

  const sendCustomerOrder: BusinessCommands['sendCustomerOrder'] = async (workpieceType) => {
    if (!workpieceType) {
      return;
    }

    const payload = {
      type: workpieceType,
      timestamp: new Date().toISOString(),
      orderType: 'PRODUCTION',
      requestId: generateRequestId(),
    };

    await publish('ccu/order/request', payload, { qos: 1, retain: false });
  };

  const requestCorrelationInfo: BusinessCommands['requestCorrelationInfo'] = async (params) => {
    const { ccuOrderId, requestId } = params ?? {};
    if (!ccuOrderId && !requestId) {
      return;
    }
    const payload: Record<string, string> = {
      timestamp: new Date().toISOString(),
    };
    if (ccuOrderId) {
      payload['ccuOrderId'] = ccuOrderId;
    }
    if (requestId) {
      payload['requestId'] = requestId;
    }
    await publish('dsp/correlation/request', payload, { qos: 1, retain: false });
  };

  const requestRawMaterial: BusinessCommands['requestRawMaterial'] = async (workpieceType) => {
    if (!workpieceType) {
      return;
    }

    const payload = {
      type: workpieceType,
      timestamp: new Date().toISOString(),
      orderType: 'RAW_MATERIAL',
      workpieceType,
    };

    await publish('omf/order/raw_material', payload, { qos: 1, retain: false });
  };

  const moveCamera: BusinessCommands['moveCamera'] = async (command, degree) => {
    // Format: ISO timestamp with milliseconds ending with Z
    // Based on session logs: "ts":"2025-11-10T16:48:45.975Z"
    // Based on examples: 'home' and 'stop' don't have 'degree' field
    const ts = new Date().toISOString();
    
    const payload: { ts: string; cmd: string; degree?: number } = {
      ts,
      cmd: command,
    };

    // Only include degree for movement commands (not for 'home' or 'stop')
    if (command !== 'home' && command !== 'stop') {
      payload.degree = degree;
    }

    await publish('/j1/txt/1/o/ptu', payload, { qos: 1, retain: false });
  };

  const resetFactory: BusinessCommands['resetFactory'] = async (withStorage = false) => {
    // Based on OMF2: omf2/ui/admin/generic_steering/factory_steering_subtab.py
    // Topic: ccu/set/reset
    // Payload: {"timestamp": datetime.now().isoformat(), "withStorage": False}
    // QoS: 1, Retain: False
    const payload = {
      timestamp: new Date().toISOString(),
      withStorage,
    };

    await publish('ccu/set/reset', payload, { qos: 1, retain: false });
  };

  return {
    orders$,
    completedOrders$,
    orderCounts$,
    stockByPart$,
    moduleStates$,
    ftsStates$,
    moduleOverview$,
    inventoryOverview$,
    flows$: gateway.flows$,
    config$,
    sensorOverview$,
    cameraFrames$,
    calibrateModule,
    setFtsCharge,
    dockFts,
    sendCustomerOrder,
    requestCorrelationInfo,
    requestRawMaterial,
    moveCamera,
    resetFactory,
  };
};
