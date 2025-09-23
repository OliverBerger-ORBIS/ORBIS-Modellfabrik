"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.publishGatewayOrderUpdate = void 0;
const ccu_1 = require("../../../../../common/protocol/ccu");
const model_1 = require("../model");
const mqtt_1 = require("../../../mqtt/mqtt");
/**
 * Get the first order that has the given order state
 * @param orders
 * @param state
 */
const getFirstOrderWithState = (orders, state) => {
    return orders.find(order => order.state === state);
};
/**
 * Publishes an overall order state for the given list of orders
 * The states are sent in this manner as an {@link GatewayOrderStateEnum}
 *  - `INPROCESS` - if any order is in progress
 *  - `ORDERED` - if no order is in progress but there is an enqueued order
 *  - `WAITINGFORORDER` - if no order is in process and none are enqueued
 *
 * @param orders
 */
const publishGatewayOrderUpdate = async (orders) => {
    let orderState = model_1.GatewayOrderStateEnum.WAITINGFORORDER;
    let type = undefined;
    // naive translation of the states of all orders to a singular state for the order component
    const order = getFirstOrderWithState(orders, ccu_1.OrderState.IN_PROGRESS) ?? getFirstOrderWithState(orders, ccu_1.OrderState.ENQUEUED);
    if (order) {
        type = order.type;
        switch (order.state) {
            case ccu_1.OrderState.IN_PROGRESS:
                orderState = model_1.GatewayOrderStateEnum.INPROCESS;
                break;
            case ccu_1.OrderState.ENQUEUED:
                orderState = model_1.GatewayOrderStateEnum.ORDERED;
                break;
        }
    }
    const gatewayOrder = {
        ts: new Date(),
        type,
        state: orderState,
    };
    return (0, mqtt_1.getMqttClient)().publish(model_1.GatewayPublishTopics.ORDER_STATE, JSON.stringify(gatewayOrder), {
        retain: true,
        qos: 1,
    });
};
exports.publishGatewayOrderUpdate = publishGatewayOrderUpdate;
