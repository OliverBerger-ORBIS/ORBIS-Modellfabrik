"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../../common/protocol");
const json_revivers_1 = require("../../../../../common/util/json.revivers");
const order_flow_service_1 = require("./order-flow-service");
exports.TOPICS = [protocol_1.CcuTopic.SET_FLOWS];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
const handleMessage = async (message) => {
    const flows = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    // Some basic check to verify that the received object is most likely a valid ProductionsFlows object
    if (flows) {
        console.debug('handleMessage: set flows to ', flows);
        order_flow_service_1.OrderFlowService.setFlows(flows);
        const status = await Promise.allSettled([order_flow_service_1.OrderFlowService.publishFlows(), order_flow_service_1.OrderFlowService.saveFlows()]);
        if (status[0].status === 'rejected') {
            console.error('handleMessage: failed to publish flows: ', status[0].reason);
        }
        if (status[1].status === 'rejected') {
            console.error('handleMessage: failed to save flows: ', status[1].reason);
        }
    }
    else {
        console.error('handleMessage: set flows failed: Received object is not a valid ProductionFlows object: ', message);
    }
};
exports.handleMessage = handleMessage;
exports.default = exports.handleMessage;
