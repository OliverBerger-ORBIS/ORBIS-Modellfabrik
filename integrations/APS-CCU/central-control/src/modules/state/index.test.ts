import { FtsState } from '../../../../common/protocol/fts';
import { ModuleState, ModuleType } from '../../../../common/protocol/module';
import { createMockMqttClient } from '../../test-helpers';
import { LogEntry, LogLevel, addFtsLogEntry, addLogEntry, addModuleLogEntry, getLog } from './index';

describe('Test production updates', () => {
  beforeEach(() => {
    createMockMqttClient();
    jest.useFakeTimers().setSystemTime(new Date('2023-02-010T10:20:19Z'));
  });

  afterEach(() => {
    getLog.length = 0;
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('should add multiple entries to the log in the added order', async () => {
    const resultLog: LogEntry[] = [
      {
        type: 'ORDER',
        orderId: 'SOME_ORDER',
        level: LogLevel.INFO,
        timestamp: new Date('2023-02-01T09:09:09Z'),
      },
      {
        type: 'ORDER',
        orderId: 'SOME_ORDER2',
        level: LogLevel.INFO,
        timestamp: new Date('2023-02-09T09:09:09Z'),
      },
      {
        type: 'ORDER',
        orderId: 'SOME_ORDER3',
        level: LogLevel.INFO,
        timestamp: new Date('2023-01-01T09:09:09Z'),
      },
    ];

    expect(getLog.length).toBe(0);
    await addLogEntry(resultLog[0]);
    await addLogEntry(resultLog[1]);
    await addLogEntry(resultLog[2]);
    expect(getLog).toEqual(resultLog);
  });

  it('should add an Fts Log entry with the correct log level', async () => {
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date('2023-02-01T12:12:12.000Z'),
      paused: false,
      driving: false,
      errors: [{ errorType: 'SAMPLE_ERROR', errorLevel: 'FATAL', timestamp: new Date('2023-01-01T12:12:12.000Z') }],
      orderId: '',
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '',
      load: [],
      orderUpdateId: 0,
    };

    const state2: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date('2023-01-01T12:12:12.000Z'),
      paused: false,
      driving: false,
      errors: [{ errorType: 'SAMPLE_WARNING', errorLevel: 'WARNING', timestamp: new Date('2023-01-01T12:12:12.000Z') }],
      orderId: '',
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '',
      load: [],
      orderUpdateId: 0,
    };

    const resultLog: Array<LogEntry> = [
      {
        type: 'FTS',
        serialNumber: state.serialNumber,
        timestamp: state.timestamp,
        orderId: state.orderId,
        level: LogLevel.ERROR,
        state: state,
      },
      {
        type: 'FTS',
        serialNumber: state2.serialNumber,
        timestamp: state2.timestamp,
        orderId: state2.orderId,
        level: LogLevel.WARNING,
        state: state2,
      },
    ];

    expect(getLog.length).toBe(0);
    await addFtsLogEntry(state);
    await addFtsLogEntry(state2);

    console.log(getLog);
    console.log(resultLog);
    expect(getLog).toStrictEqual(resultLog);
  });

  it('should add a Module Log entry with the correct log level', async () => {
    const state: ModuleState = {
      serialNumber: 'mocked',
      timestamp: new Date('2023-01-01T12:12:12.000Z'),
      paused: false,
      errors: [{ errorType: 'SAMPLE_ERROR', errorLevel: 'FATAL', timestamp: new Date('2023-01-01T12:12:12.000Z') }],
      orderId: '',
      orderUpdateId: 0,
      type: ModuleType.DRILL,
    };
    const state2: ModuleState = {
      serialNumber: 'mocked',
      timestamp: new Date('2023-01-04T12:12:12.000Z'),
      paused: false,
      errors: [{ errorType: 'SAMPLE_WARN', errorLevel: 'WARNING', timestamp: new Date('2023-01-01T12:12:12.000Z') }],
      orderId: '',
      orderUpdateId: 0,
      type: ModuleType.DRILL,
    };

    const resultLog: Array<LogEntry> = [
      {
        type: 'MODULE',
        serialNumber: state.serialNumber,
        timestamp: state.timestamp,
        orderId: state.orderId,
        level: LogLevel.ERROR,
        state: state,
      },
      {
        type: 'MODULE',
        serialNumber: state2.serialNumber,
        timestamp: state2.timestamp,
        orderId: state2.orderId,
        level: LogLevel.WARNING,
        state: state2,
      },
    ];

    expect(getLog.length).toBe(0);
    await addModuleLogEntry(state);
    await addModuleLogEntry(state2);

    console.log(getLog);
    console.log(resultLog);
    expect(getLog).toStrictEqual(resultLog);
  });
});
