"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const pairing_states_1 = require("../pairing/pairing-states");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_1 = require("../pairing");
const stock_management_service_1 = require("../order/stock/stock-management-service");
const factory_layout_service_1 = require("../layout/factory-layout-service");
const version_plausibility_service_1 = require("../version-checker/version-plausibility-service");
exports.TOPICS = [(0, protocol_1.getModuleTopic)(protocol_1.ANY_SERIAL, protocol_1.ModuleTopic.FACTSHEET), (0, protocol_1.getFtsTopic)(protocol_1.ANY_SERIAL, protocol_1.FtsTopic.FACTSHEET)];
exports.TOPIC_OPTIONS = {
    qos: 1,
};
const handleMessage = async (message, topic) => {
    if (!message) {
        // Ignoring empty message
        return;
    }
    const facts = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    const modState = pairing_states_1.PairingStates.getInstance();
    const ftsState = fts_pairing_states_1.FtsPairingStates.getInstance();
    await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(facts, false);
    if (topic.startsWith(protocol_1.ModuleTopic.ROOT)) {
        modState.updateFacts(facts);
        const moduleType = modState.getModuleType(facts.serialNumber);
        if (moduleType) {
            console.debug('REPLACING PLACEHOLDER: ' + moduleType);
            await factory_layout_service_1.FactoryLayoutService.replacePlaceholder(moduleType, facts.serialNumber);
        }
        stock_management_service_1.StockManagementService.updateBaysFromModule(facts.serialNumber);
    }
    else if (topic.startsWith(protocol_1.FtsTopic.ROOT)) {
        ftsState.updateFacts(facts);
    }
    else {
        console.error('Unknown topic: ' + topic);
        return;
    }
    return (0, pairing_1.sendPairingState)(modState, ftsState);
};
exports.handleMessage = handleMessage;
