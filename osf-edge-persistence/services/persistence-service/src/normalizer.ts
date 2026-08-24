import { ServiceConfig } from './config';
import {
  NormalizedMessage,
  ProductionOrderRow,
  ProductionStepRow,
  SensorSnapshotRow,
  ShopfloorEventRow,
  WorkpieceRow,
} from './types';
import {
  SensorPolicyState,
  effectiveSensorIntervalSeconds,
  resolveSensorReason,
  shouldPersistReason,
  updateActiveOrdersFromPayload,
} from './sensorPolicy';
import { collectLoadNfcIds, resolveWorkpieceId, resolveWorkpieceType } from './nfc';
import { asDate, extractPayload, pickString, stableHash, toRecord } from './utils';

interface NormalizeOptions {
  config: ServiceConfig;
  topic: string;
  payloadText: string;
  qos: number;
  retain: boolean;
  receivedAt: Date;
  sensorPolicyState: SensorPolicyState;
}

function eventSourceFromTopic(topic: string): string {
  if (topic.startsWith('ccu/')) return 'ccu';
  if (topic.startsWith('module/v1/ff/')) return 'module';
  if (topic.startsWith('fts/v1/ff/')) return 'fts';
  if (topic.startsWith('/j1/txt/')) return 'txt';
  if (topic.startsWith('osf/arduino/')) return 'arduino';
  if (topic === 'osf/workpiece/intake') return 'osf';
  return 'unknown';
}

function workpieceRowFromId(
  workpieceId: string | undefined,
  type: string | undefined,
  ts: Date,
  location?: string,
  state?: string
): WorkpieceRow | undefined {
  if (!workpieceId) {
    return undefined;
  }
  return {
    workpieceId,
    type,
    currentState: state,
    lastLocation: location,
    firstSeenAt: ts,
    lastSeenAt: ts,
  };
}

function parseWorkpieceIntake(
  payload: Record<string, unknown>,
  topic: string,
  receivedAt: Date
): { events: ShopfloorEventRow[]; workpieces: WorkpieceRow[] } {
  const nfc = resolveWorkpieceId(payload);
  if (!nfc) {
    return { events: [], workpieces: [] };
  }
  const workpieceType = resolveWorkpieceType(payload);
  const ts = asDate(payload.timestamp) ?? receivedAt;
  const orderId = pickString(payload, 'orderId');
  const event: ShopfloorEventRow = {
    ts,
    dedupKey: stableHash(['workpiece-intake', nfc, ts.toISOString(), orderId ?? '']),
    eventType: 'WORKPIECE_INTAKE',
    topic,
    source: 'osf',
    orderId,
    workpieceId: nfc,
    workpieceType,
    action: 'intake',
    actionState: 'FINISHED',
    payload,
  };
  const workpiece = workpieceRowFromId(nfc, workpieceType, ts, 'DPS', 'INTAKE');
  return { events: [event], workpieces: workpiece ? [workpiece] : [] };
}

function moduleFromTopic(topic: string): { moduleType?: string; moduleSerial?: string } {
  if (topic.startsWith('module/v1/ff/')) {
    const parts = topic.split('/');
    const serial = parts[4] === 'NodeRed' ? parts[5] : parts[3];
    return { moduleSerial: serial };
  }
  if (topic.startsWith('fts/v1/ff/')) {
    const parts = topic.split('/');
    return { moduleType: 'FTS', moduleSerial: parts[3] };
  }
  return {};
}

function resolveActionCommand(payload: Record<string, unknown>): string | undefined {
  const actionState = toRecord(payload.actionState);
  const action = toRecord(payload.action);
  return pickString(actionState, 'command') ?? pickString(action, 'command') ?? pickString(payload, 'command');
}

