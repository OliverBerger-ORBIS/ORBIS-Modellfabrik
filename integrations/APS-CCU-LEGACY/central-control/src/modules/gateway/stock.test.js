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
const mqttMock = __importStar(require("../../mqtt/mqtt"));
const stock_1 = require("./stock");
describe('Test Gateway Stock publishing', () => {
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
    it('should publish stock update', async () => {
        const stock = {
            ts: MOCK_DATE,
            stockItems: [
                { location: 'A3', workpiece: { id: 'wp1', type: 'BLUE', state: 'RAW' } },
                { location: 'B2', workpiece: { id: 'wp2', type: 'RED', state: 'RAW' } },
                { location: 'C1', workpiece: { id: 'wp5', type: 'WHITE', state: 'RAW' } },
            ],
        };
        await (0, stock_1.publishGatewayStock)(stock);
        const expectedTopic = '/j1/txt/1/f/i/stock';
        const expectedMessage = JSON.stringify(stock);
        expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
    });
});
