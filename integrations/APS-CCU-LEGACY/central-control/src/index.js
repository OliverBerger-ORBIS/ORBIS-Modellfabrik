"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// Patching the console to include timestamps
const console_stamp_1 = __importDefault(require("console-stamp"));
(0, console_stamp_1.default)(console);
const path_1 = __importDefault(require("path"));
const config_1 = __importDefault(require("./config"));
const helpers_1 = require("./helpers");
const calibration_1 = require("./modules/calibration");
const current_errors_1 = require("./modules/current-errors");
const factsheets_1 = require("./modules/factsheets");
const fts_1 = require("./modules/fts");
const index_1 = require("./modules/fts/charge/index");
const order_1 = require("./modules/gateway/order");
const layout_1 = require("./modules/layout");
const default_reset_1 = require("./modules/layout/default_reset");
const factory_layout_service_1 = require("./modules/layout/factory-layout-service");
const order_2 = require("./modules/order");
const flow_1 = require("./modules/order/flow");
const order_flow_service_1 = require("./modules/order/flow/order-flow-service");
const order_management_1 = require("./modules/order/management/order-management");
const pairing_1 = require("./modules/pairing");
const pair_fts_1 = require("./modules/pairing/pair_fts");
const production_1 = require("./modules/production");
const cloud_stock_1 = require("./modules/production/cloud-stock");
const reset_1 = require("./modules/reset");
const park_1 = require("./modules/park");
const settings_1 = require("./modules/settings");
const version_checker_1 = require("./modules/version-checker");
const mqtt_1 = require("./mqtt/mqtt");
const config_2 = require("./services/config");
const general_config_service_1 = require("./services/config/general-config-service");
const delete_module_service_1 = __importDefault(require("./services/delete-module/delete-module.service"));
const protocol_1 = require("../../common/protocol");
const version_plausibility_service_1 = require("./modules/version-checker/version-plausibility-service");
const startUp = async () => {
    console.debug('Starting up the whole thing');
    console.debug(`Retrieving config values:
  - CHARGING: ${JSON.stringify(config_1.default.ftsCharge)}
  - ROUTING: ${JSON.stringify(config_1.default.routing)}
  - STORAGE: ${JSON.stringify(config_1.default.storage)}`);
    await general_config_service_1.GeneralConfigService.initialize(path_1.default.join(config_1.default.storage.path, config_1.default.storage.generalConfigFile));
    await factory_layout_service_1.FactoryLayoutService.initialize(path_1.default.join(config_1.default.storage.path, config_1.default.storage.layoutFile));
    await order_flow_service_1.OrderFlowService.initialize(path_1.default.join(config_1.default.storage.path, config_1.default.storage.flowsFile));
    console.debug('Initialize the mqtt client');
    const mqtt = await (0, mqtt_1.connectMqtt)();
    console.debug('MQTT Client ready');
    await version_plausibility_service_1.VersionPlausibilityService.initialize(config_1.default.storage.requiredVersionsPath);
    delete_module_service_1.default.initialize(mqtt);
    (0, helpers_1.subscribeTopics)(fts_1.TOPICS, fts_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(production_1.TOPICS, production_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(order_2.TOPICS, order_2.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(pairing_1.TOPICS, pairing_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(pair_fts_1.TOPICS, pair_fts_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(factsheets_1.TOPICS, factsheets_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(order_2.TOPICS_CANCEL_ORDER, order_2.TOPIC_OPTIONS_CANCEL_ORDER, mqtt);
    (0, helpers_1.subscribeTopics)(layout_1.TOPICS, layout_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(default_reset_1.TOPICS, default_reset_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(order_1.TOPICS, order_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(flow_1.TOPICS, flow_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(settings_1.TOPICS, settings_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(calibration_1.TOPICS, calibration_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(reset_1.TOPICS, reset_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(park_1.TOPICS, park_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(index_1.TOPICS, index_1.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(config_2.TOPICS, config_2.TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(current_errors_1.CURRENT_ERRORS_TOPICS, current_errors_1.CURRENT_ERRORS_TOPIC_OPTIONS, mqtt);
    (0, helpers_1.subscribeTopics)(version_checker_1.TOPICS, version_checker_1.TOPIC_OPTIONS, mqtt);
    // The layout can only be published after the connection has been established
    await factory_layout_service_1.FactoryLayoutService.publishLayout();
    await general_config_service_1.GeneralConfigService.publish();
    await order_flow_service_1.OrderFlowService.publishFlows();
    await (0, cloud_stock_1.updateActiveWarehouses)();
    await order_management_1.OrderManagement.getInstance().sendOrderListUpdate();
    mqtt.on('error', console.error); // TODO: some self repair implementation
    mqtt.on('close', console.error); // TODO: Maybe some self repair implementation
    mqtt.on('message', (topic, payload) => {
        const payloadAsString = payload.toString();
        try {
            if ((0, helpers_1.matchTopics)(current_errors_1.CURRENT_ERRORS_TOPICS, topic)) {
                void (0, current_errors_1.handleCurrentErrorsMessage)(payloadAsString);
            }
            if ((0, helpers_1.matchTopics)(fts_1.TOPICS, topic)) {
                void (0, fts_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(production_1.TOPICS, topic)) {
                void (0, production_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(order_2.TOPICS, topic)) {
                void (0, order_2.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(pairing_1.TOPICS, topic)) {
                void (0, pairing_1.handleMessage)(payloadAsString, topic); // async by design
            }
            else if ((0, helpers_1.matchTopics)(pair_fts_1.TOPICS, topic)) {
                void (0, pair_fts_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(factsheets_1.TOPICS, topic)) {
                void (0, factsheets_1.handleMessage)(payloadAsString, topic); // async by design
            }
            else if ((0, helpers_1.matchTopics)(order_2.TOPICS_CANCEL_ORDER, topic)) {
                void (0, order_2.handleCancelOrders)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(layout_1.TOPICS, topic)) {
                void (0, layout_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(default_reset_1.TOPICS, topic)) {
                void (0, default_reset_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(order_1.TOPICS, topic)) {
                void (0, order_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(flow_1.TOPICS, topic)) {
                void (0, flow_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(settings_1.TOPICS, topic)) {
                void (0, settings_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(calibration_1.TOPICS, topic)) {
                void (0, calibration_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(reset_1.TOPICS, topic)) {
                void (0, reset_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(park_1.TOPICS, topic)) {
                void (0, park_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(index_1.TOPICS, topic)) {
                void (0, index_1.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(config_2.TOPICS, topic)) {
                void (0, config_2.handleMessage)(payloadAsString); // async by design
            }
            else if ((0, helpers_1.matchTopics)(version_checker_1.TOPICS, topic)) {
                void (0, version_checker_1.handleMessage)(payloadAsString); // async by design
            }
            else {
                // NOTE: Some messages are handled by services within the modules, so we don't need to handle them here
                // console.warn(`No handler found to process message: [${payloadAsString}] on topic: [${topic}]`);
            }
        }
        catch (error) {
            console.error('Error while handling message', payloadAsString, 'on topic', topic, ':', error);
            // TODO: FITEFF22-346 Did anyone think of a solution on how to inform the user that this error occurred?
        }
    });
    // send global reset 30s after startup is finished
    setTimeout(() => {
        void mqtt.publish(protocol_1.CcuTopic.SET_RESET, JSON.stringify({ timestamp: new Date() }), { qos: 2 });
    }, 30000);
};
startUp()
    .then(() => {
    console.info('CCU startup successfully');
})
    .catch(error => console.error('Error:', error));
