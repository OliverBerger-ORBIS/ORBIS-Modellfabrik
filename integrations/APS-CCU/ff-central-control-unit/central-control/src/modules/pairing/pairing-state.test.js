"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const test_helpers_1 = require("../../test-helpers");
const factsheetApi = __importStar(require("../factsheets/factsheets"));
const pairing_states_1 = require("./pairing-states");
const FIXED_SYSTEM_TIME = '2022-12-12T12:12:12Z';
describe('Test the PairingStates storage', () => {
    let factSpy;
    beforeEach(() => {
        (0, test_helpers_1.createMockMqttClient)();
        // mock the config for pairings
        jest.useFakeTimers();
        jest.setSystemTime(Date.parse(FIXED_SYSTEM_TIME));
        factSpy = jest.spyOn(factsheetApi, 'requestFactsheet').mockReturnValue(Promise.resolve());
    });
    afterEach(() => {
        jest.clearAllMocks();
        pairing_states_1.PairingStates.getInstance().reset();
    });
    it('should create only one PairingStates instance', () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const state2 = pairing_states_1.PairingStates.getInstance();
        expect(state1).toBe(state2);
    });
    it('should be empty for our tests', () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        expect(state1.getAll()).toHaveLength(0);
    });
    it('should add an entry for a module', async () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const deviceType = 'MODULE';
        const mockUpdate = {
            serialNumber: 'serial2',
            connectionState: vda_1.ConnectionState.ONLINE,
            headerId: 1,
            timestamp: new Date('2021-12-12T12:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockState = {
            type: deviceType,
            serialNumber: mockUpdate.serialNumber,
            pairedSince: undefined,
            connected: true,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            available: ccu_1.AvailableState.BLOCKED,
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        await state1.update(mockUpdate);
        expect(state1.getAll()).toEqual([mockState]);
    });
    it('should update the online state', async () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const deviceType = 'MODULE';
        const mockUpdate = {
            serialNumber: 'serial2',
            connectionState: vda_1.ConnectionState.ONLINE,
            headerId: 1,
            timestamp: new Date('2021-12-12T12:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockState = {
            type: deviceType,
            serialNumber: mockUpdate.serialNumber,
            pairedSince: undefined,
            connected: true,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            available: ccu_1.AvailableState.BLOCKED,
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        await state1.update(mockUpdate);
        expect(state1.getAll()).toEqual([mockState]);
        const mockUpdateOffline = {
            serialNumber: 'serial2',
            connectionState: vda_1.ConnectionState.CONNECTIONBROKEN,
            headerId: 1,
            timestamp: new Date('2021-12-12T13:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockStateOffline = {
            type: deviceType,
            serialNumber: mockUpdate.serialNumber,
            connected: false,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            available: ccu_1.AvailableState.BLOCKED,
            version: '0.0.0',
            ip: undefined,
        };
        await state1.update(mockUpdateOffline);
        expect(state1.getAll()).toEqual([mockStateOffline]);
        expect(factSpy).toHaveBeenCalledWith(mockStateOffline);
    });
    it('should update the online state from offline to online', async () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const deviceType = 'MODULE';
        const mockUpdateOffline = {
            serialNumber: 'serial2',
            connectionState: vda_1.ConnectionState.CONNECTIONBROKEN,
            headerId: 1,
            timestamp: new Date('2021-12-12T12:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockStateOffline = {
            type: deviceType,
            serialNumber: mockUpdateOffline.serialNumber,
            connected: false,
            available: ccu_1.AvailableState.BLOCKED,
            version: '0.0.0',
            ip: undefined,
        };
        await state1.update(mockUpdateOffline);
        expect(state1.getAll()).toEqual([mockStateOffline]);
        const mockUpdate2 = {
            serialNumber: 'serial2',
            connectionState: vda_1.ConnectionState.ONLINE,
            headerId: 1,
            timestamp: new Date('2021-12-12T13:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockState2 = {
            type: deviceType,
            serialNumber: mockUpdateOffline.serialNumber,
            connected: true,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            available: ccu_1.AvailableState.BLOCKED,
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        await state1.update(mockUpdate2);
        expect(state1.getAll()).toEqual([mockState2]);
        expect(factSpy).toHaveBeenCalledTimes(1);
        expect(factSpy).toHaveBeenCalledWith(mockState2);
    });
    it('should request a factsheet', async () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const deviceType = 'MODULE';
        const mockUpdate = {
            serialNumber: 'serial2',
            connectionState: vda_1.ConnectionState.ONLINE,
            headerId: 1,
            timestamp: new Date('2021-12-12T12:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockState = {
            type: deviceType,
            serialNumber: mockUpdate.serialNumber,
            connected: true,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            available: ccu_1.AvailableState.BLOCKED,
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        await state1.update(mockUpdate);
        expect(factSpy).toHaveBeenCalledWith(mockState);
    });
    it('should add a factsheet for a module', () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const factsheet = {
            version: '1',
            typeSpecification: {
                seriesName: 'TEST',
                navigationTypes: [],
            },
            agvGeometry: undefined,
            headerId: 0,
            loadSpecification: {},
            localizationParameters: undefined,
            manufacturer: 'MOCK',
            physicalParameters: undefined,
            protocolFeatures: {},
            protocolLimits: undefined,
            timestamp: new Date(),
            serialNumber: 'serial2',
        };
        state1.updateFacts(factsheet);
        expect(state1.getFactsheet('serial2')).toEqual(factsheet);
    });
    it('should update calibration availability', () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const factsheet = {
            version: '1',
            typeSpecification: {
                seriesName: 'TEST',
                navigationTypes: [],
            },
            agvGeometry: undefined,
            headerId: 0,
            loadSpecification: {},
            localizationParameters: undefined,
            manufacturer: 'MOCK',
            physicalParameters: undefined,
            protocolFeatures: {
                moduleActions: [
                    {
                        actionType: vda_1.InstantActions.CALIBRATION_START,
                    },
                ],
            },
            protocolLimits: undefined,
            timestamp: new Date(),
            serialNumber: 'serial2',
        };
        state1.updateFacts(factsheet);
        expect(state1.get('serial2')).toMatchObject({ hasCalibration: true });
    });
    it('should return the correct module type for a module', () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        const factsheet = {
            version: '1',
            typeSpecification: {
                seriesName: 'TEST',
                moduleClass: module_1.ModuleType.MILL,
                navigationTypes: [],
            },
            agvGeometry: undefined,
            headerId: 0,
            loadSpecification: {},
            localizationParameters: undefined,
            manufacturer: 'MOCK',
            physicalParameters: undefined,
            protocolFeatures: {},
            protocolLimits: undefined,
            timestamp: new Date(),
            serialNumber: 'serial2',
        };
        state1.updateFacts(factsheet);
        expect(state1.getModuleType('serial2')).toEqual(module_1.ModuleType.MILL);
    });
    it('should return no module type for a module without factsheet', () => {
        const state1 = pairing_states_1.PairingStates.getInstance();
        expect(state1.getModuleType('serialWithoutFactsheet')).toBeUndefined();
    });
    it('should return a PairedState if the module is connected, ready and no order id is present', async () => {
        // setup test data
        const underTest = pairing_states_1.PairingStates.getInstance();
        const serialNumber = 'test-serial-number';
        const moduleType = module_1.ModuleType.HBW;
        await setupGetAvailableState(serialNumber, underTest, moduleType);
        // actual test
        const actual = underTest.getReadyForModuleType(module_1.ModuleType.HBW, 'orderId');
        const expectedPartial = {
            type: 'MODULE',
            assigned: false,
            available: ccu_1.AvailableState.READY,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            pairedSince: new Date(FIXED_SYSTEM_TIME),
            connected: true,
            hasCalibration: false,
            subType: module_1.ModuleType.HBW,
            serialNumber,
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        expect(actual).toEqual(expectedPartial);
    });
    it('should return a PairedState if the module is connected, ready and an orderId is present and finished and equals the requested', async () => {
        // setup test data
        const underTest = pairing_states_1.PairingStates.getInstance();
        const orderId = 'orderId';
        const serialNumber = 'test-serial-number';
        const moduleType = module_1.ModuleType.HBW;
        await setupGetAvailableState(serialNumber, underTest, moduleType, orderId);
        // actual test
        const actual = underTest.getReadyForModuleType(module_1.ModuleType.HBW, orderId);
        const expectedPartial = {
            type: 'MODULE',
            assigned: true,
            available: ccu_1.AvailableState.READY,
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            pairedSince: new Date(FIXED_SYSTEM_TIME),
            connected: true,
            hasCalibration: false,
            subType: module_1.ModuleType.HBW,
            serialNumber,
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        expect(actual).toEqual(expectedPartial);
    });
    it('should not return a PairedState if the module is connected, ready and an orderId is present and finished but does not belongs to the same as requested', async () => {
        // setup test data
        const underTest = pairing_states_1.PairingStates.getInstance();
        const serialNumber = 'test-serial-number';
        const moduleType = module_1.ModuleType.HBW;
        await setupGetAvailableState(serialNumber, underTest, moduleType, 'orderId');
        // actual test
        const actual = underTest.getReadyForModuleType(module_1.ModuleType.HBW, 'second-order-id');
        expect(actual).toBeUndefined();
    });
    it('should succeed if the module with the serial is ready and an orderId is present and finished and equals the requested', async () => {
        // setup test data
        const underTest = pairing_states_1.PairingStates.getInstance();
        const orderId = 'orderId';
        const serialNumber = 'test-serial-number';
        const moduleType = module_1.ModuleType.HBW;
        await setupGetAvailableState(serialNumber, underTest, moduleType, orderId);
        // actual test
        const actual = underTest.isReadyForOrder(serialNumber, orderId);
        expect(actual).toEqual(true);
    });
    it('should fail if the module with the serial is ready and an orderId is present and finished but does not belongs to the same as requested', async () => {
        // setup test data
        const underTest = pairing_states_1.PairingStates.getInstance();
        const serialNumber = 'test-serial-number';
        const moduleType = module_1.ModuleType.HBW;
        await setupGetAvailableState(serialNumber, underTest, moduleType, 'orderId');
        // actual test
        const actual = underTest.isReadyForOrder(serialNumber, 'second-order-id');
        expect(actual).toBe(false);
    });
    it('should replace the paired state of all modules with the new module states setPairedModules is called', () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const firstPairedModules = [
            { type: module_1.ModuleType.MILL, serialNumber: 'serialM' },
            { type: module_1.ModuleType.DPS, serialNumber: 'serialD' },
            { type: module_1.ModuleType.AIQS, serialNumber: 'serialA' },
        ];
        const expectedFirstModules = [
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: new Date('2022-12-12T12:12:12.000Z'),
                productionDuration: 5,
                serialNumber: 'serialM',
                subType: 'MILL',
                type: 'MODULE',
            },
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: new Date('2022-12-12T12:12:12.000Z'),
                serialNumber: 'serialD',
                subType: 'DPS',
                type: 'MODULE',
            },
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: new Date('2022-12-12T12:12:12.000Z'),
                serialNumber: 'serialA',
                subType: 'AIQS',
                type: 'MODULE',
            },
        ];
        const secondPairedModules = [
            { type: module_1.ModuleType.MILL, serialNumber: 'serialM' },
            { type: module_1.ModuleType.AIQS, serialNumber: 'serialA' },
            { type: module_1.ModuleType.HBW, serialNumber: 'serialH' },
        ];
        const expectedSecondModules = [
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: new Date('2022-12-12T12:12:12.000Z'),
                productionDuration: 5,
                serialNumber: 'serialM',
                subType: 'MILL',
                type: 'MODULE',
            },
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: undefined,
                serialNumber: 'serialD',
                subType: 'DPS',
                type: 'MODULE',
            },
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: new Date('2022-12-12T12:12:12.000Z'),
                serialNumber: 'serialA',
                subType: 'AIQS',
                type: 'MODULE',
            },
            {
                available: 'BLOCKED',
                connected: false,
                pairedSince: new Date('2022-12-12T12:12:12.000Z'),
                serialNumber: 'serialH',
                subType: 'HBW',
                type: 'MODULE',
            },
        ];
        underTest.setPairedModules(firstPairedModules);
        expect(underTest.getAll()).toStrictEqual(expectedFirstModules);
        underTest.setPairedModules(secondPairedModules);
        expect(underTest.getAll()).toStrictEqual(expectedSecondModules);
    });
    it('should set the default production time when a paired production module is added', () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const module = { type: module_1.ModuleType.MILL, serialNumber: 'serialM' };
        underTest.setPairedModules([module]);
        expect(underTest.get(module.serialNumber)).toHaveProperty('productionDuration', 5);
    });
    it('should not set the default production time when a paired non-production module is added', () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const module = { type: module_1.ModuleType.DPS, serialNumber: 'serialM' };
        underTest.setPairedModules([module]);
        expect(underTest.get(module.serialNumber)).not.toHaveProperty('productionDuration');
    });
    it('should not set the default production time when a paired production module already had a time configured', () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const module = { type: module_1.ModuleType.MILL, serialNumber: 'serialM' };
        const NEW_DURATION = 35;
        underTest.setPairedModules([module]);
        underTest.updateDuration(module.serialNumber, NEW_DURATION);
        // check that the new duration has been set
        expect(underTest.get(module.serialNumber)).toHaveProperty('productionDuration', NEW_DURATION);
        // make sure the second call does update the pairing
        underTest.setPairedModules([]);
        expect(underTest.get(module.serialNumber)).toHaveProperty('pairedSince', undefined);
        underTest.setPairedModules([module]);
        expect(underTest.get(module.serialNumber)).toHaveProperty('pairedSince', expect.any(Date));
        // check that the new duration has been kept
        expect(underTest.get(module.serialNumber)).toHaveProperty('productionDuration', NEW_DURATION);
    });
    const setupGetAvailableState = async (serialNumber, underTest, moduleType, orderId) => {
        const mockConnection = {
            serialNumber,
            connectionState: vda_1.ConnectionState.ONLINE,
            headerId: 1,
            timestamp: new Date('2021-12-12T12:12:12Z'),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const mockFactsheet = {
            version: '1',
            typeSpecification: {
                seriesName: 'TEST',
                navigationTypes: [],
                moduleClass: moduleType,
            },
            agvGeometry: undefined,
            headerId: 0,
            loadSpecification: {},
            localizationParameters: undefined,
            manufacturer: 'MOCK',
            physicalParameters: undefined,
            protocolFeatures: {},
            protocolLimits: undefined,
            timestamp: new Date(),
            serialNumber,
        };
        await await underTest.updateAvailability('test-serial-number', ccu_1.AvailableState.BLOCKED);
        await underTest.update(mockConnection);
        underTest.updateFacts(mockFactsheet);
        underTest.setPairedModules([{ type: moduleType, serialNumber: serialNumber }]);
        expect(factSpy).toHaveBeenCalledTimes(1);
        await await underTest.updateAvailability(serialNumber, ccu_1.AvailableState.READY, orderId);
    };
    it('should return a the same module where the orderId has been set, when multiple of the same type are connected.', async () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const orderId = 'orderId';
        const testModuleType = module_1.ModuleType.MILL;
        const serialNumber1 = 'test-serial-number';
        const mod1 = mockModule(serialNumber1, testModuleType);
        const serialNumber2 = 'test-serial-number2';
        const mod2 = mockModule(serialNumber2, testModuleType);
        await underTest.update(mod1[0]);
        underTest.updateFacts(mod1[1]);
        await underTest.update(mod2[0]);
        underTest.updateFacts(mod2[1]);
        await await underTest.updateAvailability(serialNumber1, ccu_1.AvailableState.READY);
        await await underTest.updateAvailability(serialNumber2, ccu_1.AvailableState.READY, orderId);
        underTest.setPairedModules([
            { type: testModuleType, serialNumber: serialNumber1 },
            { type: testModuleType, serialNumber: serialNumber2 },
        ]);
        const actualReadyModule = underTest.getReadyForModuleType(testModuleType, orderId);
        expect(actualReadyModule).toBeDefined();
        expect(actualReadyModule?.serialNumber).toEqual(serialNumber2);
    });
    it('should return a the first module which is in the state READY and does not have an order associated with it', async () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const testModuleType = module_1.ModuleType.MILL;
        const serialNumber = 'test-serial-number';
        const orderId = 'orderId';
        const modReturned = mockModule(serialNumber, testModuleType);
        const modBlocked = mockModule('modBlocked', testModuleType);
        const modReadyForOrder = mockModule('modReadyForOrder', testModuleType);
        await underTest.update(modReturned[0]);
        underTest.updateFacts(modReturned[1]);
        await underTest.update(modBlocked[0]);
        underTest.updateFacts(modBlocked[1]);
        await underTest.update(modReadyForOrder[0]);
        underTest.updateFacts(modReadyForOrder[1]);
        await underTest.updateAvailability(serialNumber, ccu_1.AvailableState.READY);
        await underTest.updateAvailability(modBlocked[0].serialNumber, ccu_1.AvailableState.BLOCKED);
        await underTest.updateAvailability(modReadyForOrder[0].serialNumber, ccu_1.AvailableState.READY, 'orderNotReturned');
        underTest.setPairedModules([
            { type: testModuleType, serialNumber: serialNumber },
            { type: testModuleType, serialNumber: modBlocked[0].serialNumber },
            { type: testModuleType, serialNumber: modReadyForOrder[0].serialNumber },
        ]);
        const actualReadyModule = underTest.getReadyForModuleType(testModuleType, orderId);
        expect(actualReadyModule).toBeDefined();
        expect(actualReadyModule?.serialNumber).toEqual(serialNumber);
    });
    it('should return the first module which is connected and matches the module type if the orderId is not set', async () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const modType = module_1.ModuleType.MILL;
        const ser1 = 'test-serial-number';
        const ser2 = 'test-serial-number2';
        const mod1 = mockModule(ser1, modType);
        const mod2 = mockModule(ser2, modType);
        await underTest.update(mod1[0]);
        underTest.updateFacts(mod1[1]);
        await underTest.update(mod2[0]);
        underTest.updateFacts(mod2[1]);
        underTest.setPairedModules([
            { type: modType, serialNumber: ser1 },
            { type: modType, serialNumber: ser2 },
        ]);
        const actual = underTest.getForModuleType(modType);
        expect(actual).toBeDefined();
        expect(actual?.serialNumber).toEqual(ser1);
    });
    it('should return the module which is connected and set to a specific order', async () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const modType = module_1.ModuleType.MILL;
        const orderId = 'orderId';
        const ser1 = 'test-serial-number';
        const ser2 = 'test-serial-number2';
        const mod1 = mockModule(ser1, modType);
        const mod2 = mockModule(ser2, modType);
        await underTest.update(mod1[0]);
        underTest.updateFacts(mod1[1]);
        await underTest.update(mod2[0]);
        underTest.updateFacts(mod2[1]);
        await underTest.updateAvailability(ser2, ccu_1.AvailableState.READY, orderId);
        underTest.setPairedModules([
            { type: modType, serialNumber: ser1 },
            { type: modType, serialNumber: ser2 },
        ]);
        const actual = underTest.getForModuleType(modType, orderId);
        expect(actual).toBeDefined();
        expect(actual?.serialNumber).toEqual(ser2);
    });
    it('should return the module which is paired', async () => {
        const underTest = pairing_states_1.PairingStates.getInstance();
        const modType = module_1.ModuleType.MILL;
        const ser1 = 'test-serial-number';
        const ser2 = 'test-serial-number2';
        const mod1 = mockModule(ser1, modType);
        const mod2 = mockModule(ser2, modType);
        await underTest.update(mod1[0]);
        underTest.updateFacts(mod1[1]);
        await underTest.update(mod2[0]);
        underTest.updateFacts(mod2[1]);
        await underTest.updateAvailability(ser1, ccu_1.AvailableState.READY);
        await underTest.updateAvailability(ser2, ccu_1.AvailableState.READY);
        underTest.setPairedModules([{ type: modType, serialNumber: ser2 }]);
        const actual = underTest.getForModuleType(modType);
        expect(actual).toBeDefined();
        expect(actual?.serialNumber).toEqual(ser2);
        underTest.setPairedModules([{ type: modType, serialNumber: ser1 }]);
        const actual2 = underTest.getForModuleType(modType);
        expect(actual2).toBeDefined();
        expect(actual2?.serialNumber).toEqual(ser1);
    });
});
const mockModule = (serialNumber, moduleType) => {
    const mockConnection = {
        serialNumber,
        connectionState: vda_1.ConnectionState.ONLINE,
        headerId: 0,
        timestamp: new Date(),
        version: '1',
        manufacturer: 'MOCK',
        ip: '0.0.0.0',
    };
    const mockFactsheet = {
        version: '1',
        serialNumber,
        headerId: 0,
        timestamp: new Date(),
        manufacturer: 'MOCK',
        loadSpecification: {},
        typeSpecification: {
            moduleClass: moduleType,
            seriesName: 'TEST',
        },
        protocolFeatures: {},
    };
    return [mockConnection, mockFactsheet];
};
