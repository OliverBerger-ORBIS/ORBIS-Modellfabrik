"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestFactsheet = void 0;
const mqtt_1 = require("../../mqtt/mqtt");
const protocol_1 = require("../../../../common/protocol");
const vda_1 = require("../../../../common/protocol/vda");
const uuid_1 = require("uuid");
async function requestFactsheet(module) {
    const mqtt = (0, mqtt_1.getMqttClient)();
    let topic;
    switch (module.type) {
        case 'MODULE':
            topic = (0, protocol_1.getModuleTopic)(module.serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION);
            break;
        case 'FTS':
            topic = (0, protocol_1.getFtsTopic)(module.serialNumber, protocol_1.FtsTopic.INSTANT_ACTION);
            break;
        default:
            throw Error('Unknown module type');
    }
    const action = {
        timestamp: new Date(),
        serialNumber: module.serialNumber,
        actions: [{ actionId: (0, uuid_1.v4)(), actionType: vda_1.InstantActions.FACTSHEET_REQUEST }],
    };
    return mqtt.publish(topic, JSON.stringify(action), { qos: 2 });
}
exports.requestFactsheet = requestFactsheet;
