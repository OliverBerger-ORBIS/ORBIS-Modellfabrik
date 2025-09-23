"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../../common/protocol");
const json_revivers_1 = require("../../../../../common/util/json.revivers");
const factory_layout_service_1 = require("../factory-layout-service");
exports.TOPICS = [protocol_1.CcuTopic.SET_DEFAULT_LAYOUT];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
const handleMessage = async (message) => {
    const layout = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    // Some basic check to verify that the received object is most likely a valid FactoryJsonLayout
    if (layout.timestamp) {
        await factory_layout_service_1.FactoryLayoutService.resetToDefaultLayout();
    }
};
exports.handleMessage = handleMessage;
exports.default = exports.handleMessage;
