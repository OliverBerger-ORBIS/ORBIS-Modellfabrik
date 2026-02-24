"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const _1 = require(".");
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const current_errors_service_1 = __importDefault(require("../current-errors/current-errors.service"));
describe('Pairing Module', () => {
    describe('calcStatusLEDFromPairingState', () => {
        it("should return green=true when there's only the dps", () => {
            const testPairing = {
                modules: [
                    {
                        serialNumber: '4711-567',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.DPS,
                        available: ccu_1.AvailableState.READY,
                    },
                ],
                transports: [],
            };
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, '4711-567');
            const expected = { green: true, red: false, yellow: false };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        it("should return yellow=true when there's no error and a module is busy", () => {
            const testPairing = {
                modules: [
                    {
                        serialNumber: '4711-567',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.DPS,
                        available: ccu_1.AvailableState.READY,
                    },
                    {
                        serialNumber: '4711-123',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.HBW,
                        available: ccu_1.AvailableState.BUSY,
                    },
                ],
                transports: [
                    {
                        serialNumber: '4711-789',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.FTS,
                        available: ccu_1.AvailableState.READY,
                    },
                ],
            };
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, '4711-123');
            const expected = { green: false, red: false, yellow: true };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        it("should return yellow=true when there's no error and a fts is busy", () => {
            const testPairing = {
                modules: [
                    {
                        serialNumber: '4711-456',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.DPS,
                        available: ccu_1.AvailableState.READY,
                    },
                    {
                        serialNumber: '4711-123',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.HBW,
                        available: ccu_1.AvailableState.READY,
                    },
                ],
                transports: [
                    {
                        serialNumber: '4711-789',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.FTS,
                        available: ccu_1.AvailableState.BUSY,
                    },
                ],
            };
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, '4711-567');
            const expected = { green: false, red: false, yellow: true };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        it("should return red=true when there's an error and a module is blocked", () => {
            const testPairing = {
                modules: [
                    {
                        serialNumber: '4711-567',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.DPS,
                        available: ccu_1.AvailableState.READY,
                    },
                    {
                        serialNumber: '4711-123',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.HBW,
                        available: ccu_1.AvailableState.BLOCKED,
                    },
                ],
                transports: [],
            };
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([
                {
                    serialNumber: '4711-123',
                    errors: [{ errorLevel: 'FATAL', errorType: 'ERROR', timestamp: new Date() }],
                },
            ]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, '4711-123');
            const expected = { green: false, red: true, yellow: false };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        it("should return red=true when there's no error and a fts is blocked", () => {
            const testPairing = {
                modules: [
                    {
                        serialNumber: '4711-456',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.DPS,
                        available: ccu_1.AvailableState.READY,
                    },
                    {
                        serialNumber: '4711-123',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.MODULE,
                        subType: module_1.ModuleType.HBW,
                        available: ccu_1.AvailableState.READY,
                    },
                ],
                transports: [
                    {
                        serialNumber: '4711-789',
                        pairedSince: new Date(),
                        type: ccu_1.DeviceType.FTS,
                        available: ccu_1.AvailableState.BLOCKED,
                    },
                ],
            };
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([
                {
                    serialNumber: '4711-789',
                    errors: [{ errorLevel: 'FATAL', errorType: 'ERROR', timestamp: new Date() }],
                },
            ]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, '4711-789');
            const expected = { green: false, red: true, yellow: false };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        function getTestPairingState() {
            return {
                modules: [
                    {
                        serialNumber: 'SVR1E94026',
                        type: 'MODULE',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        subType: module_1.ModuleType.HBW,
                        pairedSince: new Date('2023-11-03T10:54:34.390Z'),
                        assigned: true,
                        version: '1.0.0',
                        lastSeen: new Date('2023-11-03T14:34:15.815Z'),
                        hasCalibration: true,
                    },
                    {
                        serialNumber: 'SVR3QG1902',
                        type: 'MODULE',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        subType: module_1.ModuleType.DPS,
                        pairedSince: new Date('2023-11-03T10:54:34.391Z'),
                        assigned: false,
                        version: '1.0.0',
                        lastSeen: new Date('2023-11-03T14:34:15.916Z'),
                        hasCalibration: true,
                    },
                    {
                        serialNumber: 'SVR1E95079',
                        type: 'MODULE',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        subType: module_1.ModuleType.DRILL,
                        productionDuration: 5,
                        pairedSince: new Date('2023-11-03T10:54:34.391Z'),
                        assigned: false,
                        version: '1.0.0',
                        lastSeen: new Date('2023-11-03T14:34:10.477Z'),
                        hasCalibration: false,
                    },
                    {
                        serialNumber: 'SVR1D30145',
                        type: 'MODULE',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        subType: module_1.ModuleType.MILL,
                        productionDuration: 5,
                        pairedSince: new Date('2023-11-03T10:54:34.391Z'),
                        assigned: false,
                        version: '1.0.0',
                        lastSeen: new Date('2023-11-03T14:34:10.353Z'),
                        hasCalibration: false,
                    },
                    {
                        serialNumber: 'SVR1D28511',
                        type: 'MODULE',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        subType: module_1.ModuleType.AIQS,
                        pairedSince: new Date('2023-11-03T10:54:34.391Z'),
                        assigned: false,
                        ip: '',
                        version: '1.0.0',
                        lastSeen: new Date('2023-11-03T14:34:15.590Z'),
                        hasCalibration: true,
                        calibrating: false,
                    },
                    {
                        serialNumber: 'CHRG0',
                        type: 'MODULE',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        subType: module_1.ModuleType.CHRG,
                        pairedSince: new Date('2023-11-03T12:50:41.678Z'),
                        assigned: false,
                    },
                ],
                transports: [
                    {
                        serialNumber: '4gcx',
                        type: 'FTS',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        ip: '-1',
                        version: '0.2.0+git372f4be',
                        lastSeen: new Date('2023-11-03T13:11:02.305Z'),
                        charging: false,
                        batteryVoltage: 8.7,
                        batteryPercentage: 35,
                        lastNodeId: 'UNKNOWN',
                        lastModuleSerialNumber: 'UNKNOWN',
                        lastLoadPosition: '2',
                    },
                    {
                        serialNumber: 'BCix',
                        type: 'FTS',
                        connected: true,
                        available: ccu_1.AvailableState.READY,
                        ip: '-1',
                        version: '0.2.0+git372f4be',
                        lastSeen: new Date('2023-11-03T13:15:39.672Z'),
                        charging: false,
                        batteryVoltage: 8.7,
                        batteryPercentage: 35,
                        lastNodeId: 'SVR3QG1902',
                        pairedSince: new Date('2023-11-03T13:18:39.009Z'),
                        lastModuleSerialNumber: 'SVR3QG1902',
                        lastLoadPosition: '2',
                    },
                ],
            };
        }
        it('should evaluate driving FTS to yellow', () => {
            const testPairing = getTestPairingState();
            testPairing.transports[1].available = ccu_1.AvailableState.BUSY;
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, 'SVR3QG1902');
            const expected = { green: false, red: false, yellow: true };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        it('should evaluate blocked charging FTS to yellow', () => {
            const testPairing = getTestPairingState();
            testPairing.transports[1].available = ccu_1.AvailableState.BLOCKED;
            testPairing.transports[1].charging = true;
            testPairing.transports[1].lastNodeId = 'CHRG0';
            testPairing.transports[1].lastModuleSerialNumber = 'CHRG0';
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, 'SVR3QG1902');
            const expected = { green: false, red: false, yellow: true };
            expect(result.actions[0].metadata).toEqual(expected);
        });
        it('should evaluate blocked not charging FTS with errors to red', () => {
            const testPairing = getTestPairingState();
            testPairing.transports[1].available = ccu_1.AvailableState.BLOCKED;
            testPairing.transports[1].charging = false;
            testPairing.transports[1].lastNodeId = 'CHRG0';
            testPairing.transports[1].lastModuleSerialNumber = 'CHRG0';
            jest.spyOn(current_errors_service_1.default.getInstance(), 'getAllCurrentErrors').mockReturnValue([
                {
                    serialNumber: testPairing.transports[1].serialNumber,
                    errors: [{ errorLevel: 'FATAL', errorType: 'ERROR', timestamp: new Date() }],
                },
            ]);
            const result = (0, _1.calcStatusLEDFromPairingState)(testPairing, 'SVR3QG1902');
            const expected = { green: false, red: true, yellow: false };
            expect(result.actions[0].metadata).toEqual(expected);
        });
    });
});
