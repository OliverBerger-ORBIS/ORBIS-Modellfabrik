"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../../common/protocol");
const json_revivers_1 = require("../../../../../common/util/json.revivers");
const mqtt_1 = require("../../../mqtt/mqtt");
const model_1 = require("../model");
exports.TOPICS = [model_1.GatewaySubscriptionTopics.ORDER_TOPIC];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
const handleMessage = async (message) => {
    const gatewayOrder = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if (!(gatewayOrder && gatewayOrder.type && gatewayOrder.ts)) {
        console.debug('handleMessage for gateway: received invalid order: ', gatewayOrder);
        return;
    }
    const order = {
        type: gatewayOrder.type,
        timestamp: gatewayOrder.ts,
        orderType: 'PRODUCTION',
    };
    return (0, mqtt_1.getMqttClient)().publish(protocol_1.CcuTopic.ORDER_REQUEST, JSON.stringify(order), { qos: 2 });
};
exports.handleMessage = handleMessage;