function parseOrderCompleted(payload: unknown, topic: string, receivedAt: Date): {
  orders: ProductionOrderRow[];
  steps: ProductionStepRow[];
  events: ShopfloorEventRow[];
  workpieces: WorkpieceRow[];
} {
  const ordersInput = Array.isArray(payload) ? payload : [payload];
  const orders: ProductionOrderRow[] = [];
  const steps: ProductionStepRow[] = [];
  const events: ShopfloorEventRow[] = [];
  const workpieces: WorkpieceRow[] = [];

  for (const item of ordersInput) {
    const row = toRecord(item);
    const orderId = pickString(row, 'orderId');
    if (!orderId) {
      continue;
    }

    const order: ProductionOrderRow = {
      orderId,
      orderType: pickString(row, 'orderType'),
      workpieceId: pickString(row, 'workpieceId'),
      workpieceType: pickString(row, 'type', 'workpieceType'),
      state: pickString(row, 'state'),
      receivedAt,
      startedAt: asDate(row.startedAt),
      stoppedAt: asDate(row.stoppedAt),
    };
    orders.push(order);

    const eventTs = order.stoppedAt ?? receivedAt;
    const eventPayload = row;
    events.push({
      ts: eventTs,
      dedupKey: stableHash(['order-completed', orderId, eventTs.toISOString()]),
      eventType: 'ORDER_COMPLETED',
      topic,
      source: 'ccu',
      orderId,
      workpieceId: order.workpieceId,
      workpieceType: order.workpieceType,
      action: 'completed',
      actionState: order.state,
      payload: eventPayload,
    });

    if (order.workpieceId) {
      workpieces.push({
        workpieceId: order.workpieceId,
        type: order.workpieceType,
        currentState: order.state,
        lastLocation: pickString(row, 'target', 'location'),
        firstSeenAt: order.startedAt ?? receivedAt,
        lastSeenAt: order.stoppedAt ?? receivedAt,
      });
    }

    const productionSteps = Array.isArray(row.productionSteps) ? row.productionSteps : [];
    for (const stepValue of productionSteps) {
      const step = toRecord(stepValue);
      const stoppedAt = asDate(step.stoppedAt) ?? receivedAt;
      const stepRow: ProductionStepRow = {
        dedupKey: stableHash(['production-step', orderId, step.id, step.stoppedAt, step.startedAt]),
        orderId,
        stepId: pickString(step, 'id'),
        stepType: pickString(step, 'type'),
        moduleType: pickString(step, 'moduleType'),
        moduleSerial: pickString(step, 'serialNumber'),
        command: pickString(step, 'command'),
        state: pickString(step, 'state'),
        source: pickString(step, 'source'),
        target: pickString(step, 'target'),
        startedAt: asDate(step.startedAt),
        stoppedAt,
        payload: step,
      };
      steps.push(stepRow);

      events.push({
        ts: stoppedAt,
        dedupKey: stableHash(['step-event', orderId, stepRow.stepId, stoppedAt.toISOString()]),
        eventType: 'PRODUCTION_STEP',
        topic,
        source: 'ccu',
        moduleType: stepRow.moduleType,
        moduleSerial: stepRow.moduleSerial,
        orderId,
        workpieceId: order.workpieceId,
        workpieceType: order.workpieceType,
        action: stepRow.stepType,
        actionState: stepRow.state,
        payload: step,
      });
    }
  }

  return { orders, steps, events, workpieces };
}

