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
const index_1 = require("./index");
const mqttMock = __importStar(require("../../../mqtt/mqtt"));
const protocol_1 = require("../../../../../common/protocol");
describe('Test Gateway handler', () => {
    let mqttPublishSpy;
    beforeEach(() => {
        mqttPublishSpy = jest.fn().mockImplementation(() => Promise.resolve());
        jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({ publish: mqttPublishSpy });
    });
    afterEach(() => {
        jest.restoreAllMocks();
    });
    const testGatewayOrderType = async (workpieceType, timestampString) => {
        const givenGatewayOrder = `{"type": "${workpieceType}", "ts": "${timestampString}"}`;
        const expectedOrder = {
            type: workpieceType,
            timestamp: new Date(timestampString),
            orderType: 'PRODUCTION',
        };
        await (0, index_1.handleMessage)(givenGatewayOrder);
        expect(mqttPublishSpy).toHaveBeenCalledWith(protocol_1.CcuTopic.ORDER_REQUEST, JSON.stringify(expectedOrder), { qos: 2 });
    };
    it('should have the correct topic to subscribe to', () => {
        const sourceTopic = '/j1/txt/1/f/o/order';
        expect(index_1.TOPICS).toContain(sourceTopic);
    });
    it('should send the correct order for a received cloud order for a RED workpiece', async () => {
        const timestampString = '2022-02-03T12:13:14.1234Z';
        const workpieceType = 'RED';
        await testGatewayOrderType(workpieceType, timestampString);
    });
    it('should send the correct order for a received cloud order for a WHITE workpiece', async () => {
        const timestampString = '2022-02-03T12:13:14.1234Z';
        const workpieceType = 'WHITE';
        await testGatewayOrderType(workpieceType, timestampString);
    });
    it('should send the correct order for a received cloud order for a BLUE workpiece', async () => {
        const timestampString = '2022-02-03T12:13:14.1234Z';
        const workpieceType = 'BLUE';
        await testGatewayOrderType(workpieceType, timestampString);
    });
    it('should not send an order for an incomplete request missing the timestamp', async () => {
        const workpieceType = 'BLUE';
        const givenGatewayOrder = `{"type": "${workpieceType}"}`;
        await (0, index_1.handleMessage)(givenGatewayOrder);
        expect(mqttPublishSpy).not.toHaveBeenCalled();
    });
    it('should not send an order for an incomplete request missing the workpiece', async () => {
        const timestampString = '2022-02-03T12:13:14.1234Z';
        const givenGatewayOrder = `{"ts": "${timestampString}"}`;
        await (0, index_1.handleMessage)(givenGatewayOrder);
        expect(mqttPublishSpy).not.toHaveBeenCalled();
    });
});
