import { CcuTopic, OrderResponse } from '../../../../common/protocol';
import { FtsState } from '../../../../common/protocol/fts';
import { ModuleState } from '../../../../common/protocol/module';
import { VdaError } from '../../../../common/protocol/vda';
import config from '../../config';
import { getMqttClient } from '../../mqtt/mqtt';

export enum LogLevel {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
}

type BaseLogEntry = {
  type: string;
  level: LogLevel;
  timestamp: Date;
  orderId: string;
};

export type OrderLogEntry = BaseLogEntry & {
  type: 'ORDER';
};

export type FtsLogEntry = BaseLogEntry & {
  type: 'FTS';
  serialNumber: string;
  state: FtsState;
};

export type ModuleLogEntry = BaseLogEntry & {
  type: 'MODULE';
  serialNumber: string;
  state: ModuleState;
};

export type LogEntry = OrderLogEntry | FtsLogEntry | ModuleLogEntry;

const log = new Array<LogEntry>();

/**
 * Returns the most critical error level of a list of errors.
 *
 * VdaErrors are either fatal errors or warnings.
 * Having at least one fatal error results in an `ERROR` log level
 * If we have any non-fatal errors, those must of level `WARNING`.
 * Having no errors results in the `INFO` level.
 */
export const getVdaErrorsLogLevel = (errors: VdaError[] | undefined): LogLevel => {
  if (errors?.find(e => e['errorLevel'] === 'FATAL')) {
    return LogLevel.ERROR;
  } else if (errors?.length) {
    return LogLevel.WARNING;
  } else {
    return LogLevel.INFO;
  }
};

export const addLogEntry = async (entry: LogEntry) => {
  log.push(entry);
  if (config.mqtt.debug) {
    await getMqttClient().publish(CcuTopic.LOG, JSON.stringify(log), { qos: 1, retain: true });
  } else {
    console.log('MQTT debug is disabled, not publishing log entry');
  }
};

export const addOrderLogEntry = async (order: OrderResponse) =>
  await addLogEntry({
    type: 'ORDER',
    timestamp: order.timestamp,
    orderId: order.orderId,
    level: LogLevel.INFO,
  });

export const addFtsLogEntry = async (state: FtsState) =>
  await addLogEntry({
    type: 'FTS',
    serialNumber: state.serialNumber,
    timestamp: state.timestamp,
    orderId: state.orderId,
    level: getVdaErrorsLogLevel(state.errors),
    state: state,
  });

export const addModuleLogEntry = async (state: ModuleState) =>
  await addLogEntry({
    type: 'MODULE',
    serialNumber: state.serialNumber,
    timestamp: state.timestamp,
    orderId: state.orderId,
    level: getVdaErrorsLogLevel(state.errors),
    state: state,
  });

export const getLog = log;