function parseSensorRows(
  topic: string,
  payload: Record<string, unknown>,
  receivedAt: Date,
  config: ServiceConfig,
  sensorPolicyState: SensorPolicyState
): SensorSnapshotRow[] {
  const rows: SensorSnapshotRow[] = [];
  const ts = asDate(payload.timestamp) ?? asDate(payload.ts) ?? receivedAt;
  const topicParts = topic.split('/');
  let source: SensorSnapshotRow['source'] = 'txt';
  let stationId = 'txt-station-1';
  let sensorType = topic.endsWith('/bme680') ? 'bme680' : topic.endsWith('/ldr') ? 'ldr' : 'unknown';

  // DR-18 canonical pattern: osf/arduino/<sensorType>/<deviceId>/<action>
  if (topic.startsWith('osf/arduino/')) {
    source = 'arduino';
    sensorType = topicParts[2] ?? 'unknown';
    stationId = topicParts[3] ?? 'arduino-station';
  }
  // Compatibility pattern: osf/<source>/sensor/<stationId>[/<metricHint>]
  else if (topic.startsWith('osf/') && topicParts[2] === 'sensor') {
    source = topicParts[1] === 'arduino' ? 'arduino' : 'module';
    stationId = topicParts[3] ?? `${topicParts[1] ?? 'osf'}-sensor`;
    sensorType = topicParts[4] ?? 'generic';
  }

  const metricMap: Array<{ key: string; unit?: string }> = [
    { key: 'temperature', unit: 'C' },
    { key: 'humidity', unit: '%' },
    { key: 'pressure', unit: 'hPa' },
    { key: 'iaq' },
    { key: 'brightness' },
    { key: 'gasResistance', unit: 'ohm' },
    { key: 'gasLevel' },
    { key: 'magnitude' },
    { key: 'impulseCount' },
    { key: 'vibrationDetected' },
    { key: 'vibrationLevel' },
    { key: 'flameDetected' },
    { key: 'rawValue' }
  ];

  for (const metric of metricMap) {
    const value = payload[metric.key];
    const numericValue = typeof value === 'number' && Number.isFinite(value) ? value : undefined;
    const textValue = typeof value === 'string' ? value : typeof value === 'boolean' ? String(value) : undefined;
    if (numericValue === undefined && textValue === undefined) {
      continue;
    }

    const metricKey = `${source}:${stationId}:${sensorType}:${metric.key}`;
    const intervalSeconds = effectiveSensorIntervalSeconds(
      config.runtime.sensorIntervalSeconds,
      config.runtime.sensorIdleIntervalSeconds,
      sensorPolicyState
    );
    const reason = resolveSensorReason(payload, metricKey, ts, intervalSeconds, sensorPolicyState);
    const hasExplicitReason =
      payload.reason === 'EVENT' || payload.reason === 'THRESHOLD' || payload.reason === 'INTERVAL';
    if (!hasExplicitReason && !shouldPersistReason(reason, ts, metricKey, intervalSeconds, sensorPolicyState)) {
      continue;
    }

    rows.push({
      ts,
      source,
      stationId,
      sensorType,
      metricName: metric.key,
      valueNumeric: numericValue,
      valueText: textValue,
      unit: metric.unit ?? pickString(payload, `${metric.key}Unit`, 'unit'),
      reason,
      orderId: pickString(payload, 'orderId'),
      workpieceId: pickString(payload, 'workpieceId'),
      payload,
      dedupKey: stableHash([topic, ts.toISOString(), metric.key, numericValue, textValue, reason]),
    });
  }

  return rows;
}

