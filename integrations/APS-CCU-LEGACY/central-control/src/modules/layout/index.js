"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const factory_layout_service_1 = require("./factory-layout-service");
const order_management_1 = require("../order/management/order-management");
const cloud_stock_1 = require("../production/cloud-stock");
exports.TOPICS = [protocol_1.CcuTopic.SET_LAYOUT];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
const handleMessage = async (message) => {
    const layout = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    // Some basic check to verify that the received object is most likely a valid FactoryJsonLayout
    if ('roads' in layout && 'modules' in layout && 'intersections' in layout) {
        factory_layout_service_1.FactoryLayoutService.setLayout(layout);
        await factory_layout_service_1.FactoryLayoutService.saveLayout();
        await factory_layout_service_1.FactoryLayoutService.publishLayout();
        await (0, cloud_stock_1.updateActiveWarehouses)();
        // try to resume orders and steps that were not possible with the old layout
        await order_management_1.OrderManagement.getInstance().resumeOrders();
    }
};
exports.handleMessage = handleMessage;
exports.default = exports.handleMessage;
