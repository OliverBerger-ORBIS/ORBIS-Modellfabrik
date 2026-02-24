"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_crypto_1 = __importDefault(require("node:crypto"));
const protocol_1 = require("../../../../common/protocol");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const test_helpers_1 = require("../../test-helpers");
const order_management_1 = require("../order/management/order-management");
const stock_management_service_1 = require("../order/stock/stock-management-service");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_states_1 = require("../pairing/pairing-states");
const cloud_stock_1 = require("./cloud-stock");
jest.mock('../pairing/pairing-states');
jest.mock('../pairing/fts-pairing-states');
jest.mock('../order/management/order-management');
describe('test stockhandling', () => {
    let pairingStates;
    let ftsPairingStates;
    let orderManagement;
    const MOCKED_DATE = new Date('2021-01-01T00:00:00.000Z');
    beforeEach(() => {
        pairingStates = {
            updateAvailability: jest.fn(),
            getFactsheet: jest.fn(),
            getWorkpieceId: jest.fn(),
        };
        pairing_states_1.PairingStates.getInstance = jest.fn().mockReturnValue(pairingStates);
        ftsPairingStates = {
            clearLoadingBay: jest.fn(),
            getFtsSerialNumberForOrderId: jest.fn(),
        };
        fts_pairing_states_1.FtsPairingStates.getInstance = jest.fn().mockReturnValue(ftsPairingStates);
        orderManagement = {
            getWorkpieceId: jest.fn(),
            startNextOrder: jest.fn(),
        };
        order_management_1.OrderManagement.getInstance = jest.fn().mockReturnValue(orderManagement);
        jest.useFakeTimers().setSystemTime(MOCKED_DATE);
    });
    afterEach(() => {
        jest.clearAllMocks();
        jest.useRealTimers();
    });
    it('publishes updated stock to MQTT if module type is HBW', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.HBW;
        const actionState = {
            state: vda_1.State.FINISHED,
            command: module_1.ModuleCommandType.PICK,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const load = {
            loadPosition: 'A1',
            loadId: '2318',
            loadType: vda_1.LoadType.WHITE,
        };
        const load2 = {
            loadPosition: 'A2',
            loadId: '2314',
            loadType: vda_1.LoadType.RED,
        };
        const moduleState = {
            actionState: actionState,
            orderId,
            errors: [],
            orderUpdateId: 0,
            type: moduleType,
            timestamp: new Date(),
            paused: false,
            serialNumber,
            loads: [load, load2],
        };
        jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue({
            serialNumber,
            headerId: 1,
            timestamp: new Date(),
            version: '2',
            manufacturer: 'manufacturer',
            typeSpecification: {
                seriesName: 'seriesName',
                moduleClass: module_1.ModuleType.HBW,
            },
            protocolFeatures: {
                moduleParameters: {
                    clearModuleOnPick: false,
                },
            },
        });
        const mockedUUID = 'mockedUUID';
        const mqttClientMock = (0, test_helpers_1.createMockMqttClient)();
        jest.mock('node:crypto');
        node_crypto_1.default.randomUUID = jest.fn().mockReturnValue(mockedUUID);
        jest.spyOn(stock_management_service_1.StockManagementService, 'setStock');
        await (0, cloud_stock_1.handleStock)(moduleState);
        expect(stock_management_service_1.StockManagementService.setStock).toHaveBeenCalledWith(serialNumber, [load, load2]);
        expect(orderManagement.startNextOrder).toHaveBeenCalled();
        expect(pairingStates.getFactsheet).toHaveBeenCalledWith(serialNumber);
        expect(mqttClientMock.publish).toHaveBeenCalledWith('/j1/txt/1/f/i/stock', expect.anything(), {
            qos: 1,
            retain: true,
        });
        expect(mqttClientMock.publish).toHaveBeenCalledWith(protocol_1.CcuTopic.STOCK, expect.anything(), { qos: 1, retain: true });
    });
    it('should not publish an array with the stock of the HBW-Module, not the right module', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.DRILL;
        const actionState = {
            state: vda_1.State.FINISHED,
            command: module_1.ModuleCommandType.PICK,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const load = {
            loadPosition: 'A1',
            loadId: '2318',
            loadType: vda_1.LoadType.WHITE,
        };
        const load2 = {
            loadPosition: 'A2',
            loadId: '2314',
            loadType: vda_1.LoadType.RED,
        };
        const moduleState = {
            actionState: actionState,
            orderId,
            errors: [],
            orderUpdateId: 0,
            type: moduleType,
            timestamp: new Date(),
            paused: false,
            serialNumber,
            loads: [load, load2],
        };
        jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue({
            serialNumber,
            headerId: 1,
            timestamp: new Date(),
            version: '2',
            manufacturer: 'manufacturer',
            typeSpecification: {
                seriesName: 'seriesName',
                moduleClass: module_1.ModuleType.DRILL,
            },
            protocolFeatures: {
                moduleParameters: {
                    clearModuleOnPick: false,
                },
            },
        });
        const mqttClientMock = (0, test_helpers_1.createMockMqttClient)();
        await (0, cloud_stock_1.handleStock)(moduleState);
        expect(pairingStates.getFactsheet).toHaveBeenCalledWith(serialNumber);
        expect(mqttClientMock.publish).not.toHaveBeenCalled();
    });
    it('should map empty stock to an empty cloud stock', () => {
        const stock = [];
        const result = (0, cloud_stock_1.mapHbwToCloudStock)(stock, []);
        expect(result).toEqual({
            ts: expect.any(Date),
            stockItems: [],
        });
    });
    it('should map the stored stock to the correct cloud stock', () => {
        const stock = [
            {
                hbwSerial: 'hbwA',
                reserved: false,
                workpiece: {
                    loadId: 'wp1',
                    loadType: vda_1.LoadType.BLUE,
                    loadPosition: 'A1',
                },
            },
            {
                hbwSerial: 'hbwA',
                reserved: true,
                workpiece: {
                    loadId: 'wp2',
                    loadType: vda_1.LoadType.RED,
                    loadPosition: 'C3',
                },
            },
            {
                hbwSerial: 'hbwB',
                reserved: true,
                workpiece: {
                    loadId: 'wp3',
                    loadType: vda_1.LoadType.WHITE,
                    loadPosition: 'A2',
                },
            },
            {
                hbwSerial: 'hbwC',
                reserved: false,
                workpiece: {
                    loadId: 'wp4',
                    loadType: vda_1.LoadType.BLUE,
                    loadPosition: 'B2',
                },
            },
        ];
        const expectedResult = [
            {
                hbw: 'hbwA',
                location: 'A1',
                workpiece: {
                    id: 'wp1',
                    state: 'RAW',
                    type: 'BLUE',
                },
            },
            {
                hbw: 'hbwA',
                location: 'C3',
                workpiece: {
                    id: 'wp2',
                    state: 'RESERVED',
                    type: 'RED',
                },
            },
            {
                hbw: 'hbwB',
                location: 'A2',
                workpiece: {
                    id: 'wp3',
                    state: 'RESERVED',
                    type: 'WHITE',
                },
            },
            {
                hbw: 'hbwC',
                location: 'B2',
                workpiece: {
                    id: 'wp4',
                    state: 'RAW',
                    type: 'BLUE',
                },
            },
        ];
        const result = (0, cloud_stock_1.mapHbwToCloudStock)(stock, []);
        expect(result.stockItems).toEqual(expectedResult);
    });
    it('should fill unused bays as empty', () => {
        const stock = [
            {
                hbwSerial: 'hbwA',
                reserved: false,
                workpiece: {
                    loadId: 'wp1',
                    loadType: vda_1.LoadType.BLUE,
                    loadPosition: 'A1',
                },
            },
        ];
        const expectedResult = [
            {
                hbw: 'hbwA',
                location: 'A1',
                workpiece: {
                    id: 'wp1',
                    state: 'RAW',
                    type: 'BLUE',
                },
            },
            {
                hbw: 'hbwA',
                location: 'A2',
            },
            {
                hbw: 'hbwA',
                location: 'A3',
            },
            {
                hbw: 'hbwA',
                location: 'B1',
            },
            {
                hbw: 'hbwA',
                location: 'B2',
            },
            {
                hbw: 'hbwA',
                location: 'B3',
            },
            {
                hbw: 'hbwA',
                location: 'C1',
            },
            {
                hbw: 'hbwA',
                location: 'C2',
            },
            {
                hbw: 'hbwA',
                location: 'C3',
            },
        ];
        const result = (0, cloud_stock_1.mapHbwToCloudStock)(stock, ['hbwA']);
        expect(result.stockItems).toEqual(expectedResult);
    });
});
