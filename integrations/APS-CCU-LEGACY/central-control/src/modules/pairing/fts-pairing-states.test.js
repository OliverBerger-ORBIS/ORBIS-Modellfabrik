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
const vda_1 = require("../../../../common/protocol/vda");
const test_helpers_1 = require("../../test-helpers");
const factsheetApi = __importStar(require("../factsheets/factsheets"));
const loadingBayCache_1 = require("../fts/load/loadingBayCache");
const fts_pairing_states_1 = require("./fts-pairing-states");
const fts_1 = require("../../../../common/protocol/fts");
const FIXED_SYSTEM_TIME = '2022-12-12T12:12:12Z';
describe('Test the PairingStates storage', () => {
    let factSpy;
    beforeEach(() => {
        (0, test_helpers_1.createMockMqttClient)();
        jest.useFakeTimers();
        jest.setSystemTime(Date.parse(FIXED_SYSTEM_TIME));
        factSpy = jest.spyOn(factsheetApi, 'requestFactsheet').mockReturnValue(Promise.resolve());
    });
    afterEach(() => {
        jest.restoreAllMocks();
        fts_pairing_states_1.FtsPairingStates.getInstance().reset();
    });
    it('should create only one PairingStates instance', () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const state2 = fts_pairing_states_1.FtsPairingStates.getInstance();
        expect(state1).toBe(state2);
    });
    it('should be empty for our tests', () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        expect(state1.getAll()).toHaveLength(0);
    });
    it('should add an entry for an fts', async () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const deviceType = 'FTS';
        const mockUpdate = {
            serialNumber: 'serial',
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
        expect(state1.getAll()).toEqual([mockState]);
        expect(factSpy).toHaveBeenCalledWith(mockState);
    });
    it('should update the online state', async () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const deviceType = 'FTS';
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
        await await state1.update(mockUpdate);
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
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const deviceType = 'FTS';
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
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const deviceType = 'FTS';
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
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
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
    it('should update availability', async () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const serial = 'mocked';
        await state1.updateAvailability(serial, ccu_1.AvailableState.BLOCKED);
        expect(state1.get(serial)).toHaveProperty('available', ccu_1.AvailableState.BLOCKED);
        await state1.updateAvailability(serial, ccu_1.AvailableState.READY);
        expect(state1.get(serial)).toHaveProperty('available', ccu_1.AvailableState.READY);
        await state1.updateAvailability(serial, ccu_1.AvailableState.BUSY);
        expect(state1.get(serial)).toHaveProperty('available', ccu_1.AvailableState.BUSY);
    });
    it('should get the order ID loaded onto an FTS', () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const serial = 'mocked';
        const orderId = 'mockLoad';
        const loadPosition = '1';
        state1.setLoadingBay('mocked', loadPosition, orderId);
        expect(state1.getLoadedOrderIds(serial)).toEqual([orderId]);
    });
    it('should get all order IDs loaded onto an FTS', () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const serial = 'mocked';
        const orderId1 = 'mockLoad';
        const loadPosition1 = '1';
        const orderId2 = 'mockLoad2';
        const loadPosition2 = '2';
        state1.setLoadingBay('mocked', loadPosition1, orderId1);
        state1.setLoadingBay('mocked', loadPosition2, orderId2);
        expect(state1.getLoadedOrderIds(serial)).toEqual([orderId1, orderId2]);
    });
    it('should get no workpiece IDs when the FTS is empty', () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const serial = 'mocked';
        expect(state1.getLoadedOrderIds(serial)).toEqual([]);
    });
    it('should get the FTS with the assigned order ID', async () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const ftsSerialNumber = 'mocked';
        const orderId2 = 'mockLoad2';
        const loadPosition2 = '2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        state1.setLoadingBay(ftsSerialNumber, loadPosition2, orderId2);
        await state1.update(connection);
        await state1.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, orderId2, '1');
        const ftsPaired = state1.getForOrder(orderId2);
        expect(ftsPaired).toHaveProperty('serialNumber', ftsSerialNumber);
    });
    it('should get the FTS with the loaded workpiece ID', async () => {
        const state1 = fts_pairing_states_1.FtsPairingStates.getInstance();
        const ftsSerialNumber = 'mocked';
        const orderId1 = 'mockLoad';
        const loadPosition1 = '1';
        const orderId2 = 'mockLoad2';
        const loadPosition2 = '2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        state1.setLoadingBay(ftsSerialNumber, loadPosition1, orderId1);
        state1.setLoadingBay(ftsSerialNumber, loadPosition2, orderId2);
        await state1.update(connection);
        await state1.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, orderId2, '1');
        const ftsPaired = state1.getForOrder(orderId1);
        expect(ftsPaired).toHaveProperty('serialNumber', ftsSerialNumber);
    });
    it('should return true if an FTS is at the expected position with a reserved load for the order', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const loadPosition = '1';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForOrder').mockReturnValue(loadPosition);
        expect(underTest.isFtsWaitingAtPosition(orderId, targetSerialNumber)).toBeTruthy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForOrder).toHaveBeenCalledWith(ftsSerialNumber, orderId);
    });
    it('should return false if an FTS is at the expected position but has no load reserved for the workpiece', async () => {
        const workpieceId = 'workpieceId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForOrder').mockReturnValue(undefined);
        expect(underTest.isFtsWaitingAtPosition(workpieceId, targetSerialNumber)).toBeFalsy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForOrder).toHaveBeenCalledWith(ftsSerialNumber, workpieceId);
    });
    it('should return false if an FTS is not at the expected target position for the workpiece', async () => {
        const workpieceId = 'workpieceId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForOrder').mockReturnValue(undefined);
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', 'targetSerialNumber2');
        expect(underTest.isFtsWaitingAtPosition(workpieceId, targetSerialNumber)).toBeFalsy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForOrder).not.toHaveBeenCalled();
    });
    it('should return the fts pairing if a ready FTS is docked at the expected position with an empty bay', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const loadPosition = '1';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const ftsPairedModule = {
            available: ccu_1.AvailableState.READY,
            connected: true,
            lastLoadPosition: loadPosition,
            lastModuleSerialNumber: targetSerialNumber,
            lastNodeId: '1',
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            pairedSince: new Date(FIXED_SYSTEM_TIME),
            serialNumber: ftsSerialNumber,
            type: 'FTS',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber, loadPosition);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForOrder').mockReturnValue(undefined);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForFTS').mockReturnValue({ 1: undefined, 2: 'filled', 3: 'filled2' });
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'setLoadingBay').mockReturnValue();
        expect(underTest.getFtsAtPosition(targetSerialNumber, orderId)).toEqual(ftsPairedModule);
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForFTS).toHaveBeenCalledWith(ftsSerialNumber);
    });
    it('should return undefined if an FTS is at the expected position but has no empty loading bay', async () => {
        const workpieceId = 'workpieceId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const loadingBayId = '1';
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber, loadingBayId);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForOrder').mockReturnValue(undefined);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForFTS').mockReturnValue({ 1: 'filled', 2: undefined, 3: undefined });
        expect(underTest.getFtsAtPosition(targetSerialNumber, workpieceId)).toBeFalsy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForFTS).toHaveBeenCalledWith(ftsSerialNumber);
    });
    it('should return undefined if an FTS is not at the expected target position for the workpiece', async () => {
        const workpieceId = 'workpieceId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', 'targetSerialNumber2');
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForFTS').mockReturnValue({ 1: 'filled', 2: undefined, 3: undefined });
        expect(underTest.getFtsAtPosition(targetSerialNumber, workpieceId)).toBeFalsy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForFTS).not.toHaveBeenCalled();
    });
    it('should return undefined if an FTS is not ready at the expected target position for the workpiece', async () => {
        const workpieceId = 'workpieceId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.BLOCKED, undefined, '1', targetSerialNumber);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForFTS').mockReturnValue({ 1: 'filled', 2: undefined, 3: undefined });
        expect(underTest.getFtsAtPosition(targetSerialNumber, workpieceId)).toBeFalsy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForFTS).not.toHaveBeenCalled();
    });
    it('should return undefined if an FTS is not ready at the target position for any order', async () => {
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.BUSY, undefined, '1', targetSerialNumber);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForFTS').mockReturnValue({ 1: 'filled', 2: undefined, 3: undefined });
        expect(underTest.getFtsAtPosition(targetSerialNumber)).toBeFalsy();
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForFTS).not.toHaveBeenCalled();
    });
    it('should return the state if an FTS is ready at the target position for an order', async () => {
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const ftsPairedModule = {
            available: ccu_1.AvailableState.READY,
            connected: true,
            lastLoadPosition: '1',
            lastModuleSerialNumber: targetSerialNumber,
            lastNodeId: '1',
            lastSeen: new Date(FIXED_SYSTEM_TIME),
            pairedSince: new Date(FIXED_SYSTEM_TIME),
            serialNumber: ftsSerialNumber,
            type: 'FTS',
            version: '0.0.0',
            ip: '0.0.0.0',
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber, ftsPairedModule.lastLoadPosition);
        jest.spyOn(loadingBayCache_1.LoadingBayCache.getInstance(), 'getLoadingBayForFTS').mockReturnValue({ 1: 'filled', 2: undefined, 3: undefined });
        expect(underTest.getFtsAtPosition(targetSerialNumber)).toEqual(ftsPairedModule);
        expect(loadingBayCache_1.LoadingBayCache.getInstance().getLoadingBayForFTS).not.toHaveBeenCalled();
    });
    it('should return undefined if there is an FTS for the order and it is not ready', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const ftsSerialNumber2 = 'ftsSerialNumber2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const connection2 = {
            serialNumber: ftsSerialNumber2,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.update(connection2);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '2');
        await underTest.updateAvailability(ftsSerialNumber2, ccu_1.AvailableState.BUSY, orderId, '1', targetSerialNumber);
        expect(underTest.getReady(orderId)).toBeUndefined();
    });
    it('should return undefined if there is an FTS loaded for the order and it is not ready', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const ftsSerialNumber2 = 'ftsSerialNumber2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const connection2 = {
            serialNumber: ftsSerialNumber2,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.update(connection2);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '2');
        await underTest.updateAvailability(ftsSerialNumber2, ccu_1.AvailableState.BUSY, undefined, '1', targetSerialNumber);
        underTest.setLoadingBay(ftsSerialNumber2, '1', orderId);
        expect(underTest.getReady(orderId)).toBeUndefined();
    });
    it('should return the fts if there is a ready FTS for the order', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const ftsSerialNumber2 = 'ftsSerialNumber2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const connection2 = {
            serialNumber: ftsSerialNumber2,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.update(connection2);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '2');
        await underTest.updateAvailability(ftsSerialNumber2, ccu_1.AvailableState.READY, orderId, '1', targetSerialNumber);
        expect(underTest.getReady(orderId)).toMatchObject({ serialNumber: ftsSerialNumber2 });
    });
    it('should return the correct fts state if there is a ready FTS loaded for the order', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const ftsSerialNumber2 = 'ftsSerialNumber2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const connection2 = {
            serialNumber: ftsSerialNumber2,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.update(connection2);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '2');
        await underTest.updateAvailability(ftsSerialNumber2, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber);
        underTest.setLoadingBay(ftsSerialNumber2, '1', orderId);
        expect(underTest.getReady(orderId)).toMatchObject({ serialNumber: ftsSerialNumber2 });
    });
    it('should return the correct fts state if there is a ready FTS and another loaded for a different order', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const ftsSerialNumber2 = 'ftsSerialNumber2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const connection2 = {
            serialNumber: ftsSerialNumber2,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.update(connection2);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '2');
        await underTest.updateAvailability(ftsSerialNumber2, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber);
        underTest.setLoadingBay(ftsSerialNumber2, '1', 'anotherOrder');
        expect(underTest.getReady(orderId)).toMatchObject({ serialNumber: ftsSerialNumber });
    });
    it('should return a ready fts if there is one available without an order', async () => {
        const orderId = 'orderId';
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const ftsSerialNumber2 = 'ftsSerialNumber2';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const connection2 = {
            serialNumber: ftsSerialNumber2,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.update(connection2);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, 'someOrder', '2');
        await underTest.updateAvailability(ftsSerialNumber2, ccu_1.AvailableState.READY, undefined, '1', targetSerialNumber);
        expect(underTest.getReady(orderId)).toMatchObject({ serialNumber: ftsSerialNumber2 });
    });
    it('should set an FTS to unpaired and at an unknown module if it is at an unknown node', async () => {
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const expectedStateBefore = {
            serialNumber: ftsSerialNumber,
            type: 'FTS',
            pairedSince: new Date(),
            lastNodeId: targetSerialNumber,
            lastModuleSerialNumber: targetSerialNumber,
        };
        const expectedStateAfter = {
            serialNumber: ftsSerialNumber,
            type: 'FTS',
            pairedSince: undefined,
            lastNodeId: fts_1.NODE_ID_UNKNOWN,
            lastModuleSerialNumber: fts_1.NODE_ID_UNKNOWN,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, targetSerialNumber, targetSerialNumber);
        expect(underTest.get(ftsSerialNumber)).toMatchObject(expectedStateBefore);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.BLOCKED, undefined, fts_1.NODE_ID_UNKNOWN);
        expect(underTest.get(ftsSerialNumber)).toMatchObject(expectedStateAfter);
    });
    it('should return true if an FTS is ready to work on the given order', async () => {
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const orderId = 'orderId';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, targetSerialNumber, targetSerialNumber);
        expect(underTest.isReadyForOrder(ftsSerialNumber, orderId)).toBeTruthy();
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, orderId, targetSerialNumber, targetSerialNumber);
        expect(underTest.isReadyForOrder(ftsSerialNumber, orderId)).toBeTruthy();
    });
    it('should return false if an FTS is ready, but not for the given order', async () => {
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const orderId = 'orderId';
        const anotherOrderId = 'anotherOrderId';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.READY, anotherOrderId, targetSerialNumber, targetSerialNumber);
        expect(underTest.isReadyForOrder(ftsSerialNumber, orderId)).toBeFalsy();
    });
    it('should return false if an FTS is not ready', async () => {
        const targetSerialNumber = 'targetSerialNumber';
        const ftsSerialNumber = 'ftsSerialNumber';
        const orderId = 'orderId';
        const anotherOrderId = 'anotherOrderId';
        const connection = {
            serialNumber: ftsSerialNumber,
            timestamp: new Date(),
            manufacturer: 'MOCK',
            version: '0.0.0',
            ip: '0.0.0.0',
            headerId: 0,
            connectionState: vda_1.ConnectionState.ONLINE,
        };
        const underTest = fts_pairing_states_1.FtsPairingStates.getInstance();
        await underTest.update(connection);
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.BUSY, undefined, targetSerialNumber, targetSerialNumber);
        expect(underTest.isReadyForOrder(ftsSerialNumber, orderId)).toBeFalsy();
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.BUSY, orderId, targetSerialNumber, targetSerialNumber);
        expect(underTest.isReadyForOrder(ftsSerialNumber, orderId)).toBeFalsy();
        await underTest.updateAvailability(ftsSerialNumber, ccu_1.AvailableState.BUSY, anotherOrderId, targetSerialNumber, targetSerialNumber);
        expect(underTest.isReadyForOrder(ftsSerialNumber, orderId)).toBeFalsy();
    });
});
