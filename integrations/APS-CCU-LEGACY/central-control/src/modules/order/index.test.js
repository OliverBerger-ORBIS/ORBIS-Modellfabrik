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
const module_1 = require("../../../../common/protocol/module");
const ccu_1 = require("../../../../common/protocol/ccu");
const index_1 = require("./index");
const localMqtt = __importStar(require("../../mqtt/mqtt"));
const protocol_1 = require("../../../../common/protocol");
const order_management_1 = require("./management/order-management");
const stateMock = __importStar(require("../state"));
const stock_management_service_1 = require("./stock/stock-management-service");
describe('Test order request handling', () => {
    const MOCK_DATE = new Date('2023-05-10T07:55:58.510Z');
    beforeEach(() => {
        jest.spyOn(stateMock, 'addOrderLogEntry').mockImplementation(jest.fn());
        jest.useFakeTimers().setSystemTime(MOCK_DATE);
    });
    afterEach(() => {
        jest.clearAllMocks();
        jest.useRealTimers();
    });
    it('should convert production definition to a list of response steps', () => {
        const actionIdProduction = 'actionIdProduction';
        const actionIdNavIndependent = 'actionIdNavIndependent';
        const actionIdNavDependent = 'actionIdNavDependent';
        const navTypeIndependent = {
            id: actionIdNavIndependent,
            target: module_1.ModuleType.DRILL,
            source: module_1.ModuleType.START,
            state: ccu_1.OrderState.ENQUEUED,
            type: 'NAVIGATION',
        };
        const navTypeDependent = {
            id: actionIdNavDependent,
            target: module_1.ModuleType.DPS,
            source: module_1.ModuleType.DRILL,
            dependentActionId: actionIdProduction,
            state: ccu_1.OrderState.ENQUEUED,
            type: 'NAVIGATION',
        };
        const prodType = {
            id: actionIdProduction,
            dependentActionId: actionIdNavIndependent,
            command: module_1.ModuleCommandType.DRILL,
            moduleType: module_1.ModuleType.DRILL,
            state: ccu_1.OrderState.ENQUEUED,
            type: 'MANUFACTURE',
        };
        const prodDef = {
            navigationSteps: [navTypeIndependent, navTypeDependent],
            productionSteps: [prodType],
        };
        const actualResponseSteps = (0, index_1.generateOrderStepList)(prodDef);
        const expededResponseSteps = [
            {
                id: actionIdNavIndependent,
                type: 'NAVIGATION',
                target: module_1.ModuleType.DRILL,
                source: module_1.ModuleType.START,
                state: ccu_1.OrderState.ENQUEUED,
            },
            {
                id: actionIdProduction,
                type: 'MANUFACTURE',
                moduleType: module_1.ModuleType.DRILL,
                command: module_1.ModuleCommandType.DRILL,
                dependentActionId: actionIdNavIndependent,
                state: ccu_1.OrderState.ENQUEUED,
            },
            {
                id: actionIdNavDependent,
                type: 'NAVIGATION',
                target: module_1.ModuleType.DPS,
                source: module_1.ModuleType.DRILL,
                dependentActionId: actionIdProduction,
                state: ccu_1.OrderState.ENQUEUED,
            },
        ];
        expect(actualResponseSteps.length).toBe(expededResponseSteps.length);
        expect(actualResponseSteps).toEqual(expededResponseSteps);
        expect(actualResponseSteps).toStrictEqual(expededResponseSteps);
        expect(actualResponseSteps).toStrictEqual(expededResponseSteps);
    });
    it('should send the correct order response including the set workpiece id', async () => {
        const workpieceId = '04339d7adb7281';
        const type = 'WHITE';
        const storageOrderJson = `{
      "orderType": "STORAGE",
      "timestamp": "2023-05-10T07:33:16.154840Z",
      "type": "${type}",
      "workpieceId": "${workpieceId}"
    }`;
        const storageOrder = JSON.parse(storageOrderJson);
        const orderId = 'order-id-123';
        const productionDefinition = {
            navigationSteps: [],
            productionSteps: [],
        };
        const mqtt = {
            publish: () => Promise.resolve(),
        };
        jest.spyOn(mqtt, 'publish');
        jest.spyOn(localMqtt, 'getMqttClient').mockReturnValue(mqtt);
        jest.mock('./management/order-management');
        jest.spyOn(order_management_1.OrderManagement, 'getInstance').mockReturnValue({
            cacheOrder: jest.fn().mockResolvedValue(Promise.resolve()),
        });
        await (0, index_1.sendResponse)(storageOrder, orderId, productionDefinition);
        const expectedOrderResponse = {
            orderType: 'STORAGE',
            type,
            timestamp: storageOrder.timestamp,
            orderId,
            productionSteps: [],
            receivedAt: MOCK_DATE,
            state: ccu_1.OrderState.ENQUEUED,
            workpieceId,
        };
        expect(order_management_1.OrderManagement.getInstance().cacheOrder).toHaveBeenCalledWith(expectedOrderResponse);
        expect(mqtt.publish).toHaveBeenCalledWith(protocol_1.CcuTopic.ORDER_RESPONSE, JSON.stringify(expectedOrderResponse));
    });
    it('should validate that a storage order can be generated', async () => {
        const prodDef = {
            navigationSteps: [{ id: 'first', source: module_1.ModuleType.START, target: module_1.ModuleType.DPS, type: 'NAVIGATION', state: ccu_1.OrderState.ENQUEUED }],
            productionSteps: [],
        };
        const orderRequest = {
            orderType: 'STORAGE',
            type: 'RED',
            timestamp: new Date(),
            workpieceId: 'workpieceId',
        };
        jest.spyOn(stock_management_service_1.StockManagementService, 'reserveEmptyBay').mockReturnValue('hbwId');
        const result = await (0, index_1.validateStorageOrderRequestAndReserveBay)(prodDef, 'orderId', orderRequest);
        expect(result).toBeTruthy();
    });
    it('should fail if a storage order has no navigation steps', async () => {
        const prodDef = {
            navigationSteps: [],
            productionSteps: [],
        };
        const orderRequest = {
            orderType: 'STORAGE',
            type: 'RED',
            timestamp: new Date(),
            workpieceId: 'workpieceId',
        };
        const result = await (0, index_1.validateStorageOrderRequestAndReserveBay)(prodDef, 'orderId', orderRequest);
        expect(result).toBeFalsy();
    });
    it('should fail if a storage order cannot be stored', async () => {
        const prodDef = {
            navigationSteps: [{ id: 'first', source: module_1.ModuleType.START, target: module_1.ModuleType.DPS, type: 'NAVIGATION', state: ccu_1.OrderState.ENQUEUED }],
            productionSteps: [],
        };
        const orderRequest = {
            orderType: 'STORAGE',
            type: 'RED',
            timestamp: new Date(),
            workpieceId: 'workpieceId',
        };
        jest.spyOn(stock_management_service_1.StockManagementService, 'reserveEmptyBay').mockReturnValue(undefined);
        const result = await (0, index_1.validateStorageOrderRequestAndReserveBay)(prodDef, 'orderId', orderRequest);
        expect(result).toBeFalsy();
    });
});
