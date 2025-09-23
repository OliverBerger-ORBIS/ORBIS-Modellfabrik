"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const general_config_service_1 = require("./general-config-service");
exports.TOPICS = [protocol_1.CcuTopic.SET_CONFIG];
exports.TOPIC_OPTIONS = {
    qos: 1,
};
const handleMessage = async (message) => {
    const config = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if ('productionDurations' in config) {
        await general_config_service_1.GeneralConfigService.saveConfig(config);
    }
};
exports.handleMessage = handleMessage;
exports.default = exports.handleMessage;
