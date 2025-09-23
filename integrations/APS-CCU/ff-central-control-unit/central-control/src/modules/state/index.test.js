"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const module_1 = require("../../../../common/protocol/module");
const test_helpers_1 = require("../../test-helpers");
const index_1 = require("./index");
describe('Test production updates', () => {
    beforeEach(() => {
        (0, test_helpers_1.createMockMqttClient)();
        jest.useFakeTimers().setSystemTime(new Date('2023-02-010T10:20:19Z'));
    });
    afterEach(() => {
        index_1.getLog.length = 0;
        jest.clearAllMocks();
        jest.useRealTimers();
    });
    it('should add multiple entries to the log in the added order', async () => {
        const resultLog = [
            {
                type: 'ORDER',
                orderId: 'SOME_ORDER',
                level: index_1.LogLevel.INFO,
                timestamp: new Date('2023-02-01T09:09:09Z'),
            },
            {
                type: 'ORDER',
                orderId: 'SOME_ORDER2',
                level: index_1.LogLevel.INFO,
                timestamp: new Date('2023-02-09T09:09:09Z'),
            },
            {
                type: 'ORDER',
                orderId: 'SOME_ORDER3',
                level: index_1.LogLevel.INFO,
                timestamp: new Date('2023-01-01T09:09:09Z'),
            },
        ];
        expect(index_1.getLog.length).toBe(0);
        await (0, index_1.addLogEntry)(resultLog[0]);
        await (0, index_1.addLogEntry)(resultLog[1]);
        await (0, index_1.addLogEntry)(resultLog[2]);
        expect(index_1.getLog).toEqual(resultLog);
    });
    it('should add an Fts Log entry with the correct log level', async () => {
        const state = {
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
        const state2 = {
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
        const resultLog = [
            {
                type: 'FTS',
                serialNumber: state.serialNumber,
                timestamp: state.timestamp,
                orderId: state.orderId,
                level: index_1.LogLevel.ERROR,
                state: state,
            },
            {
                type: 'FTS',
                serialNumber: state2.serialNumber,
                timestamp: state2.timestamp,
                orderId: state2.orderId,
                level: index_1.LogLevel.WARNING,
                state: state2,
            },
        ];
        expect(index_1.getLog.length).toBe(0);
        await (0, index_1.addFtsLogEntry)(state);
        await (0, index_1.addFtsLogEntry)(state2);
        console.log(index_1.getLog);
        console.log(resultLog);
        expect(index_1.getLog).toStrictEqual(resultLog);
    });
    it('should add a Module Log entry with the correct log level', async () => {
        const state = {
            serialNumber: 'mocked',
            timestamp: new Date('2023-01-01T12:12:12.000Z'),
            paused: false,
            errors: [{ errorType: 'SAMPLE_ERROR', errorLevel: 'FATAL', timestamp: new Date('2023-01-01T12:12:12.000Z') }],
            orderId: '',
            orderUpdateId: 0,
            type: module_1.ModuleType.DRILL,
        };
        const state2 = {
            serialNumber: 'mocked',
            timestamp: new Date('2023-01-04T12:12:12.000Z'),
            paused: false,
            errors: [{ errorType: 'SAMPLE_WARN', errorLevel: 'WARNING', timestamp: new Date('2023-01-01T12:12:12.000Z') }],
            orderId: '',
            orderUpdateId: 0,
            type: module_1.ModuleType.DRILL,
        };
        const resultLog = [
            {
                type: 'MODULE',
                serialNumber: state.serialNumber,
                timestamp: state.timestamp,
                orderId: state.orderId,
                level: index_1.LogLevel.ERROR,
                state: state,
            },
            {
                type: 'MODULE',
                serialNumber: state2.serialNumber,
                timestamp: state2.timestamp,
                orderId: state2.orderId,
                level: index_1.LogLevel.WARNING,
                state: state2,
            },
        ];
        expect(index_1.getLog.length).toBe(0);
        await (0, index_1.addModuleLogEntry)(state);
        await (0, index_1.addModuleLogEntry)(state2);
        console.log(index_1.getLog);
        console.log(resultLog);
        expect(index_1.getLog).toStrictEqual(resultLog);
    });
});
