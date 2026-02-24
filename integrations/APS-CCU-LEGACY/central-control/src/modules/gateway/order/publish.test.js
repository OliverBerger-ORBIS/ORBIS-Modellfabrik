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
const publish_1 = require("./publish");
const mqttMock = __importStar(require("../../../mqtt/mqtt"));
const ccu_1 = require("../../../../../common/protocol/ccu");
const model_1 = require("../model");
describe('Test Gateway publishing', () => {
    let mqttPublishSpy;
    const MOCK_DATE = new Date('2022-02-03T11:12:13.1234Z');
    beforeEach(() => {
        mqttPublishSpy = jest.fn().mockImplementation(() => Promise.resolve());
        jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({ publish: mqttPublishSpy });
        jest.useFakeTimers();
        jest.setSystemTime(MOCK_DATE);
    });
    afterEach(() => {
        jest.clearAllTimers();
        jest.restoreAllMocks();
    });
    it('should publish an in-progress order state when any order is in progress', async () => {
        const orders = [
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.CANCELLED,
                orderId: '1',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.ERROR,
                orderId: '2',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.FINISHED,
                orderId: '3',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.IN_PROGRESS,
                orderId: '4',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.ENQUEUED,
                orderId: '5',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
        ];
        await (0, publish_1.publishGatewayOrderUpdate)(orders);
        const expectedTopic = '/j1/txt/1/f/i/order';
        const expectedMessage = JSON.stringify({ ts: MOCK_DATE, type: 'BLUE', state: model_1.GatewayOrderStateEnum.INPROCESS });
        expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
    });
    it('should publish an ordered order state when any order is enqueued and none is in progress', async () => {
        const orders = [
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.CANCELLED,
                orderId: '1',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.ERROR,
                orderId: '2',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.FINISHED,
                orderId: '3',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.ENQUEUED,
                orderId: '4',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.CANCELLED,
                orderId: '5',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
        ];
        await (0, publish_1.publishGatewayOrderUpdate)(orders);
        const expectedTopic = '/j1/txt/1/f/i/order';
        const expectedMessage = JSON.stringify({ ts: MOCK_DATE, type: 'BLUE', state: model_1.GatewayOrderStateEnum.ORDERED });
        expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
    });
    it('should publish an waiting for order state when no order is waiting or in progress', async () => {
        const orders = [
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.CANCELLED,
                orderId: '1',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.ERROR,
                orderId: '2',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.FINISHED,
                orderId: '3',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
            {
                orderType: 'PRODUCTION',
                state: ccu_1.OrderState.CANCELLED,
                orderId: '5',
                type: 'BLUE',
                timestamp: new Date(),
                productionSteps: [],
                workpieceId: '',
            },
        ];
        await (0, publish_1.publishGatewayOrderUpdate)(orders);
        const expectedTopic = '/j1/txt/1/f/i/order';
        const expectedMessage = JSON.stringify({ ts: MOCK_DATE, state: model_1.GatewayOrderStateEnum.WAITINGFORORDER });
        expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
    });
});
