"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vda_1 = require("../../../../common/protocol/vda");
const mqtt_1 = require("../../mqtt/mqtt");
const test_helpers_1 = require("../../test-helpers");
const factsheets_1 = require("./factsheets");
jest.mock('uuid', () => ({ v4: () => '12345-6789-ABCDEF' }));
describe('Test requesting and recieving factsheets', () => {
    let mqtt;
    const MOCKED_DATE = new Date('2023-02-010T10:20:19Z');
    beforeEach(() => {
        mqtt = (0, test_helpers_1.createMockMqttClient)();
        jest.useFakeTimers().setSystemTime(MOCKED_DATE);
    });
    afterEach(() => {
        jest.clearAllMocks();
        jest.useRealTimers();
    });
    it('should be able to request an factshet', async () => {
        const module = {
            type: 'MODULE',
            serialNumber: 'mockedSerial',
        };
        await (0, factsheets_1.requestFactsheet)(module);
        const topic = `module/v1/ff/mockedSerial/instantAction`;
        const action = {
            timestamp: MOCKED_DATE,
            serialNumber: module.serialNumber,
            actions: [{ actionId: '12345-6789-ABCDEF', actionType: vda_1.InstantActions.FACTSHEET_REQUEST }],
        };
        expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(action), { qos: 2 });
        expect(mqtt_1.getMqttClient).toHaveBeenCalled();
    });
});
