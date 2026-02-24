"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const version_plausibility_service_1 = require("./version-plausibility-service");
exports.TOPICS = [(0, protocol_1.getModuleTopic)('NodeRed/' + protocol_1.ANY_SERIAL, protocol_1.ModuleTopic.FACTSHEET)];
exports.TOPIC_OPTIONS = {
    qos: 1,
};
const handleMessage = async (message) => {
    if (!message) {
        // Ignoring empty message
        return;
    }
    console.debug('TXT-24V: received factsheet');
    const facts = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if (facts.serialNumber && facts.typeSpecification?.seriesName) {
        await version_plausibility_service_1.VersionPlausibilityService.registerModuleVersion(facts, true);
    }
};
exports.handleMessage = handleMessage;