export function normalizeMessage({
  config,
  topic,
  payloadText,
  qos,
  retain,
  receivedAt,
  sensorPolicyState,
}: NormalizeOptions): NormalizedMessage | undefined {
  if (!config.runtime.enableCameraTopic && topic === '/j1/txt/1/i/cam') {
    return undefined;
  }

  const payload = extractPayload(payloadText);
  const payloadRecord = toRecord(payload);
  const baseEventTs = asDate(payloadRecord.timestamp) ?? asDate(payloadRecord.ts) ?? receivedAt;
  const moduleContext = moduleFromTopic(topic);

  const normalized: NormalizedMessage = {
    raw: config.runtime.enableRawMessages
      ? {
          receivedAt,
          topic,
          qos,
          retain,
          payloadJson: payload,
          payloadText,
          persistedReason: 'RAW_CAPTURE',
          payloadHash: stableHash(payloadText),
          dedupKey: stableHash([topic, receivedAt.toISOString(), payloadText]),
        }
      : undefined,
    shopfloorEvents: [],
    productionOrders: [],
    productionSteps: [],
    workpieces: [],
    sensorSnapshots: [],
  };

  if (topic === 'osf/workpiece/intake') {
    const intake = parseWorkpieceIntake(payloadRecord, topic, receivedAt);
    normalized.shopfloorEvents.push(...intake.events);
    normalized.workpieces.push(...intake.workpieces);
    return normalized;
  }

  if (topic === 'ccu/order/request' || topic === 'ccu/order/response') {
    const isRequest = topic === 'ccu/order/request';
    const orderId = pickString(payloadRecord, 'orderId');
    const workpieceId = resolveWorkpieceId(payloadRecord) ?? pickString(payloadRecord, 'workpieceId');
    const workpieceType = resolveWorkpieceType(payloadRecord);
    const orderType = pickString(payloadRecord, 'orderType');
    normalized.shopfloorEvents.push({
      ts: baseEventTs,
      dedupKey: stableHash([topic, baseEventTs.toISOString(), payload, workpieceId ?? '']),
      eventType: isRequest ? 'ORDER_REQUEST' : 'ORDER_RESPONSE',
      topic,
      source: 'ccu',
      orderId,
      workpieceId,
      workpieceType,
      action: orderType ?? (isRequest ? 'REQUEST' : 'RESPONSE'),
      actionState: isRequest ? 'REQUESTED' : 'RESPONDED',
      payload: payloadRecord,
    });
    const wp = workpieceRowFromId(workpieceId, workpieceType, baseEventTs, orderType, isRequest ? 'REQUESTED' : 'RESPONDED');
    if (wp) {
      normalized.workpieces.push(wp);
    }
    return normalized;
  }

  if (topic === 'ccu/order/completed') {
    const completed = parseOrderCompleted(payload, topic, receivedAt);
    normalized.productionOrders.push(...completed.orders);
    normalized.productionSteps.push(...completed.steps);
    normalized.shopfloorEvents.push(...completed.events);
    normalized.workpieces.push(...completed.workpieces);
    return normalized;
  }

  if (topic === 'ccu/order/active') {
    updateActiveOrdersFromPayload(payload, sensorPolicyState);
    const activeOrders = Array.isArray(payload) ? payload : [payload];
    for (const orderItem of activeOrders) {
      const row = toRecord(orderItem);
      const orderId = pickString(row, 'orderId');
      if (!orderId) {
        continue;
      }
      const workpieceId = pickString(row, 'workpieceId');
      const workpieceType = pickString(row, 'type', 'workpieceType');
      normalized.productionOrders.push({
        orderId,
        orderType: pickString(row, 'orderType'),
        workpieceId,
        workpieceType,
        state: pickString(row, 'state'),
        receivedAt,
        startedAt: asDate(row.startedAt),
      });
      const wp = workpieceRowFromId(
        workpieceId,
        workpieceType,
        asDate(row.startedAt) ?? receivedAt,
        pickString(row, 'target', 'location'),
        pickString(row, 'state')
      );
      if (wp) {
        normalized.workpieces.push(wp);
      }
    }
  }

  if (topic === '/j1/txt/1/i/bme680' || topic === '/j1/txt/1/i/ldr' || topic.startsWith('osf/arduino/')) {
    normalized.sensorSnapshots.push(
      ...parseSensorRows(topic, payloadRecord, receivedAt, config, sensorPolicyState)
    );
  }

  if (
    topic.startsWith('ccu/state/') ||
    topic.startsWith('ccu/pairing/state') ||
    topic.startsWith('module/v1/ff/') ||
    topic.startsWith('fts/v1/ff/')
  ) {
    const action = toRecord(payloadRecord.actionState);
    const actionCommand = resolveActionCommand(payloadRecord);
    const actionStateValue =
      pickString(action, 'state') ??
      (typeof payloadRecord.actionState === 'string' ? payloadRecord.actionState : undefined) ??
      pickString(payloadRecord, 'state');
    const orderId = pickString(payloadRecord, 'orderId');
    const workpieceType = resolveWorkpieceType(payloadRecord);
    const eventType = actionCommand?.toUpperCase() ?? topic.split('/').slice(-1)[0]?.toUpperCase() ?? 'STATE';
    const source = eventSourceFromTopic(topic);
    const moduleType = pickString(payloadRecord, 'moduleType', 'type') ?? moduleContext.moduleType;
    const moduleSerial = pickString(payloadRecord, 'serialNumber') ?? moduleContext.moduleSerial;

    const ftsLoadIds = source === 'fts' ? collectLoadNfcIds(payloadRecord) : [];
    const workpieceIds =
      ftsLoadIds.length > 1 ? ftsLoadIds : [resolveWorkpieceId(payloadRecord) ?? pickString(payloadRecord, 'workpieceId')];

    for (const workpieceId of workpieceIds) {
      normalized.shopfloorEvents.push({
        ts: baseEventTs,
        dedupKey: stableHash([topic, baseEventTs.toISOString(), payload, workpieceId ?? '']),
        eventType,
        topic,
        source,
        moduleType,
        moduleSerial,
        orderId,
        workpieceId,
        workpieceType,
        action: actionCommand,
        actionState: actionStateValue,
        payload: payloadRecord,
      });
      const wp = workpieceRowFromId(workpieceId, workpieceType, baseEventTs, moduleType ?? moduleSerial, actionStateValue);
      if (wp) {
        normalized.workpieces.push(wp);
      }
    }
  }

  if (normalized.sensorSnapshots.length === 0 && normalized.shopfloorEvents.length === 0 && normalized.productionOrders.length === 0) {
    return normalized.raw ? normalized : undefined;
  }
  return normalized;
}
