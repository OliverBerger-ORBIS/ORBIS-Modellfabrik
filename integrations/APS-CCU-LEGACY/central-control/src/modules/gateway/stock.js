"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.publishWarehouses = exports.publishGatewayStock = void 0;
const model_1 = require("./model");
const mqtt_1 = require("../../mqtt/mqtt");
const stock_management_service_1 = require("../order/stock/stock-management-service");
/**
 * Publish the given cloud stock to the local cloud gateway topics
 * @param stock
 */
const publishGatewayStock = (stock) => {
    return (0, mqtt_1.getMqttClient)().publish(model_1.GatewayPublishTopics.STOCK_TOPIC, JSON.stringify(stock), { qos: 1, retain: true });
};
exports.publishGatewayStock = publishGatewayStock;
const publishWarehouses = async () => {
    const info = {
        ts: new Date(),
        warehouses: stock_management_service_1.StockManagementService.getWarehouses(),
    };
    await (0, mqtt_1.getMqttClient)().publish(model_1.GatewayPublishTopics.HBW_CONFIG_TOPIC, JSON.stringify(info), { qos: 1, retain: true });
};
exports.publishWarehouses = publishWarehouses;
