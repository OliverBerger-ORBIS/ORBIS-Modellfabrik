"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const helper_1 = require("./helper");
const state_1 = require("../state");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const order_management_1 = require("../order/management/order-management");
exports.TOPICS = [(0, protocol_1.getFtsTopic)(protocol_1.ANY_SERIAL, protocol_1.FtsTopic.STATE)];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
const handleMessage = async (message) => {
    const state = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    await (0, state_1.addFtsLogEntry)(state);
    await (0, helper_1.handleFtsState)(state);
    if (state.actionState?.id) {
        console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${state.orderId} and action id: ${state.actionState.id}`);
        return order_management_1.OrderManagement.getInstance().handleActionUpdate(state.orderId, state.actionState.id, state.actionState.state);
    }
};
exports.handleMessage = handleMessage;
exports.default = exports.handleMessage;
