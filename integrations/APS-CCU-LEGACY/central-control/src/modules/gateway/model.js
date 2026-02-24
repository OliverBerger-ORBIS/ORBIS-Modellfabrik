"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GatewayOrderStateEnum = exports.GatewaySubscriptionTopics = exports.GatewayPublishTopics = exports.GW_LOCAL_CONTROLLER_TOPIC_BASE = exports.GW_LOCAL_CONTROLLER_ID = exports.Workpiece = void 0;
var protocol_1 = require("../../../../common/protocol");
Object.defineProperty(exports, "Workpiece", { enumerable: true, get: function () { return protocol_1.Workpiece; } });
exports.GW_LOCAL_CONTROLLER_ID = '1';
exports.GW_LOCAL_CONTROLLER_TOPIC_BASE = `/j1/txt/${exports.GW_LOCAL_CONTROLLER_ID}`;
exports.GatewayPublishTopics = {
    ORDER_STATE: `${exports.GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/i/order`,
    STOCK_TOPIC: `${exports.GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/i/stock`,
    HBW_CONFIG_TOPIC: `${exports.GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/i/config/hbw`,
};
exports.GatewaySubscriptionTopics = {
    ALL_TOPICS: `${exports.GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/o/#`,
    ORDER_TOPIC: `${exports.GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/o/order`,
};
var GatewayOrderStateEnum;
(function (GatewayOrderStateEnum) {
    GatewayOrderStateEnum["WAITINGFORORDER"] = "WAITING_FOR_ORDER";
    GatewayOrderStateEnum["ORDERED"] = "ORDERED";
    GatewayOrderStateEnum["INPROCESS"] = "IN_PROCESS";
    GatewayOrderStateEnum["SHIPPED"] = "SHIPPED";
})(GatewayOrderStateEnum = exports.GatewayOrderStateEnum || (exports.GatewayOrderStateEnum = {}));
